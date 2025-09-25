from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import Optional

# FastAPIアプリケーションの作成
app = FastAPI(
    title="福山市不動産価格予測API（軽量版）",
    description="町名、面積、築年数から不動産価格を予測するAPI（簡易版）",
    version="1.0.0"
)

# リクエストモデルの定義
class PropertyRequest(BaseModel):
    district_name: str
    area: float
    building_year: int
    property_type: Optional[str] = "宅地(土地と建物)"

class PropertyResponse(BaseModel):
    predicted_price: int
    confidence: str
    note: str

# 簡易的な価格予測ロジック
def predict_price_simple(district_name: str, area: float, building_year: int, property_type: str):
    """簡易的な価格予測（機械学習モデルなし）"""
    
    # 基本価格（1㎡あたり）
    base_price_per_sqm = 50000  # 50,000円/㎡
    
    # 町名による調整係数（主要な町名のみ）
    district_multipliers = {
        "神辺町": 0.8,
        "駅家町": 1.2,
        "曙町": 1.0,
        "松永町": 0.9,
        "本庄町": 1.1,
        "千代田町": 1.3,
        "元町": 1.4,
        "加茂町": 0.7,
        "木之庄町": 0.8,
        "南蔵王町": 1.0,
        "御幸町": 1.1,
        "大門町": 0.9,
        "津之郷町": 0.8,
        "引野町": 1.0,
    }
    
    # 建物タイプによる調整係数
    type_multipliers = {
        "宅地(土地と建物)": 1.0,
        "宅地(土地)": 0.6,
        "中古マンション等": 1.2,
        "農地": 0.3,
        "林地": 0.2,
    }
    
    # 築年数による調整係数
    if building_year == 0:
        year_multiplier = 1.0  # 新築
    elif building_year <= 5:
        year_multiplier = 0.95
    elif building_year <= 10:
        year_multiplier = 0.9
    elif building_year <= 20:
        year_multiplier = 0.8
    elif building_year <= 30:
        year_multiplier = 0.7
    else:
        year_multiplier = 0.6
    
    # 面積による調整
    if area < 100:
        area_multiplier = 1.2  # 小さい土地は単価が高い
    elif area < 200:
        area_multiplier = 1.0
    elif area < 500:
        area_multiplier = 0.9
    else:
        area_multiplier = 0.8  # 大きい土地は単価が安い
    
    # 町名の調整係数を取得
    district_multiplier = district_multipliers.get(district_name, 1.0)
    
    # 建物タイプの調整係数を取得
    type_multiplier = type_multipliers.get(property_type, 1.0)
    
    # 価格計算
    predicted_price = int(
        base_price_per_sqm * 
        area * 
        district_multiplier * 
        type_multiplier * 
        year_multiplier * 
        area_multiplier
    )
    
    # 信頼度の計算
    if district_name in district_multipliers and property_type in type_multipliers:
        confidence = "medium"
    else:
        confidence = "low"
    
    return predicted_price, confidence

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "福山市不動産価格予測API（軽量版）",
        "version": "1.0.0",
        "note": "簡易的な価格予測です。実際の価格とは異なる場合があります。",
        "endpoints": {
            "predict": "/predict - 価格予測",
            "health": "/health - ヘルスチェック",
            "docs": "/docs - API仕様書"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy", 
        "model": "簡易予測モデル",
        "note": "機械学習モデルを使用しない簡易版です"
    }

@app.post("/predict", response_model=PropertyResponse)
async def predict_price(request: PropertyRequest):
    """不動産価格を予測する（簡易版）"""
    
    try:
        # 簡易的な価格予測
        predicted_price, confidence = predict_price_simple(
            request.district_name,
            request.area,
            request.building_year,
            request.property_type
        )
        
        return PropertyResponse(
            predicted_price=predicted_price,
            confidence=confidence,
            note="簡易予測です。実際の価格とは異なる場合があります。"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"予測エラー: {str(e)}")

@app.get("/districts")
async def get_districts():
    """利用可能な町名のリストを取得"""
    districts = [
        "神辺町", "駅家町", "曙町", "松永町", "本庄町", "千代田町", "元町",
        "加茂町", "木之庄町", "南蔵王町", "御幸町", "大門町", "津之郷町", "引野町"
    ]
    return {"districts": districts}

@app.get("/property_types")
async def get_property_types():
    """利用可能な建物タイプのリストを取得"""
    types = ["宅地(土地と建物)", "宅地(土地)", "中古マンション等", "農地", "林地"]
    return {"property_types": types}

# Vercel用のハンドラー
handler = app
