import dash
from dash import dcc, html, Input, Output, callback, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from dash.exceptions import PreventUpdate
from _mongo import MongoHandler
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.style import index_string as in_str, colors as my_colors

ny_time = datetime.now(ZoneInfo("America/New_York"))
today_str = ny_time.strftime('%Y-%m-%d')

page_title = "喵喵今日熱股"

# Initialize the Dash app
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css"
]

app = dash.Dash(__name__, 
               suppress_callback_exceptions=True,
               external_stylesheets=external_stylesheets)

# Custom CSS
app.index_string = in_str

# Styling
colors = my_colors
title = "貓咪神-短炒Scanner"
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

# Function to create stock list page
def create_stock_list_page(stocks_data):
    stock_cards = []
    
    for stock in stocks_data:
        change_percentage = safe_float(stock.get('close_change_percentage'), 0)
        change_color = colors['positive'] if change_percentage >= 0 else colors['negative']
        
        stock_card = html.Div([
            html.Div(safe_get(stock, 'symbol'), className='stock-symbol'),
            html.Div(safe_get(stock, 'name'), className='stock-name'),
            html.Div([
                html.Div([
                    html.Div('Price', className='metric-title'),
                    html.Div(f"${safe_get(stock, 'day_close')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.Div('Change %', className='metric-title'),
                    html.Div(f"{change_percentage:.2f}%", className='metric-value', style={'color': change_color})
                ], className='metric-container'),
                html.Div([
                    html.Div('Sector', className='metric-title'),
                    html.Div(safe_get(stock, 'sector'), className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.Div('Float Risk', className='metric-title'),
                    html.Div(safe_get(stock, 'float_risk'), className='metric-value')
                ], className='metric-container'),
            ], className='stock-metrics')
        ], className='stock-card', id={'type': 'stock-card', 'index': safe_get(stock, 'symbol')})
        
        stock_cards.append(stock_card)
    
    return html.Div([
        html.Div([
            html.H1(title, className='header-title'),
            html.P(f"Data as of {safe_get(stocks_data[0], 'today_date') if stocks_data else 'N/A'}", className='header-date'),
        ], className='header'),
        
        html.Div([
            html.H2(page_title, style={'margin-bottom': '20px'}),
            html.Div(stock_cards, className='stock-list')
        ], className='main-content'),
        
        html.Div([
            html.P('© 2025 Stock Analytics Dashboard', className='footer-text'),
        ], className='footer')
    ])

# Function to create stock detail page
def create_stock_detail_page(data):
    # Calculate Market Cap
    outstanding_shares = safe_float(data.get('outstandingShares'))
    day_close = safe_float(data.get('day_close'))
    market_cap = outstanding_shares * day_close if outstanding_shares and day_close else None
    market_cap_formatted = f"${market_cap/1000000:.2f}M" if market_cap else "N/A"

    # Function to create the price chart
    def create_price_chart():
        day_low = safe_float(data.get('day_low'), 0)
        yesterday_close = safe_float(data.get('yesterday_close'), 0)
        day_close = safe_float(data.get('day_close'), 0)
        day_high = safe_float(data.get('day_high'), 0)
        
        fig = go.Figure()
        
        # Add lines for price ranges
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[day_low],
            mode='markers',
            marker=dict(color=colors['negative'], size=12),
            name='Day Low'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[yesterday_close],
            mode='markers',
            marker=dict(color=colors['neutral'], size=12),
            name='Yesterday Close'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[day_close],
            mode='markers',
            marker=dict(color=colors['positive'], size=12),
            name='Day Close'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[day_high],
            mode='markers',
            marker=dict(color=colors['warning'], size=12),
            name='Day High'
        ))
        
        # Add key level line
        fig.add_trace(go.Scatter(
            x=['Price Range', 'Price Range'],
            y=[3.02, 3.02],
            mode='lines',
            line=dict(color='black', width=2, dash='dash'),
            name='Acquisition Price ($3.02)'
        ))
        
        # Add range
        fig.add_trace(go.Scatter(
            x=['Price Range', 'Price Range'],
            y=[day_low, day_high],
            mode='lines',
            line=dict(color=colors['neutral'], width=3),
            name='Day Range'
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{safe_get(data, 'symbol')} Price Overview",
            xaxis_title='',
            yaxis_title='Price (USD)',
            template='plotly_dark',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=400
        )
        
        # Set y-axis range
        min_price = min(day_low, yesterday_close) * 0.9
        max_price = max(day_high, 3.05) * 1.1
        fig.update_yaxes(range=[min_price, max_price])
        
        return fig

    # Function to create the cash/debt chart
    def create_cash_debt_chart():
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
                template='plotly_white',
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

    # Create the key metrics card
    def create_metrics_card():
        change_percentage = safe_float(data.get('close_change_percentage'), 0)
        change_color = colors['positive'] if change_percentage >= 0 else colors['negative']
        
        return html.Div([
            html.H3('Key Metrics', className='card-title'),
            html.Div([
                html.Div([
                    html.P('Day Close', className='metric-title'),
                    html.H4(f"${safe_get(data, 'day_close')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Change %', className='metric-title'),
                    html.H4(f"{change_percentage:.2f}%", className='metric-value', style={'color': change_color})
                ], className='metric-container'),
                html.Div([
                    html.P('Day Range', className='metric-title'),
                    html.H4(f"${safe_get(data, 'day_low')} - ${safe_get(data, 'day_high')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Market Cap', className='metric-title'),
                    html.H4(market_cap_formatted, className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Float', className='metric-title'),
                    html.H4(f"{safe_get(data, 'float')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Float Risk', className='metric-title'),
                    html.H4(safe_get(data, 'float_risk'), className='metric-value')
                ], className='metric-container'),
            ], className='metrics-grid')
        ], className='card')

    # Create the company info card
    def create_company_info_card():
        return html.Div([
            html.H3('Company Information', className='card-title'),
            html.Div([
                html.P(['Symbol: ', html.Strong(safe_get(data, 'symbol'))]),
                html.P(['Name: ', html.Strong(safe_get(data, 'name'))]),
                html.P(['Sector: ', html.Strong(safe_get(data, 'sector'))]),
                html.P(['Industry: ', html.Strong(safe_get(data, 'industry'))]),
                html.P(['Country: ', html.Strong(safe_get(data, 'countryDomicile'))]),
                html.P(['Security Type: ', html.Strong(safe_get(data, 'securityType'))]),
                html.P(['ISIN: ', html.Strong(safe_get(data, 'isin'))]),
            ], className='info-list')
        ], className='card')

    # Create the SEC filing analysis card
    def create_sec_filing_card():
        sec_data = data.get('sec_filing_analysis', {})
        
        return html.Div([
            html.H3('SEC Filing Analysis', className='card-title'),
            html.Div([
                html.P(['Cash: ', html.Strong(safe_get(sec_data, 'Cash'))]),
                html.P(['Debt: ', html.Strong(safe_get(sec_data, 'Debt'))]),
                html.P(['Cash/Debt Ratio: ', html.Strong(safe_get(sec_data, 'Cash/Debt Ratio'))]),
                html.P(['ATM Risk Level: ', html.Strong(safe_get(sec_data, 'ATM Risk Level'))]),
                html.P(['Risk Reason: ', html.Strong(safe_get(sec_data, 'Risk Reason'))]),
                html.P(['Trading Recommendation: ', html.Strong(safe_get(sec_data, 'Trading Recommendation'))]),
                html.P(['Recommendation Confidence: ', html.Strong(safe_get(sec_data, 'Recommendation Confidence'))]),
                html.P(['Short Squeeze Risk: ', html.Strong(safe_get(sec_data, 'Short Squeeze Risk'))]),
            ], className='info-list'),
            html.H4('Recommendation Reasons:', className='subtitle'),
            html.Ul([
                html.Li(reason) for reason in sec_data.get('Recommendation Reasons', ["N/A"])
            ], className='reasons-list')
        ], className='card')

    # Create the trading suggestion card
    def create_suggestion_card():
        suggestion = safe_get(data, 'suggestion', 'No suggestion available')
        suggestion_parts = suggestion.split('\n\n') if suggestion else ["No suggestion available"]
        
        return html.Div([
            html.H3('Trading Suggestion', className='card-title'),
            html.Div([
                html.Div([
                    html.P(part) for part in suggestion_parts
                ], className='suggestion-text')
            ], className='suggestion-container')
        ], className='card')

    return html.Div([
        # Header
        html.Div([
            html.H1(f"{safe_get(data, 'name', 'Stock')} ({safe_get(data, 'symbol')})", className='header-title'),
            html.P(f"Data as of {safe_get(data, 'today_date')}", className='header-date'),
        ], className='header'),
        
        # Back button
        html.Div([
            html.Button('Back to Stock List', id='back-button', className='back-button')
        ], className='main-content'),
        
        # Main content
        html.Div([
            # First row
            html.Div([
                # Left column: Price chart
                html.Div([
                    dcc.Graph(figure=create_price_chart(), id='price-chart')
                ], className='chart-container'),
                
                # Right column: Key metrics
                html.Div([
                    create_metrics_card(),
                    create_company_info_card()
                ], className='metrics-column'),
            ], className='row'),
            
            # Second row
            html.Div([
                # Left column: Cash/Debt chart
                html.Div([
                    dcc.Graph(figure=create_cash_debt_chart(), id='cash-debt-chart')
                ], className='chart-container'),
                
                # Right column: SEC filing analysis
                html.Div([
                    create_sec_filing_card()
                ], className='metrics-column'),
            ], className='row'),
            
            # Third row
            html.Div([
                # Full width: Trading suggestion
                html.Div([
                    create_suggestion_card()
                ], className='full-width'),
            ], className='row'),
        ], className='main-content'),
        
        # Footer
        html.Div([
            html.P('© 2025 Stock Analytics Dashboard', className='footer-text'),
        ], className='footer'),
        
        # Store component to keep track of the current view
        dcc.Store(id='current-view', data='list'),
        dcc.Store(id='selected-stock', data=None)
    ])

# Define the app layout with a callback to switch between views
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to switch between list and detail views
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('page-content', 'children')]
)
def display_page(pathname, current_content):
    # Get data from MongoDB
    mongo_handler = MongoHandler()
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    today_str = ny_time.strftime('%Y-%m-%d')
    stocks_data = mongo_handler.find_doc('fundamentals_of_top_list_symbols', {'today_date': today_str})
    
    if not stocks_data:
        # If no data found, use a default message
        return html.Div([
            html.Div([
                html.H1(title, className='header-title'),
                html.P(f"Data as of {today_str}", className='header-date'),
            ], className='header'),
            
            html.Div([
                html.H2('No stock data available for today', style={'text-align': 'center', 'margin-top': '50px'})
            ], className='main-content'),
            
            html.Div([
                html.P('© 2025 Stock Analytics Dashboard', className='footer-text'),
            ], className='footer')
        ])
    
    if pathname == '/' or pathname == '/list':
        return create_stock_list_page(stocks_data)
    elif pathname.startswith('/stock/'):
        symbol = pathname.split('/')[-1]
        selected_stock = next((stock for stock in stocks_data if stock.get('symbol') == symbol), None)
        if selected_stock:
            return create_stock_detail_page(selected_stock)
        else:
            return html.Div('Stock not found')
    else:
        return create_stock_list_page(stocks_data)

# Callback to handle stock card clicks
@app.callback(
    Output('url', 'pathname'),
    [Input({'type': 'stock-card', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'stock-card', 'index': dash.dependencies.ALL}, 'id')]
)
def navigate_to_stock(n_clicks, ids):
    if not any(n_clicks):
        raise PreventUpdate
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]
    symbol = json.loads(clicked_id)['index']
    
    return f'/stock/{symbol}'

# Callback to handle back button click
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-button', 'n_clicks')],
    prevent_initial_call=True
)
def navigate_back(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return '/list'

# Run the app
if __name__ == '__main__':
    app.run(debug=True)