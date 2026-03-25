from sqlalchemy.orm import Session

from app import utils
from app.services.file_security import get_file_security_summary
from app.services.file_trace import get_file_traces


def get_file_trace(
        db: Session,
        file_model,
        trace_model,
        user_model,
        file_id: int,
        viewer_uuid: str,
):
    """
    获取文件追踪详情
    :param db:数据库
    :param file_model:文件模型
    :param trace_model:追踪模型
    :param user_model:用户模型
    :param file_id:文件 id
    :param viewer_uuid:当前查看用户 uuid
    :return:追踪详情
    """
    try:
        db_file = db.query(file_model).filter(file_model.id == file_id).first()
        if not db_file:
            raise utils.Error(code=404, message="文件不存在")

        owner = None
        if db_file.owner_uuid:
            owner = db.query(user_model).filter(user_model.uuid == db_file.owner_uuid).first()

        security = get_file_security_summary(
            db=db,
            file_model=file_model,
            trace_model=trace_model,
            user_model=user_model,
            file_id=file_id,
        )
        traces = get_file_traces(
            db=db,
            model=trace_model,
            file_uuid=db_file.file_uuid,
            file_id=file_id,
            user_model=user_model,
        )
        return {
            "file_id": db_file.id,
            "file_uuid": db_file.file_uuid,
            "owner_uuid": db_file.owner_uuid,
            "owner_username": owner.username if owner else None,
            "is_owner_for_viewer": db_file.owner_uuid == viewer_uuid,
            "filename": db_file.filename,
            "original_filename": db_file.original_filename,
            "tracking_id": db_file.tracking_id,
            "version_no": db_file.version_no,
            "hash": db_file.hash,
            "sign_user_uuid": db_file.sign_user_uuid,
            "security": security,
            "traces": traces,
        }
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
