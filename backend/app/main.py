from fastapi import FastAPI
from backend.app.core.config import settings


app = FastAPI(
    title="BaleVoiceReports API",
    description="سامانه مرکزی دریافت، ذخیره و بازیابی گزارش‌های سازمانی",
    version="1.0.0",
    debug=settings.DEBUG,
)

@app.get("/", tags=["Health"])
async def root():
    """Endpoint ریشه برای بررسی ساده زنده بودن سرور"""
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,}

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Endpoint بررسی سلامت سرور"""
    return {
        "status": "healthy",
        "service": "bale-voice-reports",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT
    }

