from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str
    RABBITMQ_URL: str 
    LOG_LEVEL: str
    class Config:
        env_file = ".env"

settings = Settings()
