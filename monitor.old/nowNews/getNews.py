from fetcher.stock_news_fetcher import News
import time

import json
import jsonpath


def get_msg():
    a = News()

    news_json = a.get_latest_news()
    news_json = json.dumps(news_json, ensure_ascii=False)
    # print(news_json)


    data = json.loads(news_json)
    news = jsonpath.jsonpath(data,'$.content.items[0].data')
    tag = jsonpath.jsonpath(data,'$.tag')
    evaluate = jsonpath.jsonpath(data,'$.evaluate')
    code = jsonpath.jsonpath(data,'$.entity[0].code')
    name = jsonpath.jsonpath(data,'$.entity[0].name')
    # print(news+tag+evaluate+code+name)
    return str(news+tag+evaluate+code+name)


print(get_msg())


# timeArray = time.localtime(timeStamp)
# otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
# print(otherStyleTime)
