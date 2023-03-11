"""
获取股票的详细信息
"""
import datetime
import os
from pathlib import Path
from typing import Dict, Any

import time
from pprint import pprint

import json

import requests


class StockMonitor:
    """
    对接口的基本解析
    """
    HEADERS = {
        "Cookie": "BIDUPSID=4154BAE7E88A3C256C441776949A2B1F; PSTM=1632890871; __yjs_duid=1_f47d839a61cba4039e210bbec74edfc11632975760217; BAIDUID=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; MCITY=-163%3A; newlogin=1; MAWEBCUID=web_dWKLuQjvniuSwIfDUmeJWpoSJitqQTaQMGdHXiBblvOZOuGHbB; BDUSS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; BDUSS_BFESS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; ab_sr=1.0.1_NDgzNzQ4YzNjMWQyN2FlNjU2NWM4ODU0OTM0YjRmY2NjYjE1M2UzNTE1M2FjYjMwMGY1YTMzZDlkODZhN2IzYWQ5MGM4M2U4MmY5M2ZkZmRmZjkxOWMwZDhhYmM2ZTFmZmU2OWI3NTY2NGU5MzQyMGIwNjYyZDRkYTQ2YjAwMTM3ZjA3ZWYxOGVjZWU3NWFkMzk1MmNkYWU1NmIxYWI1OA==; BA_HECTOR=0501842284a5818g0h20a58b1i0e4861m; ZFY=vD0w8lrD39F2mrHjQEwBY7bmvW5pxRHy06U:AmCaFQZY:C; BAIDUID_BFESS=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; PSINO=3; delPer=0; H_PS_PSSID=37779_36542_37554_38123_37906_38170_38289_38236_36802_38261_37934_38313_38322_37900_26350_38282_37881",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31"
    }

    API_Stock_Info = "https://finance.pae.baidu.com/selfselect/getstockquotation"
    # 上海上市的所有股票
    API_SH_Stock = "https://gushitong.baidu.com/opendata"

    def __init__(self, stock_code):

        self._result_code = None
        self.stock_code = stock_code
        self.path = Path(__file__).resolve().parent / f"data/{self.stock_code}"
        self.refresh_info()

    def _get_sh_stock(self):
        """
        获取上海上市的所有股票信息
        """
        params = {
            "resource_id": "5352",
            "query": "000001",
            "code": "000001",
            "name": "上证指数",
            "market": "ab",
            "group": "asyn_ranking",
            "pn": "0",
            "rn": "20",
            "pc_web": "1",
            "finClientType": "pc"
        }
        response = requests.get(self.API_SH_Stock, headers=self.HEADERS, params=params)
        response.raise_for_status()
        return response.json()

    def _get_response(self):
        """
        发送网络请求并返回响应数据
        """
        params = {
            "code": self.stock_code,
            "all": "1",
            "isIndex": "false",
            "isBk": "false",
            "isBlock": "false",
            "stockType": "ab",
            "group": "quotation_minute_ab",
            "finClientType": "pc",
        }
        response = requests.get(self.API_Stock_Info, headers=self.HEADERS, params=params)
        response.raise_for_status()
        return response.json()

    def refresh_info(self):
        """
        刷新股票信息
        """
        try:
            self.response = self._get_response()
        except Exception as e:
            print(f"API异常返回：{e}")
            return

        try:
            self._result_code = self.response['ResultCode']
            self._update_info = self.response['Result']['update']
            self._provider_info = self.response['Result']['provider']
            self._origin_pankou = self.response["Result"]['pankouinfos']['origin_pankou']
            self._pankou_info = self.response["Result"]['pankouinfos']['list']
            self._new_mark_data = self.response["Result"]['newMarketData']
            self._member_info = self.response["Result"]['member_info']
            self._detail_info = self.response["Result"]['detailinfos']
            self._cur_info = self.response["Result"]['cur']
            self._buy_info = self.response["Result"]['buyinfos']
            self._basic_infos = self.response["Result"]['basicinfos']
            self._ask_infos = self.response["Result"]['askinfos']
            self._price_info = self.response['Result']['priceinfo']
            self._mark_status = self.response['Result']['update']['stockStatus']

        except Exception as e:
            print(f"解析API接口时发生异常：{e}")

        try:
            self.save_stock_info()

        except Exception as e:
            print(f"save_stock_info异常：{e}")

    def save_stock_info(self):
        """
        持久化所有数据
        """
        if not self.path.exists():
            self.path.mkdir(parents=True)
        time_now = int(time.time())
        with open(self.path / f"{time_now}.json", "w", encoding="utf8") as f:
            json.dump(self.response, f, indent=2, ensure_ascii=False)

    @property
    def mark_status(self):
        """
        市场是否属于交易中
        """
        return self._mark_status

    @property
    def update_info(self):
        """
        返回一些时间戳，交易信息啊什么的
        """
        return self._update_info

    @property
    def provider_info(self):
        """
        返回信息提供商的名字
        """
        return self._provider_info

    @property
    def result_code(self):
        """
        成功请求的代码 0
        """
        return self._result_code

    @property
    def origin_pankou(self):
        """
        返回原始盘口信息
        """
        return self._origin_pankou

    @property
    def pankou_info(self):
        """
        返回盘口信息
        """
        return self._pankou_info

    @property
    def new_mark_data(self):
        """
        返回新市场数据
        """
        return self._new_mark_data

    @property
    def member_info(self):
        """
        俺也不太懂这是什么
        """
        return self._member_info

    @property
    def detail_info(self):
        """
        这个应该是成交数据。
        """
        return self._detail_info

    @property
    def cur_info(self):
        """
        看不懂是什么，但是包含了一些实时交易盘面数据
        """
        return self._cur_info

    @property
    def buy_info(self):
        """
        买盘
        """
        return self._buy_info

    @property
    def basic_infos(self):
        """
        返回股票基本信息
        """
        return self._basic_infos

    @property
    def ask_infos(self):
        """
        返回股票卖出信息
        """
        return self._ask_infos

    @property
    def price_info(self):
        """
        返回股票价格信息
        """
        return self._price_info


