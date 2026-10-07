from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VoiceReportBase(BaseModel):
    file_id: str
    duration: Optional[int] = None


class VoiceReportCreate(VoiceReportBase):
    user_id: int
    domain_id: int


class VoiceReportUpdate(BaseModel):
    file_path: Optional[str] = None
    transcription: Optional[str] = None
    status: Optional[str] = None


class VoiceReportInDBBase(VoiceReportBase):
    id: int
    user_id: int
    domain_id: int
    file_path: Optional[str] = None
    transcription: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoiceReportResponse(VoiceReportInDBBase):
    pass