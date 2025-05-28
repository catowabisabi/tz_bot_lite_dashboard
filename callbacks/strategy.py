from dash import Input, Output, State, ctx, no_update
import dash
from dash.exceptions import PreventUpdate

def register_strategy_callbacks(app):
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [
            Input('short-strategy-table', 'active_cell'),
            Input('long-strategy-table', 'active_cell')
        ],
        [
            State('short-strategy-table', 'data'),
            State('long-strategy-table', 'data')
        ],
        prevent_initial_call=True
    )
    def navigate_to_strategy(short_active, long_active, short_data, long_data):
        # 判斷是哪一個元件被觸發
        triggered_id = ctx.triggered_id

        if triggered_id == 'short-strategy-table' and short_active:
            row = short_data[short_active['row']]
            return f'/strategy/{row["名稱"]}'
        
        if triggered_id == 'long-strategy-table' and long_active:
            row = long_data[long_active['row']]
            return f'/strategy/{row["名稱"]}'
        
        return no_update

    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('long-strategy-table', 'active_cell'),
        State('long-strategy-table', 'data'),
        prevent_initial_call=True
    )
    def go_to_long_detail(active_cell, data):
        if active_cell:
            row = data[active_cell['row']]
            strategy_name = row['名稱']
            return f'/strategy/{strategy_name}'
        return dash.no_update
    
    #region Navigation Back
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('back-button-strategy', 'n_clicks')],
        prevent_initial_call=True
    )
    def navigate_back_strategy(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return '/strategy'
