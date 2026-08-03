from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import crud_user
from backend.app.db.session import get_db
from backend.app.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """ایجاد یا دریافت کاربر بر اساس شناسه بله"""
    user = await crud_user.get_or_create(db, obj_in=user_in)
    return user


@router.get("/{bale_user_id}", response_model=UserResponse)
async def read_user_by_bale_id(
    bale_user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """دریافت اطلاعات کاربر با شناسه بله"""
    user = await crud_user.get_by_bale_id(db, bale_user_id=bale_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user