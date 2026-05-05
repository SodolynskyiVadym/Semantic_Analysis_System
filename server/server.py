import os
import uuid
import json
import shutil

import pika
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

# Root endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    Returns a welcome message.
    """
    return {"message": "Semantic analysis system is active"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Uploads an audio file, saves it, and queues a task for processing.

    Args:
        file (UploadFile): The audio file to upload.

    Returns:
        dict: A response containing the task ID, filename, and status.

    Raises:
        HTTPException: If there's an issue saving the file or connecting to RabbitMQ.
    """
    task_id = str(uuid.uuid4())
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    file_location = os.path.join(uploads_dir, f"{task_id}_{file.filename}")
    
    # Save the file locally
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    # RabbitMQ Integration
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_user = os.getenv("RABBITMQ_USER", "user")         # Added
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "password")     # Added
    queue_name = "stt_tasks"

    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        
        # Pass credentials to the connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        message = {
            "task_id": task_id,
            "file_path": file_location,  # Using the relative path
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
    except pika.exceptions.AMQPConnectionError as e:
        # Clean up the saved file if RabbitMQ is down
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Could not connect to RabbitMQ or publish message: {e}")
    except Exception as e:
        # Clean up the saved file for any other unexpected RabbitMQ error
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred with RabbitMQ: {e}")

    return {
        "task_id": task_id,
        "filename": file.filename,
        "message": "Audio file uploaded and task queued successfully",
        "status": "QUEUED"
    }
