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
ny_time = datetime.now(ZoneInfo("America/New_York"))
today_str = ny_time.strftime('%Y-%m-%d')

# Initialize the Dash app
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css"
]


page_title = "喵喵今日熱股"

app = dash.Dash(__name__, 
               suppress_callback_exceptions=True,
               external_stylesheets=external_stylesheets)
# MongoDB connection

title = "貓咪神-短炒Scanner"


# Custom CSS (same as before)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background-color: #f9f9f9;
                color: #333333;
            }
            
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-bottom: 5px solid #3498db;
            }
            
            .header-title {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .header-date {
                font-size: 14px;
                opacity: 0.8;
            }
            
            .main-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .row {
                display: flex;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            
            .chart-container {
                flex: 3;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-right: 20px;
            }
            
            .metrics-column {
                flex: 2;
                display: flex;
                flex-direction: column;
            }
            
            .full-width {
                flex: 1 1 100%;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
            }
            
            .card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .card-title {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 15px;
                font-size: 18px;
            }
            
            .subtitle {
                color: #2c3e50;
                margin: 15px 0 10px 0;
                font-size: 16px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            
            .metric-container {
                padding: 10px;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            
            .metric-title {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 5px;
            }
            
            .metric-value {
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .info-list p {
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .reasons-list {
                margin-left: 20px;
                font-size: 14px;
            }
            
            .reasons-list li {
                margin-bottom: 5px;
            }
            
            .suggestion-container {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }
            
            .suggestion-text p {
                margin-bottom: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
            
            .footer {
                background-color: #2c3e50;
                color: white;
                text-align: center;
                padding: 15px;
                margin-top: 20px;
            }
            
            .footer-text {
                font-size: 12px;
                opacity: 0.8;
            }
            
            .stock-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .stock-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            .stock-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .stock-symbol {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            
            .stock-name {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
            
            .stock-metrics {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            
            .back-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin-bottom: 20px;
                font-size: 14px;
            }
            
            .back-button:hover {
                background-color: #2980b9;
            }
            
            @media (max-width: 768px) {
                .row {
                    flex-direction: column;
                }
                
                .chart-container {
                    margin-right: 0;
                    margin-bottom: 20px;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .stock-list {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Styling
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'header': '#2c3e50',
    'positive': '#27ae60',
    'negative': '#c0392b',
    'neutral': '#3498db',
    'warning': '#f39c12'
}

#region Create Stock List Page
# Function to create stock list page
def create_stock_list_page(stocks_data):
    stock_cards = []
    
    
    for stock in stocks_data:
        change_percentage = stock.get('close_change_percentage', 0)
        change_color = colors['positive'] if change_percentage >= 0 else colors['negative']
        
        stock_card = html.Div([
            html.Div(stock.get('symbol', 'N/A'), className='stock-symbol'),
            html.Div(stock.get('name', 'N/A'), className='stock-name'),
            html.Div([
                html.Div([
                    html.Div('Price', className='metric-title'),
                    html.Div(f"${stock.get('day_close', 'N/A')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.Div('Change %', className='metric-title'),
                    html.Div(f"{change_percentage:.2f}%", className='metric-value', style={'color': change_color})
                ], className='metric-container'),
                html.Div([
                    html.Div('Sector', className='metric-title'),
                    html.Div(stock.get('sector', 'N/A'), className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.Div('Float Risk', className='metric-title'),
                    html.Div(stock.get('float_risk', 'N/A'), className='metric-value')
                ], className='metric-container'),
            ], className='stock-metrics')
        ], className='stock-card', id={'type': 'stock-card', 'index': stock.get('symbol')})
        
        stock_cards.append(stock_card)
    
    return html.Div([
        html.Div([
            html.H1(title, className='header-title'),
            html.P(f"Data as of {stocks_data[0].get('today_date', 'N/A') if stocks_data else 'N/A'}", className='header-date'),
        ], className='header'),
        
        html.Div([
            html.H2(page_title, style={'margin-bottom': '20px'}),
            html.Div(stock_cards, className='stock-list')
        ], className='main-content'),
        
        html.Div([
            html.P('© 2025 Stock Analytics Dashboard', className='footer-text'),
        ], className='footer')
    ])


#region Create Stock Detail Page
# Function to create stock detail page
def create_stock_detail_page(data):
    # Calculate Market Cap
    market_cap = (data.get('outstandingShares') or 0) * (data.get('day_close') or 0)
    market_cap_formatted = f"${market_cap/1000000:.2f}M" if market_cap > 0 else "N/A"

    # Function to create the price chart
    def create_price_chart():
        price_data = {
            'Category': ['Day Low', 'Yesterday Close', 'Day Close', 'Day High', 'Key Level (3.02)'],
            'Price': [data.get('day_low', 0), data.get('yesterday_close', 0), 
                     data.get('day_close', 0), data.get('day_high', 0), 3.02]
        }
        
        df = pd.DataFrame(price_data)
        
        fig = go.Figure()
        
        # Add lines for price ranges
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[data.get('day_low', 0)],
            mode='markers',
            marker=dict(color=colors['negative'], size=12),
            name='Day Low'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[data.get('yesterday_close', 0)],
            mode='markers',
            marker=dict(color=colors['neutral'], size=12),
            name='Yesterday Close'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[data.get('day_close', 0)],
            mode='markers',
            marker=dict(color=colors['positive'], size=12),
            name='Day Close'
        ))
        
        fig.add_trace(go.Scatter(
            x=['Price Range'],
            y=[data.get('day_high', 0)],
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
            y=[data.get('day_low', 0), data.get('day_high', 0)],
            mode='lines',
            line=dict(color=colors['neutral'], width=3),
            name='Day Range'
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{data.get('symbol', '')} Price Overview",
            xaxis_title='',
            yaxis_title='Price (USD)',
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=400
        )
        
        # Set y-axis range
        min_price = min(data.get('day_low', 0), data.get('yesterday_close', 0)) * 0.9
        max_price = max(data.get('day_high', 0), 3.05) * 1.1
        fig.update_yaxes(range=[min_price, max_price])
        
        return fig

    # Function to create the cash/debt chart
    def create_cash_debt_chart():
        cash = data.get('sec_filing_analysis', {}).get('Cash (USD)', 0)
        debt = data.get('sec_filing_analysis', {}).get('Debt (USD)', 0)
        
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=['Cash', 'Debt'],
            y=[cash/1000000, debt/1000000],
            text=[f"${cash/1000000:.2f}M", f"${debt/1000000:.2f}M"],
            textposition='auto',
            marker_color=[colors['positive'], colors['negative']]
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
        change_percentage = data.get('close_change_percentage', 0)
        change_color = colors['positive'] if change_percentage >= 0 else colors['negative']
        
        return html.Div([
            html.H3('Key Metrics', className='card-title'),
            html.Div([
                html.Div([
                    html.P('Day Close', className='metric-title'),
                    html.H4(f"${data.get('day_close', 'N/A')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Change %', className='metric-title'),
                    html.H4(f"{change_percentage:.2f}%", className='metric-value', style={'color': change_color})
                ], className='metric-container'),
                html.Div([
                    html.P('Day Range', className='metric-title'),
                    html.H4(f"${data.get('day_low', 'N/A')} - ${data.get('day_high', 'N/A')}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Market Cap', className='metric-title'),
                    html.H4(market_cap_formatted, className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Float', className='metric-title'),
                    html.H4(f"{data.get('float', 'N/A'):,}", className='metric-value')
                ], className='metric-container'),
                html.Div([
                    html.P('Float Risk', className='metric-title'),
                    html.H4(data.get('float_risk', 'N/A'), className='metric-value')
                ], className='metric-container'),
            ], className='metrics-grid')
        ], className='card')

    # Create the company info card
    def create_company_info_card():
        return html.Div([
            html.H3('Company Information', className='card-title'),
            html.Div([
                html.P(['Symbol: ', html.Strong(data.get('symbol', 'N/A'))]),
                html.P(['Name: ', html.Strong(data.get('name', 'N/A'))]),
                html.P(['Sector: ', html.Strong(data.get('sector', 'N/A'))]),
                html.P(['Industry: ', html.Strong(data.get('industry', 'N/A'))]),
                html.P(['Country: ', html.Strong(data.get('countryDomicile', 'N/A'))]),
                html.P(['Security Type: ', html.Strong(data.get('securityType', 'N/A'))]),
                html.P(['ISIN: ', html.Strong(data.get('isin', 'N/A'))]),
            ], className='info-list')
        ], className='card')

    # Create the SEC filing analysis card
    def create_sec_filing_card():
        sec_data = data.get('sec_filing_analysis', {})
        
        return html.Div([
            html.H3('SEC Filing Analysis', className='card-title'),
            html.Div([
                html.P(['Cash: ', html.Strong(sec_data.get('Cash', 'N/A'))]),
                html.P(['Debt: ', html.Strong(sec_data.get('Debt', 'N/A'))]),
                html.P(['Cash/Debt Ratio: ', html.Strong(sec_data.get('Cash/Debt Ratio', 'N/A'))]),
                html.P(['ATM Risk Level: ', html.Strong(sec_data.get('ATM Risk Level', 'N/A'))]),
                html.P(['Risk Reason: ', html.Strong(sec_data.get('Risk Reason', 'N/A'))]),
                html.P(['Trading Recommendation: ', html.Strong(sec_data.get('Trading Recommendation', 'N/A'))]),
                html.P(['Recommendation Confidence: ', html.Strong(sec_data.get('Recommendation Confidence', 'N/A'))]),
                html.P(['Short Squeeze Risk: ', html.Strong(sec_data.get('Short Squeeze Risk', 'N/A'))]),
            ], className='info-list'),
            html.H4('Recommendation Reasons:', className='subtitle'),
            html.Ul([
                html.Li(reason) for reason in sec_data.get('Recommendation Reasons', [])
            ], className='reasons-list')
        ], className='card')

    # Create the trading suggestion card
    def create_suggestion_card():
        suggestion = data.get('suggestion', '')
        suggestion_parts = suggestion.split('\n\n')
        
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
            html.H1(f"{data.get('name', 'Stock')} ({data.get('symbol', '')})", className='header-title'),
            html.P(f"Data as of {data.get('today_date', 'N/A')}", className='header-date'),
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


#region Callback

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