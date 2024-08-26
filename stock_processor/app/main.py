import asyncio
import logging
from services.rabbitmq_service import start_rabbitmq_listener, report_service_status
from config import settings

# 设置日志
logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

async def main():
    # 并行执行RabbitMQ监听和状态上报
    await asyncio.gather(
        start_rabbitmq_listener(),
        report_service_status()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务停止中...")
