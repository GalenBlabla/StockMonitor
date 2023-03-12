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
    __HEADERS = {
        "Cookie": "BIDUPSID=4154BAE7E88A3C256C441776949A2B1F; PSTM=1632890871; __yjs_duid=1_f47d839a61cba4039e210bbec74edfc11632975760217; BAIDUID=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; MCITY=-163%3A; newlogin=1; MAWEBCUID=web_dWKLuQjvniuSwIfDUmeJWpoSJitqQTaQMGdHXiBblvOZOuGHbB; BDUSS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; BDUSS_BFESS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; ab_sr=1.0.1_NDgzNzQ4YzNjMWQyN2FlNjU2NWM4ODU0OTM0YjRmY2NjYjE1M2UzNTE1M2FjYjMwMGY1YTMzZDlkODZhN2IzYWQ5MGM4M2U4MmY5M2ZkZmRmZjkxOWMwZDhhYmM2ZTFmZmU2OWI3NTY2NGU5MzQyMGIwNjYyZDRkYTQ2YjAwMTM3ZjA3ZWYxOGVjZWU3NWFkMzk1MmNkYWU1NmIxYWI1OA==; BA_HECTOR=0501842284a5818g0h20a58b1i0e4861m; ZFY=vD0w8lrD39F2mrHjQEwBY7bmvW5pxRHy06U:AmCaFQZY:C; BAIDUID_BFESS=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; PSINO=3; delPer=0; H_PS_PSSID=37779_36542_37554_38123_37906_38170_38289_38236_36802_38261_37934_38313_38322_37900_26350_38282_37881",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31"
    }

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
            new_stocks = []  # 用于存储新添加的股票信息
            codes_set = set(await StockList.all().values_list('stock_code', flat=True))
            for stock in stocks_data:
                if stock['dm'] not in codes_set:
                    stock_obj = StockList(
                        stock_code=stock['dm'],
                        name=stock['mc'],
                        exchange=stock['jys']
                    )
                    stocks_to_create.append(stock_obj)
                    new_stocks.append(f"{stock_obj.name}({stock_obj.stock_code}) - {stock_obj.exchange}")
                    codes_set.add(stock['dm'])
            await StockList.bulk_create(stocks_to_create)
            print(f'Saved {len(stocks_to_create)} stocks to database.')
            return new_stocks  # 返回新添加股票的信息列表
        else:
            print(f'Failed to fetch stock data. Status code: {response.status_code}')
            return []


#
# if __name__ == '__main__':
#     a = StockCountFetcher()
