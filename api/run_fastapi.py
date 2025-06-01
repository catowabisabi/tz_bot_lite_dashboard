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
from bson import ObjectId

# 導入您的 MongoHandler
from _mongo import MongoHandler  # 假設您的文件名為 paste.py

# 導入新創建的實用工具
from api.services.fastapi_utils import format_market_cap, prepare_tvlwc_data, filter_chart_data
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import base64
import uuid
from tz_api.api_news_fetcher import Summarizer

app = FastAPI(
    title="股票數據 API",
    description="快速查詢 TradeZero_Bot 數據庫中的股票基本面數據",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態文件目錄
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# 基本策略模型（用於列表顯示）
class StrategyBase(BaseModel):
    名稱: str
    說明: str

# 完整策略模型（用於詳情頁面）
class StrategyDetail(StrategyBase):
    簡介: Optional[str] = None
    大機會出現時間: Optional[str] = None
    為什麼會出現: Optional[str] = None
    心理原因: Optional[str] = None
    圖表型態: Optional[str] = None
    參數說明: Optional[str] = None
    止損設定: Optional[str] = None
    理想風險報酬比: Optional[str] = None
    不應進場條件: Optional[str] = None

def load_strategies() -> Dict[str, List[StrategyDetail]]:
    base_path = 'assets/strategies'
    strategies = {"long": [], "short": []}
    
    # 讀取多頭策略
    long_path = os.path.join(base_path, 'long_strategies.json')
    if os.path.isfile(long_path):
        with open(long_path, encoding='utf-8') as f:
            strategies["long"] = [StrategyDetail(**item) for item in json.load(f)]
    
    # 讀取空頭策略
    short_path = os.path.join(base_path, 'short_strategies.json')
    if os.path.isfile(short_path):
        with open(short_path, encoding='utf-8') as f:
            strategies["short"] = [StrategyDetail(**item) for item in json.load(f)]
    
    return strategies

def get_image_base64(image_path: str) -> str:
    """讀取圖片並轉換為base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        # 如果讀取失敗，返回預設圖片
        with open("assets/strategies/strategy_none.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

@app.get("/api/strategies")
async def get_strategies():
    """獲取所有策略列表（只返回名稱和說明）"""
    try:
        strategies = load_strategies()
        return {
            "status": "success",
            "data": {
                "long_strategies": [{"名稱": s.名稱, "說明": s.說明} for s in strategies["long"]],
                "short_strategies": [{"名稱": s.名稱, "說明": s.說明} for s in strategies["short"]]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategy/{strategy_name}")
async def get_strategy_detail(strategy_name: str):
    """獲取特定策略的詳細信息"""
    try:
        strategies = load_strategies()
        # 在多頭和空頭策略中查找
        for strategy_type in ["long", "short"]:
            for strategy in strategies[strategy_type]:
                if strategy.名稱 == strategy_name:
                    # 獲取策略圖片
                    image_path = f"assets/strategies/{strategy_name}.png"
                    image_data = get_image_base64(image_path)
                    
                    return {
                        "status": "success",
                        "data": {
                            "strategy": strategy.dict(),
                            "image": {
                                "data": image_data,
                                "format": "base64"
                            }
                        }
                    }
        
        raise HTTPException(status_code=404, detail="Strategy not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    


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
    
@app.get("/stocks/{symbol}/fundamentals")
async def get_stock_fundamentals(
    symbol: str,
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """獲取股票基本面數據 (不包含圖表數據)"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")
    
    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        # 使用 projection 排除圖表數據
        projection = {
            "1d_chart_data": 0,
            "1m_chart_data": 0,
            "5m_chart_data": 0
        }
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query, projection)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 的數據")
        
        # 序列化並格式化市值
        serialized_result = serialize_mongo_data(result)
        market_cap_float = result.get('market_cap_float')
        if market_cap_float:
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
                "short_signal": 1,
                "sector":1
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

