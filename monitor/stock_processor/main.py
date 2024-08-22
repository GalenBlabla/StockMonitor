import logging
from app.services.rabbitmq_service import start_rabbitmq_listener
from config import settings

# 设置 pika 的日志级别为 WARNING 或更高，以隐藏调试和信息日志
logging.getLogger('pika').setLevel(logging.WARNING)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    start_rabbitmq_listener()
