import pika
import json
import logging
from config import settings
from app.factories.processor_factory import ProcessorFactory

logger = logging.getLogger(__name__)

def start_rabbitmq_listener():
    processor = ProcessorFactory.create_processor()

    def callback(ch, method, properties, body):
        message = json.loads(body)
        stock_code = message['stock_code']
        raw_data = message['data']
        processor.process(stock_code, raw_data)

    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='stock_data')
    channel.basic_consume(queue='stock_data', on_message_callback=callback, auto_ack=True)

    logger.info("已连接到RabbitMQ，等待股票数据...")
    channel.start_consuming()
