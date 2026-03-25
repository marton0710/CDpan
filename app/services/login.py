from sqlalchemy.orm import Session

from app import schemas
from app import utils


def login(
        db: Session,
        model,
        data: schemas.Login,
):
    """
    登录业务逻辑
    :param db:数据库
    :param model:数据库模型
    :param data:数据来源
    """
    try:
        db_user = db.query(model).filter(model.username == data.username).first()
        if not db_user:
            raise utils.Error(code=400, message="用户名或者密码错误")

        if not utils.verify_password_hash(data.password, db_user.password):
            raise utils.Error(code=400, message="用户名或者密码错误")

        return utils.create_access_token(
            data={"user_id": db_user.id, "sub": db_user.username},
        )
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
