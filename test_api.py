#!/usr/bin/env python3
"""
不動産価格予測APIのテストスクリプト
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health():
    """ヘルスチェックのテスト"""
    print("=== ヘルスチェックテスト ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_districts():
    """町名一覧取得のテスト"""
    print("\n=== 町名一覧テスト ===")
    try:
        response = requests.get(f"{API_BASE_URL}/districts")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"町名数: {len(data['districts'])}")
        print(f"最初の5つの町名: {data['districts'][:5]}")
        return response.status_code == 200
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_property_types():
    """建物タイプ一覧取得のテスト"""
    print("\n=== 建物タイプ一覧テスト ===")
    try:
        response = requests.get(f"{API_BASE_URL}/property_types")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"建物タイプ数: {len(data['property_types'])}")
        print(f"建物タイプ: {data['property_types']}")
        return response.status_code == 200
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_predict():
    """価格予測のテスト"""
    print("\n=== 価格予測テスト ===")
    
    test_cases = [
        {
            "district_name": "曙町",
            "area": 100.0,
            "building_year": 5,
            "property_type": "宅地(土地と建物)"
        },
        {
            "district_name": "曙町",
            "area": 200.0,
            "building_year": 0,
            "property_type": "宅地(土地)"
        },
        {
            "district_name": "曙町",
            "area": 50.0,
            "building_year": 20,
            "property_type": "中古マンション等"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        print(f"入力: {test_case}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"予測価格: {result['predicted_price']:,}円")
                print(f"信頼度: {result['confidence']}")
            else:
                print(f"エラー: {response.text}")
                
        except Exception as e:
            print(f"エラー: {e}")

def main():
    """メイン処理"""
    print("不動産価格予測APIのテストを開始します...")
    print(f"API URL: {API_BASE_URL}")
    
    # APIサーバーが起動するまで待機
    print("\nAPIサーバーの起動を待機中...")
    for i in range(30):  # 最大30秒待機
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("APIサーバーが起動しました！")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("APIサーバーが起動しませんでした。先にpython main.pyを実行してください。")
        return
    
    # テスト実行
    tests = [
        test_health,
        test_districts,
        test_property_types,
        test_predict
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"テストエラー: {e}")
    
    print(f"\n=== テスト結果 ===")
    print(f"成功: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("すべてのテストが成功しました！")
    else:
        print("一部のテストが失敗しました。")

if __name__ == "__main__":
    main()
