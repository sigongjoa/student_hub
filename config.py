import os

class Settings:
    NODE0_PORT = int(os.getenv("NODE0_PORT", "8000"))
    NODE0_HOST = os.getenv("NODE0_HOST", "0.0.0.0")

    # In-memory mocking for now, but keeping structure for later
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "student_hub")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "mathesis")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
