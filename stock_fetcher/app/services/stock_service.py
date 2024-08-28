import httpx
import json
import logging
import asyncio
from config import settings
from services.calendar_service import TradeCalendar
from aio_pika import connect_robust, Message
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

calendar_service = TradeCalendar()
ua = UserAgent()

async def fetch_stock_data(stock_code: str):
    """从API获取股票数据"""
    try:
        if not await calendar_service.is_trading_day_and_time():
            return None

        params = {
            "code": stock_code,
            "all": "1",
            "isIndex": "false",
            "isBk": "false",
            "isBlock": "false",
            "stockType": "ab",
            "group": "quotation_minute_ab",
            "finClientType": "pc",
        }

        headers = {
            "user-agent": ua.random  # 使用随机 User-Agent
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(settings.API_STOCK_INFO, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error : fetching stock {stock_code} data: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error : fetching stock {stock_code} data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error : fetching stock {stock_code} data: {e}")
    return None

async def send_to_processor(stock_code: str, data: dict):
    """将股票数据发送到 Stock Processor 服务"""
    try:
        connection = await connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()
        await channel.declare_queue('stock_data', durable=False)

        message = {
            'stock_code': stock_code,
            'data': data
        }

        await channel.default_exchange.publish(
            Message(body=json.dumps(message).encode()),
            routing_key='stock_data'
        )
        logger.info(f"已将 {stock_code} 的数据发送到 Stock Processor 服务")
    except Exception as e:
        logger.error(f"发送数据到处理服务失败: {e}")
    finally:
        try:
            await connection.close()
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")

async def fetch_and_process_stock(stock_code):
    """获取和处理单个股票的数据"""
    try:
        data = await fetch_stock_data(stock_code)
        if data:
            await send_to_processor(stock_code, data)
    except Exception as e:
        logger.error(f"处理股票 {stock_code} 的数据时发生错误: {e}")

async def periodic_stock_fetch(subscribed_stocks):
    """每3秒获取一次所有订阅股票的最新数据"""
    while True:
        try:
            if subscribed_stocks:
                for stock_code in subscribed_stocks:
                    await fetch_and_process_stock(stock_code)
            else:
                logger.info("没有订阅的股票，无需获取数据。")
        except Exception as e:
            logger.error(f"周期性股票数据获取过程中发生错误: {e}")
        finally:
            await asyncio.sleep(10)  # 调整时间为10秒