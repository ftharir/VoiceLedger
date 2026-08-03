from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.session import get_db

app = FastAPI(
    title=settings.APP_NAME,
    description="سامانه مرکزی دریافت، ذخیره و بازیابی گزارش‌های سازمانی",
    version="0.1.0",
    debug=settings.DEBUG,
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/db-check", tags=["Health"])
async def db_check(db: AsyncSession = Depends(get_db)):
    """تست اتصال زنده غیرهمزمان به پایگاه داده PostgreSQL"""
    result = await db.execute(text("SELECT 1;"))
    value = result.scalar()
    return {
        "database": "connected",
        "query_result": value,
    }