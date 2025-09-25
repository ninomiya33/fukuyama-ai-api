import json
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

def clean_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    データファイルを読み込んで、レコードを抽出する
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    records = []
    
    # レコードのパターンを検索（{ から }, まで）
    pattern = r'\{[^}]*\},'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        # 最後のカンマを削除
        match = match[:-1]
        
        # レコード内のキーと値を抽出
        record = {}
        
        # 行ごとに処理
        lines = match.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and line.count('"') >= 2:
                # キーと値を分離
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().strip('"')
                    value = parts[1].strip().strip('",')
                    
                    # 値のクリーンアップ
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    
                    record[key] = value
        
        if record:  # 空でないレコードのみ追加
            records.append(record)
    
    print(f"抽出したレコード数: {len(records)}")
    return records

def extract_numeric_value(value: str) -> float:
    """
    文字列から数値を抽出する
    """
    if pd.isna(value) or value == "" or value == " ":
        return np.nan
    
    # 数字のみを抽出
    numbers = re.findall(r'\d+', str(value))
    if numbers:
        return float(numbers[0])
    return np.nan

def extract_building_year(building_year: str) -> float:
    """
    築年数から年数を抽出する（2024年基準）
    """
    if pd.isna(building_year) or building_year == "" or building_year == " ":
        return np.nan
    
    # 年数を抽出
    year_match = re.search(r'(\d{4})年', str(building_year))
    if year_match:
        year = int(year_match.group(1))
        return 2024 - year  # 築年数を計算
    return np.nan

def preprocess_data(file_path: str) -> pd.DataFrame:
    """
    データの前処理を行う
    """
    print("データを読み込み中...")
    raw_data = clean_json_data(file_path)
    
    if not raw_data:
        print("データの読み込みに失敗しました")
        return pd.DataFrame()
    
    print(f"読み込んだレコード数: {len(raw_data)}")
    
    # 最初のレコードの内容を表示
    if raw_data:
        print("最初のレコードの内容:")
        print(raw_data[0])
        print("\n利用可能なキー:")
        print(list(raw_data[0].keys()))
    
    # DataFrameに変換
    df = pd.DataFrame(raw_data)
    
    # 利用可能な列を確認
    print(f"\nDataFrameの列: {list(df.columns)}")
    
    # 必要な列のみを抽出（存在する列のみ）
    available_columns = []
    required_columns = ['DistrictName', 'Area', 'BuildingYear', 'TradePrice', 'Type']
    
    for col in required_columns:
        if col in df.columns:
            available_columns.append(col)
        else:
            print(f"警告: 列 '{col}' が見つかりません")
    
    if available_columns:
        df = df[available_columns].copy()
        print(f"使用する列: {available_columns}")
    else:
        print("エラー: 必要な列が見つかりません")
        return pd.DataFrame()
    
    print("データクリーニング中...")
    
    # 数値データの変換
    df['Area'] = df['Area'].apply(extract_numeric_value)
    df['TradePrice'] = df['TradePrice'].apply(extract_numeric_value)
    df['BuildingYear'] = df['BuildingYear'].apply(extract_building_year)
    
    # 欠損値の処理
    print("欠損値の処理中...")
    initial_count = len(df)
    
    # 必要な列に欠損値がある行を削除（より緩い条件）
    df = df.dropna(subset=['DistrictName', 'TradePrice'])
    
    # 面積が欠損している場合は中央値で補完
    if 'Area' in df.columns:
        df['Area'] = df['Area'].fillna(df['Area'].median())
    
    # 築年数が欠損している場合は0（新築）として扱う
    df['BuildingYear'] = df['BuildingYear'].fillna(0)
    
    # 異常値の除去（より緩い条件）
    # 価格が0以下のものを削除
    df = df[df['TradePrice'] > 0]
    
    # 面積が0以下のものを削除
    df = df[df['Area'] > 0]
    
    # 築年数が負の値を0に修正
    df['BuildingYear'] = df['BuildingYear'].clip(lower=0)
    
    # 極端な外れ値を除去（価格が10億円を超えるもの、面積が10000㎡を超えるもの）
    df = df[df['TradePrice'] <= 1000000000]
    df = df[df['Area'] <= 10000]
    
    final_count = len(df)
    print(f"前処理後のレコード数: {final_count} (削除: {initial_count - final_count})")
    
    return df

def analyze_data(df: pd.DataFrame):
    """
    データの基本統計を表示
    """
    print("\n=== データ分析 ===")
    print(f"総レコード数: {len(df)}")
    print(f"町名の種類数: {df['DistrictName'].nunique()}")
    print(f"建物タイプの種類数: {df['Type'].nunique()}")
    
    print("\n=== 基本統計 ===")
    print(df[['Area', 'BuildingYear', 'TradePrice']].describe())
    
    print("\n=== 町名別レコード数（上位10位） ===")
    print(df['DistrictName'].value_counts().head(10))
    
    print("\n=== 建物タイプ別レコード数 ===")
    print(df['Type'].value_counts())

if __name__ == "__main__":
    # データの前処理
    file_path = "2024年福山市の取引情報（土地） - シート1 (1).csv"
    df = preprocess_data(file_path)
    
    if not df.empty:
        # データ分析
        analyze_data(df)
        
        # 前処理済みデータを保存
        df.to_csv("preprocessed_data.csv", index=False, encoding='utf-8')
        print(f"\n前処理済みデータを 'preprocessed_data.csv' に保存しました")
    else:
        print("データの前処理に失敗しました")
