# core/exceptions.py

class StrategyError(Exception):
    """基础策略错误"""
    pass

class DataValidationError(StrategyError):
    """数据验证错误，例如数据缺失或无效"""
    pass

class ProcessingError(StrategyError):
    """处理过程中的错误"""
    pass

class CalculationError(StrategyError):
    """计算过程中的错误"""
    pass

class ExternalServiceError(StrategyError):
    """外部服务错误，例如 API 调用失败"""
    pass
