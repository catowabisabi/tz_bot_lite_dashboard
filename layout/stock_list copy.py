from dash import html
from components.navigation import create_header, create_footer
from components.cards import create_stock_card  # 現在這個導入應該可以工作了
from utils.helpers import safe_get


title = "貓咪神-短炒Scanner"
page_title = "喵喵今日熱股"

def create_empty_state(date):
    return html.Div([
        create_header(title, f"Data as of {date}"),
        html.H2('No stock data available for today', style={'text-align': 'center'}),
        create_footer()
    ])

def create_stock_list_page(stocks_data):
    return html.Div([
        create_header(
            title,
            f"Data as of {safe_get(stocks_data[0], 'today_date') if stocks_data else 'N/A'}"
        ),
        html.Div([
            html.H2(page_title, style={'margin-bottom': '20px', 'margin-left': '50px'}),
            html.Div(
                [create_stock_card(stock) for stock in stocks_data],
                className='stock-list'
            )
        ], className='main-content'),
        create_footer()
    ])