from tortoise import fields
from tortoise.models import Model


class StockSubInfo(Model):
    userid = fields.CharField(max_length=128, null=False)
    stock_num = fields.CharField(max_length=128, null=False)
    price = fields.CharField(max_length=128, null=True)
    sub_time = fields.DatetimeField(null=True, unique=False, auto_now_add=True)
    group_id = fields.CharField(max_length=12, null=False, unique=False)

    class Meta:
        table = 'stock_sub_info'
        indexes = [('group_id', 'userid')]

    def __str__(self):
        return self.userid


class StockList(Model):
    stock_code = fields.CharField(max_length=6, description="股票代码")
    name = fields.CharField(max_length=50, description="股票名称")
    exchange = fields.CharField(max_length=2, description="交易所")

    class Meta:
        table = 'stock_list_all'

    def __str__(self):
        return self.stock_code


class GroupList(Model):
    group_id = fields.CharField(max_length=12, null=False, unique=True)

    class Meta:
        table = 'group_list'

    def __str__(self):
        return self.group_id


class StockCountFetcherDB(Model):
    """
    股票信息表
    """
    code = fields.CharField(max_length=20, null=False, unique=True, description="股票代码")
    exchange = fields.CharField(max_length=10, null=False, description="交易所")
    increase = fields.CharField(max_length=20, null=True, description="涨幅基于价格")
    market = fields.CharField(max_length=10, null=False, description="市场")
    name = fields.CharField(max_length=100, null=False, description="股票名称")
    price_status = fields.CharField(max_length=10, null=False, description="股票价格状态")
    price_value = fields.CharField(max_length=20, null=False, description="股票价格")
    ratio_status = fields.CharField(max_length=10, null=False, description="股票涨跌状态")
    ratio_value = fields.CharField(max_length=20, null=False, description="股票涨跌幅度")

    class Meta:
        table = 'stock_count_fetcher'

    def __str__(self):
        return self.code
