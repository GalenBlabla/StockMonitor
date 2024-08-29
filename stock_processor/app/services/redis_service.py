import redis
from config import settings  # 导入配置

class RedisClient:
    def __init__(self):
        # 使用 URL 初始化 Redis 客户端
        self.client = redis.Redis.from_url(settings.REDIS_URL)

    def get_client(self):
        return self.client

# 实例化 RedisClient，在其他地方可以直接使用这个实例
redis_client = RedisClient().get_client()
