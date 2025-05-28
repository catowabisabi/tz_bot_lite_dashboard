

from dash import dcc, html
from dash_tvlwc import Tvlwc
from utils.helpers import safe_get

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
    
def create_chart_container(interval='1min', name = "", chart_id='chart1', data=None, use_tvlwc=True):
    from dash import dcc, html
    from dash_tvlwc import Tvlwc

    symbol = safe_get(data, 'symbol')
    clean_data = serialize_mongo_doc(data)

    """ dcc.Dropdown(
                    id=f"{chart_id}-dropdown",
                    options=[
                        {'label': '1 Min', 'value': '1min'},
                        {'label': '5 Min', 'value': '5min'},
                        {'label': '1 Day', 'value': '1day'}
                    ],
                    value=interval,
                    clearable=False,
                    style={"width": "200px"}
                ) """

    return html.Div([
        dcc.Store(id=f"data-input-{chart_id}", data=clean_data),
        html.Div([
            html.Div([
                html.H5(f"{name.upper()}", className="card-title"),
             
            ], className="chart-header"),
            html.Div([
                Tvlwc(
                    id=f"{chart_id}-graph", 
                    height=400,
                    seriesTypes=['candlestick'],
                    chartOptions={'layout': {'background': {'color': '#1e1e1e'}}}
                ) if (Tvlwc and use_tvlwc) 
                else dcc.Graph(id=f"{chart_id}-graph", style={"height": "400px"})
            ])
        ], className="card")
    ], className="chart-container")


def create_row_chart_container(data):
    return html.Div([html.Div([
            create_chart_container('1min', name = "1 MIN (last 3 hrs)", chart_id='chart1', data=data, use_tvlwc=False),
            create_chart_container('5min', name = "5 MIN", chart_id='chart2', data=data, use_tvlwc=False),
            
        ], className='row'),
        
        html.Div([
            create_chart_container('1day', name = "Daily", chart_id='chart3', data=data, use_tvlwc=False),
            
            
        ], className='row'),
        
        ])
    
