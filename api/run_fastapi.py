import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from bson import json_util

# 導入您的 MongoHandler
from _mongo import MongoHandler  # 假設您的文件名為 paste.py

# 導入新創建的實用工具
from api.services.fastapi_utils import format_market_cap, prepare_tvlwc_data, filter_chart_data

app = FastAPI(
    title="股票數據 API",
    description="快速查詢 TradeZero_Bot 數據庫中的股票基本面數據",
    version="1.0.0"
)

# 初始化 MongoDB 連接
mongo_handler = MongoHandler()

def serialize_mongo_data(data):
    """將 MongoDB 數據序列化為 JSON 可讀格式"""
    return json.loads(json_util.dumps(data))

@app.get("/")
async def root():
    """根路徑，返回 API 信息"""
    return {
        "message": "股票數據 API",
        "version": "1.0.0",
        "endpoints": {
            "/stocks/{symbol}": "根據股票代碼查詢詳細信息 (已增強)",
            "/stocks/": "查詢所有股票或根據日期篩選",
            "/stocks/{symbol}/chart": "獲取股票圖表數據 (已增強)",
            "/stocks/{symbol}/price-overview": "獲取股票價格概覽數據 (新增)",
            "/stocks/top-movers": "獲取漲跌幅最大的股票",
            "/stocks/{symbol}/analysis": "獲取股票分析和建議 (已增強)",
            "/health": "檢查 API 和數據庫健康狀態"
        }
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    db_status = mongo_handler.is_connected()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
    }

