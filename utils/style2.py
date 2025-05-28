index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background-color: #252525;
                color: #333333;
            }
            
            .header {
                background-color: #09181F;
                color: white;
                padding: 20px;
                text-align: center;
                border-bottom: 5px solid #3498db;
            }
            
            .header-title {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .header-date {
                font-size: 14px;
                opacity: 0.8;
            }
            
            .main-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .row {
                display: flex;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            
            .chart-container {
                flex: 3;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-right: 20px;
            }
            
            .metrics-column {
                flex: 2;
                display: flex;
                flex-direction: column;
            }
            
            .full-width {
                flex: 1 1 100%;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
            }
            
            .card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .card-title {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 15px;
                font-size: 18px;
            }
            
            .subtitle {
                color: #2c3e50;
                margin: 15px 0 10px 0;
                font-size: 16px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            
            .metric-container {
                padding: 10px;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            
            .metric-title {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 5px;
            }
            
            .metric-value {
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .info-list p {
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .reasons-list {
                margin-left: 20px;
                font-size: 14px;
            }
            
            .reasons-list li {
                margin-bottom: 5px;
            }
            
            .suggestion-container {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }
            
            .suggestion-text p {
                margin-bottom: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
            
            .footer {
                background-color: #2c3e50;
                color: white;
                text-align: center;
                padding: 15px;
                margin-top: 20px;
            }
            
            .footer-text {
                font-size: 12px;
                opacity: 0.8;
            }
            
            .stock-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .stock-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            .stock-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .stock-symbol {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            
            .stock-name {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
            
            .stock-metrics {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            
            .back-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin-bottom: 20px;
                font-size: 14px;
            }
            
            .back-button:hover {
                background-color: #2980b9;
            }

            .news-item {
                margin-bottom: 15px;
                padding: 10px;
                
                border-radius: 5px;
            }

            .news-timestamp {
                font-size: 12px;
                color: #666;
                margin-bottom: 5px;
            }

            .news-text {
                white-space: pre-wrap;
                margin-bottom: 10px;
                background-color: #f8f9fa;
                margin-right: 70px;
            }

            .submit-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                float: right;
                margin-bottom: 20px;
                margin-top: 20px;
                font-size: 14px;

                
            }

            .submit-button:hover {
                background-color: #ff6666;
            }

            .delete-news-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                cursor: pointer;
                float: right;
                margin-bottom: 20px;
                margin-top: -50px;
                font-size: 10px;

                
            }

            .delete-news-button:hover {
                background-color: #ff5252;
            }
            
            @media (max-width: 768px) {
                .row {
                    flex-direction: column;
                }
                
                .chart-container {
                    margin-right: 0;
                    margin-bottom: 20px;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .stock-list {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'header': '#2c3e50',
    'positive': '#27ae60',
    'negative': '#c0392b',
    'neutral': '#3498db',
    'warning': '#f39c12'
}