class StockPriceMonitor(StockMonitor):
    """
    对股票状态做进一步的简单的解析,并且实施监控
    """

    def __init__(self, stock_code):
        super().__init__(stock_code)
        self.is_trading = self._mark_status == "交易中"

    def detect_price_change(self, n: int = 6):
        """
        判断股票价格异动

        Parameters:
            n (int): 计算相对涨跌幅的时间区间，单位为分钟

        Returns:
            str: 返回值为"up"表示股票价格异动为拉升，"down"表示股票价格异动为打压，"no change"表示未发生异动
        """
        # 获取时间区间内的价格列表
        data = self._price_info[-n:]
        price_list = [float(item['price']) for item in data]

        # 计算相对涨跌幅
        if len(price_list) < n:
            return "no change"
        else:
            avg_price = sum(price_list[:-1]) / (n - 1)
            relative_change = (price_list[-1] - avg_price) / avg_price
            if relative_change > 0.01:
                return "up", relative_change * 100
            elif relative_change < -0.01:
                return "down", relative_change * 100
            else:
                return "no change"

    async def price_fluctuation(self) -> float:
        """
        股票异动拉升，猛烈打压监控
        """
        with os.scandir(self.path) as entries:
            files = sorted(entries, key=lambda entry: entry.name[:-5], reverse=True)

        prices = [
            float(item['value'].strip('%'))
            for file in files[:3:2]
            for item in json.load(open(file.path, encoding='utf8'))['Result']['pankouinfos']['list']
            if item['ename'] == 'priceLimit'
        ]
        return round(prices[0] - prices[1], 2)

    async def price_limit(self) -> dict:
        """
        涨跌幅，以及涨跌状态
        """
        return next((item for item in self.pankou_info if item['ename'] == 'priceLimit'), None)

    def large_purchase(self):
        pass


class Strategy(StockPriceMonitor):
    """
    定义属于自己的策略
    """

    def __init__(self, stock_code):
        super(Strategy, self).__init__(stock_code)

    # TODO

# if __name__ == '__main__':
#     # a = StockPriceMonitor('605178')
#     # b = a.priceLimit()
#     # pprint(a.detect_price_change())
#     # print(a.response)
#     # print(a.url)
#     # print(a.resp_for_stock_name)
#     a = StockCountFetcher()
#     pprint(a.get_sh_stock_data()["Result"][0]['DisplayData']['resultData']['tplData']['result']['list'])
