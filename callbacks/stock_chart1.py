# callbacks/stock_chart.py
from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd

import datetime
from utils.helpers import safe_get

def get_data(data):

    data_dict = {}
    chart_1m = safe_get(data, '1m_chart_data', [])
    chart_5m = safe_get(data, '5m_chart_data', [])
    chart_1d = safe_get(data, '1d_chart_data', [])


    if chart_1d:
        data_dict = {
            '1min': chart_1m,
            '5min': chart_5m,
            '1day': chart_1d
        }
        print("使用真實 MongoDB 資料")
    else:
        print("找不到今天的 MongoDB 資料，使用假資料")
        data_dict = {
            '1min': [
                {'datetime': datetime.datetime(2025, 5, 22, 13, 27), 'open': 0.41965, 'high': 0.41965, 'low': 0.41965, 'close': 0.41965, 'volume': 1.0},
                {'datetime': datetime.datetime(2025, 5, 22, 13, 28), 'open': 0.42, 'high': 0.421, 'low': 0.419, 'close': 0.4205, 'volume': 5.0},
            ],
            '5min': [],
            '1day': []
        }

    return data_dict


def create_figure(data_list):
    """創建 Plotly 蠟燭圖"""
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
        template="plotly_dark"
    )
    return fig



def register_stock_chart_callbacks(app):

    #region UPDATE CHART
    # 回調函數們 - 統一使用 Plotly 圖表
    @app.callback(
        Output('chart1-graph', 'figure'),
        Input('chart1-dropdown', 'value'),
        Input("data-input-chart1", "data"),
        prevent_initial_call=True

    )
    def update_chart1(interval, data):
        """更新第一個圖表 (Plotly)"""
        return create_figure(get_data(data)[interval])

    @app.callback(
        Output('chart2-graph', 'figure'),
        Input('chart2-dropdown', 'value'),
        Input("data-input-chart2", "data"),
        prevent_initial_call=True
    )
    def update_chart2(interval, data):
        """更新第二個圖表 (Plotly)"""
        return create_figure(get_data(data)[interval])

    @app.callback(
        Output('chart3-graph', 'figure'),
        Input('chart3-dropdown', 'value'),
        Input("data-input-chart3", "data"),
        prevent_initial_call=True
    )
    def update_chart3(interval, data):
        """更新第三個圖表 (Plotly)"""
        return create_figure(get_data(data)[interval])