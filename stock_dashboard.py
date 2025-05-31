from taipy.gui import Gui, notify
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from _mongo import MongoHandler
from utils.helpers import create_candle_figure, safe_get, safe_float
# Import strategy data directly
from layout.strategy_list import short_strategies, long_strategies
# Commenting out Dash-specific component imports for now, will reintegrate logic if needed
# from components.cards import (
#     create_metrics_card, create_company_info_card, 
#     create_suggestion_card, create_sec_filing_card,
#     create_news_input_card, create_news_display_card
# )
from tz_api.api_news_fetcher import Summarizer # Will be used later
import uuid # For news item unique IDs

# --- Language Settings ---
LANG = {
    'title': {'en': 'Stock Scanner', 'zh_tw': '股票掃描器', 'zh_cn': '股票扫描器'},
    'stock_list': {'en': 'Stock List', 'zh_tw': '股票列表', 'zh_cn': '股票列表'},
    'stock_detail_page_title': {'en': 'Stock Detail', 'zh_tw': '股票詳情', 'zh_cn': '股票详情'},
    'strategy': {'en': 'Strategy', 'zh_tw': '策略', 'zh_cn': '策略'},
    'charts': {'en': 'Charts', 'zh_tw': '圖表', 'zh_cn': '图表'},
    'search': {'en': 'Search Stocks...', 'zh_tw': '搜尋股票...', 'zh_cn': '搜索股票...'},
    'back_to_list': {'en': '< Back to List', 'zh_tw': '< 返回列表', 'zh_cn': '< 返回列表'},
    'view_details': {'en': 'Details', 'zh_tw': '詳情', 'zh_cn': '详情'}, # For table action, if we use it
    # Stock Detail Labels
    'key_metrics': {'en': 'Key Metrics', 'zh_tw': '關鍵指標', 'zh_cn': '关键指标'},
    'company_info': {'en': 'Company Info', 'zh_tw': '公司資訊', 'zh_cn': '公司信息'},
    'label_symbol': {'en': 'Symbol', 'zh_tw': '代號', 'zh_cn': '代码'},
    'label_price': {'en': 'Price', 'zh_tw': '價格', 'zh_cn': '价格'},
    'label_change': {'en': 'Change', 'zh_tw': '漲跌幅', 'zh_cn': '涨跌幅'},
    'label_volume': {'en': 'Volume', 'zh_tw': '成交量', 'zh_cn': '成交量'},
    'label_market_cap': {'en': 'Market Cap', 'zh_tw': '市值', 'zh_cn': '市值'},
    'label_sector': {'en': 'Sector', 'zh_tw': '板塊', 'zh_cn': '板块'},
    'label_industry': {'en': 'Industry', 'zh_tw': '行業', 'zh_cn': '行业'},
    # News section
    'news_analysis_title': {'en': 'News Analysis', 'zh_tw': '新聞分析', 'zh_cn': '新闻分析'},
    'add_news_subtitle': {'en': 'Add News', 'zh_tw': '新增新聞', 'zh_cn': '新增新闻'},
    'label_password': {'en': 'Password', 'zh_tw': '密碼', 'zh_cn': '密码'},
    'label_news_text': {'en': 'News Text', 'zh_tw': '新聞內容', 'zh_cn': '新闻内容'},
    'button_submit_news': {'en': 'Submit News', 'zh_tw': '提交新聞', 'zh_cn': '提交新闻'},
    'stored_news_subtitle': {'en': 'Stored News', 'zh_tw': '已存新聞', 'zh_cn': '已存新闻'},
    'trading_suggestion_title': {'en': 'Trading Suggestion', 'zh_tw': '交易建議', 'zh_cn': '交易建议'},
    'no_suggestion': {'en': 'No suggestion available.', 'zh_tw': '暫無建議。', 'zh_cn': '暂无建议。'},
    'invalid_password_status': {'en': 'Invalid password.', 'zh_tw': '密碼無效。', 'zh_cn': '密码无效。'},
    'news_input_missing_status': {'en': 'News text or stock data missing.', 'zh_tw': '缺少新聞內容或股票數據。', 'zh_cn': '缺少新闻内容或股票数据。'},
    'db_connection_error_status': {'en': 'Database connection error.', 'zh_tw': '數據庫連接錯誤。', 'zh_cn': '数据库连接错误。'},
    'news_submit_success_status': {'en': 'News submitted successfully!', 'zh_tw': '新聞提交成功！', 'zh_cn': '新闻提交成功！'},
    'news_submit_fail_status': {'en': 'Failed to submit news.', 'zh_tw': '新聞提交失敗。', 'zh_cn': '新闻提交失败。'},
    'label_summary': {'en': 'Summary', 'zh_tw': '摘要', 'zh_cn': '摘要'},
    'label_timestamp': {'en': 'Timestamp', 'zh_tw': '時間戳', 'zh_cn': '时间戳'},
    'short_strategies_title': {'en': 'Short Strategies', 'zh_tw': '空頭策略', 'zh_cn': '空头策略'},
    'long_strategies_title': {'en': 'Long Strategies', 'zh_tw': '多頭策略', 'zh_cn': '多头策略'},
    'no_news_items_message': {'en': 'No news items available.', 'zh_tw': '目前沒有新聞項目。', 'zh_cn': '当前没有新闻项目。'}
}

