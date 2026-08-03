from fastapi import APIRouter

from backend.app.api.v1.endpoints import users, voice_reports

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(
    voice_reports.router, prefix="/voice-reports", tags=["Voice Reports"]
)