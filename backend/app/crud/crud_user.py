from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    async def get_by_bale_id(self, db: AsyncSession, bale_user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.bale_user_id == bale_user_id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        db_obj = User(
            bale_user_id=obj_in.bale_user_id,
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_or_create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        user = await self.get_by_bale_id(db, bale_user_id=obj_in.bale_user_id)
        if not user:
            user = await self.create(db, obj_in=obj_in)
        return user


crud_user = CRUDUser()