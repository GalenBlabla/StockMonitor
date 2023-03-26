import re

import urllib.parse
from pprint import pprint
import json
import jsonpath
import requests


class News:
    URL = "https://finance.pae.baidu.com/selfselect/news"
    HEADERS = {
        "Cookies": 'BIDUPSID=4154BAE7E88A3C256C441776949A2B1F; PSTM=1632890871; __yjs_duid=1_f47d839a61cba4039e210bbec74edfc11632975760217; BAIDUID=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; MCITY=-163:; newlogin=1; MAWEBCUID=web_dWKLuQjvniuSwIfDUmeJWpoSJitqQTaQMGdHXiBblvOZOuGHbB; BDUSS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; BDUSS_BFESS=k9iN3VoV35iMjFDd0pXYklrVWNTZ1ZWbjRBMlFCMFlTdTRPM0pxMHhGZTFqQzVrSVFBQUFBJCQAAAAAAQAAAAEAAADjzYZAVHJhc2hlc3RBcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALX~BmS1~wZkd; ZFY=vD0w8lrD39F2mrHjQEwBY7bmvW5pxRHy06U:AmCaFQZY:C; BAIDUID_BFESS=5C09C8E4512FE4E5AB1338D54340F9F6:FG=1; ariaDefaultTheme=undefined; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=3; BDRCVFR[S4-dAuiWMmn]=I67x6TjHwwYf0; delPer=0; MBD_AT=0; RT="z=1&dm=baidu.com&si=1b37083f-7d9f-4a28-96c7-0a3a5fabf483&ss=lfaqa46f&sl=3&tt=16r&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=4rr&ul=ls3&hd=lsv"; BA_HECTOR=858h25a70halag008k00ak881i191661m; H_PS_PSSID=38185_36542_38123_38368_38309_38170_38289_38236_36802_38261_37934_38313_38382_38285_37900_26350_38282_37881; ab_sr=1.0.1_MmViNjJkOGEzZGY2YzMyZTgxMTMyZmExYjY4ODRjZjY2NzgxM2VkYzM3N2U1ZjY5ZjRhZTc0Y2U4YmRkZjRmMzYwYThjYTY1M2FmYjA0YjgyNTdjMGE5YThhMjIxM2Q0NjM2MzliOWJiYWQ1MzQ1M2JkY2QzNDUyYjNkMDg4MTA5OTU4YjkyNzE2OTJkOGYyMTM0OTg0YjdlNWNkMmU4MA==',
        "Use-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
        "Referer": "https://gushitong.baidu.com/"
    }

    def __init__(self):
        self.refresh_info()

    def __get_response(self):
        """
        获取新闻接口返回
        """
        params = {
            "rn": 10,
            "pn": 0,
            "finClientType": "pc"
        }
        # 对参数进行 URL 编码
        encoded_params = urllib.parse.urlencode(params)
        url = f"{self.URL}?{encoded_params}"
        resp = requests.get(url, headers=self.HEADERS)
        return resp.json()

    def refresh_info(self):
        """
        刷新新闻列表
        """
        self.response = self.__get_response()
        self.__result_code = self.response['ResultCode']
        self.__result_tag = self.response['Result']['tabs'][0]['contents']['tag']
        self.__news_list = self.response['Result']['tabs'][0]['contents']['list']

    def get_latest_news(self):
        """
        获取最近的一条新闻
        @return:
        """
        return self.__news_list[0]


class NewsClassify(News):
    def __init__(self):
        super(NewsClassify, self).__init__()

    def message(self):
        news_latest = self.get_latest_news()

        news_json = news_latest.get_latest_news()
        news_json = json.dumps(news_json, ensure_ascii=False)

        data = json.loads(news_json)

        return str(
            jsonpath.jsonpath(data, '$.content.items[0].data')
            +
            jsonpath.jsonpath(data, '$.tag')
            +
            jsonpath.jsonpath(data, '$.evaluate') + jsonpath.jsonpath(data, '$.entity[0].code')
            +
            jsonpath.jsonpath(data, '$.entity[0].name')
        )


if __name__ == '__main__':
    news = NewsClassify()
    news_latest = news.message()
    print(news_latest)
