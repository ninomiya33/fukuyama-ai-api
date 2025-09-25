# 不動産価格予測API - Vercelデプロイ版

## Vercelでのデプロイ方法

### 1. 前提条件
- GitHubアカウント
- Vercelアカウント
- 学習済みモデルファイル（models/、label_encoders/ディレクトリ）

### 2. デプロイ手順

1. **GitHubにプッシュ**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Vercelでデプロイ**
   - [Vercel](https://vercel.com)にログイン
   - "New Project"をクリック
   - GitHubリポジトリを選択
   - フレームワーク: "Other"
   - ルートディレクトリ: そのまま
   - ビルドコマンド: 空のまま
   - 出力ディレクトリ: 空のまま

3. **環境変数の設定**
   - Vercelダッシュボードでプロジェクトを選択
   - Settings > Environment Variables
   - 必要に応じて環境変数を設定

### 3. モデルファイルのアップロード

**重要**: Vercelの無料プランではファイルサイズ制限があるため、以下の方法を推奨：

#### 方法1: 外部ストレージを使用
- Google Drive、Dropbox、AWS S3などにモデルファイルをアップロード
- アプリケーション起動時にダウンロード

#### 方法2: モデルファイルを圧縮
```bash
# モデルファイルを圧縮
tar -czf models.tar.gz models/ label_encoders/
```

#### 方法3: 軽量なモデルに変更
- より小さなモデル（例：Linear Regression）を使用
- 特徴量を削減

### 4. APIエンドポイント

デプロイ後、以下のエンドポイントが利用可能：

- `https://your-project.vercel.app/` - ルート情報
- `https://your-project.vercel.app/health` - ヘルスチェック
- `https://your-project.vercel.app/predict` - 価格予測
- `https://your-project.vercel.app/districts` - 町名一覧
- `https://your-project.vercel.app/property_types` - 建物タイプ一覧
- `https://your-project.vercel.app/docs` - API仕様書

### 5. 使用例

```bash
# 価格予測
curl -X POST "https://your-project.vercel.app/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "district_name": "曙町",
       "area": 100.0,
       "building_year": 5,
       "property_type": "宅地(土地と建物)"
     }'
```

### 6. 制限事項

- **ファイルサイズ制限**: 無料プランでは50MB
- **実行時間制限**: 無料プランでは10秒
- **メモリ制限**: 無料プランでは1024MB
- **月間リクエスト数**: 無料プランでは100GB

### 7. トラブルシューティング

#### モデルファイルが見つからない場合
```python
# api/index.py の load_models() 関数を修正
def load_models():
    try:
        # ローカルファイルを試行
        model_info = joblib.load('models/model_info.pkl')
        # ...
    except FileNotFoundError:
        # 外部ストレージからダウンロード
        import requests
        # モデルファイルをダウンロード
        # ...
```

#### メモリ不足の場合
- より軽量なモデルを使用
- 特徴量を削減
- バッチ処理を避ける

### 8. 代替案

Vercelが制限が厳しい場合は、以下の代替案を検討：

- **Railway**: より柔軟な制限
- **Render**: 無料プランでより多くのリソース
- **Heroku**: 定番のPaaS
- **AWS Lambda**: サーバーレス関数
- **Google Cloud Functions**: サーバーレス関数
