from fastapi import APIRouter, Depends, Body, status, HTTPException
from sqlmodel import Session
import sql.models as models
from sql.database import get_session
import utils.schemas as schemas
from utils.authorization import *
import utils.response_format as rf
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/admin/register",
            summary="管理员账号注册",
            status_code=status.HTTP_201_CREATED)
async def admin_register(admin: schemas.AdminRegisterRequest, 
session: Session=Depends(get_session)):
    """内部接口，不对外开放
    """
    admin_for_db = models.Admin(username=admin.username, 
                            hashed_password=get_password_hash(admin.password))
    try:
        session.add(admin_for_db)
        session.commit()
        session.refresh(admin_for_db)
    except IntegrityError: 
        return rf.res_400(message="用户名已存在")
    return rf.res_201(message="注册成功", 
        data={
        "id": admin_for_db.id,
        "username": admin_for_db.username
    })


@router.post("/admin/login",
            summary="管理员账号登录")
async def admin_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
session: Session=Depends(get_session)):
    """请求体中包含以下字段：
    - **username**: 用户名
    - **password**: 密码

    可能要包含的字段：
    - **grant_type**: 设置为`password`
    
    须以表单形式提交。
    """
    user = session.exec(select(models.Admin).filter_by(username=form_data.username)).first()
    if not user:
        return rf.res_401(message="账号或密码错误")
    if not verify_password(form_data.password, user.hashed_password):
        return rf.res_401(message="账号或密码错误")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    token = Token(access_token=access_token, refresh_token=refresh_token,
                token_type="bearer", username=user.username)
    return rf.res_200(message="登录成功", data=token.model_dump())


@router.delete("/admin/delete",
            summary="删除管理员账号")
async def admin_delete(admin=Depends(admin_verify_token),
session: Session=Depends(get_session)):
    """内部接口, 不对外开放
    """
    if admin.id:
        admin_in_db = session.get(models.Admin, admin.id)
        if not admin_in_db:
            return rf.res_404(message="该账号不存在")
        session.delete(admin_in_db)
        session.commit()
        return rf.res_204(message="账号删除成功")


@router.get("/admin/refresh-token", response_model=Token,
            summary="当access_token过期时，用refresh_token获取新的access_token和refresh_token")
async def admin_refresh_token(refresh_token: Annotated[str, Depends(oauth2_scheme)], 
                session: Session = Depends(get_session)):
    """在请求头添加`Authorization`字段并设置值为`Bearer <refresh_token>`。"""
    # refresh_token_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="无效的身份验证凭据",
    #     headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # raise refresh_token_exception
            return rf.res_401(message="无效的身份验证凭据")
        token_data = TokenData(username=username)
    except InvalidTokenError:
        # raise refresh_token_exception
            return rf.res_401(message="无效的身份验证凭据")
    user = session.exec(select(models.Admin).filter_by(username=token_data.username)).first()
    if not user:
        # raise refresh_token_exception
        return rf.res_401(message="无效的身份验证凭据")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return rf.res_200(message="刷新成功", data=Token(access_token=access_token, refresh_token=refresh_token,
            username=user.username, token_type="bearer").model_dump())


@router.post("/user",
            summary="用户修改党支部信息")
async def create_user(user: schemas.UserChangePartyBranchRequest, 
session: Session=Depends(get_session)):
    """如果用户是初次修改党支部信息，则在数据库中创建一个用户。
    如果用户已经存在，则更新其党支部信息。
    """
    user_in_db = session.get(models.User, user.student_id)
    if not user_in_db: # 数据库中无此用户，创建新用户
        user_for_db = models.User.model_validate(user)
        session.add(user_for_db)
        session.commit()
        session.refresh(user_for_db)
        return rf.res_201(message="党支部信息创建成功",
            data=user_for_db.model_dump())
    else: # 数据库已有此用户，更新其党支部信息
        user_in_db.party_branch = user.party_branch
        session.add(user_in_db)
        session.commit()
        session.refresh(user_in_db)
        return rf.res_200(message="党支部信息更新成功",
            data=user_in_db.model_dump())

