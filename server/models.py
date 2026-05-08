from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class AudioTask(Base):
    __tablename__ = "audio_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    file_name = Column(String, index=True)

    status = Column(String, default="PENDING")

    created_at = Column(DateTime, default=datetime.utcnow)

    transcription = relationship("Transcription", back_populates="task", uselist=False)
    
    nlp_entities = relationship("NLPEntity", back_populates="task")


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    audio_task_id = Column(String(36), ForeignKey("audio_tasks.id"), unique=True)

    segments = Column(JSONB, nullable=False)

    task = relationship("AudioTask", back_populates="transcription")


class NLPEntity(Base):
    __tablename__ = "nlp_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    audio_task_id = Column(String(36), ForeignKey("audio_tasks.id"))
    
    entity_type = Column(String, index=True) 
    
    entity_value = Column(String)

    task = relationship("AudioTask", back_populates="nlp_entities")