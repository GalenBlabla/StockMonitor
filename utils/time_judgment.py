"""
存放通用的功能函数
"""
import time

from datetime import datetime


class Judgment:
    now_time = time.strftime("%H:%M:%S", time.localtime())

    def trading_session_a_day(self):
        """
        判断一天中的交易时段
        """
        if "09:15:00" < self.now_time < "09:25:00":
            return "竞价时间"
        elif "09:30:00" < self.now_time < "11:30:00":
            return True
        elif "13:00:00" < self.now_time < "15:00:00":
            return True
        else:
            return False

    @staticmethod
    def trading_session_a_week():
        """
        判断一周中的交易日
        """
        now_date = datetime.now().date()
        weekday = now_date.weekday()
        if weekday == 5 or weekday == 6:  # 周六周日不交易
            return False
        else:
            return True

# if __name__ == '__main__':
#     a = Judgment().trading_session_a_day()
#     print(a)
