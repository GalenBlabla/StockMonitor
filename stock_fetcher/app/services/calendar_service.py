import datetime
import pandas as pd
import os
import httpx
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = "cache/trade_calendar"
os.makedirs(CACHE_DIR, exist_ok=True)

class TradeCalendar:
    __COLUMNS = ['trade_date', 'trade_status', 'day_week']

    def __init__(self) -> None:
        super().__init__()

    async def get_calendar(self, year=None) -> pd.DataFrame:
        """获取股票交易日历"""
        if not year:
            year = datetime.datetime.now().year
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

    def _get_csv_path(self, year):
        return os.path.join(CACHE_DIR, f"trade_calendar_{year}.csv")

    async def _fetch_calendar_from_szse(self, year=None) -> pd.DataFrame:
        """从深交所获取交易日历"""
        data = []
        async with httpx.AsyncClient() as client:
            for i in range(12):
                api_url = f"http://www.szse.cn/api/report/exchange/onepersistenthour/monthList?month={year}-{i + 1}"
                try:
                    res = await client.get(api_url)
                    res.raise_for_status()
                    res_json = res.json()
                    result = res_json.get('data', [])
                    if not result:
                        break
                    data.extend(result)
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logger.error(f"获取 {year}-{i + 1} 月的交易日历数据时出错: {e}")
                    continue
        
        if not data:
            return pd.DataFrame(columns=self.__COLUMNS)
        
        rename = {'jyrq': 'trade_date', 'jybz': 'trade_status', 'zrxh': 'day_week'}
        return pd.DataFrame(data=data).rename(columns=rename)[self.__COLUMNS]

    async def is_trading_day_and_time(self) -> bool:
        """检查今天是否是交易日，并且当前时间是否在交易时段内"""
        today = datetime.datetime.now().strftime('%Y%m%d')
        calendar_df = await self.get_calendar()
        
        if not isinstance(calendar_df, pd.DataFrame):
            logger.error("获取到的交易日历数据格式不正确。")
            return False

        trading_days = calendar_df.query("trade_status == 1")['trade_date'].tolist()

        if today not in trading_days:
            logger.info("今日非交易日。")
            return False

        current_time = datetime.datetime.now().time()
        trading_hours = [
            (datetime.time(9, 15), datetime.time(9, 30)),  # 竞价时间
            (datetime.time(9, 30), datetime.time(11, 30)),  # 上午交易时段
            (datetime.time(13, 0), datetime.time(14, 55)),  # 下午交易时段
            (datetime.time(14, 55), datetime.time(15, 0))   # 收盘前竞价
        ]

        for start, end in trading_hours:
            if start <= current_time <= end:
                return True

        logger.info("当前时间不在交易时段内。")
        return False
