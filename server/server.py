import os
import uuid
import json
import shutil
from dotenv import load_dotenv
import pika
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import AudioTask
import models

models.Base.metadata.create_all(bind=engine)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)


load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS", "password")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "stt_tasks")

AUDIO_DIR = os.getenv("AUDIO_DIR", "uploads")
AUDIO_DIR = os.getenv("AUDIO_DIR", "uploads")
if os.getenv("ENV", "NoEnv") == "DockerEnv":
    pass
else:
    AUDIO_DIR = os.path.join(PROJECT_ROOT, AUDIO_DIR)

os.makedirs(AUDIO_DIR, exist_ok=True)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Semantic analysis system is active"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    file_name = f"{task_id}_{file.filename}"
    
    file_location = os.path.join(AUDIO_DIR, file_name)
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    try:
        new_task = AudioTask(
            id=task_id,
            file_name=file_name,
            status="PENDING"
        )
        db.add(new_task)
        db.commit()
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials,
            heartbeat=600
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)

        message = {
            "task_id": task_id,
            "file_name": file_name,
            "status": "PENDING"
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
        
    except Exception as e:
        task = db.query(AudioTask).filter(AudioTask.id == task_id).first()
        if task:
            task.status = "FAILED"
            db.commit()
            
        if os.path.exists(file_location):
            os.remove(file_location)
            
        raise HTTPException(status_code=500, detail=f"Message queue error: {e}")

    return {
        "task_id": task_id,
        "filename": file.filename,
        "message": "Audio file uploaded and task queued successfully",
        "status": "PENDING"
    }