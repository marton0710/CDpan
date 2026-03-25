import os

from sqlalchemy.orm import Session

from app import utils


def get_file_security_summary(
        db: Session,
        file_model,
        trace_model,
        user_model,
        file_id: int,
):
    """
    获取文件安全摘要
    :param db:数据库
    :param file_model:文件模型
    :param trace_model:追踪模型
    :param user_model:用户模型
    :param file_id:文件 id
    :return:安全摘要
    """
    db_file = db.query(file_model).filter(file_model.id == file_id).first()
    if not db_file:
        raise utils.Error(code=404, message="文件不存在")

    traces = (
        db.query(trace_model)
        .filter(
            trace_model.file_uuid == db_file.file_uuid
            if db_file.file_uuid
            else trace_model.file_id == file_id
        )
        .order_by(trace_model.id.asc())
        .all()
    )
    upload_traces = [
        trace for trace in traces
        if trace.event_type in {"upload", "upload_new_version"}
    ]
    download_traces = [trace for trace in traces if trace.event_type == "download"]
    verify_traces = [trace for trace in traces if trace.event_type == "verify"]
    repeat_upload_traces = [trace for trace in traces if trace.event_type == "reupload_same_version"]

    verify_ok = False
    if db_file.signature and db_file.sign_user_uuid:
        db_user = db.query(user_model).filter(user_model.uuid == db_file.sign_user_uuid).first()
        if db_user and db_user.public_key:
            verify_ok = utils.verify_file_signature(
                file_hash=db_file.hash,
                signature=db_file.signature,
                public_key=db_user.public_key,
            )

    file_exists = bool(db_file.path and os.path.exists(db_file.path))
    upload_hashes = {trace.file_hash for trace in upload_traces}
    related_hashes = _get_related_hashes(db=db, file_model=file_model, db_file=db_file)

    reasons = []
    security_level = "high"
    if db_file.is_deleted:
        if security_level == "high":
            security_level = "medium"
        reasons.append("文件已删除，保留审计记录")
    elif not file_exists:
        security_level = "low"
        reasons.append("文件实体不存在")
    if not db_file.signature or not verify_ok:
        security_level = "low"
        reasons.append("签名缺失或验签失败")
    if not upload_traces:
        if security_level == "high":
            security_level = "medium"
        reasons.append("缺少上传追踪记录")
    if len(upload_hashes) > 1:
        if security_level != "low":
            security_level = "medium"
        reasons.append("同一文件存在多次上传 hash 变化")
    if len(related_hashes) > 1:
        if security_level == "high":
            security_level = "medium"
        if db_file.tracking_id:
            reasons.append("同一追踪文档存在多个版本")
        else:
            reasons.append("同名文件存在多个版本")
    if not reasons:
        reasons.append("签名有效，追踪记录完整")

    return {
        "security_level": security_level,
        "security_reason": "；".join(reasons),
        "verify_ok": verify_ok,
        "file_exists": file_exists,
        "upload_count": len(upload_traces),
        "repeat_upload_count": len(repeat_upload_traces),
        "download_count": len(download_traces),
        "verify_count": len(verify_traces),
        "known_hash_count": len(upload_hashes),
        "related_hash_count": len(related_hashes),
        "latest_hash": db_file.hash,
    }


def _get_related_hashes(db: Session, file_model, db_file) -> set[str]:
    if db_file.tracking_id:
        related_files = (
            db.query(file_model)
            .filter(
                file_model.owner_uuid == db_file.owner_uuid,
                file_model.tracking_id == db_file.tracking_id,
            )
            .all()
        )
    else:
        related_files = (
            db.query(file_model)
            .filter(
                file_model.owner_uuid == db_file.owner_uuid,
                file_model.original_filename == db_file.original_filename,
            )
            .all()
        )
    return {item.hash for item in related_files if item.hash}
