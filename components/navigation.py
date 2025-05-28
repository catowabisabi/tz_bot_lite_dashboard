from dash import html

def create_header(title, subtitle=None):
    return html.Div([
        html.H1(title, className='header-title'),
        html.P(subtitle, className='header-date') if subtitle else None
    ], className='header')

def create_footer():
    return html.Div([
        html.P('© 2025 Stock Analytics Dashboard', className='footer-text'),
    ], className='footer')

def create_back_button():
    return html.Button(
        'Back to Stock List', 
        id='back-button', 
        className='back-button'
    )

def create_back_button_strategy():
    return html.Button(
        'Back to Strategy List', 
        id='back-button-strategy', 
        className='back-button'
    )