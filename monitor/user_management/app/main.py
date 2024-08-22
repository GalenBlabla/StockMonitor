import asyncio
from contextlib import asynccontextmanager
import json
import pika
import logging
from fastapi import FastAPI, HTTPException
from tortoise import Tortoise
from app.config import settings
from app.models.sub_models import Subscription  # 确保导入模型

# 设置日志级别
logging.getLogger('pika').setLevel(logging.WARNING)
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

notifications = []  # 用于存储通知消息的列表

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Initialize the database and RabbitMQ listener
    await Tortoise.init(db_url=settings.DATABASE_URL, modules={"models": ["app.models.sub_models"]})
    await Tortoise.generate_schemas()
    logger.info("Database connected and schemas generated.")
    
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start_rabbitmq_listener)
    
    yield

    # Shutdown logic: Close the database connections
    await Tortoise.close_connections()
    logger.info("Database connections closed.")

app = FastAPI(lifespan=lifespan)

async def send_subscription_update(stock_code, action):
    """Send the subscription update to the Stock Fetcher Service."""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    message = json.dumps({
        'stock_code': stock_code,
        'action': action  # "subscribe" or "unsubscribe"
    })

    channel.queue_declare(queue='subscription_updates')
    channel.basic_publish(exchange='',
                          routing_key='subscription_updates',
                          body=message)

    logger.info(f"Sent subscription update: {stock_code} ({action})")
    connection.close()

@app.post("/subscribe/{user_id}/{stock_code}")
async def subscribe(user_id: int, stock_code: str):
    """Subscribe a user to a stock."""
    await Subscription.create(user_id=user_id, stock_code=stock_code)
    await send_subscription_update(stock_code, "subscribe")
    return {"status": "subscribed", "stock_code": stock_code}

@app.post("/unsubscribe/{user_id}/{stock_code}")
async def unsubscribe(user_id: int, stock_code: str):
    """Unsubscribe a user from a stock."""
    deleted_count = await Subscription.filter(user_id=user_id, stock_code=stock_code).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await send_subscription_update(stock_code, "unsubscribe")
    return {"status": "unsubscribed", "stock_code": stock_code}

def callback(ch, method, properties, body):
    """从RabbitMQ接收通知消息并处理"""
    logging.info(f"Received notification message: {body}")
    message = json.loads(body)
    notifications.append(message)

def start_rabbitmq_listener():
    """启动RabbitMQ监听，接收通知消息"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='noti_data')
    channel.basic_consume(queue='noti_data', on_message_callback=callback, auto_ack=True)

    logger.info("Connected to RabbitMQ, waiting for notifications...")
    
    channel.start_consuming()

@app.get("/get-notifications/")
async def get_notifications():
    """模拟客户端通过轮询获取通知"""
    if notifications:
        return {"notifications": notifications}
    else:
        return {"notifications": []}
