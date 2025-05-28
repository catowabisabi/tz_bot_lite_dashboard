import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

from _mongo import MongoHandler



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
#print (fundamentals_data_today[0]['1m_chart_data'])
data_1min = fundamentals_data_today[0]['1m_chart_data']
data_5min = fundamentals_data_today[0]['5m_chart_data']
data_day = fundamentals_data_today[0]['1d_chart_data']


def keep_last_day_data(data_1min):
    if not data_1min:return []
    last_date = max(item['datetime'].date() for item in data_1min)
    filtered_data = [item for item in data_1min if item['datetime'].date() == last_date]
    return filtered_data

data_1min = keep_last_day_data(data_1min)
data_5min = keep_last_day_data(data_5min)




data_dict = {
    '1min': data_1min,
    '5min': data_5min,
    '1day': data_day
}
# 初始化 app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_figure(data_list):
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

def chart_container(interval='1min', chart_id='chart1'):
    return dbc.Container([
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"Stock Chart - {interval.upper()}", className="card-title"),
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
                dcc.Graph(id=f"{chart_id}-graph")
            ])
        ], className="my-4")
    ], fluid=True)


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(chart_container('1min', chart_id='chart1'), xs=12, md=4),
        dbc.Col(chart_container('5min', chart_id='chart2'), xs=12, md=4),
        dbc.Col(chart_container('1day', chart_id='chart3'), xs=12, md=4),
    ], justify="center", className="gy-4")  # gy-4 加上垂直間距
], fluid=True)



@app.callback(
    Output('chart1-graph', 'figure'),
    Input('chart1-dropdown', 'value')
)
def update_chart1(interval):
    return create_figure(data_dict[interval])

@app.callback(
    Output('chart2-graph', 'figure'),
    Input('chart2-dropdown', 'value')
)
def update_chart2(interval):
    return create_figure(data_dict[interval])

@app.callback(
    Output('chart3-graph', 'figure'),
    Input('chart3-dropdown', 'value')
)
def update_chart3(interval):
    return create_figure(data_dict[interval])


if __name__ == '__main__':
    app.run(debug=True)
