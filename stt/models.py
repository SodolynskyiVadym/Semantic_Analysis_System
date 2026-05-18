from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "TRANSCRIBED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TranscribeSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: float = Field(ge=0.0, le=1.0) 


class Analysis(BaseModel):
    id: str
    status: AnalysisStatus
    file_name: str


class AnalysisUpdate(BaseModel):
    status: AnalysisStatus
    transcription: Optional[list[TranscribeSegment]] = None



