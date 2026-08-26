"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Runtime configuration for the Adaptive RAG application."""

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "adaptive_rag")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "storage/faiss")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


settings = Settings()
