import asyncio
import hashlib
import os
import shutil
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app import config
from app import utils
from app.services.file_trace import create_file_trace


def get_file_hash(file_path: str) -> str:
    """
    获取 pdf 哈希
    :param file_path:文件路径
    :return:pdf 唯一 hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


async def upload_file(
        file: UploadFile,
        model,
        trace_model,
        db: Session,
        current_user,
):
    """
    上传文件
    :param file:上传文件
    :param model:文件模型
    :param trace_model:追踪模型
    :param db:数据库
    :param current_user:当前登录用户
    :return:上传结果
    """
    try:
        original_filename = os.path.basename(file.filename or "")
        name, ext = os.path.splitext(original_filename)
        if ext.lower() != ".pdf":
            raise utils.Error(code=400, message="请传输 pdf 文件")

        if not current_user.uuid:
            raise utils.Error(code=400, message="当前用户缺少签名身份")

        user_static_dir = os.path.join(config.STATIC_DIR, current_user.uuid)
        os.makedirs(user_static_dir, exist_ok=True)

        file_path = os.path.join(user_static_dir, original_filename)
        count = 1
        while os.path.exists(file_path):
            file_path = os.path.join(user_static_dir, f"{name}_{count}{ext}")
            count += 1

        with open(file_path, "wb") as f:
            await asyncio.to_thread(shutil.copyfileobj, file.file, f)

        raw_hash = get_file_hash(file_path)
        incoming_tracking_id = await asyncio.to_thread(utils.read_pdf_tracking_id, file_path)

        active_same_version_file = (
            db.query(model)
            .filter(
                model.owner_uuid == current_user.uuid,
                model.raw_hash == raw_hash,
                (model.is_deleted == 0) | (model.is_deleted.is_(None)),
            )
            .order_by(model.version_no.desc(), model.id.desc())
            .first()
        )
        if active_same_version_file:
            os.remove(file_path)
            create_file_trace(
                db=db,
                model=trace_model,
                file_id=active_same_version_file.id,
                file_uuid=active_same_version_file.file_uuid,
                tracking_id=active_same_version_file.tracking_id,
                event_type="reupload_same_version",
                file_hash=active_same_version_file.hash,
                actor_uuid=current_user.uuid,
                detail=(
                    f"original_filename={original_filename};"
                    f"tracking_id={active_same_version_file.tracking_id};"
                    f"version_no={active_same_version_file.version_no};"
                    "metadata_written=False"
                ),
            )
            db.refresh(active_same_version_file)
            return {
                "file": active_same_version_file,
                "upload_type": "same_version",
            }

        deleted_same_version_file = (
            db.query(model)
            .filter(
                model.owner_uuid == current_user.uuid,
                model.raw_hash == raw_hash,
                model.is_deleted == 1,
            )
            .order_by(model.version_no.desc(), model.id.desc())
            .first()
        )
        if deleted_same_version_file:
            target_tracking_id = deleted_same_version_file.tracking_id or str(uuid.uuid4())
            metadata_written = await asyncio.to_thread(
                utils.write_pdf_tracking_id,
                file_path,
                target_tracking_id,
            )
            file_hash = get_file_hash(file_path)
            signature = utils.sign_file_hash(file_hash=file_hash, user_uuid=current_user.uuid)

            deleted_same_version_file.filename = os.path.basename(file_path)
            deleted_same_version_file.original_filename = original_filename
            deleted_same_version_file.path = file_path
            deleted_same_version_file.owner_uuid = current_user.uuid
            deleted_same_version_file.tracking_id = target_tracking_id
            deleted_same_version_file.raw_hash = raw_hash
            deleted_same_version_file.hash = file_hash
            deleted_same_version_file.signature = signature
            deleted_same_version_file.sign_user_uuid = current_user.uuid
            deleted_same_version_file.is_deleted = 0
            deleted_same_version_file.deleted_at = None
            db.commit()
            db.refresh(deleted_same_version_file)

            create_file_trace(
                db=db,
                model=trace_model,
                file_id=deleted_same_version_file.id,
                file_uuid=deleted_same_version_file.file_uuid,
                tracking_id=deleted_same_version_file.tracking_id,
                event_type="restore_same_version",
                file_hash=deleted_same_version_file.hash,
                actor_uuid=current_user.uuid,
                detail=(
                    f"original_filename={original_filename};"
                    f"tracking_id={deleted_same_version_file.tracking_id};"
                    f"version_no={deleted_same_version_file.version_no};"
                    f"metadata_written={metadata_written}"
                ),
            )
            db.refresh(deleted_same_version_file)
            return {
                "file": deleted_same_version_file,
                "upload_type": "restore_same_version",
            }

        target_tracking_id = incoming_tracking_id or str(uuid.uuid4())
        metadata_written = await asyncio.to_thread(
            utils.write_pdf_tracking_id,
            file_path,
            target_tracking_id,
        )
        file_hash = get_file_hash(file_path)

        latest_version_file = (
            db.query(model)
            .filter(
                model.owner_uuid == current_user.uuid,
                model.tracking_id == target_tracking_id,
            )
            .order_by(model.version_no.desc(), model.id.desc())
            .first()
        )
        upload_type = "new_file"
        version_no = 1
        event_type = "upload"
        if latest_version_file:
            upload_type = "new_version"
            version_no = (latest_version_file.version_no or 0) + 1
            event_type = "upload_new_version"

        signature = utils.sign_file_hash(file_hash=file_hash, user_uuid=current_user.uuid)
        saved_file = model(
            file_uuid=str(uuid.uuid4()),
            owner_uuid=current_user.uuid,
            filename=os.path.basename(file_path),
            original_filename=original_filename,
            tracking_id=target_tracking_id,
            version_no=version_no,
            path=file_path,
            raw_hash=raw_hash,
            hash=file_hash,
            signature=signature,
            sign_user_uuid=current_user.uuid,
            is_deleted=0,
            deleted_at=None,
        )
        db.add(saved_file)
        db.commit()
        db.refresh(saved_file)

        create_file_trace(
            db=db,
            model=trace_model,
            file_id=saved_file.id,
            file_uuid=saved_file.file_uuid,
            tracking_id=saved_file.tracking_id,
            event_type=event_type,
            file_hash=saved_file.hash,
            actor_uuid=current_user.uuid,
            detail=(
                f"original_filename={original_filename};"
                f"tracking_id={saved_file.tracking_id};"
                f"version_no={version_no};"
                f"metadata_written={metadata_written}"
            ),
        )
        db.refresh(saved_file)
        return {
            "file": saved_file,
            "upload_type": upload_type,
        }
    except utils.Error:
        raise
    except Exception:
        db.rollback()
        raise utils.Error(code=500, message="未知错误")
