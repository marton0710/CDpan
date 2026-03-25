from sqlalchemy import Column, Integer, String

from app import database


class File(database.Base):
    """
    文件主表。

    一条记录代表系统中的一个具体文件版本。
    同一文档链使用 `tracking_id` 关联；
    同一具体文件版本使用 `file_uuid` 追踪；
    `id` 只作为数据库主键和接口定位使用。
    """

    __tablename__ = "files"

    # 自增主键，只用于数据库内部定位当前记录。
    id = Column(Integer, primary_key=True, index=True)

    # 文件版本的稳定标识，不受删除后主键复用影响。
    file_uuid = Column(String(64), nullable=True, index=True, unique=True)

    # 文件归属用户 uuid。
    # 所有文件列表和文件操作都基于这个字段做账号隔离。
    owner_uuid = Column(String(64), nullable=True, index=True)

    # 实际落盘文件名，通常会在重名时自动追加序号。
    filename = Column(String(255))

    # 用户上传时看到的原始文件名。
    original_filename = Column(String(255), nullable=True)

    # 文档链标识。
    # 同一文档的不同版本共用一个 tracking_id。
    tracking_id = Column(String(64), nullable=True, index=True)

    # 当前文件在同一 tracking_id 下的版本号。
    version_no = Column(Integer, nullable=True)

    # 文件在服务器上的物理路径。
    # 软删除后这里可能会被置空。
    path = Column(String(1000))

    # 用户原始上传文件的二进制哈希。
    # 用于判断“是不是同一个原始 PDF”。
    raw_hash = Column(String(255), nullable=True, index=True)

    # 当前系统内文件实体的哈希。
    # 如果写入了 tracking_id 等元数据，这个值可能与 raw_hash 不同。
    hash = Column(String(255), nullable=False)

    # 使用签名用户私钥对当前 hash 生成的签名值。
    signature = Column(String, nullable=True)

    # 负责签名的用户 uuid。
    sign_user_uuid = Column(String(64), nullable=True)

    # 软删除标记：0/NULL 表示有效，1 表示已删除。
    is_deleted = Column(Integer, nullable=True, default=0, index=True)

    # 软删除时间，便于审计和恢复。
    deleted_at = Column(String(32), nullable=True)
