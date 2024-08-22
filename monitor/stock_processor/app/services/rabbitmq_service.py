import json
import pika
import logging

from config import settings
from .strategy_layer import analyze_stock_data  # 假设这是你的策略层分析函数
from .data_cleaning import clean_stock_data

logger = logging.getLogger(__name__)

def process_stock_data(stock_code, raw_data):
    """接收到股票数据，进行清洗和策略分析，并决定是否发送通知"""
    cleaned_data = clean_stock_data(raw_data, stock_code)
    analysis_result = analyze_stock_data(stock_code, cleaned_data)

    # 模拟处理逻辑，假设这里总是决定发送通知
    notify = True
    
    if notify:
        send_notification(stock_code, analysis_result)

def send_notification(stock_code, data):
    """将通知消息发送到通知服务"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='notifications')

    message = json.dumps({
        'stock_code': stock_code,
        'message': f'Stock {stock_code} has significant updates: {data}'
    })

    channel.basic_publish(exchange='',
                          routing_key='notifications',
                          body=message)

    logger.info(f"Notification sent for {stock_code}")
    connection.close()

def callback(ch, method, properties, body):
    """从RabbitMQ接收股票数据并处理"""
    message = json.loads(body)
    stock_code = message['stock_code']
    data = message['data']
    process_stock_data(stock_code, data)

def start_rabbitmq_listener():
    """启动RabbitMQ监听，接收股票数据"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()

    channel.queue_declare(queue='stock_data')
    channel.basic_consume(queue='stock_data', on_message_callback=callback, auto_ack=True)

    logger.info("Connected to RabbitMQ, waiting for stock data...")
    
    channel.start_consuming()
