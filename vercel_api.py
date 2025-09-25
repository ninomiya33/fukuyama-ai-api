from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Optional
import os
import re

# FastAPIアプリケーションの作成
app = FastAPI(
    title="福山市不動産価格予測API",
    description="町名、面積、築年数から不動産価格を予測するAPI",
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
    predicted_price_log: float
    confidence: str

# モデルとエンコーダーの読み込み
def load_models():
    """学習済みモデルとエンコーダーを読み込む"""
    try:
        # モデル情報の読み込み
        model_info = joblib.load('models/model_info.pkl')
        
        # 最良のモデルを読み込み
        best_model = joblib.load('models/best_model.pkl')
        
        # スケーラーを読み込み
        scaler = joblib.load('models/scaler.pkl')
        
        # エンコーダーを読み込み
        district_encoder = joblib.load('label_encoders/district_encoder.pkl')
        type_encoder = joblib.load('label_encoders/type_encoder.pkl')
        year_encoder = joblib.load('label_encoders/year_encoder.pkl')
        
        return {
            'model': best_model,
            'scaler': scaler,
            'district_encoder': district_encoder,
            'type_encoder': type_encoder,
            'year_encoder': year_encoder,
            'feature_columns': model_info['feature_columns'],
            'model_name': model_info['best_model_name']
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"モデルファイルが見つかりません: {e}")

# グローバル変数でモデルを保持
models = None

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にモデルを読み込む"""
    global models
    try:
        models = load_models()
        print(f"モデル読み込み完了: {models['model_name']}")
    except Exception as e:
        print(f"モデル読み込みエラー: {e}")
        models = None

def preprocess_input(district_name: str, area: float, building_year: int, property_type: str):
    """入力データの前処理"""
    
    # 築年数のカテゴリ化
    def categorize_building_year(year):
        if year == 0:
            return 'new'
        elif year <= 5:
            return 'very_new'
        elif year <= 10:
            return 'new'
        elif year <= 20:
            return 'medium'
        elif year <= 30:
            return 'old'
        else:
            return 'very_old'
    
    # 特徴量の作成
    features = {}
    
    # 町名のエンコーディング
    try:
        features['DistrictName_encoded'] = models['district_encoder'].transform([district_name])[0]
    except ValueError:
        # 未知の町名の場合は最も頻度の高い町名で置換
        features['DistrictName_encoded'] = 0
    
    # 建物タイプのエンコーディング
    try:
        features['Type_encoded'] = models['type_encoder'].transform([property_type])[0]
    except ValueError:
        # 未知のタイプの場合はデフォルト値
        features['Type_encoded'] = 0
    
    # 面積
    features['Area'] = area
    features['Area_log'] = np.log1p(area)
    
    # 築年数
    features['BuildingYear'] = building_year
    
    # 築年数カテゴリのエンコーディング
    year_category = categorize_building_year(building_year)
    try:
        features['BuildingYear_category_encoded'] = models['year_encoder'].transform([year_category])[0]
    except ValueError:
        features['BuildingYear_category_encoded'] = 0
    
    # 交互作用項
    features['Area_BuildingYear_interaction'] = area * building_year
    
    return features

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "福山市不動産価格予測API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict - 価格予測",
            "health": "/health - ヘルスチェック",
            "docs": "/docs - API仕様書"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    if models is None:
        return {"status": "unhealthy", "message": "モデルが読み込まれていません"}
    return {"status": "healthy", "model": models['model_name']}

@app.post("/predict", response_model=PropertyResponse)
async def predict_price(request: PropertyRequest):
    """不動産価格を予測する"""
    
    if models is None:
        raise HTTPException(status_code=500, detail="モデルが読み込まれていません")
    
    try:
        # 入力データの前処理
        features = preprocess_input(
            request.district_name,
            request.area,
            request.building_year,
            request.property_type
        )
        
        # 特徴量をDataFrameに変換
        feature_df = pd.DataFrame([features])
        
        # 特徴量の順序を調整
        X = feature_df[models['feature_columns']]
        
        # 特徴量の標準化
        X_scaled = models['scaler'].transform(X)
        
        # 予測（対数変換された価格）
        price_log_pred = models['model'].predict(X_scaled)[0]
        
        # 元の価格に変換
        price_pred = np.expm1(price_log_pred)
        
        # 信頼度の計算（簡易版）
        confidence = "high" if 0.7 <= abs(price_log_pred) <= 2.0 else "medium" if 0.5 <= abs(price_log_pred) <= 2.5 else "low"
        
        return PropertyResponse(
            predicted_price=int(price_pred),
            predicted_price_log=float(price_log_pred),
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"予測エラー: {str(e)}")

@app.get("/districts")
async def get_districts():
    """利用可能な町名のリストを取得"""
    if models is None:
        raise HTTPException(status_code=500, detail="モデルが読み込まれていません")
    
    try:
        districts = models['district_encoder'].classes_.tolist()
        return {"districts": districts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"町名リスト取得エラー: {str(e)}")

@app.get("/property_types")
async def get_property_types():
    """利用可能な建物タイプのリストを取得"""
    if models is None:
        raise HTTPException(status_code=500, detail="モデルが読み込まれていません")
    
    try:
        types = models['type_encoder'].classes_.tolist()
        return {"property_types": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"建物タイプリスト取得エラー: {str(e)}")

# Vercel用のハンドラー
def handler(request):
    return app
