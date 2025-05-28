import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dash import Input, Output, State, callback_context, no_update, html
import dash
from dash.exceptions import PreventUpdate
from _mongo import MongoHandler
from datetime import datetime
from zoneinfo import ZoneInfo



import json
import uuid

from tz_api.api_news_fetcher import Summarizer






    




#region Single Stock Page
def register_stock_callbacks(app):


    #region Navigation Stock
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


    #region Navigation Back
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('back-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def navigate_back(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return '/list'
    










    #region Submit News
    @app.callback(
        Output('news-submission-status', 'children'),
        Input('submit-news-button', 'n_clicks'),
        State('password-input', 'value'),
        State('raw-news-input', 'value'),
        State('stock-data-store', 'data-symbol'),
        State('stock-data-store', 'data-date'),
        
        prevent_initial_call=True
    )
    def submit_news(n_clicks, password, news_text, symbol, date):

        if password != '123456':
            return html.Div("Invalid password", style={'color': 'red'})
        
        if not news_text or not symbol or not date:
            return html.Div("Please enter news text before submitting.", style={'color': 'red'})

        mongo = MongoHandler()
        if not mongo.is_connected():
            return html.Div("Database connection error.", style={'color': 'red'})

        collection_name = "fundamentals_of_top_list_symbols"
        query = {"symbol": symbol, "today_date": date}
        existing_doc = mongo.db[collection_name].find_one(query)

        raw_news_list = existing_doc.get("raw_news", []) if existing_doc else []
        existing_suggestion = existing_doc.get("suggestion", "None") if existing_doc else "None"

        # GPT Summary
        gpt_summarizer = Summarizer()
        summary = gpt_summarizer.summarize(news_text)

        news_entry = {
            "uuid": str(uuid.uuid4()),
            "text": news_text,
            "summary": summary,
            "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
        raw_news_list.append(news_entry)

        # Prompt GPT for new suggestion
        prompt_for_suggestion = f"""
    新的新聞 (New News):
    {summary}

    原有的總結 (Original Summary):
    {existing_suggestion}

    請為這則新聞提供建議 (Please provide suggestions for this input):
    """
        new_suggestion = gpt_summarizer.suggestion(prompt_for_suggestion)

        # Update both fields in one call
        update_result = mongo.db[collection_name].update_one(
            query,
            {"$set": {
                "raw_news": raw_news_list,
                "suggestion": new_suggestion
            }},
            upsert=True
        )

        if update_result.modified_count > 0 or update_result.upserted_id:
            return html.Div("News successfully added!", style={'color': 'green'})
        else:
            return html.Div("Failed to add news.", style={'color': 'red'})



    #region Show Delete Confirmation
    # Callback to show confirmation dialog
    
    @app.callback([
        Output('delete-news-confirm', 'displayed'),
        Output('delete-news-confirm', 'message'),
        Output('uuid-to-delete-store', 'data')],  # 存儲要刪除的 UUID
        Input({'type': 'delete-news-button', 'uuid': dash.dependencies.ALL}, 'n_clicks'),
        State('current-symbol-store', 'data'),
        State('current-date-store', 'data'),
        prevent_initial_call=True
    )
    def show_delete_confirmation(n_clicks, symbol, date):
        ctx = callback_context
        print(f"=== show_delete_confirmation 被調用 ===")
        print(f"觸發上下文: {ctx.triggered}")
        print(f"n_clicks: {n_clicks}")
        
        if not ctx.triggered or not any(n_clicks):
            print("沒有觸發或沒有點擊")
            return no_update, no_update, no_update
        
        try:
            button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
            uuid = button_id['uuid']
            print(f"要刪除的 UUID: {uuid}")

            mongo = MongoHandler()
            if not mongo.is_connected():
                print("MongoDB 未連接")
                return no_update, no_update, no_update

            doc = mongo.db["fundamentals_of_top_list_symbols"].find_one({
                "symbol": symbol,
                "today_date": date
            })

            if not doc or 'raw_news' not in doc:
                print("找不到文檔或 raw_news")
                return no_update, no_update, no_update

            news_item = next((n for n in doc['raw_news'] if n.get("uuid") == uuid), None)
            if not news_item:
                print("找不到新聞項目")
                return no_update, no_update, no_update

            news_text = news_item['text'][:50] + "..." if len(news_item['text']) > 50 else news_item['text']
            print(f"顯示確認對話框: {news_text}")
            return True, f'確定要刪除這條新聞嗎？\n\n"{news_text}"', uuid  # 返回 UUID
            
        except Exception as e:
            print(f"show_delete_confirmation 錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return no_update, no_update, no_update


    #region Delete News
    @app.callback(
        Output('news-delete-trigger', 'data'),
        Input('delete-news-confirm', 'submit_n_clicks'),
        State('uuid-to-delete-store', 'data'),
        State('current-symbol-store', 'data'),
        State('current-date-store', 'data'),
        prevent_initial_call=True
    )
    def handle_news_deletion(submit_clicks, uuid_to_delete, symbol, date):
        print(f"=== handle_news_deletion 被調用 ===")
        print(f"submit_clicks: {submit_clicks}")
        print(f"uuid_to_delete: {uuid_to_delete}")
        print(f"symbol: {symbol}, date: {date}")
        
        if not submit_clicks:
            print("沒有 submit_clicks")
            raise PreventUpdate
            
        if not uuid_to_delete:
            print("沒有 uuid_to_delete")
            raise PreventUpdate

        try:
            print(f"開始刪除 UUID: {uuid_to_delete}")
            mongo = MongoHandler()
            if not mongo.is_connected():
                print("MongoDB 連接失敗")
                raise PreventUpdate

            collection_name = "fundamentals_of_top_list_symbols"
            query = {"symbol": symbol, "today_date": date}
            doc = mongo.find_one(collection_name, query)

            if not doc or 'raw_news' not in doc:
                print("找不到文檔或 raw_news")
                raise PreventUpdate

            original_count = len(doc['raw_news'])
            updated_news = [n for n in doc['raw_news'] if n.get("uuid") != uuid_to_delete]
            new_count = len(updated_news)
            
            print(f"原始數量: {original_count}, 更新後數量: {new_count}")

            update_result = mongo.update_one(
                collection_name,
                query,
                {"raw_news": updated_news}
            )

            print(f"更新結果: {update_result}")
            
            if not update_result or update_result.get('modified_count', 0) == 0:
                print("更新失敗")
                raise PreventUpdate

            print("刪除成功!")
            return {'status': 'success', 'timestamp': datetime.now().timestamp()}
            
        except Exception as e:
            print(f"handle_news_deletion 錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            raise PreventUpdate
    

