import plotly.graph_objects as go
from utils.helpers import safe_float
from utils.style import colors
from utils.helpers import safe_get
from dash import html,dcc

def create_price_chart(data):
    day_low = safe_float(data.get('day_low'), 0)
    yesterday_close = safe_float(data.get('yesterday_close'), 0)
    day_close = safe_float(data.get('day_close'), 0)
    day_high = safe_float(data.get('day_high'), 0)
    market_open_high = safe_float(data.get('market_open_high'), 0)
    market_open_low = safe_float(data.get('market_open_low'), 0)
    key_levels = data.get('key_levels', [])  # 獲取關鍵價位列表
    
    fig = go.Figure()
    
    # X軸位置（按時間順序排列）
    x_positions = ['Yesterday Close', 'Day Low', 'Day High', 'Day Close']
    x_range = ['Yesterday Close', 'Day Close']  # 用於水平線的範圍
    
    # 主價格線（連接所有價格點）
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=[yesterday_close, day_low, day_high, day_close],
        mode='markers+lines',
        marker=dict(
            color=[colors['neutral'], colors['negative'], colors['warning'], colors['positive']],
            size=12
        ),
        line=dict(color=colors['neutral'], width=1),
        name='Price Movement',
        showlegend=False
    ))
    
    # 添加關鍵價位線
    for i, level in enumerate(key_levels, 1):
        fig.add_trace(go.Scatter(
            x=x_range,
            y=[level, level],
            mode='lines',
            line=dict(color='purple', width=1.5, dash='dot'),
            name=f'Key Level {i} ({level})',
            opacity=0.7,
            showlegend=False
        ))
    
    # 為每個價格點添加單獨的圖例項
    fig.add_trace(go.Scatter(
        x=['Yesterday Close'],
        y=[yesterday_close],
        mode='markers',
        marker=dict(color=colors['neutral'], size=12),
        name='Yesterday Close',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=['Day Low'],
        y=[day_low],
        mode='markers',
        marker=dict(color=colors['negative'], size=12),
        name='Day Low',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=['Day High'],
        y=[day_high],
        mode='markers',
        marker=dict(color=colors['warning'], size=12),
        name='Day High',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=['Day Close'],
        y=[day_close],
        mode='markers',
        marker=dict(color=colors['positive'], size=12),
        name='Day Close',
        showlegend=True
    ))

    # Add key level line
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[market_open_high, market_open_high],
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'Market Open High ({market_open_high})'
    ))

    # Add key level line
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[market_open_low, market_open_low],
        mode='lines',
        line=dict(color='green', width=2, dash='dash'),
        name=f'Market Open Low ({market_open_low})'
    ))
    
    # 更新佈局
    fig.update_layout(
        #title=f"{safe_get(data, 'symbol')} Price Overview",
        xaxis_title='',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        #height=400
    )
    
    # 設置Y軸範圍（包含所有關鍵價位）
    all_values = [yesterday_close, day_low, day_high, day_close] + key_levels
    min_price = min(all_values) * 0.95
    max_price = max(all_values) * 1.05
    fig.update_yaxes(range=[min_price, max_price])
    
    return fig

def create_cash_debt_chart(data):
    sec_data = data.get('sec_filing_analysis', {})
    cash = safe_float(sec_data.get('Cash (USD)'))
    debt = safe_float(sec_data.get('Debt (USD)'))
    
    # 如果没有数据，显示提示信息
    if cash is None and debt is None:
        fig = go.Figure()
        fig.add_annotation(
            text="No cash/debt data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Cash vs Debt Position',
            template='plotly_dark',
            height=350
        )
        return fig
    
    fig = go.Figure()
    
    # 分别添加现金和债务柱状图
    if cash is not None:
        fig.add_trace(go.Bar(
            x=['Cash'],
            y=[cash/1000000],
            text=[f"${cash/1000000:.2f}M" if cash is not None else "N/A"],
            textposition='auto',
            marker_color=colors['positive'],
            name='Cash'
        ))
    
    if debt is not None:
        fig.add_trace(go.Bar(
            x=['Debt'],
            y=[debt/1000000],
            text=[f"${debt/1000000:.2f}M" if debt is not None else "N/A"],
            textposition='auto',
            marker_color=colors['negative'],
            name='Debt'
        ))
    
    # Update layout
    fig.update_layout(
        title='Cash vs Debt Position (in millions USD)',
        yaxis_title='Amount (USD Millions)',
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_price_chart_card(data):
    """創建包含標題和圖表的卡片組件"""
    return html.Div([
        html.H3(f"{safe_get(data, 'symbol')} Price Chart", className='card-title'),
        html.Div([
            dcc.Graph(
                figure=create_price_chart(data),
                className='price-chart-container'
            )
        ], className='card-content')
    ], className='chart-card')