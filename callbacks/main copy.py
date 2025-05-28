""" 
from _mongo import MongoHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from dash import  Input, Output

def register_main_callbacks(app):
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        
        mongo_handler = MongoHandler()
        today_str = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
        stocks_data = mongo_handler.find_doc('fundamentals_of_top_list_symbols', {'today_date': today_str})
        
        if not stocks_data:
            from layout.stock_list import create_empty_state
            return create_empty_state(today_str)
        
        if pathname == '/' or pathname == '/list':
            from layout.stock_list import create_stock_list_page
            return create_stock_list_page(stocks_data)
        elif pathname.startswith('/stock/'):
            symbol = pathname.split('/')[-1]
            selected_stock = next((stock for stock in stocks_data if stock.get('symbol') == symbol), None)
            if selected_stock:
                from layout.stock_detail import create_stock_detail_page
                return create_stock_detail_page(selected_stock)
        
        return 'Page not found'
    
 """
from _mongo import MongoHandler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dash import Input, Output

def register_main_callbacks(app):
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        mongo_handler = MongoHandler()
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz).date()
        yesterday = today - timedelta(days=1)
        five_days_ago = today - timedelta(days=5)

        # 嘗試找今天的資料
        today_str = today.strftime('%Y-%m-%d')
        today_data = mongo_handler.find_doc('fundamentals_of_top_list_symbols', {'today_date': today_str})

        # 如果今天有資料，就用今天的資料為主
        if today_data:
            base_date = today
        else:
            base_date = yesterday
            today_str = yesterday.strftime('%Y-%m-%d')

        # 取最近五天的所有資料
        all_recent_data = mongo_handler.find_doc(
            'fundamentals_of_top_list_symbols',
            {'today_date': {'$gte': five_days_ago.strftime('%Y-%m-%d')}}
        )

        # 按日期排序，找每個 symbol 的最新一筆資料
        symbol_latest_map = {}
        for doc in sorted(all_recent_data, key=lambda x: x['today_date'], reverse=True):
            symbol = doc.get('symbol')
            if symbol and symbol not in symbol_latest_map:
                symbol_latest_map[symbol] = doc

        # 最終的顯示資料，根據 base_date 過濾
        final_data = [
            doc for doc in symbol_latest_map.values()
            if doc.get('today_date') == base_date.strftime('%Y-%m-%d')
        ]

        # 加這段
        final_data.sort(
            key=lambda x: (
                x.get('today_date', ''), 
                float(x.get('close_change_percentage', -999))
            ),
            reverse=True
        )

        if not final_data:
            from layout.stock_list import create_empty_state
            return create_empty_state(today_str)

        # 路由邏輯
        if pathname == '/' or pathname == '/list':
            from layout.stock_list import create_stock_list_page
            return create_stock_list_page(final_data)

        elif pathname.startswith('/stock/'):
            symbol = pathname.split('/')[-1]
            selected_stock = next((stock for stock in final_data if stock.get('symbol') == symbol), None)
            if selected_stock:
                from layout.stock_detail import create_stock_detail_page
                return create_stock_detail_page(selected_stock)

        return 'Page not found'
