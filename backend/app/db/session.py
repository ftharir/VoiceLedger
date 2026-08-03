from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.core.config import settings

# ساخت موتور اتصال غیرهمزمان
engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DEBUG,
    future=True,
)

# ساخت SessionFactory برای دیتابیس
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    تزریق‌کننده وابسته (Dependency) برای کدهای FastAPI جهت ارائه نشست دیتابیس
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()