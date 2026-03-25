import os
from datetime import datetime

from sqlalchemy.orm import Session

from app import utils
from app.services.file_trace import create_file_trace


def delete_file(
        file_id: int,
        db: Session,
        model,
        trace_model,
        owner_uuid: str,
        actor_uuid: str | None = None,
):
    """
    删除文件
    :param file_id:文件 id
    :param db:数据库
    :param model:文件模型
    :param trace_model:追踪模型
    :param owner_uuid:当前用户 uuid
    :param actor_uuid:操作用户 uuid
    :return:删除文件的信息
    """
    try:
        db_file = (
            db.query(model)
            .filter(
                model.id == file_id,
                model.owner_uuid == owner_uuid,
                (model.is_deleted == 0) | (model.is_deleted.is_(None)),
            )
            .first()
        )
        if not db_file:
            raise utils.Error(code=404, message="文件不存在")

        create_file_trace(
            db=db,
            model=trace_model,
            file_id=db_file.id,
            file_uuid=db_file.file_uuid,
            tracking_id=db_file.tracking_id,
            event_type="delete",
            file_hash=db_file.hash,
            actor_uuid=actor_uuid,
            detail=f"filename={db_file.filename}",
        )

        if db_file.path and os.path.exists(db_file.path):
            os.remove(db_file.path)

        db_file.path = None
        db_file.is_deleted = 1
        db_file.deleted_at = datetime.now().isoformat(timespec="seconds")

        deleted_file = {
            "id": db_file.id,
            "filename": db_file.filename,
            "hash": db_file.hash,
        }
        db.commit()
        return deleted_file
    except utils.Error:
        raise
    except Exception:
        db.rollback()
        raise utils.Error(code=500, message="未知错误")
