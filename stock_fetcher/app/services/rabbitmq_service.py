import json
import logging
import asyncio
import time
from aio_pika import connect_robust, Message
from config import settings

logger = logging.getLogger(__name__)

market_status = {}

async def market_status_callback(message):
    """处理从RabbitMQ接收的市场状态更新"""
    async with message.process():
        data = json.loads(message.body.decode())
        stock_code = data['stock_code']
        is_market_open = data['is_market_open']
        market_status[stock_code] = is_market_open
        logger.info(f"接收到市场状态更新：{stock_code} - {'开放' if is_market_open else '关闭'}")

async def subscription_callback(message, subscribed_stocks):
    """处理订阅更新"""
    async with message.process():
        data = json.loads(message.body.decode())
        stock_code = data['stock_code']
        action = data['action']

        if action == "subscribe":
            subscribed_stocks.add(stock_code)
            logger.info(f"已订阅 {stock_code}")
        elif action == "unsubscribe":
            subscribed_stocks.discard(stock_code)
            logger.info(f"已取消订阅 {stock_code}")

async def start_rabbitmq_listener(subscribed_stocks):
    """启动RabbitMQ监听，接收订阅更新和市场状态更新"""
    connection = await connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

    # 订阅更新的队列
    subscription_queue = await channel.declare_queue('subscription_updates', durable=False)
    await subscription_queue.consume(lambda message: asyncio.create_task(subscription_callback(message, subscribed_stocks)))

    # 市场状态更新的队列
    market_status_queue = await channel.declare_queue('market_status_updates', durable=False)
    await market_status_queue.consume(market_status_callback)

    logger.info("已连接到 RabbitMQ，等待订阅更新...")
    await asyncio.Future()  # 阻止函数退出，保持监听状态

async def report_status():
    """每30秒上报一次服务状态到 RabbitMQ"""
    while True:
        try:
            connection = await connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()
            await channel.declare_queue('stock_fetcher_status', durable=False)

            status_message = {
                'service': 'stock_fetcher',
                'status': 'online',
                'timestamp': time.time()
            }

            await channel.default_exchange.publish(
                Message(body=json.dumps(status_message).encode()),
                routing_key='stock_fetcher_status'
            )
        except Exception as e:
            logger.error(f"上报服务状态时发生错误: {e}")
        finally:
            await connection.close()

        # 每隔30秒上报一次状态
        await asyncio.sleep(30)
