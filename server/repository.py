import uuid
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from models import AudioTaskCreate, AudioTaskUpdate, AudioTaskResponse, TaskStatus


def _doc_to_audio_task_response(doc: dict) -> AudioTaskResponse:
    return AudioTaskResponse(
        id=str(doc["_id"]),
        file_name=doc["file_name"],
        status=TaskStatus(doc["status"]), 
        transcription=doc.get("transcription"),  
        analysis=doc.get("analysis"),            
        entities=doc.get("entities"),            
        created_at=doc["created_at"],
    )


class AudioTaskRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["audio_tasks"]

    async def create(self, payload: AudioTaskCreate) -> AudioTaskResponse:
            doc = {
                "_id": payload.id,
                "file_name": f"{payload.id}_{payload.file_name}",
                "status": TaskStatus.PENDING, 
                "created_at": datetime.now(timezone.utc),
            }
            await self.collection.insert_one(doc)
            return _doc_to_audio_task_response(doc)


    async def list(
        self,
        status: Optional[TaskStatus] = None,
        entity: Optional[str] = None,
    ) -> list[AudioTaskResponse]:
        query: dict = {}
        if status:
            query["status"] = status
        if entity:
            query["entities"] = {"$in": [entity]}

        cursor = self.collection.find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [_doc_to_audio_task_response(d) for d in docs]


    async def get(self, task_id: str) -> Optional[AudioTaskResponse]:
        doc = await self.collection.find_one({"_id": task_id})
        return _doc_to_audio_task_response(doc) if doc else None


    async def update(
        self, task_id: str, payload: AudioTaskUpdate
    ) -> Optional[AudioTaskResponse]:
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            return await self.get(task_id)

        if "analysis" in changes:
            changes["analysis"] = [s.model_dump() for s in payload.analysis]
        
        if "transcription" in changes:
            changes["transcription"] = [s.model_dump() for s in payload.analysis]

        result = await self.collection.find_one_and_update(
            {"_id": task_id},
            {"$set": changes},
            return_document=True,
        )
        return _doc_to_audio_task_response(result) if result else None


    async def delete(self, task_id: str) -> bool:
        result = await self.collection.delete_one({"_id": task_id})
        return result.deleted_count == 1