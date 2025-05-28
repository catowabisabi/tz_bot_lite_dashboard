from dash import html, dcc
from components.navigation import create_header, create_footer
from components.cards import create_stock_card
from utils.helpers import safe_get
from collections import defaultdict
from datetime import datetime
# 匯入策略頁面函式
from layout.strategy_list import strategy_list_page

title = "貓咪神-短炒Scanner"
page_title = "喵喵熱股追蹤"




def group_stocks_by_date(stocks_data):
    """將股票數據按日期分組"""
    grouped = defaultdict(list)
    for stock in stocks_data:
        date = stock.get('today_date')
        if date:
            grouped[date].append(stock)
    return grouped

def format_date_tab(date_str):
    """格式化日期顯示"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%m/%d")
    except:
        return date_str

def create_tabs_for_stocks(stocks_data):
    """創建包含多個日期標籤的頁面"""
    grouped_stocks = group_stocks_by_date(stocks_data)
    if not grouped_stocks:
        return create_empty_state("No date available")
    
    # 按日期降序排序
    sorted_dates = sorted(grouped_stocks.keys(), reverse=True)
    
    tabs = []

    # ➊ 加入策略整理頁面為第一個 Tab
    tabs.append(dcc.Tab(
        label="🧠 策略整理",
        value="strategy",
        children=html.Div([
            html.H2("策略一覽", style={'margin': '10px auto', 'color': 'white', 'maxWidth': '1200px'}),
            strategy_list_page()
        ])
    ))
    
    for date in sorted_dates:
        stocks = grouped_stocks[date]
        tab_content = html.Div([
            html.H2(f"{page_title} - {date}", style={'margin-bottom': '20px', 'margin-left': '30px'}),
            html.Div(
                [create_stock_card(stock) for stock in stocks],
                className='stock-list'
            )
        ])
        
        tabs.append(dcc.Tab(
            label=format_date_tab(date),
            value=date,
            children=tab_content
        ))


    
    return html.Div([
        create_header(title, f"數據更新至 {sorted_dates[0]}"),
        dcc.Tabs(
            id="date-tabs",
            value=sorted_dates[0],  # 默認顯示最新日期
            children=tabs,
            style={'margin-bottom': '20px'}
        ),
        create_footer()
    ])

def create_empty_state(date):
    return html.Div([
        create_header(title, f"Data as of {date}"),
        html.H2('No stock data available', style={'text-align': 'center'}),
        create_footer()
    ])





def create_stock_list_page(stocks_data):
    if not stocks_data:
        return create_empty_state("N/A")
    
    # 檢查是否有不同日期的數據
    unique_dates = {stock.get('today_date') for stock in stocks_data if stock.get('today_date')}
    
    if len(unique_dates) > 1:
        return create_tabs_for_stocks(stocks_data)
    else:
        # 只有一個日期的數據，顯示簡單列表
        date = safe_get(stocks_data[0], 'today_date') if stocks_data else 'N/A'
        return html.Div([
            create_header(title, f"Data as of {date}"),
            html.Div([
                html.H2(page_title, style={'margin-bottom': '20px', 'margin-left': '50px'}),
                html.Div(
                    [create_stock_card(stock) for stock in stocks_data],
                    className='stock-list'
                )
            ], className='main-content'),
            create_footer()
        ])