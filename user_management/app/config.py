from pydantic_settings import BaseSettings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.theme import Theme
from rich.box import DOUBLE_EDGE  # 使用 Rich 的双边框样式

class Settings(BaseSettings):
    DATABASE_URL: str 
    REDIS_URL: str 
    RABBITMQ_URL: str
    LOG_LEVEL: str

    class Config:
        env_file = ".env"

# 初始化设置
settings = Settings()

# 创建一个自定义的主题
custom_theme = Theme({
    "title": "bold magenta",
    "setting": "bold cyan",
    "value": "bold green",
    "info": "dim cyan"
})

# 使用自定义主题
console = Console(theme=custom_theme)

# 创建一个表格来展示配置
table = Table(show_header=True, header_style="bold yellow", box=DOUBLE_EDGE)

table.add_column("Setting", style="setting")
table.add_column("Value", style="value")

# 动态添加行
config_dict = settings.model_dump()
for key, value in config_dict.items():
    table.add_row(key, value)

# 包装在一个面板中以增加视觉效果
panel = Panel(table, title="Loaded Configuration", title_align="left", border_style="bright_blue")

# 输出表格和面板
console.print(panel)
