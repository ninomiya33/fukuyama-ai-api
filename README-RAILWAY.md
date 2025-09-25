# 不動産価格予測API - Railwayデプロイ版

## Railwayでのデプロイ方法（推奨）

### 1. 前提条件
- GitHubアカウント
- Railwayアカウント（[railway.app](https://railway.app)）
- 学習済みモデルファイル

### 2. デプロイ手順

1. **GitHubにプッシュ**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Railwayでデプロイ**
   - [Railway](https://railway.app)にログイン
   - "New Project"をクリック
   - "Deploy from GitHub repo"を選択
   - リポジトリを選択
   - 自動的にデプロイが開始されます

3. **環境変数の設定（必要に応じて）**
   - Railwayダッシュボードでプロジェクトを選択
   - Variables タブで環境変数を設定

### 3. 利点

- **ファイルサイズ制限**: より緩い制限
- **実行時間制限**: なし
- **メモリ制限**: より多くのメモリ
- **永続化**: ファイルシステムが永続化される
- **簡単**: 設定ファイルだけでデプロイ可能

### 4. デプロイ後の確認

デプロイが完了すると、以下のようなURLが提供されます：
```
https://your-project-name.up.railway.app
```

### 5. APIエンドポイント

- `https://your-project-name.up.railway.app/` - ルート情報
- `https://your-project-name.up.railway.app/health` - ヘルスチェック
- `https://your-project-name.up.railway.app/predict` - 価格予測
- `https://your-project-name.up.railway.app/districts` - 町名一覧
- `https://your-project-name.up.railway.app/property_types` - 建物タイプ一覧
- `https://your-project-name.up.railway.app/docs` - API仕様書

### 6. 使用例

```bash
# 価格予測
curl -X POST "https://your-project-name.up.railway.app/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "district_name": "曙町",
       "area": 100.0,
       "building_year": 5,
       "property_type": "宅地(土地と建物)"
     }'
```

### 7. 料金

- **無料プラン**: 月500時間、512MB RAM
- **Proプラン**: $5/月、無制限時間、8GB RAM

### 8. トラブルシューティング

#### デプロイが失敗する場合
1. ログを確認
2. 依存関係が正しくインストールされているか確認
3. モデルファイルが存在するか確認

#### メモリ不足の場合
1. より軽量なモデルを使用
2. Proプランにアップグレード

### 9. その他のPaaS選択肢

- **Render**: 無料プランでより多くのリソース
- **Heroku**: 定番のPaaS（有料）
- **Fly.io**: 軽量で高速
- **DigitalOcean App Platform**: シンプルで安価
