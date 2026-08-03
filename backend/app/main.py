from fastapi import FastAPI

app = FastAPI(
    title="BaleVoiceReports API",
    description="سامانه مرکزی دریافت، ذخیره و بازیابی گزارش‌های سازمانی",
    version="1.0.0",
)

@app.get("/", tags=["Health"])
async def root():
    """Endpoint ریشه برای بررسی ساده زنده بودن سرور"""
    return {
        "status": "online",
        "message": "BaleVoiceReports API is running!"}

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Endpoint بررسی سلامت سرور"""
    return {
        "status": "healthy",
        "service": "bale-voice-reports",
        "version": "0.1.0",
    }

