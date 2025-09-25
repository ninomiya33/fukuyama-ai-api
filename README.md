# 不動産価格予測API

福山市の不動産取引データを使用して、町名・面積・築年数から価格を予測する機械学習APIです。

## 機能

- **価格予測**: 町名、面積、築年数から不動産価格を予測
- **RESTful API**: FastAPIを使用したWeb API
- **複数モデル**: 線形回帰、ランダムフォレスト、勾配ブースティングなど
- **自動選択**: 最適なモデルを自動選択

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. データの準備

`2024年福山市の取引情報（土地） - シート1 (1).csv` ファイルがプロジェクトルートに配置されていることを確認してください。

### 3. 実行

```bash
python main.py
```

または、個別に実行する場合：

```bash
# データ前処理
python data_preprocessing.py

# モデル学習
python model_training.py

# API起動
python api.py
```

## API仕様

### エンドポイント

- `GET /` - ルート情報
- `GET /health` - ヘルスチェック
- `POST /predict` - 価格予測
- `GET /districts` - 利用可能な町名一覧
- `GET /property_types` - 利用可能な建物タイプ一覧

### 価格予測リクエスト

```json
{
  "district_name": "曙町",
  "area": 100.0,
  "building_year": 5,
  "property_type": "宅地(土地と建物)"
}
```

### 価格予測レスポンス

```json
{
  "predicted_price": 25000000,
  "predicted_price_log": 17.03,
  "confidence": "high"
}
```

## 使用例

### cURLでのAPI呼び出し

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "district_name": "曙町",
       "area": 100.0,
       "building_year": 5,
       "property_type": "宅地(土地と建物)"
     }'
```

### PythonでのAPI呼び出し

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "district_name": "曙町",
        "area": 100.0,
        "building_year": 5,
        "property_type": "宅地(土地と建物)"
    }
)

result = response.json()
print(f"予測価格: {result['predicted_price']:,}円")
```

## ファイル構成

```
不動産API/
├── main.py                          # メイン実行スクリプト
├── data_preprocessing.py            # データ前処理
├── model_training.py               # モデル学習
├── api.py                          # FastAPIアプリケーション
├── requirements.txt                # 依存関係
├── README.md                       # このファイル
├── preprocessed_data.csv           # 前処理済みデータ（生成される）
├── models/                         # 学習済みモデル（生成される）
│   ├── best_model.pkl
│   ├── scaler.pkl
│   └── model_info.pkl
└── label_encoders/                 # エンコーダー（生成される）
    ├── district_encoder.pkl
    ├── type_encoder.pkl
    └── year_encoder.pkl
```

## 特徴量

- **町名**: ラベルエンコーディング
- **面積**: 数値特徴量（対数変換も含む）
- **築年数**: 数値特徴量（カテゴリ化も含む）
- **建物タイプ**: ラベルエンコーディング
- **交互作用項**: 面積×築年数

## モデル

以下のモデルを比較し、最適なものを自動選択：

- Linear Regression
- Ridge Regression
- Lasso Regression
- Random Forest
- Gradient Boosting

## 注意事項

- データは福山市の2024年第1四半期の取引情報に基づいています
- 予測精度は学習データの品質と量に依存します
- 実際の不動産取引では、より多くの要因を考慮する必要があります

## ライセンス

このプロジェクトは教育・研究目的で作成されています。
