import pika
import json
import logging
from config import settings
from app.factories.processor_factory import ProcessorFactory
from app.services.notification_service import RabbitMQNotifier

logger = logging.getLogger(__name__)

def start_rabbitmq_listener():
    processor = ProcessorFactory.create_processor()
    notifier = RabbitMQNotifier()

    def callback(ch, method, properties, body):
        message = json.loads(body)
        stock_code = message['stock_code']
        raw_data = message['data']

        # 使用 processor 进行数据处理
        events = processor.process(stock_code, raw_data)

        # 将处理后的事件传递给通知服务
        notifier.notify(stock_code, events)

    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='stock_data')
    channel.basic_consume(queue='stock_data', on_message_callback=callback, auto_ack=True)

    logger.info("已连接到RabbitMQ，等待股票数据...")
    channel.start_consuming()
