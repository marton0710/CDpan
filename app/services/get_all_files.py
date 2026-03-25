from sqlalchemy.orm import Session

from app import utils
from app.services.file_security import get_file_security_summary


def get_all_files(
        db: Session,
        model,
        trace_model,
        user_model,
        viewer_uuid: str,
):
    """
    获取全部文件
    :param db:数据库
    :param model:文件模型
    :param trace_model:追踪模型
    :param user_model:用户模型
    :param viewer_uuid:当前查看用户 uuid
    :return:全部文件的 json
    """
    try:
        all_files = (
            db.query(model)
            .filter((model.is_deleted == 0) | (model.is_deleted.is_(None)))
            .order_by(model.id.desc())
            .all()
        )
        owner_uuids = {file.owner_uuid for file in all_files if file.owner_uuid}
        owner_username_map = {}
        if owner_uuids:
            owners = db.query(user_model).filter(user_model.uuid.in_(owner_uuids)).all()
            owner_username_map = {
                owner.uuid: owner.username
                for owner in owners
                if owner.uuid
            }
        return [
            {
                "id": file.id,
                "file_uuid": file.file_uuid,
                "owner_uuid": file.owner_uuid,
                "owner_username": owner_username_map.get(file.owner_uuid),
                "is_owner_for_viewer": file.owner_uuid == viewer_uuid,
                "filename": file.filename,
                "original_filename": file.original_filename,
                "tracking_id": file.tracking_id,
                "version_no": file.version_no,
                "hash": file.hash,
                "sign_user_uuid": file.sign_user_uuid,
                **get_file_security_summary(
                    db=db,
                    file_model=model,
                    trace_model=trace_model,
                    user_model=user_model,
                    file_id=file.id,
                ),
            }
            for file in all_files
        ]
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
