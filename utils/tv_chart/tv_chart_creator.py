
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class TVChartCreator:
    def __init__(self, yf_df):
        self.yf_df = yf_df
        self.hist = self.prepare_data()

    #region Prepare Data
    def prepare_data(self):
         # 準備資料用於繪圖
        self.hist = self.yf_df.copy()
        self.hist.index.name = 'Datetime'
        self.hist.reset_index(inplace=True)
        
        # 計算蠟燭圖顏色
        self.hist['Color'] = ['green' if c >= o else 'red' for c, o in zip(self.hist['close'], self.hist['open'])]
        return self.hist
    
    #region Create Figure
    def create_basic_figure(self):
        hist = self.hist
        # 創建子圖 (上方 K 線圖，下方成交量)
        self.fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # 添加 K 線圖
        self.fig.add_trace(go.Candlestick(
            x=hist["Datetime"],
            open=hist['open'],
            high=hist['high'],
            low=hist['low'],
            close=hist['close'],
            increasing_line_color='lime',  
            decreasing_line_color='red',
            name="OHLC"
        ), row=1, col=1)
        return self.fig
    
    #region Create Volume Figure
    def create_volume_figure(self):
        hist = self.hist

        # 添加成交量圖
        self.fig.add_trace(go.Bar(
            x=hist["Datetime"],
            y=hist['volume'],
            marker=dict(color=hist['Color']),
            opacity=0.3,
            name="Volume"
        ), row=2, col=1)
        return self.fig
    
    #region Create Time Line
    def create_time_line(self):
        hist = self.hist
        # 添加時間間隔線
        for i, time in enumerate(hist["Datetime"]):
            if i == 0 or i == len(hist)-1:
                continue
                
            minute = time.minute
            if minute == 0:  # 每小時標記
                self.fig.add_shape(type="line",
                          x0=time, y0=0,
                          x1=time, y1=1,
                          xref='x', yref='paper',
                          line=dict(color="white", width=0.5, dash="dot"))
        return self.fig
    
    #region Create Premarket Background0
    def create_premarket_background_color0(self):

        hist = self.hist    
        # 标记盘前时段（美东时间 4:00 - 9:30）
        pre_market_start = hist["Datetime"].iloc[0].replace(hour=4, minute=0, second=0)
        pre_market_end = hist["Datetime"].iloc[0].replace(hour=9, minute=30, second=0)
        self.fig.add_vrect(
            x0=pre_market_start, x1=pre_market_end,
            fillcolor="yellow", opacity=0.2,
            layer="below", line_width=0,
            row="all", col="all"
        )

        # 标记盘后时段（美东时间 16:00 - 20:00）
        post_market_start = hist["Datetime"].iloc[0].replace(hour=16, minute=0, second=0)
        post_market_end = hist["Datetime"].iloc[0].replace(hour=20, minute=0, second=0)
        self.fig.add_vrect(
            x0=post_market_start, x1=post_market_end,
            fillcolor="navy", opacity=0.2,
            layer="below", line_width=0,
            row="all", col="all"
        )
        return self.fig


    #region Create Premarket Background
    def create_premarket_background_color(self):
        hist = self.hist
        # 添加前市時間區間的背景顏色
        # 获取所有唯一的日期（处理多日数据）
        unique_dates = pd.to_datetime(hist["Datetime"].dt.date.unique())

        for date in unique_dates:
            # 盘前时段（4:00 - 9:30 ET）
            pre_market_start = pd.to_datetime(f"{date.strftime('%Y-%m-%d')} 04:00:00").tz_localize("America/New_York")
            pre_market_end = pd.to_datetime(f"{date.strftime('%Y-%m-%d')} 09:30:00").tz_localize("America/New_York")
            
            # 盘后时段（16:00 - 20:00 ET）
            post_market_start = pd.to_datetime(f"{date.strftime('%Y-%m-%d')} 16:00:00").tz_localize("America/New_York")
            post_market_end = pd.to_datetime(f"{date.strftime('%Y-%m-%d')} 20:00:00").tz_localize("America/New_York")
            
            # 添加背景色
            self.fig.add_vrect(
                x0=pre_market_start, x1=pre_market_end,
                fillcolor="yellow", opacity=0.2,
                layer="below", line_width=0,
                row="all", col="all"
            )
            self.fig.add_vrect(
                x0=post_market_start, x1=post_market_end,
                fillcolor="navy", opacity=0.2,
                layer="below", line_width=0,
                row="all", col="all"
            )

        return self.fig
    
    def create_support_lines(self, sr_levels):
        hist = self.hist
        # 添加支撐位水平線
        support_colors = ['#00FFFF', '#00BFFF', '#1E90FF', '#0000FF', '#00008B']
        for i, (method, level) in enumerate(sr_levels['Support'][:5]):  # 限制顯示前5個支撐位
            if level is None or np.isnan(level):
                continue
                
            color_idx = min(i, len(support_colors)-1)
            self.fig.add_shape(type="line",
                          x0=hist["Datetime"].iloc[0], y0=level,
                          x1=hist["Datetime"].iloc[-1], y1=level,
                          line=dict(color=support_colors[color_idx], width=1.5, dash="solid"),
                          opacity=0.7,
                          row=1, col=1)
            self.fig.add_annotation(
                x=hist["Datetime"].iloc[-1], y=level,
                text=f"S: {method} ({level:.2f})",
                showarrow=False,
                xanchor="right",
                font=dict(color=support_colors[color_idx], size=10),
                row=1, col=1
            )
        return self.fig
    
    def create_resistance_lines(self, sr_levels):
        hist = self.hist
        # 添加阻力位水平線
         # 添加阻力位水平線
        resistance_colors = ['#FFC0CB', '#F08080', '#FA8072', '#FF6347', '#FF0000']
        for i, (method, level) in enumerate(sr_levels['Resistance'][:5]):  # 限制顯示前5個阻力位
            if level is None or np.isnan(level):
                continue
                
            color_idx = min(i, len(resistance_colors)-1)
            self.fig.add_shape(type="line",
                          x0=hist["Datetime"].iloc[0], y0=level,
                          x1=hist["Datetime"].iloc[-1], y1=level,
                          line=dict(color=resistance_colors[color_idx], width=1.5, dash="solid"),
                          opacity=0.7,
                          row=1, col=1)
            self.fig.add_annotation(
                x=hist["Datetime"].iloc[-1], y=level,
                text=f"R: {method} ({level:.2f})",
                showarrow=False,
                xanchor="right",
                font=dict(color=resistance_colors[color_idx], size=10),
                row=1, col=1
            )
        return self.fig
    
    def create_chart_style(self, ticker_symbol, period, interval):
        # 設定 TradingView 風格
        self.fig.update_layout(
            title=f'{ticker_symbol.upper()} {period} {interval} Chart with Support/Resistance (ET)',
            xaxis_title='Time (ET)',
            yaxis_title='Price ($)',
            xaxis_rangeslider_visible=False,
            paper_bgcolor="black",
            plot_bgcolor="#0F1B2A",
            font=dict(color="white"),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.2)",
                showticklabels=True
            ),
            yaxis=dict(gridcolor="rgba(255, 255, 255, 0.2)"),
            yaxis2=dict(gridcolor="rgba(255, 255, 255, 0.2)"),
            margin=dict(l=50, r=50, t=80, b=50),
            height=800
        )
        return self.fig