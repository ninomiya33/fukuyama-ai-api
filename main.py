#!/usr/bin/env python3
"""
不動産価格予測システムのメインスクリプト
データ前処理 → モデル学習 → API起動の一連の流れを実行
"""

import os
import sys
import subprocess
import time

def run_script(script_name, description):
    """Pythonスクリプトを実行する"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """メイン処理"""
    print("不動産価格予測システムを開始します...")
    
    # 必要なディレクトリを作成
    os.makedirs('models', exist_ok=True)
    os.makedirs('label_encoders', exist_ok=True)
    
    # 1. データ前処理
    if not run_script('data_preprocessing.py', 'データ前処理を実行中...'):
        print("データ前処理に失敗しました。終了します。")
        return
    
    # 2. モデル学習
    if not run_script('model_training.py', 'モデル学習を実行中...'):
        print("モデル学習に失敗しました。終了します。")
        return
    
    print("\n" + "="*50)
    print("学習完了！APIサーバーを起動します...")
    print("="*50)
    print("APIドキュメント: http://localhost:8000/docs")
    print("価格予測エンドポイント: http://localhost:8000/predict")
    print("終了するには Ctrl+C を押してください")
    print("="*50)
    
    # 3. APIサーバー起動
    try:
        subprocess.run([sys.executable, 'api.py'])
    except KeyboardInterrupt:
        print("\n\nAPIサーバーを停止しました。")

if __name__ == "__main__":
    main()
