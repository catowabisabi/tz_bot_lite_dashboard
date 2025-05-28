# app.py (main application file)
import dash
from dash import dcc, html
from utils.style import index_string

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.index_string = index_string

# Import callbacks after app creation
from callbacks.main import register_main_callbacks
from callbacks.stock import register_stock_callbacks
from callbacks.strategy import register_strategy_callbacks
from callbacks.stock_chart import register_stock_chart_callbacks

# Register callbacks
register_main_callbacks(app)
register_stock_callbacks(app)
register_strategy_callbacks(app)
register_stock_chart_callbacks(app)

# Set layout
app.layout = html.Div([
    dcc.Store(id='current-news-data'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

if __name__ == '__main__':
    app.run(debug=True)