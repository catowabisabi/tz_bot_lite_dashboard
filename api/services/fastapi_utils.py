# _utils.py

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

def format_market_cap(value: Optional[float]) -> str:
    """
    Formats a market capitalization value into a human-readable string (e.g., 1.23B, 456M).
    """
    if value is None:
        return "N/A"
    
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"{value:.2f}"

def prepare_tvlwc_data(chart_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepares chart data for the dash_tvlwc component.
    Converts 'datetime' to Unix timestamp (seconds) and ensures OHLC values are floats.
    """
    if not chart_data:
        return []
    
    formatted_data = []
    for item in chart_data:
        if isinstance(item.get('datetime'), str):
            try:
                dt = datetime.fromisoformat(item['datetime'])
            except ValueError:
                continue
        else:
            dt = item.get('datetime')
            
        if not dt:
            continue
            
        formatted_data.append({
            'time': dt.isoformat(),
            'open': float(item.get('open', 0)),
            'high': float(item.get('high', 0)),
            'low': float(item.get('low', 0)),
            'close': float(item.get('close', 0)),
            'volume': float(item.get('volume', 0))
        })
    
    return formatted_data

def filter_chart_data(chart_data: List[Dict[str, Any]], interval: str = '1min') -> List[Dict[str, Any]]:
    """根據時間間隔過濾圖表數據"""
    if not chart_data:
        return []
    
    df = pd.DataFrame(chart_data)
    if 'datetime' not in df.columns:
        return []
    
    # 確保datetime列是datetime類型
    if df['datetime'].dtype == 'object':
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    now = datetime.now()
    
    if interval == '1min':
        # 只保留最近3小時的數據
        cutoff = now - timedelta(hours=3)
        df = df[df['datetime'] >= cutoff]
    elif interval == '5min':
        # 只保留當天的數據
        today = now.date()
        df = df[df['datetime'].dt.date == today]
    elif interval == '1day':
        # 保留最近30天的數據
        cutoff = now - timedelta(days=30)
        df = df[df['datetime'] >= cutoff]
    
    # 按時間排序
    df = df.sort_values('datetime')
    
    return df.to_dict('records')