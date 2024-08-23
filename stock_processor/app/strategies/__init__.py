import os
import importlib
import inspect
from app.core.interfaces import Strategy

# 动态导入策略模块
strategy_modules = []
strategy_dir = os.path.dirname(__file__)

for file in os.listdir(strategy_dir):
    if file.endswith("_strategy.py") and file != "__init__.py":
        module_name = f"app.strategies.{file[:-3]}"
        module = importlib.import_module(module_name)
        strategy_modules.append(module)

# 动态获取所有非抽象策略类
strategies = []
for module in strategy_modules:
    for attr in dir(module):
        strategy_class = getattr(module, attr)
        if inspect.isclass(strategy_class) and issubclass(strategy_class, Strategy) and not inspect.isabstract(strategy_class):
            strategies.append(strategy_class)

# 导出所有非抽象策略类
__all__ = [strategy.__name__ for strategy in strategies]

