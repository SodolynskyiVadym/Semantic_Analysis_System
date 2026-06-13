from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from nlp.models import AudioTask, AudioTaskUpdate, TaskStatus

client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
db = client[settings.MONGO_DB_NAME]
audio_tasks_collection = db[settings.MONGO_AUDIO_TASK_COLLECTION]


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


async def update(task_id: str, payload: AudioTaskUpdate) -> bool:
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        return False

    if "analysis" in changes and payload.analysis is not None:
        changes["analysis"] = [s.model_dump() for s in payload.analysis]

    result = await audio_tasks_collection.update_one(
        {"_id": task_id, "status": TaskStatus.TRANSCRIBED},
        {"$set": changes}
    )
    return result.matched_count > 0
