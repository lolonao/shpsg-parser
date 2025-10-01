"""
パーサーモジュール間で共有される基本機能やヘルパー関数を定義するモジュール
"""
import re
import os
from urllib.parse import urljoin
from typing import Optional

BASE_URL = "https://shopee.sg"

class ParserError(Exception):
    """
    解析中に回復不能なエラーが発生した場合に送出されるカスタム例外
    """
    pass

def to_absolute_url(url: str) -> str:
    """
    相対URLを絶対URLに変換する。
    既に絶対URLの場合はそのまま返す。
    """
    if not url or url.startswith('http'):
        return url
    return urljoin(BASE_URL, url)

def to_absolute_image_url(url: str) -> str:
    """
    画像用の相対URLを絶対URLに変換する。
    ファイル名をそのまま結合する。
    """
    if not url or url.startswith('http'):
        return url

    # Extract filename from path
    filename = os.path.basename(url)

    # Remove thumbnail suffix `_tn` if it exists
    if filename.endswith('_tn.webp'):
        filename = filename.replace('_tn.webp', '.webp')
    elif filename.endswith('_tn'):
        filename = filename[:-3]

    return f"https://down-sg.img.susercontent.com/file/{filename}"

def extract_price(price_str: str) -> float:
    """価格文字列から数値のみを抽出する"""
    if not price_str:
        return 0.0
    # " - " で区切られている範囲価格の場合、低い方の価格を取得
    price_str = price_str.split('-')[0].strip()
    match = re.search(r'[\d,.]+', price_str)
    if match:
        return float(match.group(0).replace(',', ''))
    return 0.0

def extract_sold(sold_str: str) -> int:
    """販売数文字列から数値を抽出する"""
    if not sold_str:
        return 0

    value_str = sold_str.lower().replace('sold/month', '').replace('sold', '').strip()
    multiplier = 1

    if 'k' in value_str:
        multiplier = 1000
        value_str = value_str.replace('k', '').strip()
    elif 'm' in value_str:
        multiplier = 1000000
        value_str = value_str.replace('m', '').strip()

    try:
        numeric_part = re.search(r'[\d.]+', value_str)
        if numeric_part:
            return int(float(numeric_part.group(0)) * multiplier)
    except (ValueError, TypeError):
        return 0
    return 0


def extract_rating(rating_str: Optional[str]) -> Optional[float]:
    """
    評価文字列から評価値を抽出し、浮動小数点数として返す。
    抽出できない場合はNoneを返す。
    """
    if not rating_str:
        return None

    # 正規表現で数値（小数を含む）を検索
    match = re.search(r'[\d.]+', rating_str)
    if match:
        try:
            # 抽出した文字列を浮動小数点数に変換
            return float(match.group(0))
        except (ValueError, TypeError):
            # 変換に失敗した場合はNoneを返す
            return None

    return None
