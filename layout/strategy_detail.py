import os
import json
from dash import html
from components.navigation import create_header, create_footer, create_back_button_strategy
from urllib.parse import unquote

def load_strategy_description(strategy_name):
    base_path = 'assets/strategies'
    short_path = os.path.join(base_path, 'short_strategies.json')
    long_path = os.path.join(base_path, 'long_strategies.json')

    data = []
    for path in [short_path, long_path]:
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as f:
                try:
                    part_data = json.load(f)
                    if isinstance(part_data, list):
                        data.extend(part_data)
                except json.JSONDecodeError:
                    continue

    for item in data:
        if item.get('名稱') == strategy_name:
            return item
    return None

def create_strategy_detail_page(strategy_name):
    decoded_name = unquote(strategy_name)
    base_path = 'assets/strategies'
    image_file = f'{decoded_name}.png'
    image_path = os.path.join(base_path, image_file)

    if not os.path.isfile(image_path):
        image_file = 'strategy_none.png'

    strategy = load_strategy_description(decoded_name)

    cards = []

    # --- 圖片卡片（<s-card>） ---
    cards.append(html.Div([
        html.Div([
            html.Img(
                src=f'/assets/strategies/{image_file}',
                style={
                    'width': '100%',
                    'borderRadius': '8px',
                    'objectFit': 'contain'
                }
            )
        ])
    ], className='s-card image-card'))

    if strategy is None:
        cards.append(html.Div("⚠️ 策略說明未完成，請稍後補上。", className='s-card error-card'))
    else:
        def s_card(title, key):
            return html.Div([
                html.H4(title, className='card-title'),
                html.P(strategy.get(key, ""), className='card-text')
            ], className='s-card')

        cards.extend([
            s_card("名稱", "名稱"),
            s_card("說明", "說明"),
            s_card("簡介", "簡介"),
            s_card("大機會出現時間", "大機會出現時間"),
            s_card("為什麼會出現", "為什麼會出現"),
            s_card("心理原因", "心理原因"),
            s_card("圖表型態", "圖表型態"),
            s_card("參數說明", "參數說明"),
            s_card("止損設定", "止損設定"),
            s_card("理想風險報酬比", "理想風險報酬比"),
            s_card("不應進場條件", "不應進場條件")
        ])

    return html.Div([
        create_header(f"{strategy_name} 策略詳細", ""),
        html.Div([
            create_back_button_strategy(),
            html.Div(cards, className='s-card-container')
        ], className='main-content', style={'padding': '20px'}),
        create_footer()
    ])
