from tortoise.models import Model
from tortoise import fields

class Subscription(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    stock_code = fields.CharField(max_length=10)
