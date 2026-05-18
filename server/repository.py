import uuid
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from models import AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisStatus


def _doc_to_response(doc: dict) -> AnalysisResponse:
    return AnalysisResponse(
        id=str(doc["_id"]),
        file_name=doc["file_name"],
        status=doc["status"],
        transcription=doc.get("transcription"),  
        analysis=doc.get("analysis"),            
        entities=doc.get("entities"),            
        created_at=doc["created_at"],
    )


class AnalysisRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["audio_tasks"]

    async def create(self, payload: AnalysisCreate) -> AnalysisResponse:
            doc = {
                "_id": payload.id,
                "file_name": f"{payload.id}_{payload.file_name}",
                "status": AnalysisStatus.PENDING, 
                "created_at": datetime.now(timezone.utc),
            }
            await self.collection.insert_one(doc)
            return _doc_to_response(doc)


    async def list(
        self,
        status: Optional[AnalysisStatus] = None,
        entity: Optional[str] = None,
    ) -> list[AnalysisResponse]:
        query: dict = {}
        if status:
            query["status"] = status
        if entity:
            query["entities"] = {"$in": [entity]}

        cursor = self.collection.find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [_doc_to_response(d) for d in docs]


    async def get(self, analysis_id: str) -> Optional[AnalysisResponse]:
        doc = await self.collection.find_one({"_id": analysis_id})
        return _doc_to_response(doc) if doc else None


    async def update(
        self, analysis_id: str, payload: AnalysisUpdate
    ) -> Optional[AnalysisResponse]:
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            return await self.get(analysis_id)

        if "analysis" in changes:
            changes["analysis"] = [s.model_dump() for s in payload.analysis]

        result = await self.collection.find_one_and_update(
            {"_id": analysis_id},
            {"$set": changes},
            return_document=True,
        )
        return _doc_to_response(result) if result else None


    async def delete(self, analysis_id: str) -> bool:
        result = await self.collection.delete_one({"_id": analysis_id})
        return result.deleted_count == 1