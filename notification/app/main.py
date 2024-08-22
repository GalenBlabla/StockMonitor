import json
import pika
import logging
from config import settings
logging.getLogger('pika').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(stock_code, data):
    """将通知消息发送到 RabbitMQ 的 notifications 队列"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='noti_data')

    message = json.dumps({
        'stock_code': stock_code,
        'data': data
    })

    channel.basic_publish(exchange='',
                          routing_key='noti_data',
                          body=message)

    logger.info(f"Notification sent for {stock_code}")
    connection.close()

def callback(ch, method, properties, body):
    """从RabbitMQ接收股票数据并处理"""
    logging.info(f"Received message: {body}")
    message = json.loads(body)
    stock_code = message['stock_code']
    data = message['data']
    send_notification(stock_code, data)

def start_rabbitmq_listener():
    """启动RabbitMQ监听，接收股票数据"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='notifications')
    channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

    logger.info("Connected to RabbitMQ, waiting for stock data...")
    
    channel.start_consuming()

if __name__ == "__main__":
    start_rabbitmq_listener()
