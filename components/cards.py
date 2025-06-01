from dash import html, dcc
from utils.helpers import safe_get, safe_float
from utils.style import colors

# region Metrics Card
def create_metrics_card(data, market_cap_formatted):
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

# region Company Info Card
def create_company_info_card(data):
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


#region Suggestion Card
def create_suggestion_card(data):
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


#region Stock Card
def create_stock_card(stock):
    """創建單個股票卡片組件"""
    change_percentage = safe_float(stock.get('close_change_percentage'), 0)
    change_color = colors['positive'] if change_percentage >= 0 else colors['negative']
    
    return html.Div([
        html.Div([
            html.Div([html.Div(safe_get(stock, 'symbol'), className='stock-symbol')], className='clear-metric-container'),
            html.Div([html.Div(html.P(f"{safe_get(stock, 'today_date')}", style={'fontSize': '16px', 'color': '#666'}))], className='clear-metric-container-right')
            ],className='stock-metrics'),
        
        html.Div([html.Div([html.Div(safe_get(stock, 'name'), className='stock-name')]),],className='clear-metric-container'),
        
        
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



# region SEC Filing Card
def create_sec_filing_card(data):
    sec_data = data.get('sec_filing_analysis', {})
    
    # 安全獲取所有可能為None的字段
    cash = safe_get(sec_data, 'Cash (USD)', 'N/A')
    debt = safe_get(sec_data, 'Debt (USD)', 'N/A')
    ratio = safe_get(sec_data, 'Cash/Debt Ratio', 'N/A')
    atm_risk = safe_get(sec_data, 'ATM Risk Level', 'N/A')
    risk_reason = safe_get(sec_data, 'Risk Reason', 'N/A')
    recommendation = safe_get(sec_data, 'Trading Recommendation', 'N/A')
    confidence = safe_get(sec_data, 'Recommendation Confidence', 'N/A')
    squeeze_risk = safe_get(sec_data, 'Short Squeeze Risk', 'N/A')
    reasons = sec_data.get('Recommendation Reasons', ["No reasons provided"])
    
    return html.Div([
        html.H3('SEC Filing Analysis', className='card-title'),
        html.Div([
            html.P(['Cash: ', html.Strong(cash)]),
            html.P(['Debt: ', html.Strong(debt)]),
            html.P(['Cash/Debt Ratio: ', html.Strong(ratio)]),
            html.P(['ATM Risk Level: ', html.Strong(atm_risk)]),
            html.P(['Risk Reason: ', html.Strong(risk_reason)]),
            html.P(['Trading Recommendation: ', html.Strong(recommendation)]),
            html.P(['Recommendation Confidence: ', html.Strong(confidence)]),
            html.P(['Short Squeeze Risk: ', html.Strong(squeeze_risk)]),
        ], className='info-list'),
        html.H4('Recommendation Reasons:', className='subtitle'),
        html.Ul([html.Li(reason) for reason in reasons], className='reasons-list')
    ], className='card')

#region News Input Card
def create_news_input_card(data):
    return html.Div([
        html.H3('Add News Analysis', className='card-title'),

        html.Div([
            # 密碼輸入欄位
            dcc.Input(
                id='password-input',
                type='password',
                placeholder='Enter password...',
                value='',  # ✅ 加上這行避免警告
                style={
                    'width': '100%',
                    'marginBottom': '10px',
                    'padding': '8px',
                    'borderRadius': '4px',
                    'border': '1px solid #444',
                    'backgroundColor': '#1e1e1e',
                    'color': '#EBEBEB',
                    'fontSize': '12px',
                    'fontFamily': 'Arial, sans-serif',
                }
            ),

            # 新聞內容輸入
            dcc.Textarea(
                id='raw-news-input',
                placeholder='Paste news article text here...',
                value='',  # ✅ 加上這行避免警告
                style={
                    'width': '100%',
                    'height': '200px',
                    'padding': '10px 20px',
                    'backgroundColor': '#1e1e1e',
                    'color': '#EBEBEB',
                    'fontSize': '12px',
                    'fontFamily': 'Arial, sans-serif',
                    'border': '1px solid #444',
                    'borderRadius': '6px'
                },
            ),

            html.Button(
                'Submit News',
                id='submit-news-button',
                n_clicks=0,
                className='submit-button'
            ),
        ]),

        html.Div(id='news-submission-status'),

        html.Div(id='stock-data-store', style={'display': 'none'}, **{
            'data-symbol': safe_get(data, 'symbol'),
            'data-date': safe_get(data, 'today_date')
        })
    ], className='card')


#region News Display Card
#region News Display Card
def create_news_display_card(data):
    raw_news = data.get('raw_news', [])
    
    news_items = []
    for news in raw_news:  # 直接遍歷新聞項目，不使用 idx
        news_text = news.get('summary', '')
        timestamp = news.get('timestamp', '')
        uuid = news.get('uuid', '')  # 從新聞項目中獲取 UUID
        excerpt = news_text[:50] + '... <<EXCERPT>>' if len(news_text) > 100 else news_text
        
        news_items.append(
            html.Div([
                html.P(timestamp, className='news-timestamp'),
                html.P(excerpt, className='news-text'),
                html.Button(
                    'Delete',
                    id={'type': 'delete-news-button', 'uuid': uuid},  # 使用 uuid 而不是 index
                    className='delete-news-button',
                    n_clicks=0  # 添加 n_clicks 初始化
                ),
                html.Hr()
            ], className='news-item')
        )
    
    return html.Div([


        html.H3('Stored News Articles', className='card-title'),
        html.Div(news_items, id='news-list-container'),
        dcc.ConfirmDialog(
            id='delete-news-confirm',
            message='Are you sure you want to delete this news article?',
        ),



        # Store for callbacks
        dcc.Store(id='current-symbol-store', data=data.get('symbol', '')),
        dcc.Store(id='current-date-store', data=data.get('today_date', '')),
        dcc.Store(id='news-delete-trigger', data={'timestamp': 0}),
        dcc.Store(id='uuid-to-delete-store', data='')  # 添加這行來存儲要刪除的 UUID



    ], className='chart-card')

















#region Stock Chart Card
