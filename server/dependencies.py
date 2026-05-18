from typing import Annotated
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings
from repository import AnalysisRepository
from fastapi import Request
from rabbit import RabbitClient


def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.mongo_client


def get_db(client: Annotated[AsyncIOMotorClient, Depends(get_mongo_client)]) -> AsyncIOMotorDatabase:
    return client[settings.MONGO_DB_NAME]

def get_repo(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]) -> AnalysisRepository:
    return AnalysisRepository(db)

def get_rabbit(request: Request) -> RabbitClient:
    return request.app.state.rabbit
 
 
 
RabbitDep = Annotated[RabbitClient, Depends(get_rabbit)]
RepoDep = Annotated[AnalysisRepository, Depends(get_repo)]