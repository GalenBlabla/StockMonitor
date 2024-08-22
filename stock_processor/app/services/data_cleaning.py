import json
import logging
from pathlib import Path
from typing import Dict, Any
import pika
from config import settings

logger = logging.getLogger(__name__)

def clean_stock_data(raw_data: Dict[str, Any],stock_code: str) -> Dict[str, Any]:
    """清洗并解析股票数据"""
    try:
        result = raw_data.get('Result', {})
        cleaned_data = {
            'result_code': raw_data.get('ResultCode'),
            'update_info': result.get('update'),
            'provider_info': result.get('provider'),
            'origin_pankou': result.get('pankouinfos', {}).get('origin_pankou'),
            'pankou_info': result.get('pankouinfos', {}).get('list'),
            'new_market_data': result.get('newMarketData'),
            'member_info': result.get('member_info'),
            'detail_info': result.get('detailinfos'),
            'cur_info': result.get('cur'),
            'buy_info': result.get('buyinfos'),
            'basic_infos': result.get('basicinfos'),
            'ask_infos': result.get('askinfos'),
            'price_info': result.get('priceinfo'),
            'market_status': result.get('update', {}).get('stockStatus'),
        }

        # 判断市场是否处于交易状态
        is_market_open = cleaned_data['market_status'] == "已收盘"
        cleaned_data['is_market_open'] = is_market_open
        send_market_status(stock_code=stock_code, is_market_open=is_market_open)
        
        return cleaned_data
    except Exception as e:
        logger.error(f"Error cleaning stock data: {e}")
        return {}
    
def send_market_status(stock_code: str, is_market_open: bool):
    """将市场状态发送回请求微服务"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='market_status_updates')

        message = json.dumps({
            'stock_code': stock_code,
            'is_market_open': is_market_open
        })

        channel.basic_publish(exchange='',
                              routing_key='market_status_updates',
                              body=message)
        logger.info(f"Sent market status for {stock_code}: {is_market_open}")
    except Exception as e:
        logger.error(f"Failed to send market status: {e}")
    finally:
        connection.close()
