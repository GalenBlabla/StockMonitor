import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from tortoise import Tortoise
from app.api.v1.services.subscription_service import push_all_subscriptions_to_mq
from app.api.v1.services.rabbitmq_service import start_rabbitmq_listener,report_service_status
from app.notification_handle import notification_handle
from app.config import settings
from app.core.logger import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动逻辑：初始化数据库和RabbitMQ监听器
    await Tortoise.init(db_url=settings.DATABASE_URL, modules={"models": ["app.models.sub_models"]})
    await Tortoise.generate_schemas()
    logger.info("数据库已连接，模式已生成。")
    
    # 启动RabbitMQ监听器和状态上报任务
    rabbitmq_listener_task = asyncio.create_task(start_rabbitmq_listener())
    status_report_task = asyncio.create_task(report_service_status())
    # 推送所有用户订阅的股票到 MQ
    await push_all_subscriptions_to_mq()
    yield

    # 关闭逻辑：关闭数据库连接和取消异步任务
    await Tortoise.close_connections()
    logger.info("数据库连接已关闭。")

    rabbitmq_listener_task.cancel()
    status_report_task.cancel()

    try:
        await asyncio.gather(rabbitmq_listener_task, status_report_task)
    except asyncio.CancelledError:
        logger.info("RabbitMQ监听器和状态上报任务已取消。")