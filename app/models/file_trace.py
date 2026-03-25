from sqlalchemy import Column, Integer, String

from app import database


class FileTrace(database.Base):
    """
    文件追踪表。

    一条记录代表一次文件行为事件，例如：
    上传、下载、验签、删除、重复上传、恢复已删除版本。
    """

    __tablename__ = "file_traces"

    # 追踪记录自己的主键。
    id = Column(Integer, primary_key=True, index=True)

    # 兼容旧逻辑保留的文件表主键。
    # 新逻辑不再把它当作稳定追踪标识。
    file_id = Column(Integer, nullable=False, index=True)

    # 具体文件版本的稳定标识。
    # 追踪链路优先依赖这个字段。
    file_uuid = Column(String(64), nullable=True, index=True)

    # 文档链标识，用来关联同一文档的不同版本。
    tracking_id = Column(String(64), nullable=True, index=True)

    # 事件类型，如 upload / download / verify / delete。
    event_type = Column(String(32), nullable=False)

    # 本次事件对应的文件 hash。
    file_hash = Column(String(255), nullable=False)

    # 谁触发了这次行为，对应用户 uuid。
    actor_uuid = Column(String(64), nullable=True)

    # 事件附加信息，当前以 key=value;key=value 的字符串形式保存。
    detail = Column(String(1000), nullable=True)

    # 事件发生时间。
    created_at = Column(String(32), nullable=False)
