import asyncio
from typing import Any

import requests
import os

from ..models.models import StockCountFetcherDB, StockList


class StockCountFetcher:
    """
    https://gushitong.baidu.com/opendata?resource_id=5352&query=399001&code=399001&name=%E6%B7%B1%E8%AF%81%E6%88%90%E6%8C%87&market=ab&group=asyn_ranking&pn=0&rn=50&pc_web=1&finClientType=pc
    """
    __API_SH_Stock = "https://gushitong.baidu.com/opendata"
    __API_SZ_Stock = "https://gushitong.baidu.com/opendata"
    __HEADERS = {""}

    def __init__(self):
        pass

    def _get_sh_stock_data(self) -> Any:
        params = {
            "resource_id": 5352,
            "query": "000001",
            "code": "000001",
            "name": "上证指数",
            "market": "ab",
            "group": "asyn_ranking",
            "pn": 0,
            "rn": 2200,
            "pc_web": 1,
            "finClientType": "pc",
        }
        response = requests.get(self.__API_SH_Stock, headers=self.__HEADERS, params=params)
        return response.json()

    def _get_sz_stock_data(self) -> Any:
        params = {
            "resource_id": 5352,
            "query": "399001",
            "code": "399001",
            "name": "深证成指",
            "market": "sz",
            "group": "asyn_ranking",
            "pn": 0,
            "rn": 1000,
            "pc_web": 1,
            "finClientType": "pc",
        }
        response = requests.get(self.__API_SZ_Stock, headers=self.__HEADERS, params=params)
        return response.json()

    async def update_stocks(self):
        print("正在更新数据")
        # 查询已经存在的股票代码
        existing_codes = await StockCountFetcherDB.all().values_list('code', flat=True)

        # 获取最新的股票数据
        sh_stocks_list = self._get_sh_stock_data()["Result"][0]['DisplayData']['resultData']['tplData']['result'][
            'list']
        sz_stocks_list = self._get_sz_stock_data()["Result"][0]['DisplayData']['resultData']['tplData']['result'][
            'list']

        # 合并两个列表
        stocks_list = sh_stocks_list + sz_stocks_list

        # 初始化待创建和待更新列表
        stocks_to_create = []
        stocks_to_update = []

        for stock in stocks_list:
            if stock['code'] in existing_codes:
                # 如果股票已经存在，则添加到更新列表
                stocks_to_update.append({
                    'code': stock['code'],
                    'exchange': stock['exchange'],
                    'increase': stock['increase'],
                    'market': stock['market'],
                    'name': stock['name'],
                    'price_status': stock['price']['status'],
                    'price_value': stock['price']['value'],
                    'ratio_status': stock['ratio']['status'],
                    'ratio_value': stock['ratio']['value']
                })
            else:
                # 如果股票不存在，则添加到创建列表
                stocks_to_create.append(StockCountFetcherDB(
                    code=stock['code'],
                    exchange=stock['exchange'],
                    increase=stock['increase'],
                    market=stock['market'],
                    name=stock['name'],
                    price_status=stock['price']['status'],
                    price_value=stock['price']['value'],
                    ratio_status=stock['ratio']['status'],
                    ratio_value=stock['ratio']['value']
                ))

        # 批量创建待创建列表中的股票数据
        await StockCountFetcherDB.bulk_create(stocks_to_create)
        # 批量更新现有股票
        for stock in stocks_to_update:
            stock_obj = await StockCountFetcherDB.get(code=stock['code'])
            for key, value in stock.items():
                setattr(stock_obj, key, value)
            await stock_obj.save()

        print("数据更新完毕")


class StockInfoSyncFetcher:
    API_URL = 'http://api.mairui.club/hslt/list/f270014d4323d6593c'

    @staticmethod
    async def fetch_and_save():
        response = requests.get(StockInfoSyncFetcher.API_URL)
        if response.status_code == 200:
            stocks_data = response.json()
            stocks_to_create = []
            for stock in stocks_data:
                stocks_to_create.append(
                    StockList(
                        stock_code=stock['dm'],
                        name=stock['mc'],
                        exchange=stock['jys']
                    )
                )
            await StockList.bulk_create(stocks_to_create)
            print(f'Saved {len(stocks_to_create)} stocks to database.')
        else:
            print(f'Failed to fetch stock data. Status code: {response.status_code}')
#
# if __name__ == '__main__':
#     a = StockCountFetcher()
