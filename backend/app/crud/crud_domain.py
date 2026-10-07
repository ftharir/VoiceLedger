from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.domain import Domain


class CRUDDomain:
    async def get_by_slug(
        self,
        db: AsyncSession,
        slug: str,
    ) -> Optional[Domain]:
        result = await db.execute(
            select(Domain).where(Domain.slug == slug)
        )
        return result.scalars().first()


crud_domain = CRUDDomain()