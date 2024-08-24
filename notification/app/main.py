import json
import pika
import logging
from config import settings

logging.getLogger('pika').setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(stock_code, event_type, data):
    """将通知消息发送到 RabbitMQ 的 notifications 队列"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='noti_data')

    message = json.dumps({
        'stock_code': stock_code,
        'event_type': event_type,
        'data': data
    })

    channel.basic_publish(exchange='',
                          routing_key='noti_data',
                          body=message)

    logger.info(f"Notification sent for {stock_code} with event type {event_type}")
    connection.close()

def callback(ch, method, properties, body):
    """从RabbitMQ接收事件数据并处理"""
    logging.info(f"Received message: {body}")
    message = json.loads(body)
    stock_code = message.get('stock_code')
    event_type = message.get('event_type')
    data = message.get('data')

    if event_type == 'price_limit':
        handle_price_limit_event(stock_code, data)
    elif event_type == 'price_fluctuation':
        handle_price_fluctuation_event(stock_code, data)
    # 根据需要添加更多的事件处理逻辑

    # 发送处理后的通知
    send_notification(stock_code, event_type, data)

def handle_price_limit_event(stock_code, data):
    """处理涨跌停相关的事件"""
    logger.info(f"Handling price limit event for {stock_code}")
    # 在这里处理涨跌停事件的逻辑
    # 例如，可以记录事件或修改数据
    # 你可以在这里添加其他事件处理逻辑

def handle_price_fluctuation_event(stock_code, data):
    """处理价格波动相关的事件"""
    logger.info(f"Handling price fluctuation event for {stock_code}")
    # 在这里处理价格波动事件的逻辑
    # 例如，计算波动率或生成报告
    # 你可以在这里添加其他事件处理逻辑

def start_rabbitmq_listener():
    """启动RabbitMQ监听，接收事件数据"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='notifications')
    channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

    logger.info("Connected to RabbitMQ, waiting for event data...")
    
    channel.start_consuming()

if __name__ == "__main__":
    start_rabbitmq_listener()
