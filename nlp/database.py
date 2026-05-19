from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from config import settings
from models import Analysis, AnalysisUpdate

client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
db = client[settings.MONGO_DB_NAME]

audio_tasks_collection = db["audio_tasks"]


def _doc_to_response(doc: dict) -> Analysis:
    return Analysis(
        id=str(doc["_id"]),
        status=doc["status"],
        transcription=doc.get("transcription"),
        analysis=doc.get("analysis"),
        entities=doc.get("entities")
    )


async def get(analysis_id: str) -> Optional[Analysis]:
    doc = await audio_tasks_collection.find_one({"_id": analysis_id})
    return _doc_to_response(doc) if doc else None


async def update(analysis_id: str, payload: AnalysisUpdate) -> Optional[Analysis]:
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        return await get(analysis_id)

    if "analysis" in changes and payload.analysis is not None:
        changes["analysis"] = [s.model_dump() for s in payload.analysis]

    result = await audio_tasks_collection.find_one_and_update(
        {"_id": analysis_id},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,
    )
    return _doc_to_response(result) if result else None