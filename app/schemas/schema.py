from pydantic import BaseModel


class Register(BaseModel):
    """注册验证模型"""
    username: str
    password: str


class Login(BaseModel):
    """登陆验证模型"""
    username: str
    password: str