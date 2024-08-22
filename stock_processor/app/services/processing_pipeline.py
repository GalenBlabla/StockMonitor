from .data_cleaning import clean_stock_data
from .strategy_layer import analyze_stock_data
from .notification_service import send_notification

def process_stock_data(stock_code, raw_data):
    """处理股票数据：清洗、分析、通知"""
    cleaned_data = clean_stock_data(raw_data, stock_code)
    analysis_result = analyze_stock_data(stock_code, cleaned_data)
    print("Analysis Result:", analysis_result)  # 打印分析结果进行检查
    send_notification(stock_code, analysis_result)
