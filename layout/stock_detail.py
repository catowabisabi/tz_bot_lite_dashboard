# layout/stock_detail.py

from dash import dcc, html

# 修改後：
from components.navigation import create_header, create_footer, create_back_button
from components.charts import  create_cash_debt_chart, create_price_chart_card
from components.cards import (
    create_metrics_card,
    create_company_info_card,
    create_sec_filing_card,
    create_suggestion_card,
    create_news_input_card,
    create_news_display_card
)
from components.components_stock_charts import create_row_chart_container

from utils.helpers import safe_float

from utils.helpers import safe_get, safe_float
import json
from utils.helpers import JSONEncoder
from bson import ObjectId
import datetime


def serialize_mongo_doc(doc):
    if isinstance(doc, list):
        return [serialize_mongo_doc(i) for i in doc]
    elif isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime.datetime):
        return doc.isoformat()
    else:
        return doc
    

#region Create Stock Detail Page
def create_stock_detail_page(data):



    market_cap_formatted = "N/A"
    outstanding_shares = safe_float(data.get('outstandingShares'))
    day_close = safe_float(data.get('day_close'))

    market_cap = outstanding_shares * day_close if outstanding_shares and day_close else None
    market_cap_formatted = f"${market_cap/1000000:.2f}M" if market_cap else "N/A"


    
    _1m_chart_data = safe_get(data,'1m_chart_data',[])
    #print(data['1m_chart_data'])
    #print(_1m_chart_data)
    _5m_chart_data = safe_get(data,'1m_chart_data',[])
    _1d_chart_data = safe_get(data,'1m_chart_data',[])
    data_dict = {
    '1min': _1m_chart_data,
    '5min': _5m_chart_data,
    '1day': _1d_chart_data
}

    
    # 把完整数据存入 Store，给后续callback用
    clean_data_dict_json = json.dumps(data_dict, cls=JSONEncoder)  # 把dict转成json字符串 """

    clean_data = serialize_mongo_doc(data)



    

    return html.Div([
        create_header(
            f"{data.get('name', 'Stock')} ({data.get('symbol')})",
            f"Data as of {data.get('today_date')}"
        ),
        dcc.Store(id='stock-data-store', data=clean_data),  # 新增存储组件


        html.Div([create_back_button()], className='main-content'),
        html.Div([
            
            create_row_chart_container(data),
            # 第一行
            html.Div([
                html.Div([create_price_chart_card(data)], className='chart-container'),
                html.Div([create_metrics_card(data, market_cap_formatted), create_company_info_card(data)], className='metrics-column'),
            ], className='row'),
            # 第二行
            html.Div([
                html.Div([dcc.Graph(figure=create_cash_debt_chart(data))], className='chart-container'),
                html.Div([create_sec_filing_card(data)], className='metrics-column'),
            ], className='row'),
            # 第三行
            html.Div([create_suggestion_card(data)], className='row'),


            html.Div([
            html.Div([create_news_display_card(data)], className='chart-container'),
            html.Div([create_news_input_card(data)], className='metrics-column'),
            ], className='row'),



        ], className='main-content'),
        create_footer()
    ])