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
    if not await calendar_service.is_trading_day_and_time():
        return None

    try:
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

        # 测试代码
        # 自定义请求头
        headers = {
            "acs-token": "1724598117709_1724655123677_8ly4y42TcKodl1BOgzaWdIzwsoPoPhphKpnVr3FiIQGDMP1SHhfG4q7rkT58gi/zcIO0EkpMMs+oQgq9AdeKT5LZOam83UNx73UFgwRJoZOZvIw4Czi2rNZmGGkCU4FjsZwdIz2qyMJzqaHfvDxUgGr9SJ3i5GgdDLA/LlW2e60h3OWj8zzpv6BBWP9ZPJ0/P3BFhVMxj+CiTXWofeSPwPbFhuypj1yw71L9Caea8CdRhBeJWWoaU2TiqDHrX8uBwqq5CdVoc7PAuTY1CNMFYY23A4kjxMAybFqjPQlNAoDRoZUEUdNm13U7EWE/R2Q2xSmmbrqjz1M6mlSK9sMhwsKGhJzh6VZaGr4ILcwcOg6BeJ01KaoW3RGirz0OvZInjnIwQMiwKbYVdj49oRBI1g==",
            "cookie": "BAIDUID=3D0026984A2F9757383A4A9CEDFD7E2C:FG=1; BIDUPSID=3D0026984A2F9757383A4A9CEDFD7E2C; PSTM=1706694602; BAIDUID_BFESS=3D0026984A2F9757383A4A9CEDFD7E2C:FG=1; ZFY=8n9wWZUJ4X3kjDAyAnJEnJqYc09zFT4RvXZtkJZPooo:C; H_PS_PSSID=60450_60567_60447_60574_60360; H_WISE_SIDS=60450_60567_60447_60574_60360; RT=\"z=1&dm=baidu.com&si=87f47046-7f40-4447-bfda-aabcb5e5cdd9&ss=m07qjefu&sl=0&tt=0&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ul=24e&hd=24q\"",
            "origin": "https://gushitong.baidu.com",
            "priority": "u=1, i",
            "referer": "https://gushitong.baidu.com/",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": ua.random  # 使用随机 User-Agent
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(settings.API_STOCK_INFO, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"获取股票 {stock_code} 数据时出错: {e}")
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
        await connection.close()

async def fetch_and_process_stock(stock_code):
    """获取和处理单个股票的数据"""
    data = await fetch_stock_data(stock_code)
    if data:
        await send_to_processor(stock_code, data)

async def periodic_stock_fetch(subscribed_stocks):
    """每3秒获取一次所有订阅股票的最新数据，并发处理每个股票的获取请求"""
    while True:
        if subscribed_stocks:
            for stock_code in subscribed_stocks:
                await fetch_and_process_stock(stock_code=stock_code)
        else:
            logger.info("没有订阅的股票，无需获取数据。")
        await asyncio.sleep(10)

#谨慎异步，不要太嚣张
# async def periodic_stock_fetch(subscribed_stocks):
#     """每3秒获取一次所有订阅股票的最新数据，并发处理每个股票的获取请求"""
#     while True:
#         if subscribed_stocks:
#             tasks = [fetch_and_process_stock(stock_code) for stock_code in subscribed_stocks]
#             await asyncio.gather(*tasks)  # 并发执行所有股票的数据获取和处理
#         else:
#             logger.info("没有订阅的股票，无需获取数据。")
#         await asyncio.sleep(3)