# --- Global State Variables ---
current_lang = "zh_tw"
search_text = ""
active_view = "stock_list" 
all_stocks_data = [] 
filtered_stocks_display = [] 
selected_stock_data = None 
current_chart = go.Figure() 

# News specific state (will be part of Taipy state for UI binding)
news_password = ""
news_text_input = ""
news_submission_status = ""
# news_to_delete_uuid = None # For managing news deletion through proxy

# 在文件開頭的全局變量部分添加
short_strategies_data = pd.DataFrame()
long_strategies_data = pd.DataFrame()

# --- Data Loading & Preparation ---
def load_and_prepare_data(state):
    global all_stocks_data, filtered_stocks_display
    try:
        mongo = MongoHandler()
        if not mongo.is_connected():
            all_stocks_data = []
            filtered_stocks_display = []
            print("[ERROR] Database connection error")
            return
        
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz).date()
        thirty_days_ago = today - timedelta(days=30) 
        
        data = mongo.find_doc(
            'fundamentals_of_top_list_symbols',
            {'today_date': {'$gte': thirty_days_ago.strftime('%Y-%m-%d')}}
        )
        all_stocks_data = data
        filtered_stocks_display = prepare_stocks_for_display(data)
        print(f"[INFO] Loaded {len(all_stocks_data)} stock records.")
    except Exception as e:
        all_stocks_data = []
        filtered_stocks_display = []
        print(f"[ERROR] Error loading data: {str(e)}")

def prepare_stocks_for_display(stock_data_list):
    if not stock_data_list:
        return pd.DataFrame(columns=["symbol", "name", "price", "change", "volume"])
    
    display_list = []
    for stock in stock_data_list:
        display_list.append({
            "symbol": safe_get(stock, 'symbol', 'N/A'),
            "name": safe_get(stock, 'name', 'N/A'),
            "price": f"${safe_get(stock, 'day_close', 0.0):.2f}",
            "change": f"{safe_float(stock.get('close_change_percentage'), 0.0):.2f}%",
            "volume": f"{safe_get(stock, 'day_volume', 0):,}"
        })
    
    return pd.DataFrame(display_list)

