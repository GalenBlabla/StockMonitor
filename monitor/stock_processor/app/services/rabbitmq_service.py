import json
import pika
import logging
from config import settings
from .processing_pipeline import process_stock_data

logger = logging.getLogger(__name__)

def start_rabbitmq_listener():
    """启动RabbitMQ监听，接收股票数据"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='stock_data')
    channel.basic_consume(queue='stock_data', on_message_callback=callback, auto_ack=True)

    logger.info("已连接到RabbitMQ，等待股票数据...")
    channel.start_consuming()

def callback(ch, method, properties, body):
    """从RabbitMQ接收股票数据并处理"""
    message = json.loads(body)
    stock_code = message['stock_code']
    data = message['data']
    process_stock_data(stock_code, data)
