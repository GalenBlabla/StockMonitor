import asyncio
import logging

import redis

from services.rabbitmq_service import start_rabbitmq_listener, report_service_status
from config import settings
from services.redis_service import redis_client
# 设置日志
logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

async def main():
    # 并行执行RabbitMQ监听和状态上报
        # 检查 Redis 连接
    try:
        redis_client.ping()
        print("Successfully connected to Redis")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
    await asyncio.gather(
        start_rabbitmq_listener(),
        report_service_status()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务停止中...")
