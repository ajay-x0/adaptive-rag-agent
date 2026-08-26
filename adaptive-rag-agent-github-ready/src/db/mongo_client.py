"""MongoDB client initialization."""

from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
