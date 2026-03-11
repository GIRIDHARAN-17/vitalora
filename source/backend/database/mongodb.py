from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.core.config import settings


class Mongo:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    @classmethod
    def connect(cls) -> None:
        if not settings.mongodb_uri:
            raise RuntimeError("MONGODB_URI is not set. Create a .env based on env.example.")
        cls.client = AsyncIOMotorClient(settings.mongodb_uri)
        cls.db = cls.client[settings.mongodb_db]

    @classmethod
    def close(cls) -> None:
        if cls.client:
            cls.client.close()
        cls.client = None
        cls.db = None


def get_db() -> AsyncIOMotorDatabase:
    if Mongo.db is None:
        raise RuntimeError("MongoDB not initialized")
    return Mongo.db

