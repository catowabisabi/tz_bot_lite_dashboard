# layouts/strategy_list_page.py


# 空頭策略
short_strategies = [
    {"名稱": "Low Hanging Fruit", "說明": "做空開盤跳空大漲、漲幅過大的「容易下跌」股，目標是快速回落的早盤套利。"},
    {"名稱": "Bounce Short", "說明": "等待股票反彈後反手做空，捕捉反彈結束後的下跌。"},
    {"名稱": "Stuff and Fizzle", "說明": "股票強拉但無力突破前高（stuff），然後量縮橫盤（fizzle），做空等待下跌。"},
    {"名稱": "Parabolic Reversal", "說明": "做空盤中急漲呈抛物線走勢的股票，預期會迅速回調。"},
    {"名稱": "Gap and Crap", "說明": "開盤跳空高開（Gap），但開盤後迅速賣壓湧現（Crap），做空開盤回落。"},
    {"名稱": "Overextended Short", "說明": "做空連續幾天漲幅過大的股票，尋找轉折回調點。"},
    {"名稱": "VWAP Rejection Short", "說明": "價格觸及 VWAP 無法突破並回落時做空。"},
    {"名稱": "Broken Chart Short", "說明": "做空已跌破重要支撐（如趨勢線、日線支撐）後的下跌延續。"},
    {"名稱": "Pop and Drop", "說明": "開盤快速拉升（Pop）吸引追高盤，然後迅速回落（Drop）做空。"},
    {"名稱": "Failed Breakout Short", "說明": "假突破（Fakeout）後做空，利用追高者的失敗來獲利。"},
    {"名稱": "Late Day Fade", "說明": "接近尾盤時做空當日強勢股的疲弱走勢，預期收盤前回落。"},
    {"名稱": "Double Top Rejection", "說明": "在雙頂形態處做空，預期下跌。"},
    {"名稱": "SSR Trigger Short", "說明": "股票觸發 SSR（Short Sale Restriction）前搶先做空，利用流動性下降反向操作。"},
    {"名稱": "Pump and Dump", "說明": "針對盤中被明顯操控的炒作股做空，預期隨後迅速崩潰。"},
    {"名稱": "Pre-exhaustion Short", "說明": "在盤中拉升出現疲態、量價背離或異常交易後做空。"},
    {"名稱": "Bear Flag Breakdown", "說明": "價格在下跌後橫盤整理成 bear flag，等待破位下跌做空。"}
]

# 多頭策略
long_strategies = [
    {"名稱": "Dip Buy", "說明": "股價下跌至支撐位時進場做多，預期反彈。"},
    {"名稱": "Red to Green Move", "說明": "開盤下跌轉為上漲（由紅翻綠）時追多，通常伴隨動能放大。"},
    {"名稱": "Gap and Go", "說明": "開盤跳空上漲，盤中持續放量走高，開盤不久即追多。"},
    {"名稱": "VWAP Bounce Long", "說明": "價格回踩 VWAP 不破反彈，進場做多。"},
    {"名稱": "Opening Range Breakout (ORB)", "說明": "做多突破開盤價格區間（通常前5-15分鐘）的股票。"},
    {"名稱": "Parabolic Squeeze", "說明": "多頭快速上攻形成抛物線走勢，進場追多動能。"},
    {"名稱": "High-of-Day Breakout", "說明": "價格突破當日高點時做多，預期觸發追價盤。"},
    {"名稱": "Consolidation Breakout", "說明": "橫盤整理後放量突破壓力區，進場做多。"},
    {"名稱": "Morning Push", "說明": "開盤後的第一波多頭攻勢，快速搶進做多。"},
    {"名稱": "Momentum Ignition", "說明": "突破壓力或技術位時出現量能爆發，做多追動能。"},
    {"名稱": "Pre-market High Break", "說明": "開盤突破盤前高點做多，通常搭配熱點題材。"},
    {"名稱": "SSR Bounce", "說明": "前日觸發 SSR 的股票早盤出現強勁反彈，做多低吸搶反彈。"},
    {"名稱": "Backside Dip Long", "說明": "股票經歷大跌後，尋找底部反彈機會進場做多。"},
    {"名稱": "Retest and Go", "說明": "股價突破壓力後回踩不破，再次啟動上漲波段。"},
    {"名稱": "First Green Day", "說明": "多日下跌後第一根大陽線（轉多信號），做多轉勢反彈。"},
    {"名稱": "EMA Crossover Long", "說明": "短期 EMA 上穿長期 EMA 時做多（例如 9EMA 上穿 20EMA）。"},
    {"名稱": "Flag Breakout", "說明": "上漲後橫盤整理成旗形，再次放量突破做多。"}
]



from dash import html, dcc, dash_table, Input, Output, State, callback_context
import os
from dash import html, dcc
from urllib.parse import quote, unquote

def create_s_cards(strategies):
    cards = []
    for strat in strategies:
        cards.append(
            dcc.Link(
                
                href=f'/strategy/{quote(strat["名稱"])}',
                
                children=html.Div([
                    html.Div(strat['名稱'], className='card-title'),
                    html.Div(strat['說明'], className='card-text'),
                ], className='s-card'),
                style={'textDecoration': 'none'}
            )
            
        )
        
    return cards
def strategy_list_page():
    return html.Div([
        dcc.Location(id='url-strategy', refresh=False),

        html.H2("📊 日內多空策略", style={'margin': '20px auto', 'color': 'white', 'maxWidth': '1200px'}),

        html.H4("🥷 空頭策略（Short Strategies）", style={'margin': '10px auto', 'color': 'white', 'maxWidth': '1200px'}),
        html.Div(
            create_s_cards(short_strategies),
            className="s-card-container"
        ),

        html.Div(style={'height': '100px'}),
        
        html.H4("🐱 多頭策略（Long Strategies）", style={'margin': '10px auto', 'color': 'white', 'maxWidth': '1200px'}),
        html.Div(
            create_s_cards(long_strategies),
            className="s-card-container"
        ),
    ], style={"backgroundColor": "#121212", "minHeight": "100vh", "paddingBottom": "40px"})