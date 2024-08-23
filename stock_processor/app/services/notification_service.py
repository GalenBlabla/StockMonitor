from app.core.interfaces import Notifier
from typing import Dict, Any
import pika
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class RabbitMQNotifier(Notifier):
    def notify(self, stock_code: str, analysis_result: Dict[str, Any]):
        try:
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
        finally:
            connection.close()
