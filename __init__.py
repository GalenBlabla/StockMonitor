import asyncio
import re

from typing import Union

from nonebot import require, on_fullmatch

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot

from nonebot import on_command

from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    PrivateMessageEvent
)
from nonebot import get_driver

from .config import Config
from .fetcher.fetcher import StockPriceMonitor
from .fetcher.monitor import StockCountFetcher, StockInfoSyncFetcher
from .models.models import StockList, StockSubInfo, GroupList
from .models.database import DBinit
from .utils.time_judgment import Judgment

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def process_stock_info(stock_num):
    status = StockPriceMonitor(stock_code=stock_num)

    if not status.is_trading:
        return

    delta_rate_task = asyncio.create_task(status.price_fluctuation())
    price_limit_task = asyncio.create_task(status.price_limit())
    delta_rate, price_limit = await asyncio.gather(delta_rate_task, price_limit_task)
    stock_name = await StockList.get(stock_code=stock_num)
    stock_name = stock_name.name
    # 拉升或者打压检测
    if delta_rate >= 1:
        message = f"{status.stock_code}{stock_name}：急速拉升 {delta_rate}%。当前涨跌幅{price_limit['value']}。"
    elif delta_rate <= -1:
        message = f"{status.stock_code}猛烈打压 {delta_rate}%。当前涨跌幅{price_limit['value']}。"
    else:
        message = None
    try:
        bot: Bot = get_bot()
        groups_id = [536763872, 760478066]
        for group_id in groups_id:
            if bot is None:
                print("连接tx中")
            if message:
                # 查询订阅了该股票的用户
                sub_users = await StockSubInfo.filter(stock_num=status.stock_code, group_id=group_id).values('userid')
                # 如果订阅用户为空，则跳过该群的消息发送
                if not sub_users:
                    continue
                # 遍历订阅用户，推送异动信息
                user_ids = [sub['userid'] for sub in sub_users]
                at_users = ''.join([f"[CQ:at,qq={user_id}]" for user_id in user_ids])
                await bot.send_group_msg(group_id=group_id,
                                         message=f"{at_users}您订阅的股票出现异动：\n{message}", )
    except ValueError:
        print("连接tx中1")


async def process_stock_infos():
    await DBinit()
    stock_sub_info_list = await StockSubInfo.all().distinct().values_list('stock_num', flat=True)
    tasks = [asyncio.create_task(process_stock_info(stock_num)) for stock_num in stock_sub_info_list]
    await asyncio.gather(*tasks)


@scheduler.scheduled_job("interval", seconds=15, id="1", args=[1], kwargs={"arg2": 2})
async def run_every_15_seconds(arg1, arg2):
    if Judgment().trading_session_a_day() not in [True, "竞价时间"]:
        return
    await process_stock_infos()


@scheduler.scheduled_job("interval", minutes=10, id="2")
async def run_every_10_minutes():
    if Judgment().trading_session_a_day() not in [True, "竞价时间"]:
        return
    await DBinit()
    stock_count_fetcher = StockCountFetcher()
    await stock_count_fetcher.update_stocks()


# scheduler.add_job(run_every_day_from_program_start, "interval", days=1, id="xxx")

update_stock_list = on_command('/更新')

groups_id = [536763872, 760478066]


@update_stock_list.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    if event.group_id not in groups_id:
        return
    try:

        await DBinit()
        new_stocks = await StockInfoSyncFetcher.fetch_and_save()
        if len(new_stocks) > 0:
            # 构造新添加股票的消息
            new_stocks_msg = "新增股票：\n" + "\n".join(new_stocks)
            msg = f"更新股票信息成功！{new_stocks_msg}"
        else:
            msg = "更新股票信息成功,本次更新没有新增股票！"
    except Exception as e:
        msg = f"更新股票信息失败，错误信息：{str(e)}"
    await update_stock_list.finish(message=msg)


# 订阅股票
subscribe = on_command('订阅', aliases={'取消'})


@subscribe.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    # 数据库初始化
    if event.group_id not in groups_id:
        return
    await DBinit()

    message = str(event.get_message())
    user_id = event.get_user_id()
    stock_code = re.findall(r'\d+', message)[0]
    if event.message_type == "private":
        await subscribe.finish(message=stock_code)
        return
    group_id = event.group_id
    if not await StockList.filter(stock_code=stock_code).exists():
        msg = "数据库中未匹配到该股票代码。如果您确认有此股票代码，请联系管理员。"
        await subscribe.finish(message=msg, at_sender=True)
        return

    stock_name = await StockList.get(stock_code=stock_code)
    stock_name = stock_name.name

    # 判断当前用户在该群是否已经订阅该股票，是，则取消订阅，否则订阅
    exists = await StockSubInfo.exists(userid=user_id, stock_num=stock_code, group_id=group_id)
    if message.startswith("订阅"):
        if exists:
            await subscribe.finish(f"已经订阅过了{stock_code}{stock_name}", at_sender=True)
        else:
            await StockSubInfo(userid=user_id, stock_num=stock_code, group_id=group_id).save()
            msg = f"成功订阅{stock_code}{stock_name}"
            await subscribe.finish(message=msg, at_sender=True)
    elif message.startswith("取消"):
        if exists:
            await StockSubInfo.filter(userid=user_id, stock_num=stock_code, group_id=group_id).delete()
            msg = f"已经成功取消订阅{stock_code}{stock_name}"
            await subscribe.finish(message=msg, at_sender=True)
        else:
            await subscribe.finish(f"您并未订阅{stock_code}{stock_name}，无法取消", at_sender=True)

    # TODO 检查code是否合法


# 我的订阅
my_subscribe = on_command('我的订阅')


@my_subscribe.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    if event.group_id not in groups_id:
        return
        # 数据库初始化
    await DBinit()

    if event.message_type == "private":
        userid = event.get_user_id()
        subscribe_list = await StockSubInfo.filter(userid=userid).all()
        if len(subscribe_list) == 0:
            await my_subscribe.finish(message="您当前没有订阅任何股票")
        else:
            msg = "您当前订阅的股票有：\n"
            for stock in subscribe_list:
                stock_name = await StockList.get(stock_code=stock.stock_num)
                stock_name = stock_name.name
                msg += f"{stock.stock_num}{stock_name}\n"
            await my_subscribe.finish(message=msg, at_sender=True)
    else:
        userid = event.get_user_id()
        group_id = event.group_id
        subscribe_list = await StockSubInfo.filter(userid=userid, group_id=group_id).all()
        if len(subscribe_list) == 0:
            await my_subscribe.finish(message="您当前在本群没有订阅任何股票", at_sender=True)
        else:
            msg = "您当前在本群订阅的股票有：\n"
            for stock in subscribe_list:
                stock_name = await StockList.get(stock_code=stock.stock_num)
                stock_name = stock_name.name
                msg += f"{stock.stock_num}{stock_name}\n"
            await my_subscribe.finish(message=msg, at_sender=True)

# MONITORED_CLASSES = [(MyClass1, 1), (MyClass2, 2), (MyClass3, 3)]
#
#
# @scheduler.scheduled_job("cron", hour=9, minute=0, id="monitor_job")
# async def run_monitor_job():
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     for cls, status_code in MONITORED_CLASSES:
#         try:
#             # 进行自检操作
#             obj = cls()
#             if obj.self_check():
#                 print(f"[{now}] {cls.__name__}: {status_code} - OK")
#             else:
#                 print(f"[{now}] {cls.__name__}: {status_code} - Failed")
#         except Exception as e:
#             print(f"[{now}] {cls.__name__}: {status_code} - Failed ({e})")
