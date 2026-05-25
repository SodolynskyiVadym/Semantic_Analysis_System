from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    TRANSCRIBED = "TRANSCRIBED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TranscribeSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: float = Field(ge=0.0, le=1.0) 


class AudioTask(BaseModel):
    id: str
    status: TaskStatus
    file_name: str


class AudioTaskUpdate(BaseModel):
    status: TaskStatus
    transcription: Optional[list[TranscribeSegment]] = None



