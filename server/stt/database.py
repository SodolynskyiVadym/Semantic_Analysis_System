from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from config import settings
from stt.models import AudioTask, AudioTaskUpdate

client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
db = client[settings.MONGO_DB_NAME]
audio_tasks_collection = db[settings.MONGO_AUDIO_TASK_COLLECTION]


def _doc_to_audio_task(doc: dict) -> AudioTask:
    return AudioTask(
        id=str(doc["_id"]),
        file_name=doc["file_name"],
        status=doc["status"],
        transcription=doc.get("transcription")
    )


async def get(task_id: str) -> Optional[AudioTask]:
    doc = await audio_tasks_collection.find_one({"_id": task_id})
    return _doc_to_audio_task(doc) if doc else None


async def update(task_id: str, payload: AudioTaskUpdate) -> Optional[AudioTask]:
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        return False
    
    if "transcription" in changes and payload.transcription:
        changes["transcription"] = [s.model_dump() for s in payload.transcription]

    result = await audio_tasks_collection.update_one(
        {"_id": task_id},
        {"$set": changes}
    )
    return result.matched_count > 0
