import pytest
from shpsg_parser.parser_base import (
    to_absolute_url,
    extract_price,
    extract_sold,
    BASE_URL,
)

def test_to_absolute_url():
    """to_absolute_url関数のテスト"""
    # 既に絶対URLの場合
    assert to_absolute_url("https://example.com/page") == "https://example.com/page"
    # 相対URLの場合
    assert to_absolute_url("/product/123") == f"{BASE_URL}/product/123"
    # 空の場合
    assert to_absolute_url("") == ""
    # Noneの場合
    assert to_absolute_url(None) is None

def test_extract_price():
    """extract_price関数のテスト"""
    assert extract_price("$27.25") == 27.25
    assert extract_price("1,234.56") == 1234.56
    assert extract_price("Price: 500") == 500.0
    assert extract_price("10.00 - 20.00") == 10.00 # 範囲価格
    assert extract_price("No price here") == 0.0
    assert extract_price("") == 0.0
    assert extract_price(None) == 0.0

def test_extract_sold():
    """extract_sold関数のテスト"""
    assert extract_sold("10 sold") == 10
    assert extract_sold("1.2k sold") == 1200
    assert extract_sold("5.6K sold/month") == 5600
    assert extract_sold("1m sold") == 1000000
    assert extract_sold("2M sold") == 2000000
    assert extract_sold("No sales") == 0
    assert extract_sold("") == 0
    assert extract_sold(None) == 0
