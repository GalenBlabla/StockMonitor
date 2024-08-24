from app.core.interfaces import Notifier
from app.core.events import AnalysisEvent
from typing import List
import pika
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class RabbitMQNotifier(Notifier):
    def notify(self, stock_code: str, events: List[AnalysisEvent]):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue='notifications')
            
            for event in events:
                message = json.dumps(event.to_dict())
                channel.basic_publish(exchange='',
                                      routing_key='notifications',
                                      body=message)
                logger.info(f"Notification sent for {stock_code}: {event.event_type}")
        finally:
            connection.close()
