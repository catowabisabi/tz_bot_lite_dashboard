import requests
import json
from datetime import datetime
import pandas as pd 

class TradingViewScanner:
    def __init__(self, 
                 lowest_pm_change=50, 
                 num_stocks=200, 
                 lowest_price=0.5, 
                 highest_price=10, 
                 lowest_volume=100000,
                 scan="penny_stocks"):
        self.lowest_pm_change = lowest_pm_change
        self.num_stocks = num_stocks
        self.lowest_price = lowest_price
        self.highest_price = highest_price
        self.lowest_volume = lowest_volume
        self.scan = scan
        
        self.url = "https://scanner.tradingview.com/america/scan?label-product=markets-screener"
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://www.tradingview.com",
            "referer": "https://www.tradingview.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        
        self.column_mappings = [
            ["name", "Symbol"],
            ["close", "Price"],
            ["premarket_gap", "PM % Gap"],
            ["premarket_change", "PM % Chg"],
            ["change", "% Chg"],
            ["premarket_close", "PM Close"],
            ["premarket_volume", "PM Vol"],
            ["market_cap_basic", "Market Cap"],
            ["gross_margin_ttm", "Gross Margin %"],
            ["operating_margin_ttm", "Operating Margin %"],
            ["free_cash_flow_margin_ttm", "FCF Margin %"],
            ["total_revenue_yoy_growth_ttm", "Rev YOY %"],
            ["cash_n_short_term_invest_to_total_debt_fq", "Cash/Debt"],
        ]

    def fetch_data(self):
        payload_columns = [col[0] for col in self.column_mappings]
        payload = {
            "columns": payload_columns,
            "ignore_unknown_fields": False,
            "options": {"lang": "en"},
            "range": [0, self.num_stocks],
            "sort": {
                #"sortBy": "premarket_change",
                "sortBy": "change",
                "sortOrder": "desc",
                "nullsFirst": False
            },
            "preset": self.scan
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            print(f"Request failed with status code: {response.status_code}")
            return []

        response_data = response.json()
        data_list = []

        for item in response_data['data']:
            record = {}
            for idx, mapping in enumerate(self.column_mappings):
                original_name, custom_name = mapping

                if original_name == "name":
                    value = item['s'].split(":")[1] if ":" in item['s'] else item['s']
                else:
                    try:
                        value = item['d'][idx]
                        if isinstance(value, (int, float)):
                            value = round(value, 2)
                    except (IndexError, KeyError):
                        value = None
                record[custom_name] = value
            
            data_list.append(record)
        
        return data_list

    def filter_data(self, data_list):
        filtered = []
        for record in data_list:
            try:
                chg = record ["% Chg"]
                price = record["Price"]
                pm_chg = record["PM % Chg"]
                pm_vol = record["PM Vol"]

                if price is None or pm_chg is None or pm_vol is None or chg is None:
                    continue
                if not (self.lowest_price <= price <= self.highest_price):
                    continue
                if not (pm_chg > self.lowest_pm_change or chg > self.lowest_pm_change):
                    continue
                if pm_vol < self.lowest_volume:
                    continue


                filtered.append(record)
            except KeyError:
                continue
        
        return filtered

    def run(self):
        raw_data = self.fetch_data()
        
        # 打印 raw data 前10個
        if raw_data:
            df_raw = pd.DataFrame(raw_data)
            print("\nRaw Data (Top 20 rows):")
            print(df_raw.head(20))
        else:
            print("No raw data fetched.")
        
        filtered_data = self.filter_data(raw_data)
        if filtered_data:
            df_filtered = pd.DataFrame(filtered_data)
            print("\nFiltered Data (Top 20 rows):")
            print(df_filtered.head(20))
        else:
            print("No filtered  data fetched.")
        
        # 取 symbol list
        symbol_list = [item["Symbol"] for item in filtered_data]
        
        # 取當前時間
        scan_datetime = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        
        return filtered_data, symbol_list, scan_datetime

        

# ========== 使用示例 ==========

scanner = TradingViewScanner(
    lowest_pm_change=20, 
    num_stocks=200, 
    lowest_price=0.5, 
    highest_price=10, 
    lowest_volume=10000,
    #scan = "penny_stocks"
    scan = "all_stocks"
    #scan = "pre-market-gainers" #9點半前
)

data_list, symbol_list, scan_time = scanner.run()

#print(f"Data List ({len(data_list)} items):")
#print(data_list)
print(f"\nSymbol List ({len(symbol_list)} symbols):")
print(symbol_list)
print(f"\nScan Datetime: {scan_time}")
