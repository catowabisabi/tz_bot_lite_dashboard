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
        background-color: #121212;
        color: #e0e0e0;
    }

    .header {
        background-color: #1f2c33;
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
        background-color: #1e1e1e;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(255, 255, 255, 0.05);
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
        background-color: #1e1e1e;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(255, 255, 255, 0.05);
        padding: 15px;
    }

    .card {
        background-color: #1e1e1e;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(255, 255, 255, 0.05);
        padding: 15px;
        margin-bottom: 20px;
    }

    .card-title {
        color: #ffffff;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-size: 18px;
    }

    .subtitle {
        color: #bbbbbb;
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
        background-color: #2a2a2a;
    }

    .metric-title {
        font-size: 12px;
        color: #aaaaaa;
        margin-bottom: 5px;
    }

    .metric-value {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
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
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 5px;
    }

    .suggestion-text p {
        margin-bottom: 15px;
        font-size: 14px;
        line-height: 1.5;
    }

    .footer {
        background-color: #1e1e1e;
        color: #aaaaaa;
        text-align: center;
        padding: 15px;
        margin-top: 20px;
    }

    .footer-text {
        font-size: 12px;
        opacity: 0.6;
    }

    .stock-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }



    .stock-card {
        background-color: #1e1e1e;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(255, 255, 255, 0.05);
        padding: 15px;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .stock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(255, 255, 255, 0.05);
    }

    .stock-symbol {
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .stock-name {
        font-size: 14px;
        color: #cccccc;
        margin-bottom: 10px;
    }

    .stock-metrics {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }

    .back-button,
    .submit-button,
    .delete-news-button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    }

    .back-button:hover,
    .submit-button:hover {
        background-color: #2980b9;
    }

    .delete-news-button {
        font-size: 10px;
        padding: 8px 12px;
    }

    .delete-news-button:hover {
        background-color: #e74c3c;
    }

    .news-item {
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 5px;
    }

    .news-timestamp {
        font-size: 12px;
        color: #999999;
        margin-bottom: 5px;
    }

    .news-text {
        white-space: pre-wrap;
        margin-bottom: 10px;
        background-color: #2a2a2a;
        margin-right: 70px;
        padding: 10px;
        border-radius: 5px;
        color: #e0e0e0;
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

    .stock-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

#date-tabs .tab {
    padding: 10px 15px;
    background-color: #2a2a2a;
    border: 1px solid #444;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    color: #e0e0e0;
}
#date-tabs .tab--selected {
    background-color: #1a1a1a;
    border-bottom: 1px solid #1a1a1a;
    font-weight: bold;
    color: #fff;
}


.strategy-section {
    margin-bottom: 2rem;
}

.strategy-section h3 {
    margin-bottom: 0.5rem;
    color: #333;
}

.strategy-section p {
    margin: 0;
    line-height: 1.6;
}






/* 卡片網格容器，最多 4 欄，自動 RWD */
.s-card-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 每張卡片通用樣式 */
.s-card {
  background-color: #1e1e1e;
  color: #f2f2f2;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
  transition: transform 0.2s ease;
}

/* 圖片卡片佔 2x2 格（4 格） */
.image-card {
  grid-column: span 2;
  grid-row: span 2;
}

@media screen and (max-width: 768px) {
  .image-card {
    grid-column: span 1;
    grid-row: span 1;
  }
}

/* 卡片 hover 效果 */
.s-card:hover {
  transform: translateY(-6px);
}

.s-card img {
  width: 100%;
  height: auto;
  border-radius: 10px;
  object-fit: cover;
}

/* 卡片標題與內文 */
.card-title {
  font-size: 18px;
  color: #ffd700;
  margin-bottom: 10px;
  font-weight: bold;
}

.card-text {
  font-size: 15px;
  color: #ddd;
  line-height: 1.6;
}

.error-card {
  background-color: #440000;
  color: white;
  font-weight: bold;
}


.custom-chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    width: 100%;
}
.chart-container {
    background-color: #1e1e1e;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: white;
}
.chart-header {
    margin-bottom: 12px;
}
.chart-card {
    width: 100%;
}

    .chart-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr)); /* 一行三欄 */
    gap: 10px;
    
    margin-top: 20px;
    padding: 10px;
}

/* 平板或小螢幕時變兩欄 */
@media (max-width: 1024px) {
    .chart-list {
        grid-template-columns: repeat(2, 1fr);
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