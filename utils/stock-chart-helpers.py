import pandas as pd

def prepare_tvlwc_data(data_list):
    """準備 Tvlwc 組件需要的資料格式"""
    try:
        df = pd.DataFrame(data_list)
        
        # 確保 datetime 列存在
        if 'datetime' not in df.columns:
            print("警告：資料中沒有 datetime 欄位")
            return []
        
        # 轉換時間戳
        df['time'] = pd.to_datetime(df['datetime']).astype(int) // 10**9
        
        # 轉換為 Tvlwc 需要的格式
        tvlwc_data = []
        for _, row in df.iterrows():
            tvlwc_data.append({
                'time': int(row['time']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
        
        print(f"準備了 {len(tvlwc_data)} 筆 Tvlwc 資料")
        if len(tvlwc_data) > 0:
            print(f"第一筆資料範例: {tvlwc_data[0]}")
        
        return tvlwc_data
    except Exception as e:
        print(f"準備 Tvlwc 資料時發生錯誤: {e}")
        return []