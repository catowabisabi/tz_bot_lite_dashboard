
import yfinance as yf
import pandas as pd
import pytz


class YahooFinanceDataLoader():

    @staticmethod
    def get_stock_data(ticker, period='5d', interval='15m'):
        ticker = ticker.upper()
    
        try:
            # 獲取資料
            data = yf.download(ticker, period=period, interval=interval,  prepost=True)
            
            if data.empty:
                raise ValueError(f"No data found for ticker {ticker}")
        
            # 修正 MultiIndex (如果需要)
            if isinstance(data.columns, pd.MultiIndex):
                new_data = pd.DataFrame()
                new_data['open'] = data[('Open', ticker)] if ('Open', ticker) in data.columns else data['Open']
                new_data['high'] = data[('High', ticker)] if ('High', ticker) in data.columns else data['High']
                new_data['low'] = data[('Low', ticker)] if ('Low', ticker) in data.columns else data['Low'] 
                new_data['close'] = data[('Close', ticker)] if ('Close', ticker) in data.columns else data['Close']
                new_data['volume'] = data[('Volume', ticker)] if ('Volume', ticker) in data.columns else data['Volume']
                new_data.index = data.index
                data = new_data
            else:
                data.columns = data.columns.str.lower()
                data = data[['open', 'high', 'low', 'close', 'volume']]
            
            # 設置時區(如果時區資訊缺失)
            if data.index.tzinfo is None:
                et_tz = pytz.timezone('America/New_York')
                data.index = data.index.tz_localize('UTC').tz_convert(et_tz)
            else:
                et_tz = pytz.timezone('America/New_York')
                data.index = data.index.tz_convert(et_tz)
                
            # 確保時間排序正確
            data = data.sort_index(ascending=True)
            
            return data
            
        except Exception as e:
            raise ValueError(f"Error downloading data for {ticker}: {str(e)}")
