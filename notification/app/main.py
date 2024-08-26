import json
import asyncio
import logging
from aio_pika import connect_robust, Message, IncomingMessage
from config import settings
import time

logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_notification(stock_code, event_type, data):
    """将通知消息发送到 RabbitMQ 的 notifications 队列"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        await channel.declare_queue('noti_data', durable=False)

        message = {
            'stock_code': stock_code,
            'event_type': event_type,
            'data': data
        }

        await channel.default_exchange.publish(
            Message(body=json.dumps(message).encode()),
            routing_key='noti_data'
        )

        logger.info(f"已发送通知: {stock_code} ({event_type})")
        await connection.close()

    except Exception as e:
        logger.error(f"发送通知时发生错误: {e}")

async def callback(message: IncomingMessage):
    """异步处理从 RabbitMQ 接收的事件数据"""
    async with message.process():
        body = message.body.decode()
        logger.info(f"接收到消息: {body}")
        data = json.loads(body)
        stock_code = data.get('stock_code')
        event_type = data.get('event_type')
        event_data = data.get('data')

        if event_type == 'price_limit':
            await handle_price_limit_event(stock_code, event_data)
        elif event_type == 'price_fluctuation':
            await handle_price_fluctuation_event(stock_code, event_data)
        # 根据需要添加更多的事件处理逻辑

        # 发送处理后的通知
        await send_notification(stock_code, event_type, event_data)

async def handle_price_limit_event(stock_code, data):
    """处理涨跌停相关的事件"""
    logger.info(f"处理涨跌停事件: {stock_code}")
    # 在这里处理涨跌停事件的逻辑

async def handle_price_fluctuation_event(stock_code, data):
    """处理价格波动相关的事件"""
    logger.info(f"处理价格波动事件: {stock_code}")
    # 在这里处理价格波动事件的逻辑

async def start_rabbitmq_listener():
    """启动RabbitMQ监听，异步接收事件数据"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        queue = await channel.declare_queue('notifications', durable=False)
        await queue.consume(callback)

        logger.info("已连接到 RabbitMQ，等待事件数据...")
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
                'service': 'notification_service',
                'status': 'online',
                'timestamp': time.time()
            }

            await channel.declare_queue('notification_status', durable=False)
            await channel.default_exchange.publish(
                Message(body=json.dumps(status_message).encode()),
                routing_key='notification_status'
            )

            await connection.close()

        except Exception as e:
            logger.error(f"上报服务状态时发生错误: {e}")

        # 每隔30秒上报一次状态
        await asyncio.sleep(30)

async def main():
    # 并行启动RabbitMQ监听器和状态上报任务
    await asyncio.gather(
        start_rabbitmq_listener(),
        report_service_status()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务停止中...")
        logger.info("服务已停止。")
