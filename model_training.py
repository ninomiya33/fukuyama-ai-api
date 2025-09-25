import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import joblib
import warnings
warnings.filterwarnings('ignore')

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    特徴量エンジニアリングを行う
    """
    print("特徴量エンジニアリング中...")
    
    # コピーを作成
    df_features = df.copy()
    
    # 1. 町名のエンコーディング
    le_district = LabelEncoder()
    df_features['DistrictName_encoded'] = le_district.fit_transform(df_features['DistrictName'])
    
    # 2. 建物タイプのエンコーディング
    le_type = LabelEncoder()
    df_features['Type_encoded'] = le_type.fit_transform(df_features['Type'])
    
    # 3. 面積の対数変換（価格との関係を線形に近づける）
    df_features['Area_log'] = np.log1p(df_features['Area'])
    
    # 4. 築年数のカテゴリ化
    def categorize_building_year(year):
        if year == 0:
            return 'new'  # 新築
        elif year <= 5:
            return 'very_new'  # 築5年以内
        elif year <= 10:
            return 'new'  # 築10年以内
        elif year <= 20:
            return 'medium'  # 築20年以内
        elif year <= 30:
            return 'old'  # 築30年以内
        else:
            return 'very_old'  # 築30年超
    
    df_features['BuildingYear_category'] = df_features['BuildingYear'].apply(categorize_building_year)
    le_year = LabelEncoder()
    df_features['BuildingYear_category_encoded'] = le_year.fit_transform(df_features['BuildingYear_category'])
    
    # 5. 面積と築年数の交互作用項
    df_features['Area_BuildingYear_interaction'] = df_features['Area'] * df_features['BuildingYear']
    
    # 6. 価格の対数変換（ターゲット変数）
    df_features['TradePrice_log'] = np.log1p(df_features['TradePrice'])
    
    # エンコーダーを保存
    joblib.dump(le_district, 'label_encoders/district_encoder.pkl')
    joblib.dump(le_type, 'label_encoders/type_encoder.pkl')
    joblib.dump(le_year, 'label_encoders/year_encoder.pkl')
    
    print(f"特徴量作成完了。特徴量数: {df_features.shape[1]}")
    
    return df_features

def train_models(X_train, X_test, y_train, y_test):
    """
    複数のモデルを学習・評価する
    """
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=0.1),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{name} を学習中...")
        
        # モデル学習
        model.fit(X_train, y_train)
        
        # 予測
        y_pred = model.predict(X_test)
        
        # 評価指標計算
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # クロスバリデーション
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        
        results[name] = {
            'model': model,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        
        print(f"R² Score: {r2:.4f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        print(f"CV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return results

def select_best_model(results):
    """
    最良のモデルを選択する
    """
    best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
    best_model = results[best_model_name]['model']
    
    print(f"\n最良のモデル: {best_model_name}")
    print(f"R² Score: {results[best_model_name]['r2']:.4f}")
    
    return best_model_name, best_model

def main():
    """
    メイン処理
    """
    print("=== 不動産価格予測モデル学習 ===")
    
    # データ読み込み
    try:
        df = pd.read_csv('preprocessed_data.csv')
        print(f"データ読み込み完了: {len(df)} レコード")
    except FileNotFoundError:
        print("前処理済みデータが見つかりません。先にdata_preprocessing.pyを実行してください。")
        return
    
    # 特徴量作成
    df_features = create_features(df)
    
    # 特徴量とターゲットの分離
    feature_columns = [
        'DistrictName_encoded', 'Type_encoded', 'Area', 'Area_log', 
        'BuildingYear', 'BuildingYear_category_encoded', 'Area_BuildingYear_interaction'
    ]
    
    X = df_features[feature_columns]
    y = df_features['TradePrice_log']  # 対数変換した価格
    
    print(f"特徴量数: {X.shape[1]}")
    print(f"サンプル数: {X.shape[0]}")
    
    # 訓練・テストデータの分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"訓練データ: {X_train.shape[0]} サンプル")
    print(f"テストデータ: {X_test.shape[0]} サンプル")
    
    # 特徴量の標準化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # スケーラーを保存
    joblib.dump(scaler, 'models/scaler.pkl')
    
    # モデル学習・評価
    results = train_models(X_train_scaled, X_test_scaled, y_train, y_test)
    
    # 最良のモデルを選択
    best_model_name, best_model = select_best_model(results)
    
    # 最良のモデルを保存
    joblib.dump(best_model, 'models/best_model.pkl')
    
    # 結果を保存
    model_info = {
        'best_model_name': best_model_name,
        'feature_columns': feature_columns,
        'results': {name: {k: v for k, v in result.items() if k != 'model'} 
                   for name, result in results.items()}
    }
    
    joblib.dump(model_info, 'models/model_info.pkl')
    
    print(f"\nモデル学習完了！")
    print(f"最良のモデル: {best_model_name}")
    print(f"モデルファイル: models/best_model.pkl")
    print(f"スケーラーファイル: models/scaler.pkl")
    print(f"エンコーダーファイル: label_encoders/")

if __name__ == "__main__":
    # 必要なディレクトリを作成
    import os
    os.makedirs('models', exist_ok=True)
    os.makedirs('label_encoders', exist_ok=True)
    
    main()
