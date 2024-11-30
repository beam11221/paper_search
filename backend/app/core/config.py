from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Worker Settings
    APP_PORT: int = 7890

    # OpenAI Settings
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIM: int = 3072

    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_PROCESSING_TOPIC: str = "paper_processing"
    KAFKA_STATUS_TOPIC: str = "paper_status"
    KAFKA_NUM_PARTITIONS: int = 30

    # Vector DB Settings
    VECTOR_DB_COLLECTION_NAME: str = "papers"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Cache settings to avoid loading .env file multiple times"""
    return Settings()

# Create a global instance
settings = get_settings()