import time
import json
import asyncio
import logging
from aio_pika import connect_robust, Message, ExchangeType
from app.config import settings

logger = logging.getLogger(__name__)

async def send_subscription_update(stock_code, action):
    """异步发送订阅更新到 Stock Fetcher 服务。"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        await channel.declare_queue('subscription_updates')

        message = {
            'stock_code': stock_code,
            'action': action  # "subscribe" 或 "unsubscribe"
        }

        await channel.default_exchange.publish(
            Message(body=json.dumps(message).encode()),
            routing_key='subscription_updates'
        )

        logger.info(f"已发送订阅更新: {stock_code} ({action})")
        await connection.close()

    except Exception as e:
        logger.error(f"发送订阅更新时发生错误: {e}")

async def callback(message):
    """异步处理从 RabbitMQ 接收到的通知消息。"""
    async with message.process():
        body = message.body.decode()
        logger.info(f"接收到通知消息: {body}")
        data = json.loads(body)
        # 这里处理接收到的通知消息
        # 例如: notifications.append(data)

async def start_rabbitmq_listener():
    """启动 RabbitMQ 监听，异步接收通知消息。"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        queue = await channel.declare_queue('noti_data')
        await queue.consume(callback)

        logger.info("已连接到 RabbitMQ，等待通知消息...")
        await asyncio.Future()  # 阻止函数退出，保持监听状态

    except Exception as e:
        logger.error(f"RabbitMQ 监听启动时发生错误: {e}")

async def report_service_status():
    """定期上报服务在线状态"""
    while True:
        try:
            connection = await connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()

            status_message = {
                'service': 'user_management',
                'status': 'online',
                'timestamp': time.time()
            }

            await channel.declare_queue('user_management_status')
            await channel.default_exchange.publish(
                Message(body=json.dumps(status_message).encode()),
                routing_key='user_management_status'
            )

            await connection.close()

        except Exception as e:
            logger.error(f"上报服务状态时发生错误: {e}")

        # 每隔60秒上报一次状态
        await asyncio.sleep(30)