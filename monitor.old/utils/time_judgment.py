from datetime import datetime, time, timedelta


class Judgment:
    def __init__(self):
        self.now_time = datetime.now().time()

    def trading_session_a_day(self):
        """
        判断一天中的交易时段
        """
        if time(9, 15) < self.now_time < time(9, 25):
            return "竞价时间"
        elif time(9, 30) < self.now_time < time(11, 30):
            return True
        elif time(13, 0) < self.now_time < time(15, 0):
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
        if weekday >= 5:  # 周六周日不交易
            return False
        else:
            return True
