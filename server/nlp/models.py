from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    TRANSCRIBED = "TRANSCRIBED"
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
    start: float
    end: float
    text: str
    confidence: float = Field(ge=0.0, le=1.0) 


class AnalysisSegment(BaseModel):
    start: float
    end: float
    word: str
    score: float
    entity_group: EntityType


class AudioTask(BaseModel):
    id: str
    status: TaskStatus
    transcription: Optional[list[TranscribeSegment]] = None
    analysis: Optional[list[AnalysisSegment]] = None
    entities: Optional[list[EntityType]] = None


class AudioTaskUpdate(BaseModel):
    status: TaskStatus
    analysis: Optional[list[AnalysisSegment]] = None
    entities: Optional[list[str]] = None 