import hashlib
import os
import sqlite3
import uuid
from datetime import datetime

from app import utils


def ensure_schema() -> None:
    """
    执行数据库迁移
    """
    conn = sqlite3.connect("Smart_Signing_Guardian.db")
    cur = conn.cursor()
    try:
        _ensure_file_traces_table(cur)
        _ensure_column(cur, "users", "uuid", "VARCHAR(64)")
        _ensure_column(cur, "users", "public_key", "TEXT")
        _ensure_column(cur, "files", "file_uuid", "VARCHAR(64)")
        _ensure_column(cur, "files", "owner_uuid", "VARCHAR(64)")
        _ensure_column(cur, "files", "signature", "TEXT")
        _ensure_column(cur, "files", "sign_user_uuid", "VARCHAR(64)")
        _ensure_column(cur, "files", "original_filename", "VARCHAR(255)")
        _ensure_column(cur, "files", "tracking_id", "VARCHAR(64)")
        _ensure_column(cur, "files", "version_no", "INTEGER")
        _ensure_column(cur, "files", "raw_hash", "VARCHAR(255)")
        _ensure_column(cur, "files", "is_deleted", "INTEGER")
        _ensure_column(cur, "files", "deleted_at", "VARCHAR(32)")
        _ensure_column(cur, "file_traces", "file_uuid", "VARCHAR(64)")
        _ensure_column(cur, "file_traces", "tracking_id", "VARCHAR(64)")
        _backfill_original_filename(cur)
        _backfill_users(cur)
        _backfill_file_uuid(cur)
        _backfill_owner_uuid(cur)
        _backfill_tracking_id(cur)
        _backfill_raw_hash(cur)
        _backfill_soft_delete(cur)
        _backfill_version_no(cur)
        _backfill_file_traces(cur)
        conn.commit()
    finally:
        conn.close()


