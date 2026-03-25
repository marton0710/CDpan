from sqlalchemy import Column, Integer, String

from app import database


class User(database.Base):
    """
    用户表。

    既保存登录认证所需信息，也保存文件签名体系需要的身份信息。
    """

    __tablename__ = "users"

    # 自增主键。
    id = Column(Integer, primary_key=True, index=True)

    # 登录用户名，系统内唯一。
    username = Column(String(20), unique=True)

    # 用户稳定身份标识。
    # 主要用于签名身份、行为追踪和公钥绑定。
    uuid = Column(String(64), nullable=True)

    # 用户签名公钥，用于文件验签。
    public_key = Column(String, nullable=True)

    # 密码哈希，不存明文密码。
    password = Column(String(255), nullable=False)

    # 预留字段：白名单配置。
    WhiteList = Column(String(1000))

    # 预留字段：黑名单配置。
    BlackList = Column(String(1000))
