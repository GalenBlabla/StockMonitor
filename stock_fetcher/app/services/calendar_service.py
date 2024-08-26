import asyncio
import datetime
import pandas as pd
import os
import httpx
import logging
from zoneinfo import ZoneInfo  # Python 3.9+ 提供的时区支持
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CACHE_DIR = "cache/trade_calendar"
os.makedirs(CACHE_DIR, exist_ok=True)

class TradeCalendar:
    __COLUMNS = ['trade_date', 'trade_status', 'day_week']
    __TIMEZONE = ZoneInfo("Asia/Shanghai")  # 设置为北京时间
    __CACHE_DIR = "cache/trade_calendar"
    __CACHE_FILENAME_TEMPLATE = "trade_calendar_{year}.csv"

    def __init__(self) -> None:
        super().__init__()
        os.makedirs(self.__CACHE_DIR, exist_ok=True)

    async def get_calendar(self, year=None) -> pd.DataFrame:
        """获取股票交易日历"""
        if not year:
            year = datetime.datetime.now(self.__TIMEZONE).year
        cache_path = self._get_csv_path(year)
        
        # 尝试从缓存中读取数据
        if os.path.exists(cache_path):
            logger.info(f"从缓存中读取交易日历数据: {cache_path}")
            return pd.read_csv(cache_path, header=0)
        
        # 从远程接口获取数据
        calendar_df = await self._fetch_calendar_from_szse(year=year)
        if not calendar_df.empty:
            calendar_df.to_csv(cache_path, index=False)
            logger.info(f"已缓存交易日历数据到: {cache_path}")
        return calendar_df

    def _get_csv_path(self, year) -> str:
        """生成缓存文件的路径"""
        return os.path.join(self.__CACHE_DIR, self.__CACHE_FILENAME_TEMPLATE.format(year=year))

    async def _fetch_month_data(self, client: httpx.AsyncClient, year: int, month: int) -> List[Dict[str, Any]]:
        """获取特定月份的交易日历数据"""
        api_url = f"http://www.szse.cn/api/report/exchange/onepersistenthour/monthList?month={year}-{month}"
        try:
            res = await client.get(api_url)
            res.raise_for_status()
            res_json = res.json()
            return res_json.get('data', [])
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"获取 {year}-{month} 月的交易日历数据时出错: {e}")
            return []

    async def _fetch_calendar_from_szse(self, year=None) -> pd.DataFrame:
        """从深交所获取交易日历"""
        async with httpx.AsyncClient() as client:
            tasks = [self._fetch_month_data(client, year, month) for month in range(1, 13)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        data = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"获取月度数据时出错: {result}")
                continue
            if result:
                data.extend(result)

        if not data:
            return pd.DataFrame(columns=self.__COLUMNS)

        rename = {'jyrq': 'trade_date', 'jybz': 'trade_status', 'zrxh': 'day_week'}
        return pd.DataFrame(data=data).rename(columns=rename)[self.__COLUMNS]

    async def is_trading_day_and_time(self) -> bool:
        """检查今天是否是交易日，并且当前时间是否在交易时段内"""
        # 使用北京时间获取当前日期
        today = datetime.datetime.now(self.__TIMEZONE).strftime('%Y-%m-%d')
        calendar_df = await self.get_calendar()

        # 确保 trade_status 是整数类型，trade_date 是字符串类型
        calendar_df['trade_status'] = calendar_df['trade_status'].astype(int)
        calendar_df['trade_date'] = calendar_df['trade_date'].astype(str)

        trade_dates = calendar_df.query("trade_status == 1")['trade_date'].tolist()

        if today not in trade_dates:
            logger.info("今日非交易日...")
            return False

        # 使用北京时间获取当前时间
        current_time = datetime.datetime.now(self.__TIMEZONE).time()

        trading_hours = [
            (datetime.time(9, 15), datetime.time(9, 30)),  # 竞价时间
            (datetime.time(9, 30), datetime.time(11, 30)),  # 上午交易时段
            (datetime.time(13, 0), datetime.time(14, 55)),  # 下午交易时段
            (datetime.time(14, 55), datetime.time(15, 0))   # 收盘前竞价
        ]

        return any(start <= current_time <= end for start, end in trading_hours)
