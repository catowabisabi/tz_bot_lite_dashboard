import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

from _mongo import MongoHandler
# 修正導入 - 統一使用 Tvlwc
try:
    from dash_tvlwc import Tvlwc
except ImportError:
    print("Warning: dash_tvlwc not found, using regular plotly charts")
    Tvlwc = None

est_timezone                = ZoneInfo("America/New_York")
est_time_today              = datetime.datetime.now(est_timezone)
est_time_today_date_str     = est_time_today.strftime('%Y-%m-%d')#MongoDB Format

est_time_today_date         = datetime.datetime.now(est_timezone).date()#用作計算yesterday
est_time_yesterday_date     = est_time_today_date - timedelta(days=1)
est_time_5days_ago_date     = est_time_today_date - timedelta(days=5)

mongo_handler = MongoHandler()
fundamentals_data_today = mongo_handler.find_doc('fundamentals_of_top_list_symbols', {'today_date': est_time_today_date_str})
fundamentals_data_5days = mongo_handler.find_doc(
            'fundamentals_of_top_list_symbols',
            {'today_date': {'$gte': est_time_5days_ago_date.strftime('%Y-%m-%d')}},
        )

print (f'Length of fundamentals_data_today: {len(fundamentals_data_today)}')

show_chart = False
if len(fundamentals_data_today) > 0:
    show_chart = True

# 假資料===========================================================
data_1min = [
    {'datetime': datetime.datetime(2025, 5, 22, 13, 27), 'open': 0.41965, 'high': 0.41965, 'low': 0.41965, 'close': 0.41965, 'volume': 1.0},
    {'datetime': datetime.datetime(2025, 5, 22, 13, 28), 'open': 0.42, 'high': 0.421, 'low': 0.419, 'close': 0.4205, 'volume': 5.0},
    # 可以加入更多資料
]

data_5min = data_1min  # 假設用同樣資料做展示
data_day = data_1min   # 假設用同樣資料做展示

# 包裝成 dict
data_dict = {
    '1min': data_1min,
    '5min': data_5min,
    '1day': data_day
}

# 假資料===========================================================

# 試用真正的 MongoDB 資料
if len(fundamentals_data_today) > 0:
    try:
        data_1min = fundamentals_data_today[0]['1m_chart_data']
        data_5min = fundamentals_data_today[0]['5m_chart_data']
        data_day = fundamentals_data_today[0]['1d_chart_data']
        data_dict = {
            '1min': data_1min,
            '5min': data_5min,
            '1day': data_day
        }
        print("使用真實 MongoDB 資料")
    except KeyError as e:
        print(f"MongoDB 資料格式錯誤: {e}, 使用假資料")

# 初始化 app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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

def prepare_tvlwc_data(data_list):
    """準備 Tvlwc 組件需要的資料格式"""
    try:
        df = pd.DataFrame(data_list)
        
        # 確保 datetime 列存在
        if 'datetime' not in df.columns:
            print("警告：資料中沒有 datetime 欄位")
            return []
        
        # 轉換時間戳
        df['time'] = pd.to_datetime(df['datetime']).astype(int) // 10**9
        
        # 轉換為 Tvlwc 需要的格式
        tvlwc_data = []
        for _, row in df.iterrows():
            tvlwc_data.append({
                'time': int(row['time']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
        
        print(f"準備了 {len(tvlwc_data)} 筆 Tvlwc 資料")
        if len(tvlwc_data) > 0:
            print(f"第一筆資料範例: {tvlwc_data[0]}")
        
        return tvlwc_data
    except Exception as e:
        print(f"準備 Tvlwc 資料時發生錯誤: {e}")
        return []

def chart_container(interval='1min', chart_id='chart1', use_tvlwc=True):
    """創建圖表容器"""
    return dbc.Container([
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"Chart - {interval.upper()}", className="card-title"),
                dcc.Dropdown(
                    id=f"{chart_id}-dropdown",
                    options=[
                        {'label': '1 Min', 'value': '1min'},
                        {'label': '5 Min', 'value': '5min'},
                        {'label': '1 Day', 'value': '1day'}
                    ],
                    value=interval,
                    clearable=False,
                    style={"width": "200px"}
                )
            ]),
            dbc.CardBody([
                # 根據是否有 Tvlwc 組件來選擇使用哪種圖表
                Tvlwc(
                    id=f"{chart_id}-graph", 
                    height=400,
                    seriesTypes=['candlestick'],  # 設定為蠟燭圖
                    chartOptions={'layout': {'background': {'color': '#1e1e1e'}}}  # 設定深色主題
                ) if (Tvlwc and use_tvlwc) 
                else dcc.Graph(id=f"{chart_id}-graph", style={"height": "400px"})
            ])
        ], className="my-4")
    ], fluid=True)

# 應用程式佈局 - 暫時所有圖表都使用 Plotly
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(chart_container('1min', chart_id='chart1', use_tvlwc=False), xs=12, md=4),
        dbc.Col(chart_container('5min', chart_id='chart2', use_tvlwc=False), xs=12, md=4),
        dbc.Col(chart_container('1day', chart_id='chart3', use_tvlwc=False), xs=12, md=4),
    ], justify="center", className="gy-4")  # gy-4 加上垂直間距
], fluid=True)

# 回調函數們 - 統一使用 Plotly 圖表
@app.callback(
    Output('chart1-graph', 'figure'),
    Input('chart1-dropdown', 'value')
)
def update_chart1(interval):
    """更新第一個圖表 (Plotly)"""
    return create_figure(data_dict[interval])

@app.callback(
    Output('chart2-graph', 'figure'),
    Input('chart2-dropdown', 'value')
)
def update_chart2(interval):
    """更新第二個圖表 (Plotly)"""
    return create_figure(data_dict[interval])

@app.callback(
    Output('chart3-graph', 'figure'),
    Input('chart3-dropdown', 'value')
)
def update_chart3(interval):
    """更新第三個圖表 (Plotly)"""
    return create_figure(data_dict[interval])

if __name__ == '__main__':
    app.run(debug=True)