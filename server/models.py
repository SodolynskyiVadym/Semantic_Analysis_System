from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
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


class TranscribeSegment(BaseModel):
    start_time: float
    whisper_score: float
    annotated_text: str 


class AnalysisSegment(BaseModel):
    start: float
    end: float
    word: str
    score: float
    entity_group: EntityType


class AudioTaskCreate(BaseModel):
    id: str = Field(...)
    file_name: str = Field(
        ..., 
        pattern=r"^.+\.(wav|mp3|m4a|flac|mp4)$"
    )


class AudioTaskUpdate(BaseModel):
    transcription: Optional[list[TranscribeSegment]] = None
    analysis: Optional[list[AnalysisSegment]] = None
    entities: Optional[list[EntityType]] = None


class AudioTaskResponse(BaseModel):
    id: str                             
    file_name: str
    status: TaskStatus
    analysis: Optional[list[AnalysisSegment]] = None
    transcription: Optional[list[TranscribeSegment]] = None
    entities: Optional[list[EntityType]] = None
    created_at: datetime