def _ensure_file_traces_table(cur: sqlite3.Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS file_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            file_uuid VARCHAR(64),
            tracking_id VARCHAR(64),
            event_type VARCHAR(32) NOT NULL,
            file_hash VARCHAR(255) NOT NULL,
            actor_uuid VARCHAR(64),
            detail VARCHAR(1000),
            created_at VARCHAR(32) NOT NULL
        )
        """
    )


def _ensure_column(
        cur: sqlite3.Cursor,
        table_name: str,
        column_name: str,
        column_type: str,
) -> None:
    columns = [row[1] for row in cur.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def _backfill_original_filename(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, filename, original_filename FROM files").fetchall()
    for file_id, filename, original_filename in rows:
        if not original_filename:
            cur.execute(
                "UPDATE files SET original_filename = ? WHERE id = ?",
                (filename, file_id),
            )


def _backfill_users(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, uuid, public_key FROM users").fetchall()
    for user_id, user_uuid, public_key in rows:
        new_uuid, new_public_key = utils.get_or_create_signature_identity(user_uuid, public_key)
        cur.execute(
            "UPDATE users SET uuid = ?, public_key = ? WHERE id = ?",
            (new_uuid, new_public_key, user_id),
        )


def _backfill_file_uuid(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, file_uuid FROM files").fetchall()
    for file_id, file_uuid in rows:
        if not file_uuid:
            cur.execute(
                "UPDATE files SET file_uuid = ? WHERE id = ?",
                (str(uuid.uuid4()), file_id),
            )


def _backfill_owner_uuid(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, owner_uuid, sign_user_uuid FROM files").fetchall()
    for file_id, owner_uuid, sign_user_uuid in rows:
        if not owner_uuid and sign_user_uuid:
            cur.execute(
                "UPDATE files SET owner_uuid = ? WHERE id = ?",
                (sign_user_uuid, file_id),
            )


def _backfill_tracking_id(cur: sqlite3.Cursor) -> None:
    rows = cur.execute(
        "SELECT id, path, tracking_id, sign_user_uuid FROM files"
    ).fetchall()
    for file_id, file_path, tracking_id, sign_user_uuid in rows:
        if tracking_id:
            continue

        if file_path and os.path.exists(file_path):
            new_tracking_id, _ = utils.ensure_pdf_tracking_id(file_path)
            new_hash = _get_file_hash(file_path)
            if sign_user_uuid:
                new_signature = utils.sign_file_hash(new_hash, sign_user_uuid)
                cur.execute(
                    "UPDATE files SET tracking_id = ?, hash = ?, signature = ? WHERE id = ?",
                    (new_tracking_id, new_hash, new_signature, file_id),
                )
            else:
                cur.execute(
                    "UPDATE files SET tracking_id = ?, hash = ? WHERE id = ?",
                    (new_tracking_id, new_hash, file_id),
                )
        else:
            cur.execute(
                "UPDATE files SET tracking_id = ? WHERE id = ?",
                (str(uuid.uuid4()), file_id),
            )


def _backfill_raw_hash(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, raw_hash, hash FROM files").fetchall()
    for file_id, raw_hash, file_hash in rows:
        if not raw_hash:
            cur.execute(
                "UPDATE files SET raw_hash = ? WHERE id = ?",
                (file_hash, file_id),
            )


def _backfill_soft_delete(cur: sqlite3.Cursor) -> None:
    rows = cur.execute("SELECT id, is_deleted FROM files").fetchall()
    for file_id, is_deleted in rows:
        if is_deleted is None:
            cur.execute(
                "UPDATE files SET is_deleted = 0 WHERE id = ?",
                (file_id,),
            )


def _backfill_file_traces(cur: sqlite3.Cursor) -> None:
    rows = cur.execute(
        """
        SELECT id, file_uuid, hash, sign_user_uuid, original_filename, tracking_id, version_no
        FROM files
        """
    ).fetchall()
    for file_id, file_uuid, file_hash, sign_user_uuid, original_filename, tracking_id, version_no in rows:
        exists = cur.execute(
            "SELECT 1 FROM file_traces WHERE file_uuid = ? AND event_type IN ('upload', 'upload_new_version') LIMIT 1",
            (file_uuid,),
        ).fetchone()
        detail = (
            f"original_filename={original_filename};"
            f"tracking_id={tracking_id};"
            f"version_no={version_no}"
        )
        if not exists:
            cur.execute(
                """
                INSERT INTO file_traces (
                    file_id, file_uuid, tracking_id, event_type, file_hash, actor_uuid, detail, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id,
                    file_uuid,
                    tracking_id,
                    "upload",
                    file_hash,
                    sign_user_uuid,
                    detail,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
        else:
            cur.execute(
                """
                UPDATE file_traces
                SET file_id = ?, tracking_id = ?, file_hash = ?, detail = ?
                WHERE file_uuid = ? AND event_type IN ('upload', 'upload_new_version')
                """,
                (
                    file_id,
                    tracking_id,
                    file_hash,
                    detail,
                    file_uuid,
                ),
            )

    _link_existing_trace_identities(cur)


def _link_existing_trace_identities(cur: sqlite3.Cursor) -> None:
    files = cur.execute(
        "SELECT id, file_uuid, tracking_id, hash FROM files"
    ).fetchall()
    file_by_hash = {}
    file_by_tracking_and_hash = {}
    for file_id, file_uuid, tracking_id, file_hash in files:
        if file_hash:
            file_by_hash.setdefault(file_hash, []).append((file_id, file_uuid, tracking_id))
        if tracking_id and file_hash:
            file_by_tracking_and_hash[(tracking_id, file_hash)] = (file_id, file_uuid, tracking_id)

    traces = cur.execute(
        """
        SELECT id, file_id, file_uuid, tracking_id, file_hash, detail
        FROM file_traces
        WHERE file_uuid IS NULL OR tracking_id IS NULL
        """
    ).fetchall()
    for trace_id, file_id, trace_file_uuid, trace_tracking_id, file_hash, detail in traces:
        parsed_detail = _parse_detail(detail)
        detail_tracking_id = parsed_detail.get("tracking_id")
        matched = None

        if detail_tracking_id and file_hash:
            matched = file_by_tracking_and_hash.get((detail_tracking_id, file_hash))

        if not matched and file_hash:
            matches = file_by_hash.get(file_hash, [])
            if len(matches) == 1:
                matched = matches[0]

        if not matched and file_hash and file_id:
            matched_row = cur.execute(
                "SELECT id, file_uuid, tracking_id FROM files WHERE id = ? AND hash = ? LIMIT 1",
                (file_id, file_hash),
            ).fetchone()
            if matched_row:
                matched = matched_row

        if matched:
            matched_file_id, matched_file_uuid, matched_tracking_id = matched
            cur.execute(
                """
                UPDATE file_traces
                SET file_id = ?, file_uuid = ?, tracking_id = ?
                WHERE id = ?
                """,
                (
                    matched_file_id,
                    matched_file_uuid,
                    matched_tracking_id or detail_tracking_id or trace_tracking_id,
                    trace_id,
                ),
            )


def _parse_detail(detail: str | None) -> dict[str, str]:
    if not detail:
        return {}

    parsed = {}
    for item in detail.split(";"):
        key, _, value = item.partition("=")
        key = key.strip()
        if key:
            parsed[key] = value.strip()
    return parsed


def _backfill_version_no(cur: sqlite3.Cursor) -> None:
    rows = cur.execute(
        "SELECT id, tracking_id, version_no FROM files ORDER BY tracking_id, id"
    ).fetchall()
    version_map = {}
    for file_id, tracking_id, version_no in rows:
        if version_no:
            continue
        key = tracking_id or f"file-{file_id}"
        version_map[key] = version_map.get(key, 0) + 1
        cur.execute(
            "UPDATE files SET version_no = ? WHERE id = ?",
            (version_map[key], file_id),
        )


def _get_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
