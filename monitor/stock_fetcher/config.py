from pydantic_settings import BaseSettings
import json
class Settings(BaseSettings):
    REDIS_URL: str 
    RABBITMQ_URL: str
    API_STOCK_INFO: str
    CACHE_EXPIRATION: int
    HEADERS: str
    LOG_LEVEL: str

    class Config:
        env_file = ".env"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 解析 HEADERS 为字典
        self.HEADERS = json.loads(self.HEADERS)

settings = Settings()
