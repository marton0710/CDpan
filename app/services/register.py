from sqlalchemy.orm import Session

from app import schemas
from app import utils


def regiser(
        db: Session,
        model,
        data: schemas.Register,
):
    """
    注册业务逻辑
    :param db:数据库
    :param model:数据库模型
    :param data:数据来源
    """
    try:
        username = data.username
        db_user = db.query(model).filter(model.username == username).first()
        if db_user:
            raise utils.Error(code=400, message="用户已经存在")

        hashed_password = utils.get_password_hash(data.password)
        user_uuid, public_key = utils.create_signature_identity()
        new_user = model(
            username=username,
            uuid=user_uuid,
            public_key=public_key,
            password=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
