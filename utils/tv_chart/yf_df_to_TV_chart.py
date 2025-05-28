
import pandas as pd

from support_resistance_analyzer import SupportResistanceAnalyzer
from yahoo_finance_dataLoader import YahooFinanceDataLoader as yf
from tv_chart_creator import TVChartCreator






def create_stock_chart_with_sr(ticker_symbol, period='5d', interval='15m'):
    try:
        # 獲取數據
        df = yf.get_stock_data(ticker_symbol, period=period, interval=interval)
        if not df.empty:
            print(f"Successfully fetched data for {ticker_symbol}")
            print(df.head())


        """
           Successfully fetched data for AAPL
                             open    high     low   close  volume
Datetime
2025-05-21 04:00:00-04:00  206.10  206.26  206.05  206.14       0
2025-05-21 04:05:00-04:00  206.20  206.20  206.05  206.12       0
2025-05-21 04:10:00-04:00  206.18  206.21  206.16  206.21       0
2025-05-21 04:15:00-04:00  206.20  206.20  206.01  206.13       0
2025-05-21 04:20:00-04:00  206.11  206.11  206.11  206.11       0
           """
        
        # 運行支撐阻力分析
        analyzer = SupportResistanceAnalyzer(df)
        results = analyzer.run_all_analysis()
        
        # 獲取所有支撐阻力水平
        sr_levels = analyzer.get_all_levels()
        analyzer.print_result(symbol=ticker_symbol)
        """
           📈 Support & Resistance Analysis Report for AAPL
============================================================

🔍 Fibonacci:
  • 0%: 211.77
  • 23.6%: 207.37
  • 38.2%: 204.65
  • 50%: 202.45
  • 61.8%: 200.25
  • 100%: 193.13

🔍 Pivot Points:
  • Support: [193.18 195.34 201.2  202.28 204.06 205.53]
  • Resistance: [196.29 197.7  202.12 206.24 207.97 211.77]

🔍 Bollinger Bands:
  • Support: 195.27
  • Resistance: 195.71

🔍 KMeans Clusters:
  • Levels: [194.39 195.82 201.2  202.05 205.91]

🔍 Volume Profile:
  • Levels: [195.75 196.25 196.75 201.75]

🔍 Trendlines:
  • Current Support: 200.85
  • Current Resistance: 197.53
           """
        
        # 創建圖表
        chart_creator = TVChartCreator(df)
        chart_creator.create_basic_figure()
        chart_creator.create_volume_figure()
        chart_creator.create_time_line()
        chart_creator.create_support_lines(sr_levels)
        chart_creator.create_premarket_background_color()
        chart_creator.create_support_lines(sr_levels)
        chart_creator.create_resistance_lines(sr_levels)
        chart_creator.create_chart_style(ticker_symbol, period, interval)
        fig = chart_creator.fig

        
        
        # 返回圖表和分析結果
        return fig, results
        
    except Exception as e:
        print(f"Error creating chart: {str(e)}")
        return None, None






if __name__ == "__main__":
    # 設定股票代碼和參數
    stock_symbol = 'AAPL'  # 可以更改為其他股票代碼
    time_period = '3d'     # 推薦使用更長的時間範圍
    time_interval = '5m'  # 推薦使用15分鐘線
    
    try:
        # 創建圖表和獲取分析結果
        fig, results = create_stock_chart_with_sr(stock_symbol, period=time_period, interval=time_interval)
        
        if fig is None:
            raise ValueError("Failed to create chart")
        
        # 顯示圖表
        fig.show()


        
                
    except Exception as e:
        print(f"Error in main execution: {str(e)}")