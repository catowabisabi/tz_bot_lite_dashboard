
from bson import ObjectId
import json
import pandas as pd
from plotly import graph_objects as go
from datetime import datetime


def safe_get(data, key, default="N/A"):
    """安全获取数据，如果值为None则返回默认值"""
    value = data.get(key)
    return default if value is None else value

def safe_float(value, default=0):
    """安全转换为浮点数"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
    

def create_candle_figure(data_list):
    df = pd.DataFrame(data_list)
    fig = go.Figure(data=[
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Price"
        )
    ])
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False,
        height=400,
        template="plotly_white"
    )
    return fig
    

def get_chart_data(data_dict, chart_key='1m_chart_data'):
    chart_data_raw = safe_get(data_dict, chart_key, {})
    chart_data = {
        'timestamp': [item['datetime'] for item in chart_data_raw],
        'open': [item['open'] for item in chart_data_raw],
        'high': [item['high'] for item in chart_data_raw],
        'low': [item['low'] for item in chart_data_raw],
        'close': [item['close'] for item in chart_data_raw],
        'volume': [item['volume'] for item in chart_data_raw],
}
    return chart_data





class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            # 把 datetime 轉成 ISO 格式字串
            return o.isoformat()
        elif isinstance(o, ObjectId):
            # 把 ObjectId 轉成字串
            return str(o)
        return super().default(o)
