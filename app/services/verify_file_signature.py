from sqlalchemy.orm import Session

from app import utils
from app.services.file_trace import create_file_trace


def verify_file_signature(
        file_id: int,
        db: Session,
        file_model,
        user_model,
        trace_model,
        actor_uuid: str | None = None,
):
    """
    验证文件签名
    :param file_id:文件 id
    :param db:数据库
    :param file_model:文件模型
    :param user_model:用户模型
    :param trace_model:追踪模型
    :param actor_uuid:操作用户 uuid
    :return:验签结果
    """
    try:
        db_file = (
            db.query(file_model)
            .filter(
                file_model.id == file_id,
                (file_model.is_deleted == 0) | (file_model.is_deleted.is_(None)),
            )
            .first()
        )
        if not db_file:
            raise utils.Error(code=404, message="文件不存在")

        if not db_file.signature or not db_file.sign_user_uuid:
            raise utils.Error(code=400, message="文件未签名")

        db_user = db.query(user_model).filter(user_model.uuid == db_file.sign_user_uuid).first()
        if not db_user or not db_user.public_key:
            raise utils.Error(code=404, message="签名用户不存在")

        is_valid = utils.verify_file_signature(
            file_hash=db_file.hash,
            signature=db_file.signature,
            public_key=db_user.public_key,
        )
        create_file_trace(
            db=db,
            model=trace_model,
            file_id=db_file.id,
            file_uuid=db_file.file_uuid,
            tracking_id=db_file.tracking_id,
            event_type="verify",
            file_hash=db_file.hash,
            actor_uuid=actor_uuid,
            detail=f"is_valid={is_valid}",
        )
        return {
            "file_id": db_file.id,
            "filename": db_file.filename,
            "sign_user_uuid": db_file.sign_user_uuid,
            "is_valid": is_valid,
        }
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
