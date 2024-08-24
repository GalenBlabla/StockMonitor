from app.processors.stock_processor import StockProcessor
from app.processors.strategy_combiner import StrategyCombiner
from app.strategies import strategies  # 从 strategies 动态导入的策略类列表
from app.services.data_cleaning import DefaultDataCleaner
from app.services.notification_service import RabbitMQNotifier

class ProcessorFactory:
    @staticmethod
    def create_processor() -> StockProcessor:
        strategy_instances = [strategy() for strategy in strategies]
        combiner = StrategyCombiner(strategy_instances)
        cleaner = DefaultDataCleaner()
        return StockProcessor(cleaner, combiner)
