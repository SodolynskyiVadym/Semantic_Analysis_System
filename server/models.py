from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "TRANSCRIBED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EntityType(str, Enum):
    QUANTITY = "QUANTITY"
    LOCATION = "LOCATION"
    PERSONNEL_FRIENDLY = "PERSONNEL-FRIENDLY"
    PERSONNEL_ENEMY = "PERSONNEL-ENEMY"
    EQUIPMENT_FRIENDLY = "EQUIPMENT-FRIENDLY"
    EQUIPMENT_ENEMY = "EQUIPMENT-ENEMY"


class AnalysisSegment(BaseModel):
    start_time: float
    whisper_score: float
    annotated_text: str 


class AnalysisCreate(BaseModel):
    id: str = Field(...)
    file_name: str = Field(
        ..., 
        pattern=r"^.+\.(wav|mp3|m4a|flac|mp4)$"
    )


class AnalysisUpdate(BaseModel):
    analysis: Optional[list[AnalysisSegment]] = None
    entities: Optional[list[EntityType]] = None


class AnalysisResponse(BaseModel):
    id: str                             
    file_name: str
    status: AnalysisStatus
    analysis: Optional[list[AnalysisSegment]] = None
    entities: Optional[list[EntityType]] = None
    created_at: datetime