@app.get("/api/stocks/{symbol}/news")
async def get_stock_news(
    symbol: str,
    date: Optional[str] = Query(None, description="日期格式: YYYY-MM-DD")
):
    """獲取指定股票的新聞"""
    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")

    query = {"symbol": symbol.upper()}
    if date:
        query["today_date"] = date
    
    try:
        # Use projection to fetch only necessary fields
        projection = {
            "_id": 0,  # Exclude the default _id field
            "symbol": 1,
            "today_date": 1,
            "raw_news": 1
        }
        result = mongo_handler.find_one("fundamentals_of_top_list_symbols", query, projection=projection)
        if not result:
            raise HTTPException(status_code=404, detail=f"找不到股票代碼 {symbol} 在日期 {date} 的數據")
        
        news_data = result.get("raw_news", [])
        return JSONResponse(content={
            "symbol": symbol.upper(),
            "date": date,
            "news_count": len(news_data),
            "news": serialize_mongo_data(news_data)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢新聞錯誤: {str(e)}")

class NewsItem(BaseModel):
    password: str
    news: str
    target_document_id: str # MongoDB ObjectId of the target fundamentals document

@app.post("/api/stocks/{symbol}/add-news")
async def add_stock_news(
    symbol: str,
    item: NewsItem
):
    """為指定股票的特定文檔添加新聞 (通過文檔 MongoDB _id 定位)"""
    if item.password != "Abc123456.":
        raise HTTPException(status_code=401, detail="密碼錯誤")

    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")

    if not item.news or not item.target_document_id:
        raise HTTPException(status_code=400, detail="新聞內容和目標文檔ID為必填項")

    try:
        # Validate and convert target_document_id to ObjectId
        target_oid = ObjectId(item.target_document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="目標文檔ID格式無效")

    collection_name = "fundamentals_of_top_list_symbols"
    # Query by symbol and the target document's _id
    query = {"symbol": symbol.upper(), "_id": target_oid}
    
    try:
        existing_doc = mongo_handler.db[collection_name].find_one(query)

        if not existing_doc:
            raise HTTPException(status_code=404, detail=f"找不到對應的股票基本面數據 (Symbol: {symbol.upper()}, Document ID: {item.target_document_id})，無法添加新聞。")

        raw_news_list = existing_doc.get("raw_news", [])
        existing_suggestion = existing_doc.get("suggestion", "None") # No 'else "None"' needed

        # GPT Summary
        gpt_summarizer = Summarizer()
        summary = gpt_summarizer.summarize(item.news)

        news_entry = {
            "uuid": str(uuid.uuid4()),
            "text": item.news,
            "summary": summary,
            "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
        raw_news_list.append(news_entry)

        prompt_for_suggestion = f"""
    新的新聞 (New News):
    {summary}

    原有的總結 (Original Summary):
    {existing_suggestion}

    請為這則新聞提供建議 (Please provide suggestions for this input):
    """
        new_suggestion = gpt_summarizer.suggestion(prompt_for_suggestion)

        update_result = mongo_handler.db[collection_name].update_one(
            query,
            {"$set": {
                "raw_news": raw_news_list,
                "suggestion": new_suggestion
            }},
            upsert=False # Changed from True to False
        )

        if update_result.modified_count > 0: # Removed 'or update_result.upserted_id'
            return JSONResponse(content={"status": "success", "message": "新聞已成功添加"})
        else:
            # This will be hit if the document was found but not modified (e.g., update data was identical or another issue)
            raise HTTPException(status_code=500, detail="添加新聞失敗，文檔未被修改。可能數據已存在或更新未生效。")
            
    except HTTPException as http_exc: # Re-raise HTTPException to preserve its status and detail
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加新聞時發生錯誤: {str(e)}")

class DeleteNewsItem(BaseModel):
    password: str
    target_document_id: str # MongoDB ObjectId of the target fundamentals document

@app.delete("/api/stocks/{symbol}/news/{news_uuid}")
async def delete_stock_news(
    symbol: str,
    news_uuid: str, # UUID of the specific news item to delete from raw_news
    item: DeleteNewsItem
):
    """刪除指定股票特定文檔中的特定新聞條目 (通過文檔 MongoDB _id 和新聞 UUID 定位)"""
    if item.password != "Abc123456.":
        raise HTTPException(status_code=401, detail="密碼錯誤")

    if not mongo_handler.is_connected():
        raise HTTPException(status_code=503, detail="數據庫連接失敗")

    try:
        # Validate and convert target_document_id to ObjectId
        target_oid = ObjectId(item.target_document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="目標文檔ID格式無效")

    collection_name = "fundamentals_of_top_list_symbols"
    # Query by symbol and the target document's _id
    query = {"symbol": symbol.upper(), "_id": target_oid}

    try:
        doc = mongo_handler.find_one(collection_name, query)
        if not doc or 'raw_news' not in doc:
            raise HTTPException(status_code=404, detail=f"找不到股票 {symbol} 對應ID {item.target_document_id} 的新聞數據")

        original_news_count = len(doc['raw_news'])
        # The news_uuid from the path is used here to filter the specific news item
        updated_news = [n for n in doc['raw_news'] if n.get("uuid") != news_uuid]
        
        if len(updated_news) == original_news_count:
            # This means the news_uuid was not found in the raw_news array of the specified document
            raise HTTPException(status_code=404, detail=f"在文檔ID {item.target_document_id} 中找不到 UUID 為 {news_uuid} 的新聞條目")

        update_result = mongo_handler.update_one(
            collection_name,
            query,
            {"raw_news": updated_news}
        )

        if update_result and update_result.get('modified_count', 0) > 0:
            return JSONResponse(content={"status": "success", "message": "新聞已成功刪除"})
        else:
            # This case might happen if the document was found but the news item was already deleted by another process
            # or if the update operation itself failed for some reason.
            existing_doc_after_attempt = mongo_handler.find_one(collection_name, query)
            if existing_doc_after_attempt and any(n.get("uuid") == news_uuid for n in existing_doc_after_attempt.get('raw_news', [])):
                raise HTTPException(status_code=500, detail="刪除新聞失敗，請重試")
            else: # Already deleted or never existed post initial check, but update_one reported no modification
                 return JSONResponse(content={"status": "success", "message": "新聞先前已被刪除或未找到"})

    except HTTPException as e:
        raise e # Re-raise HTTPException to preserve status code and detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除新聞時發生錯誤: {str(e)}")

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