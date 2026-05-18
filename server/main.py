import os
import uuid
import shutil
from contextlib import asynccontextmanager
 
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorClient
 
from config import settings
from dependencies import RabbitDep, RepoDep
from models import AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisStatus
from rabbit import rabbit_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo_client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
    await rabbit_client.connect()
    app.state.rabbit = rabbit_client
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)

    yield

    await rabbit_client.disconnect()
    app.state.mongo_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Audio Analysis API works"}



@app.post(
    "/transcribe",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_analysis(file: UploadFile = File(...), repo: RepoDep = None, mq: RabbitDep = None):
    id = str(uuid.uuid4())
    file_location = os.path.join(settings.AUDIO_DIR, f"{id}_{file.filename}")

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    try:
        response = await repo.create(AnalysisCreate(id=id, file_name=file.filename))
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {e}")
    
    try:
        await mq.publish({
            "task_id": id,
            "file_name": f"{id}_{file.filename}"
        })
    except RuntimeError as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        await repo.collection.delete_one({"_id": id})
        raise HTTPException(status_code=500, detail=str(e))
    
    return response
    
    
@app.get(
    "/analyses",
    response_model=list[AnalysisResponse]
)
async def list_analyses(status: AnalysisStatus | None = None, entity: str | None = None, repo: RepoDep = None):
    return await repo.list(status=status, entity=entity)


@app.get(
    "/analyses/{analysis_id}",
    response_model=AnalysisResponse
)
async def get_analysis(analysis_id: str, repo: RepoDep = None):
    result = await repo.get(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return result


@app.patch(
    "/analyses/{analysis_id}",
    response_model=AnalysisResponse
)
async def update_analysis(analysis_id: str, payload: AnalysisUpdate, repo: RepoDep = None):
    result = await repo.update(analysis_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return result


@app.delete(
    "/analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_analysis(analysis_id: str, repo: RepoDep = None):
    deleted = await repo.delete(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")