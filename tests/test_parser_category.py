import pytest
from pathlib import Path
from shpsg_parser.parser_category import (
    parse_from_file,
    parse_from_string,
)
from shpsg_parser.models import ProductBasicItem

SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
CATEGORY_HTML_PATH = SAMPLES_DIR / "category_sample.html"
ITEM_HTML_PATH = SAMPLES_DIR / "product_detail_sample.html"
NON_EXISTENT_FILE_PATH = SAMPLES_DIR / "non_existent_file.html"

def test_parse_from_file_category_page():
    """T-001: `parse_from_file` がカテゴリページのHTMLを正しく解析し、全項目を抽出できることを確認する"""
    results = parse_from_file(str(CATEGORY_HTML_PATH))
    assert isinstance(results, list)
    # サンプルファイルには60個の商品が含まれている
    assert len(results) == 60

    # 1番目のアイテムを詳細にチェック
    first_item = results[0]
    assert isinstance(first_item, ProductBasicItem)
    assert "AdPower 2 pieces Car Static suppression sheet" in first_item.product_name
    assert first_item.price == 63.60
    assert first_item.sold == 18
    assert first_item.rating == 4.9
    assert first_item.page_type == "category"
    assert str(first_item.product_url).startswith("https://shopee.sg")
    assert str(first_item.image_url).startswith("https://")
    assert first_item.location == "Japan"

    # 4番目のアイテム（レートあり、販売数あり）をチェック
    fourth_item = results[3]
    assert "[Direct from Japan] [Set of 6] John's Blend Air Freshener" in fourth_item.product_name
    assert fourth_item.price == 26.71
    assert fourth_item.sold == 4
    assert fourth_item.rating == 4.7
    assert fourth_item.location == "Japan"

    # 14番目のアイテム（レートなし）をチェック
    # この商品はレート情報を持たないため、ratingが0.0であることを確認する
    item_with_no_rating = results[13]
    assert "[authentic product]\nTrust Radiator Cap" in item_with_no_rating.product_name
    assert item_with_no_rating.rating == 0.0
    assert item_with_no_rating.sold == 2
    assert item_with_no_rating.location == "Japan"

def test_parse_from_string_category_page():
    """T-002: `parse_from_string` がカテゴリページのHTML文字列を正しく解析することを確認する"""
    html_content = CATEGORY_HTML_PATH.read_text(encoding="utf-8")
    results = parse_from_string(html_content)
    assert isinstance(results, list)
    assert len(results) == 60 # アイテム数が正しいか

    first_item = results[0]
    assert isinstance(first_item, ProductBasicItem)
    assert "AdPower 2 pieces Car Static suppression sheet" in first_item.product_name
    assert first_item.rating == 4.9
    assert first_item.sold == 18
    assert first_item.location == "Japan"

def test_parse_from_file_item_page():
    """T-008: `parse_from_file` が商品詳細ページのHTMLを正しく解析することを確認する"""
    results = parse_from_file(str(ITEM_HTML_PATH))
    assert isinstance(results, list)
    assert len(results) == 1

    item = results[0]
    assert isinstance(item, ProductBasicItem)
    assert "Dr. Scholl Medi Qtto" in item.product_name
    assert item.price == 27.25
    assert item.sold > 0
    assert item.page_type == "item"
    assert str(item.product_url).startswith("https://shopee.sg")
    assert str(item.image_url).startswith("https://")

def test_image_url_is_absolute():
    """T-010: image_urlが常に絶対URLであることを検証する"""
    results = parse_from_file(str(CATEGORY_HTML_PATH))
    for item in results:
        assert str(item.image_url).startswith("https://")

def test_parse_from_file_not_found():
    """T-004: 存在しないファイルを指定した場合に `FileNotFoundError` が発生することを確認する"""
    with pytest.raises(FileNotFoundError):
        parse_from_file(str(NON_EXISTENT_FILE_PATH))

def test_parse_from_string_invalid_html():
    """T-005: 不正なHTMLを渡した際に空のリストが返ることを確認する"""
    result = parse_from_string("This is not valid HTML.")
    assert result == []

def test_parse_from_string_empty_html():
    """T-006: 商品情報を含まないHTMLを渡した際に空のリストが返ることを確認する"""
    result = parse_from_string("<html><body></body></html>")
    assert result == []
