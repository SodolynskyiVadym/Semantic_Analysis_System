from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from api.config import settings


async def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
 
 
async def get_database(client: AsyncIOMotorClient = None) -> AsyncIOMotorDatabase:
    return client[settings.MONGO_DB_NAME]
 