@app.get("/stocks/{symbol}")
async def get_stock_by_symbol(
    symbol: str,
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """根據股票代碼查詢詳細信息 (已增強)"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query)
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 的數據")
        
        # Add formatted market cap
        serialized_result = serialize_mongo_data(result)
        market_cap_float = result.get('market_cap_float')
        serialized_result['market_cap_formatted'] = format_market_cap(market_cap_float)

        return JSONResponse(content=serialized_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")

@app.get("/stocks/")
async def get_stocks(
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD"),
    limit: int = Query(50, ge=1, le=500, description="返回結果數量限制"),
    skip: int = Query(0, ge=0, description="跳過的結果數量")
):
    """查詢股票列表，可根據日期篩選"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    query = {}
    if date:
        query["today_date"] = date
    
    try:
        # 使用 MongoDB 的聚合管道來實現分頁
        pipeline = [
            {"$match": query},
            {"$skip": skip},
            {"$limit": limit},
            {"$project": {
                "symbol": 1,
                "name": 1,
                "day_close": 1,
                "yesterday_close": 1,
                "close_change_percentage": 1,
                "high_change_percentage": 1,
                "day_high": 1,
                "day_low": 1,
                "today_date": 1,
                "float_risk": 1,
                "short_signal": 1
            }}
        ]
        
        collection = mongo_handler.db["fundamentals_of_top_list_symbols"]
        results = list(collection.aggregate(pipeline))
        
        return JSONResponse(content={
            "count": len(results),
            "data": serialize_mongo_data(results)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")

@app.get("/stocks/{symbol}/chart")
async def get_stock_chart(
    symbol: str,
    timeframe: str = Query("1d", description="時間框架: 1m, 5m, 1d"),
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """獲取股票圖表數據 (已增強，返回 Tvlwc 格式數據)"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    if timeframe not in ["1m", "5m", "1d"]:
        raise HTTPException(status_code=400, detail="時間框架必須是 1m, 5m, 或 1d")
    
    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query)
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 的數據")
        
        chart_field = f"{timeframe}_chart_data"
        raw_chart_data = result.get(chart_field, [])

        # Filter the chart data based on timeframe (e.g., last 3 hours for 1m, latest day for 5m/1d)
        filtered_chart_data = filter_chart_data(raw_chart_data, timeframe)
        
        # Prepare data for dash_tvlwc component (Unix timestamp for time)
        tvlwc_chart_data = prepare_tvlwc_data(filtered_chart_data)
        
        return JSONResponse(content={
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data_points": len(tvlwc_chart_data),
            "chart_data": tvlwc_chart_data # Return processed data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")

@app.get("/stocks/{symbol}/price-overview")
async def get_stock_price_overview(
    symbol: str,
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """獲取股票價格概覽數據 (新增)"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query)
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 的數據")
        
        # Extract and organize relevant price points and key levels
        price_overview_data = {
            "symbol": result.get("symbol"),
            "yesterday_close": result.get("yesterday_close"),
            "day_low": result.get("day_low"),
            "day_high": result.get("day_high"),
            "day_close": result.get("day_close"),
            "market_open_high": result.get("market_open_high"),
            "market_open_low": result.get("market_open_low"),
            "key_levels": result.get("key_levels", [])
        }
        
        return JSONResponse(content=serialize_mongo_data(price_overview_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")


@app.get("/top-movers")
async def get_top_movers(
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD"),
    limit: int = Query(10, ge=1, le=50, description="返回結果數量"),
    sort_by: str = Query("close_change_percentage", description="排序字段: close_change_percentage 或 high_change_percentage")
):
    """獲取漲跌幅最大的股票"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    if sort_by not in ["close_change_percentage", "high_change_percentage"]:
        raise HTTPException(status_code=400, detail="排序字段必須是 close_change_percentage 或 high_change_percentage")
    
    query = {}
    if date:
        query["today_date"] = date
    
    try:
        pipeline = [
            {"$match": query},
            {"$sort": {sort_by: -1}},
            {"$limit": limit},
            {"$project": {
                "symbol": 1,
                "name": 1,
                "day_close": 1,
                "yesterday_close": 1,
                "close_change_percentage": 1,
                "high_change_percentage": 1,
                "day_high": 1,
                "day_low": 1,
                "today_date": 1,
                "float_risk": 1,
                "short_signal": 1
            }}
        ]
        
        collection = mongo_handler.db["fundamentals_of_top_list_symbols"]
        results = list(collection.aggregate(pipeline))
        
        return JSONResponse(content={
            "sorted_by": sort_by,
            "count": len(results),
            "data": serialize_mongo_data(results)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")

@app.get("/stocks/{symbol}/analysis")
async def get_stock_analysis(
    symbol: str,
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """獲取股票分析和建議 (已增強，包含現金和債務百萬值)"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query)
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 的數據")
        
        # Calculate cash and debt in millions
        cash = result.get("cash")
        debt = result.get("debt")
        
        cash_in_millions = float(cash / 1_000_000) if cash is not None else None
        debt_in_millions = float(debt / 1_000_000) if debt is not None else None

        analysis_data = {
            "symbol": result.get("symbol"),
            "suggestion": result.get("suggestion"),
            "sec_filing_analysis": result.get("sec_filing_analysis"),
            "key_levels": result.get("key_levels"),
            "float_risk": result.get("float_risk"),
            "short_signal": result.get("short_signal"),
            "hype_score": result.get("hype_score"),
            "squeeze_score": result.get("squeeze_score"),
            "atm_urgency": result.get("atm_urgency"),
            "cash_in_millions": cash_in_millions,  # Added
            "debt_in_millions": debt_in_millions   # Added
        }
        
        return JSONResponse(content=serialize_mongo_data(analysis_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤: {str(e)}")

if __name__ == "__main__":
    # 檢查數據庫連接
    if not mongo_handler.is_connected():
        print("警告: 無法連接到 MongoDB 數據庫")
        print("請確保:")
        print("1. MongoDB 服務正在運行")
        print("2. 環境變量 MONGODB_CONNECTION_STRING 已正確設置")
        print("3. 網絡連接正常")
        # 不要因為數據庫連接問題就退出，繼續啟動服務器
    else:
        print("✅ 成功連接到 MongoDB 數據庫")
    
    print("🚀 啟動 FastAPI 服務器...")
    print("📊 API 文檔地址: http://localhost:8000/docs")
    print("🔍 交互式文檔: http://localhost:8000/redoc")
    print("🛑 按 Ctrl+C 停止服務器")
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1",  # 改為本地地址
            port=8000,
            reload=False,  # 關閉自動重載以避免導入問題
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服務器已停止")
    except Exception as e:
        print(f"❌ 服務器啟動失敗: {e}")
        print("\n🔧 解決方案:")
        print("1. 檢查端口 8000 是否被佔用")
        print("2. 嘗試使用命令行啟動: uvicorn run_fastapi:app --host 127.0.0.1 --port 8000")
        print("3. 檢查防火牆設置")