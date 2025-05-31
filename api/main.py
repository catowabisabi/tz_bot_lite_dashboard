from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
import base64
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI()

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

# 其他現有的路由和功能保持不變
# ... existing code ... 