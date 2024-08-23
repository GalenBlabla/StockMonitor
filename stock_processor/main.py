# app/main.py

import logging
from app.services.rabbitmq_service import start_rabbitmq_listener
from config import settings

# 设置日志
logging.getLogger('pika').setLevel(logging.WARNING)
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    start_rabbitmq_listener()
