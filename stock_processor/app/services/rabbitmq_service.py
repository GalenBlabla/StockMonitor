import json
import logging
import asyncio
import time
from aio_pika import connect_robust, Message, IncomingMessage
from config import settings
from factories.processor_factory import ProcessorFactory
from services.notification_service import RabbitMQNotifier

logger = logging.getLogger(__name__)

async def start_rabbitmq_listener():
    processor = ProcessorFactory.create_processor()
    notifier = RabbitMQNotifier()

    async def callback(message: IncomingMessage):
        async with message.process():
            data = json.loads(message.body.decode())
            stock_code = data['stock_code']
            raw_data = data['data']

            # 使用 processor 进行数据处理
            events = await processor.process(stock_code, raw_data)

            # 将处理后的事件传递给通知服务
            await notifier.notify(stock_code, events)

    connection = await connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

    # 声明队列
    queue = await channel.declare_queue('stock_data', durable=False)
    
    # 消费队列
    await queue.consume(callback)

    logger.info("已连接到RabbitMQ，等待股票数据...")
    await asyncio.Future()  # 保持运行，监听消息

async def report_service_status():
    """定期上报服务状态到 stock_processor_status 队列"""
    while True:
        try:
            connection = await connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()

            status_message = {
                'service': 'stock_processor',
                'status': 'online',
                'timestamp': time.time()
            }

            await channel.declare_queue('stock_processor_status', durable=False)
            await channel.default_exchange.publish(
                Message(body=json.dumps(status_message).encode()),
                routing_key='stock_processor_status'
            )


            await connection.close()

        except Exception as e:
            logger.error(f"上报服务状态时发生错误: {e}")

        await asyncio.sleep(30)  # 每30秒上报一次