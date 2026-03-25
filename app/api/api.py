from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import database
from app import models
from app import schemas
from app import services
from app import utils
from app.services.file_security import get_file_security_summary

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/upload")
async def post_file(
        file: UploadFile = File(...),
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    上传文件
    :param file:要上传的文件
    :param db:数据库
    :param current_user:当前登录用户
    :return:返回文件信息
    """
    try:
        upload_result = await services.upload_file(
            file=file,
            db=db,
            model=models.File,
            trace_model=models.FileTrace,
            current_user=current_user,
        )
        saved_file = upload_result["file"]
        security = get_file_security_summary(
            db=db,
            file_model=models.File,
            trace_model=models.FileTrace,
            user_model=models.User,
            file_id=saved_file.id,
        )
        return {
            "code": 200,
            "message": {
                "msg": f"{saved_file.filename} is OK",
                "upload_type": upload_result["upload_type"],
                "tracking_id": saved_file.tracking_id,
                "version_no": saved_file.version_no,
                "hash": saved_file.hash,
                "signature": saved_file.signature,
                "sign_user_uuid": saved_file.sign_user_uuid,
                "security": security,
            },
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.post("/delete/{file_id}")
def delete_file(
        file_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    删除文件
    :param file_id:文件 id
    :param db:数据库
    :param current_user:当前登录用户
    :return:删除文件的信息
    """
    try:
        deleted_file = services.delete_file(
            file_id=file_id,
            db=db,
            model=models.File,
            trace_model=models.FileTrace,
            owner_uuid=current_user.uuid,
            actor_uuid=current_user.uuid,
        )
        return {
            "code": 200,
            "message": {
                "msg": "Delete Success",
                "file": deleted_file,
            },
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.get("/download/{file_id}")
def download_file(
        file_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    下载文件
    :param file_id:文件 id
    :param db:数据库
    :param current_user:当前登录用户
    :return:pdf 文件流
    """
    try:
        db_file = services.download_file(
            file_id=file_id,
            db=db,
            model=models.File,
        )
        services.create_file_trace(
            db=db,
            model=models.FileTrace,
            file_id=db_file.id,
            file_uuid=db_file.file_uuid,
            tracking_id=db_file.tracking_id,
            event_type="download",
            file_hash=db_file.hash,
            actor_uuid=current_user.uuid,
            detail=f"filename={db_file.filename}",
        )
        return FileResponse(
            path=db_file.path,
            media_type="application/pdf",
            filename=db_file.filename,
        )
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.get("/verify/{file_id}")
def verify_file_signature(
        file_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    验证文件签名
    :param file_id:文件 id
    :param db:数据库
    :param current_user:当前登录用户
    :return:验签结果
    """
    try:
        verify_result = services.verify_file_signature(
            file_id=file_id,
            db=db,
            file_model=models.File,
            user_model=models.User,
            trace_model=models.FileTrace,
            actor_uuid=current_user.uuid,
        )
        verify_result["security"] = get_file_security_summary(
            db=db,
            file_model=models.File,
            trace_model=models.FileTrace,
            user_model=models.User,
            file_id=file_id,
        )
        return {
            "code": 200,
            "message": verify_result,
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.get("/trace/{file_id}")
def get_file_trace(
        file_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    获取文件追踪详情
    :param file_id:文件 id
    :param db:数据库
    :param current_user:当前登录用户
    :return:文件追踪详情
    """
    try:
        trace_result = services.get_file_trace(
            db=db,
            file_model=models.File,
            trace_model=models.FileTrace,
            user_model=models.User,
            file_id=file_id,
            viewer_uuid=current_user.uuid,
        )
        trace_result["viewer_uuid"] = current_user.uuid
        return {
            "code": 200,
            "message": trace_result,
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.get("/files")
def get_all_files(
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user),
):
    """
    获取全部文件
    :param db:数据库
    :param current_user:当前登录用户
    :return:全部文件的 json 格式
    """
    try:
        all_files = services.get_all_files(
            db=db,
            model=models.File,
            trace_model=models.FileTrace,
            user_model=models.User,
            viewer_uuid=current_user.uuid,
        )
        return {
            "code": 200,
            "message": all_files,
            "current_user_uuid": current_user.uuid,
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.post("/register")
def register(
        user: schemas.Register,
        db: Session = Depends(database.get_db),
):
    """
    注册
    :param user:数据模型
    :param db:数据库
    """
    try:
        new_user = services.regiser(db=db, model=models.User, data=user)
        return {
            "code": 200,
            "message": {
                "id": new_user.id,
                "um": new_user.username,
                "uuid": new_user.uuid,
            },
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )


@router.post("/login")
def login(
        data: schemas.Login,
        db: Session = Depends(database.get_db),
):
    """
    登录
    :param data:数据模型
    :param db:数据库
    """
    try:
        access_token = services.login(db=db, model=models.User, data=data)
        return {
            "code": 200,
            "message": {
                "msg": "Success",
                "token": access_token,
                "token_type": "bearer",
            },
        }
    except utils.Error as e:
        raise HTTPException(
            status_code=e.code,
            detail={"code": e.code, "message": e.message},
        )
