from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class AudioTask(Base):
    __tablename__ = "audio_tasks"

    # Головна інформація про завдання
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String, index=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Відношення (Relationships) - магія SQLAlchemy.
    # Це дозволить в Python робити так: task.transcription.segments або task.nlp_entities
    transcription = relationship("Transcription", back_populates="task", uselist=False) # Зв'язок 1-до-1
    nlp_entities = relationship("NLPEntity", back_populates="task") # Зв'язок 1-до-багатьох


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Зовнішній ключ (Foreign Key) посилається на головне завдання
    audio_task_id = Column(String(36), ForeignKey("audio_tasks.id"), unique=True)
    
    # Самі сегменти від Whisper
    segments = Column(JSONB, nullable=False)

    # Зворотний зв'язок
    task = relationship("AudioTask", back_populates="transcription")


class NLPEntity(Base):
    __tablename__ = "nlp_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Зовнішній ключ (Foreign Key) посилається на головне завдання
    audio_task_id = Column(String(36), ForeignKey("audio_tasks.id"))
    
    # Тип сутності (наприклад: "CALLSIGN", "ENEMY_EQUIPMENT", "LOCATION")
    entity_type = Column(String, index=True) 
    
    # Саме значення (наприклад: "Сокіл", "Т-72", "Бахмут")
    entity_value = Column(String)

    # Зворотний зв'язок
    task = relationship("AudioTask", back_populates="nlp_entities")