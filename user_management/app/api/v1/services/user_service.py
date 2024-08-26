from tortoise.exceptions import DoesNotExist
from fastapi import HTTPException
from app.models.sub_models import User
from passlib.context import CryptContext
from app.schemas.user_schema import UserCreate, UserResponse

# 初始化密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate) -> UserResponse:
    # 检查用户名或邮箱是否已存在
    if await User.filter(username=user.username).exists():
        raise HTTPException(status_code=400, detail="用户名已被注册")
    
    if await User.filter(email=user.email).exists():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 加密密码并创建用户
    hashed_password = pwd_context.hash(user.password)
    new_user = await User.create(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    
    return UserResponse(id=new_user.id, username=new_user.username, email=new_user.email)

async def get_user_by_id(user_id: int) -> UserResponse:
    try:
        user = await User.get(id=user_id)
        return UserResponse(id=user.id, username=user.username, email=user.email)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="用户未找到")
