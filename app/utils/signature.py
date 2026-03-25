import base64
import os
import uuid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app import config


def get_private_key_path(user_uuid: str) -> str:
    """
    获取用户私钥路径
    :param user_uuid:用户 uuid
    :return:私钥路径
    """
    return os.path.join(config.KEY_DIR, f"{user_uuid}.pem")


def create_signature_identity() -> tuple[str, str]:
    """
    创建签名身份
    :return:uuid 和公钥
    """
    user_uuid = str(uuid.uuid4())
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    with open(get_private_key_path(user_uuid), "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return user_uuid, public_key.decode("utf-8")


def get_or_create_signature_identity(user_uuid: str | None, public_key: str | None) -> tuple[str, str]:
    """
    获取或创建签名身份
    :param user_uuid:用户 uuid
    :param public_key:用户公钥
    :return:uuid 和公钥
    """
    if user_uuid and public_key and os.path.exists(get_private_key_path(user_uuid)):
        return user_uuid, public_key
    return create_signature_identity()


def sign_file_hash(file_hash: str, user_uuid: str) -> str:
    """
    对文件 hash 进行签名
    :param file_hash:文件 hash
    :param user_uuid:用户 uuid
    :return:base64 编码签名
    """
    with open(get_private_key_path(user_uuid), "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    signature = private_key.sign(
        file_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_file_signature(file_hash: str, signature: str, public_key: str) -> bool:
    """
    验证文件签名
    :param file_hash:文件 hash
    :param signature:base64 编码签名
    :param public_key:用户公钥
    :return:是否验证成功
    """
    public_key_obj = serialization.load_pem_public_key(public_key.encode("utf-8"))
    try:
        public_key_obj.verify(
            base64.b64decode(signature.encode("utf-8")),
            file_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception as e:
        return False
