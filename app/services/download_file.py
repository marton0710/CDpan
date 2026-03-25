import os

from sqlalchemy.orm import Session

from app import utils


def download_file(
        file_id: int,
        db: Session,
        model,
):
    """
    下载文件
    :param file_id:文件 id
    :param db:数据库
    :param model:文件模型
    :return:文件数据库记录
    """
    try:
        db_file = (
            db.query(model)
            .filter(
                model.id == file_id,
                (model.is_deleted == 0) | (model.is_deleted.is_(None)),
            )
            .first()
        )
        if not db_file:
            raise utils.Error(code=404, message="文件不存在")

        if not db_file.path or not os.path.exists(db_file.path):
            raise utils.Error(code=404, message="文件不存在")

        return db_file
    except utils.Error:
        raise
    except Exception:
        raise utils.Error(code=500, message="未知错误")
