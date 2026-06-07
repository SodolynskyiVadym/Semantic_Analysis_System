import asyncio
import logging
import os
import uuid
import shutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File, status
from fastapi.responses import FileResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import settings
from api.dependencies import RabbitDep, RepoDep
from api.models import AudioTaskCreate, AudioTaskUpdate, AudioTaskResponse, TaskStatus
from api.rabbit import rabbit_client


import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient



logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    try:
        logger.info("Connecting to RabbitMQ...")
        await rabbit_client.connect()
        app.state.rabbit = rabbit_client
        
        logger.info("Connecting to MongoDB...")
        app.state.mongo_client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
        await app.state.mongo_client.admin.command('ping')
        logger.info("All services connected successfully.")
        
    except Exception:
        logger.exception("Critical error during service initialization:")
        raise 
    
    yield

    logger.info("Shutting down application, closing connections...")
    if hasattr(app.state, 'rabbit'):
        await app.state.rabbit.disconnect()
    if hasattr(app.state, 'mongo_client'):
        app.state.mongo_client.close()



app = FastAPI(lifespan=lifespan)



@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Audio Analysis API works"}


@app.post(
    "/tasks",
    response_model=AudioTaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_audio_task(file: UploadFile = File(...), repo: RepoDep = None, mq: RabbitDep = None):
    id = str(uuid.uuid4())
    file_location = os.path.join(settings.AUDIO_DIR, f"{id}_{file.filename}")

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    try:
        response = await repo.create(AudioTaskCreate(id=id, file_name=file.filename))
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {e}")
    
    try:
        await mq.publish_stt({
            "id": id,
            "file_name": f"{id}_{file.filename}"
        })
    except RuntimeError as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        await repo.collection.delete_one({"_id": id})
        raise HTTPException(status_code=500, detail=str(e))
    
    return response
    
    
@app.get(
    "/tasks",
    response_model=list[AudioTaskResponse]
)
async def list_audio_tasks(status: TaskStatus | None = None, entity: str | None = None, repo: RepoDep = None):
    return await repo.list(status=status, entity=entity)


@app.get(
    "/tasks/{task_id}",
    response_model=AudioTaskResponse
)
async def get_audio_task(task_id: str, repo: RepoDep = None):
    result = await repo.get(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return result


@app.patch(
    "/tasks/analysis/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_audio_task(task_id: str, payload: AudioTaskUpdate, repo: RepoDep = None):
    result = await repo.update_analysis(task_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.patch(
    "/tasks/transcription/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_transcription(task_id: str, payload: AudioTaskUpdate, repo: RepoDep = None, mq: RabbitDep = None):
    result = await repo.update_transcription(task_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    
    try:
        await mq.publish_nlp(task_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_audio_task(task_id: str, repo: RepoDep = None):
    deleted = await repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")



@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(settings.AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/wav")