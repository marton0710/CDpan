from datetime import datetime

from sqlalchemy.orm import Session

from app import utils


def create_file_trace(
        db: Session,
        model,
        file_id: int,
        file_uuid: str | None,
        tracking_id: str | None,
        event_type: str,
        file_hash: str,
        actor_uuid: str | None = None,
        detail: str | None = None,
):
    """
    创建文件追踪记录
    :param db:数据库
    :param model:追踪模型
    :param file_id:文件 id
    :param file_uuid:文件稳定标识
    :param tracking_id:文档追踪标识
    :param event_type:事件类型
    :param file_hash:文件 hash
    :param actor_uuid:操作用户 uuid
    :param detail:附加信息
    :return:追踪记录
    """
    try:
        trace = model(
            file_id=file_id,
            file_uuid=file_uuid,
            tracking_id=tracking_id,
            event_type=event_type,
            file_hash=file_hash,
            actor_uuid=actor_uuid,
            detail=detail,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        db.add(trace)
        db.commit()
        db.refresh(trace)
        return trace
    except Exception:
        db.rollback()
        raise utils.Error(code=500, message="未知错误")


def get_file_traces(
        db: Session,
        model,
        file_uuid: str | None = None,
        file_id: int | None = None,
        user_model=None,
):
    """
    获取文件追踪记录
    :param db:数据库
    :param model:追踪模型
    :param file_uuid:文件稳定标识
    :param file_id:兼容旧数据的文件 id
    :param user_model:用户模型，用于补充操作者用户名
    :return:追踪记录
    """
    try:
        query = db.query(model)
        if file_uuid:
            query = query.filter(model.file_uuid == file_uuid)
        elif file_id is not None:
            query = query.filter(model.file_id == file_id)
        else:
            return []

        traces = query.order_by(model.id.desc()).all()
        actor_username_map = {}
        if user_model:
            actor_uuids = {trace.actor_uuid for trace in traces if trace.actor_uuid}
            if actor_uuids:
                users = (
                    db.query(user_model)
                    .filter(user_model.uuid.in_(actor_uuids))
                    .all()
                )
                actor_username_map = {
                    user.uuid: user.username
                    for user in users
                    if user.uuid
                }

        return [
            {
                "id": trace.id,
                "file_uuid": trace.file_uuid,
                "tracking_id": trace.tracking_id,
                "event_type": trace.event_type,
                "file_hash": trace.file_hash,
                "actor_uuid": trace.actor_uuid,
                "actor_username": actor_username_map.get(trace.actor_uuid),
                "detail": trace.detail,
                "created_at": trace.created_at,
            }
            for trace in traces
        ]
    except Exception:
        raise utils.Error(code=500, message="未知错误")
