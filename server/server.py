import os
import uuid
import json
import shutil

import pika
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Імпортуємо налаштування БД та моделі
from database import SessionLocal, engine
from models import AudioTask
import models

models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dependency для отримання сесії бази даних (Connection Pool)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    Returns a welcome message.
    """
    return {"message": "Semantic analysis system is active"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads an audio file, saves it, creates a DB record, and queues a task.
    """
    task_id = str(uuid.uuid4())
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    file_location = os.path.join(uploads_dir, f"{task_id}_{file.filename}")
    
    # 1. Save the file locally
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    # 2. Create the record in PostgreSQL
    try:
        new_task = AudioTask(
            id=task_id,
            file_name=file.filename,
            status="PENDING"
        )
        db.add(new_task)
        db.commit()
    except Exception as e:
        # Якщо база лежить, видаляємо файл і перериваємо процес
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # 3. RabbitMQ Integration
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_user = os.getenv("RABBITMQ_USER", "user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "password")
    queue_name = "stt_tasks"

    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        message = {
            "task_id": task_id,
            "file_path": file_location, 
            "status": "PENDING"
        }
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()
        
    except Exception as e:
        # Якщо RabbitMQ впав, оновлюємо статус в БД на FAILED, щоб мати слід проблеми
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