# --- Chart Creation ---
def generate_stock_detail_chart(stock_data_dict):
    # This function should now update state.current_chart if called from a Taipy action
    # For now, let's assume it prepares a figure, and the caller updates state.
    if not stock_data_dict or not isinstance(stock_data_dict, dict) or 'chart_data' not in stock_data_dict or not stock_data_dict['chart_data']:
        fig = go.Figure()
        fig.update_layout(title="No chart data available", template="plotly_dark", paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a', font={'color': '#ffffff'})
        return fig

    chart_df_data = stock_data_dict['chart_data']
    try:
        df = pd.DataFrame(chart_df_data)
        if df.empty or not all(col in df.columns for col in ['datetime', 'open', 'high', 'low', 'close']):
            raise ValueError("Chart data missing required columns")
        
        # Using the provided create_candle_figure helper
        fig = create_candle_figure(chart_df_data) 
        fig.update_layout(
            title=f"{stock_data_dict.get('symbol', 'N/A')} Price Chart",
            template="plotly_dark", height=400,
            paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a', font={'color': '#ffffff'},
            xaxis_rangeslider_visible=False
        )
        return fig
    except Exception as e:
        print(f"[ERROR] Chart generation error: {str(e)}")
        fig = go.Figure()
        fig.update_layout(title=f"Error generating chart for {stock_data_dict.get('symbol', 'N/A')}", template="plotly_dark", paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a', font={'color': '#ffffff'})
        return fig

# --- Page/View Navigation Actions ---
def navigate_to(state, action_name_or_id, payload_or_details=None):
    # For buttons with 'id', Taipy passes the id as action_name_or_id
    # For table on_action, it passes the action name, then id (index), then row_data
    view_id = action_name_or_id 
    stock_symbol_to_view = None

    if isinstance(payload_or_details, dict) and 'id' in payload_or_details: # From table action
        row_index = payload_or_details['id'] # This is how Taipy table on_action provides index
        if row_index is not None and 0 <= row_index < len(state.filtered_stocks_display):
             stock_symbol_to_view = state.filtered_stocks_display[row_index]['symbol']
             view_id = "stock_detail" # Implicitly navigate to detail
        else: # Should not happen if row is valid
            notify(state, "warning", "Invalid row selected from table.")
            return 
    elif isinstance(action_name_or_id, str) and payload_or_details is None: # From sidebar buttons
        view_id = action_name_or_id # id of button is the view_id
    # else: it might be a direct call like navigate_to(state, 'stock_detail', 'AAPL') - handled by view_id assignment

    state.active_view = view_id
    if view_id == "stock_detail" and stock_symbol_to_view:
        found_stock = next((s for s in all_stocks_data if safe_get(s, 'symbol') == stock_symbol_to_view), None)
        if found_stock:
            state.selected_stock_data = found_stock
            state.current_chart = generate_stock_detail_chart(found_stock)
            # Reset news form fields
            state.news_password = ""
            state.news_text_input = ""
            state.news_submission_status = ""
        else:
            notify(state, "error", f"Stock {stock_symbol_to_view} details not found.")
            state.active_view = "stock_list"
    elif view_id == "stock_list":
        state.selected_stock_data = None
        # state.filtered_stocks_display = prepare_stocks_for_display(all_stocks_data) # Refresh list
    elif view_id == "charts": 
        if state.selected_stock_data: 
            state.current_chart = generate_stock_detail_chart(state.selected_stock_data)
        else: 
             fig = go.Figure()
             fig.update_layout(title="Select a stock to view chart", template="plotly_dark", paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a', font={'color': '#ffffff'})
             state.current_chart = fig

# --- Stock List Actions ---
def filter_displayed_stocks(state):
    search_val = state.search_text.lower()
    if not search_val:
        state.filtered_stocks_display = prepare_stocks_for_display(all_stocks_data)
    else:
        new_filtered_raw = [
            stock for stock in all_stocks_data
            if search_val in safe_get(stock, 'symbol', '').lower() or \
               search_val in safe_get(stock, 'name', '').lower()
        ]
        state.filtered_stocks_display = prepare_stocks_for_display(new_filtered_raw)
    notify(state, "info", f"Filtered list: {len(state.filtered_stocks_display)} stocks.")


# --- Stock Detail Actions (News) ---
def submit_news_action(state):
    if not state.selected_stock_data:
        notify(state, "error", "No stock selected.")
        return

    if state.news_password != "123456": # Basic check
        state.news_submission_status = LANG['invalid_password_status'][state.current_lang]
        notify(state, "error", state.news_submission_status)
        return

    if not state.news_text_input:
        state.news_submission_status = LANG['news_input_missing_status'][state.current_lang]
        notify(state, "error", state.news_submission_status)
        return

    mongo = MongoHandler()
    if not mongo.is_connected():
        state.news_submission_status = LANG['db_connection_error_status'][state.current_lang]
        notify(state, "error", state.news_submission_status)
        return

    try:
        stock_data = state.selected_stock_data
        symbol = stock_data['symbol']
        date = stock_data.get('today_date', datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d'))
        collection_name = "fundamentals_of_top_list_symbols"
        query = {"symbol": symbol, "today_date": date}
        
        existing_doc = mongo.db[collection_name].find_one(query)
        raw_news_list = existing_doc.get("raw_news", []) if existing_doc else []
        existing_suggestion = existing_doc.get("suggestion", "") if existing_doc else ""

        gpt_summarizer = Summarizer()
        summary = gpt_summarizer.summarize(state.news_text_input)

        news_entry = {
            "uuid": str(uuid.uuid4()), "text": state.news_text_input,
            "summary": summary, "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
        raw_news_list.append(news_entry)

        prompt_for_suggestion = f"New News Summary:\\n{summary}\\n\\nExisting Overall Suggestion:\\n{existing_suggestion}\\n\\nBased on all news, what is the updated trading suggestion?"
        new_overall_suggestion = gpt_summarizer.suggestion(prompt_for_suggestion)
        
        update_result = mongo.db[collection_name].update_one(
            query,
            {"$set": {"raw_news": raw_news_list, "suggestion": new_overall_suggestion}},
            upsert=True
        )

        if update_result.modified_count > 0 or update_result.upserted_id:
            state.news_submission_status = LANG['news_submit_success_status'][state.current_lang]
            notify(state, "success", state.news_submission_status)
            updated_stock_doc = mongo.db[collection_name].find_one(query)
            if updated_stock_doc:
                 state.selected_stock_data = updated_stock_doc # Refresh data in state
            state.news_text_input = "" 
        else:
            state.news_submission_status = LANG['news_submit_fail_status'][state.current_lang]
            notify(state, "error", state.news_submission_status)
            
    except Exception as e:
        state.news_submission_status = f"Error: {str(e)}"
        notify(state, "error", state.news_submission_status)
        print(f"Error submitting news: {str(e)}")

def delete_news_action_proxy(state): # Renamed as it's a proxy
    news_uuid = getattr(state, 'news_to_delete_uuid', None) # Get from state
    if news_uuid and state.selected_stock_data:
        mongo = MongoHandler()
        if not mongo.is_connected():
            notify(state, "error", LANG['db_connection_error_status'][state.current_lang])
            return
        try:
            stock_data = state.selected_stock_data
            symbol = stock_data['symbol']
            date = stock_data.get('today_date', datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d'))
            collection_name = "fundamentals_of_top_list_symbols"
            query = {"symbol": symbol, "today_date": date}

            current_doc = mongo.db[collection_name].find_one(query)
            if not current_doc or "raw_news" not in current_doc:
                notify(state, "error", "News item not found for deletion.")
                return
            
            updated_raw_news = [n for n in current_doc["raw_news"] if n.get("uuid") != news_uuid]

            if len(updated_raw_news) < len(current_doc["raw_news"]):
                update_result = mongo.db[collection_name].update_one(query, {"$set": {"raw_news": updated_raw_news}})
                if update_result.modified_count > 0:
                    notify(state, "success", "News item deleted.")
                    updated_stock_doc = mongo.db[collection_name].find_one(query)
                    if updated_stock_doc:
                        state.selected_stock_data = updated_stock_doc
                else:
                    notify(state, "error", "Failed to delete news from DB.")
            else:
                notify(state, "warning", "News item with specified UUID not found.")
            state.news_to_delete_uuid = None # Clear after use
        except Exception as e:
            notify(state, "error", f"Error deleting news: {str(e)}")
    else:
        notify(state, "error", "Cannot delete: Missing UUID or stock data.")


# News display helper (Taipy Markdown)
def render_news_item_taipy(item): 
    global current_lang # Access global current_lang for this renderer
    if not item: return ""
    
    summary_label = LANG['label_summary'].get(current_lang, 'Summary')
    timestamp_label = LANG['label_timestamp'].get(current_lang, 'Timestamp')
    item_summary = safe_get(item, 'summary', 'No summary available.')
    item_timestamp = safe_get(item, 'timestamp', 'N/A')
    item_uuid = safe_get(item, 'uuid', '')

    try:
        parsed_dt = datetime.fromisoformat(item_timestamp)
        item_timestamp_display = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        item_timestamp_display = item_timestamp if len(item_timestamp) <= 19 else item_timestamp[:19]

    expander_title = f"News Summary ({item_timestamp_display})"

    return f"""
<|part|expandable|title='{expander_title}'|expanded=False|
    <|card class_name=item_card|
        <|layout|columns=1fr auto|gap=10px|>
            <|part|
                **{summary_label}:** {item_summary}<br/>
                _{timestamp_label}: {item_timestamp_display}_
            |>
            <|Delete|button|class_name=delete_button|on_action={{lambda s: s.assign("news_to_delete_uuid", "{item_uuid}") and s.invoke_callback(delete_news_action_proxy) }}|>
        |>
    |>
|>
"""

# --- Taipy Page Definition (Markdown with Embedded CSS) ---
page_with_embedded_css = f"""
<style>
  body {{ margin: 0; font-family: sans-serif; background-color: #121212; color: white; }}
  .taipy-container {{ display: flex; height: 100vh; }}
  .sidebar {{ width: 250px; min-width:250px; padding: 20px; background-color: #1a1a1a; color: white; border-right: 1px solid #333; overflow-y: auto; }}
  .main-content {{ flex-grow: 1; padding: 20px; overflow-y: auto; background-color: #121212; }}
  .nav_button {{ width: 100%; margin: 8px 0; padding: 12px; background-color: #2a2a2a; color: white; border: 1px solid #3a3a3a; cursor: pointer; text-align: left; font-size: 1em; border-radius: 4px; }}
  .nav_button:hover {{ background-color: #3a3a3a; }}
  .search_input {{ width: calc(100% - 22px); margin-bottom: 20px; padding: 10px; background-color: #2a2a2a; color: white; border: 1px solid #3a3a3a; font-size: 1em; border-radius: 4px;}}
  h1, h2, h3 {{ color: #00d4aa; }}
  .detail_card {{ background-color: #1e1e1e; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #2e2e2e; }}
  .detail_label {{ font-weight: bold; color: #8884d8; margin-right: 5px;}}
  .item_card {{ background-color: #282828; margin-bottom: 10px; padding:10px; border-radius: 4px;}}
  .delete_button {{ background-color: #c0392b; color:white; border:none; padding: 5px 10px; border-radius:3px; font-size:0.9em;}}
  .delete_button:hover {{ background-color: #e74c3c;}}
  .taipy-table table {{ width: 100%; color: white; }} 
  .taipy-table th {{ background-color: #2a2a2a !important; color: #00d4aa !important; }}
  .taipy-table td {{ border-bottom: 1px solid #2e2e2e !important; }}
  .no_news_message {{color: #aaaaaa; font-style: italic; margin-top: 10px;}}
</style>

<|layout|columns=250px 1fr|class_name=taipy-container|
<|part|class_name=sidebar|
<h1>{LANG['title'][current_lang]}</h1>
<|{LANG['stock_list'][current_lang]}|button|class_name=nav_button|on_action=navigate_to|id=stock_list|>
<|{LANG['strategy'][current_lang]}|button|class_name=nav_button|on_action=navigate_to|id=strategy|>
<|{LANG['charts'][current_lang]}|button|class_name=nav_button|on_action=navigate_to|id=charts|>
|>

<|part|class_name=main-content|
<|part|render={{active_view=="stock_list"}}|
<h2>{LANG['stock_list'][current_lang]}</h2>
<|{search_text}|input|class_name=search_input|label={LANG['search'][current_lang]}|on_change=filter_displayed_stocks|change_delay=300|>
<|{filtered_stocks_display}|table|columns=symbol;name;price;change;volume|on_action=navigate_to|width=100%|height=calc(100vh - 180px)|class_name=stock-table-custom|show_all=True|page_size=50|allow_sorting=True|>
|>

<|part|render={{active_view=="stock_detail"}}|
<h2>{LANG['stock_detail_page_title'][current_lang]}: {selected_stock_data['symbol'] if selected_stock_data else 'N/A'}</h2>
<|{LANG['back_to_list'][current_lang]}|button|class_name=nav_button|on_action=navigate_to|id=stock_list|style=margin-bottom:20px; width: auto;|>

<|{selected_stock_data}|expandable|title={(selected_stock_data['name'] if selected_stock_data else '') + ' Details'}|expanded=True|
<|layout|columns=1 1|gap=20px|
<|part|
<div class="detail_card">
<h3>{LANG['key_metrics'][current_lang]}</h3>
<span class="detail_label">{LANG['label_symbol'][current_lang]}:</span> {selected_stock_data['symbol'] if selected_stock_data else 'N/A'}<br/>
<span class="detail_label">{LANG['label_price'][current_lang]}:</span> {selected_stock_data['day_close'] if selected_stock_data else 'N/A'}<br/>
<span class="detail_label">{LANG['label_change'][current_lang]}:</span> {selected_stock_data['close_change_percentage'] if selected_stock_data else 'N/A'}%<br/>
<span class="detail_label">{LANG['label_volume'][current_lang]}:</span> {selected_stock_data['day_volume'] if selected_stock_data else 'N/A'}<br/>
<span class="detail_label">{LANG['label_market_cap'][current_lang]}:</span> {selected_stock_data['marketCap'] if selected_stock_data else 'N/A'}<br/>
</div>
|>
<|part|
<div class="detail_card">
<h3>{LANG['company_info'][current_lang]}</h3>
<span class="detail_label">{LANG['label_sector'][current_lang]}:</span> {selected_stock_data['sector'] if selected_stock_data else 'N/A'}<br/>
<span class="detail_label">{LANG['label_industry'][current_lang]}:</span> {selected_stock_data['industry'] if selected_stock_data else 'N/A'}<br/>
</div>
|>
|>

<|{current_chart}|chart|figure={current_chart}|>

<div class="detail_card">
<h3>{LANG['trading_suggestion_title'][current_lang]}</h3>
<|{selected_stock_data['suggestion'] if selected_stock_data and 'suggestion' in selected_stock_data else LANG['no_suggestion'][current_lang]}|text|raw=True|>
</div>

<div class="detail_card">
<h3>{LANG['news_analysis_title'][current_lang]}</h3>
<|layout|columns=1 1|gap=15px|
<|part|
<h4>{LANG['add_news_subtitle'][current_lang]}</h4>
{LANG['label_password'][current_lang]}: <|{news_password}|input|password=True|label={LANG['label_password'][current_lang]}|class_name=search_input|not_update_on_change=True|>
{LANG['label_news_text'][current_lang]}: <|{news_text_input}|input|multiline=True|class_name=search_input|height=100px|not_update_on_change=True|>
<|{LANG['button_submit_news'][current_lang]}|button|on_action=submit_news_action|class_name=nav_button|>
<|{news_submission_status}|text|>
|>
<|part|
<h4>{LANG['stored_news_subtitle'][current_lang]}</h4>
<|{[news for news in (selected_stock_data or {}).get('raw_news', [])]}|part|render=render_news_item_taipy|>
|>
|>
</div>
|>
|>

<|part|render={{active_view=="strategy"}}|
<h2>{LANG['strategy'][current_lang]}</h2>
<h3>{LANG['short_strategies_title'][current_lang]}</h3>
<|{pd.DataFrame(short_strategies)[['名稱', '說明']]}|table|columns=名稱;說明|width=100%|class_name=taipy-table|page_size=10|allow_sorting=True|show_all=True|>
<h3>{LANG['long_strategies_title'][current_lang]}</h3>
<|{pd.DataFrame(long_strategies)[['名稱', '說明']]}|table|columns=名稱;說明|width=100%|class_name=taipy-table|page_size=10|allow_sorting=True|show_all=True|>
|>

<|part|render={{active_view=="charts"}}|
<h2>{LANG['charts'][current_lang]}</h2>
<|{current_chart}|chart|figure={current_chart}|>
|>
|>
|>
"""


if __name__ == "__main__":
    # Define initial_state_vars first
    initial_state_vars = {
        "current_lang": current_lang,
        "search_text": "",
        "active_view": "stock_list",
        "all_stocks_data": [],
        "filtered_stocks_display": [],
        "selected_stock_data": None,
        "current_chart": go.Figure(),
        "news_password": "",
        "news_text_input": "",
        "news_submission_status": "",
        "news_to_delete_uuid": None,
        # 直接在模板中創建 DataFrame，而不是在這裡初始化
        "short_strategies_data": None,
        "long_strategies_data": None,
    }

    LANG['no_news_items_message'] = {'en': 'No news items available.', 'zh_tw': '目前沒有新聞項目。', 'zh_cn': '当前没有新闻项目。'}

    class TempState:
        def __init__(self, initial_vars):
            for k, v in initial_vars.items():
                setattr(self, k, v)

    temp_state_for_load = TempState(initial_state_vars)
    load_and_prepare_data(temp_state_for_load)
    
    initial_state_vars["all_stocks_data"] = temp_state_for_load.all_stocks_data
    initial_state_vars["filtered_stocks_display"] = temp_state_for_load.filtered_stocks_display

    gui = Gui(page=page_with_embedded_css)
    gui.run(
        dark_mode=True, 
        port=5000,
        host="0.0.0.0",
        title=LANG['title'][initial_state_vars['current_lang']],
        margin="0px",
        use_reloader=False, # Disabled reloader for troubleshooting
        initial_state=initial_state_vars
    ) 