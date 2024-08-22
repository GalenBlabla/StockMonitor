import json
from typing import Any, Dict
import pika
import logging
from config import settings

logger = logging.getLogger(__name__)

def send_notification(stock_code: str, analysis_result: Dict[str, Any]):
    """将通知消息发送到通知服务"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='notifications')

    message = json.dumps({
        'stock_code': stock_code,
        'data': analysis_result
    })

    channel.basic_publish(exchange='',
                          routing_key='notifications',
                          body=message)

    logger.info(f"Notification sent for {stock_code}")
    connection.close()
