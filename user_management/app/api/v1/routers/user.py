from fastapi import APIRouter
from app.schemas.user_schema import UserCreate, UserResponse
from app.api.v1.services.user_service import create_user, get_user_by_id

router = APIRouter()

@router.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate):
    return await create_user(user)

@router.get("/users/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int):
    return await get_user_by_id(user_id)
