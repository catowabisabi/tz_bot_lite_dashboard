from _mongo import MongoHandler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dash import Input, Output
from urllib.parse import unquote
from datetime import timezone
from layout.stock_list import create_empty_state
# 股票列表页逻辑
from layout.stock_list import create_stock_list_page
from layout.stock_detail import create_stock_detail_page
from layout.stock_list import strategy_list_page
from layout.strategy_detail import create_strategy_detail_page


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
        #five_days_ago_dt = datetime.combine(five_days_ago, datetime.min.time()).replace(tzinfo=timezone.utc)

        # 获取最近5天的所有数据
        all_recent_data = mongo_handler.find_doc(
            'fundamentals_of_top_list_symbols',
            {'today_date': {'$gte': five_days_ago.strftime('%Y-%m-%d')}},
             #{'today_date': {'$gte': five_days_ago_dt}}
        )

        # 如果没有数据，返回空状态
        if not all_recent_data:
            
            return create_empty_state(today.strftime('%Y-%m-%d'))

        # 按日期分组数据
        date_grouped_data = {}
        for doc in all_recent_data:
            date = doc.get('today_date')
            if date not in date_grouped_data:
                date_grouped_data[date] = []
            date_grouped_data[date].append(doc)

        # 对每个日期的数据按涨跌幅排序
        for date in date_grouped_data:
            date_grouped_data[date].sort(
                key=lambda x: float(x.get('close_change_percentage', -999)),
                reverse=True
            )

        # 路由逻辑
        if pathname.startswith('/stock/'):
            # 个股详情页逻辑
            symbol = pathname.split('/')[-1]
            # 查找该symbol的最新数据
            selected_stock = None
            for date in sorted(date_grouped_data.keys(), reverse=True):
                for stock in date_grouped_data[date]:
                    if stock.get('symbol') == symbol:
                        selected_stock = stock
                        break
                if selected_stock:
                    break
            
            if selected_stock:
                
                return create_stock_detail_page(selected_stock)
            else:
                return 'Stock not found'

        elif pathname == '/strategy':
            
            return strategy_list_page()
            
        elif pathname.startswith('/strategy/'):
            
            strategy_name = pathname.split('/')[-1]
            unquoted_strategy_name = unquote(strategy_name)
            #print(unquoted_strategy_name)
            return create_strategy_detail_page(unquoted_strategy_name)
        else:
            
            
            # 准备传递给create_stock_list_page的数据
            # 将所有日期的数据合并成一个列表，但保留日期信息
            all_data = []
            for date in date_grouped_data:
                all_data.extend(date_grouped_data[date])
            
            return create_stock_list_page(all_data)

        return 'Page not found'