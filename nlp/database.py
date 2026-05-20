from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from config import settings
from nlp.models import AudioTask, AudioTaskUpdate

client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
db = client[settings.MONGO_DB_NAME]

audio_tasks_collection = db["audio_tasks"]


def _doc_to_audio_task(doc: dict) -> AudioTask:
    return AudioTask(
        id=str(doc["_id"]),
        status=doc["status"],
        transcription=doc.get("transcription"),
        analysis=doc.get("analysis"),
        entities=doc.get("entities")
    )

async def get(task_id: str) -> Optional[AudioTask]:
    doc = await audio_tasks_collection.find_one({"_id": task_id})
    return _doc_to_audio_task(doc) if doc else None


async def update(task_id: str, payload: AudioTaskUpdate) -> Optional[AudioTask]:
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        return await get(task_id)

    if "analysis" in changes and payload.analysis is not None:
        changes["analysis"] = [s.model_dump() for s in payload.analysis]

    result = await audio_tasks_collection.find_one_and_update(
        {"_id": task_id},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,
    )
    return _doc_to_audio_task(result) if result else None
