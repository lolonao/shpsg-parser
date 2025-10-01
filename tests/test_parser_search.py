import pytest
from pathlib import Path
from shpsg_parser.parser_search import parse_from_file, parse_from_string
from shpsg_parser.models import ProductBasicItem

SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
SEARCH_HTML_PATH = SAMPLES_DIR / "keyword_search_result_sample.html"

def test_parse_search_page_from_file():
    """T-S01: `parse_from_file` がキーワード検索結果ページを正しく解析することを確認する"""
    assert SEARCH_HTML_PATH.exists(), f"テスト用のHTMLファイルが見つかりません: {SEARCH_HTML_PATH}"
    products = parse_from_file(str(SEARCH_HTML_PATH))

    assert isinstance(products, list)
    assert len(products) == 60

    first_item = products[0]
    assert isinstance(first_item, ProductBasicItem)
    assert "MegaHouse, Look Up Series, Demon Slayer" in first_item.product_name
    assert first_item.price > 50.0
    assert first_item.sold == 3 # 販売数を正確に検証
    assert first_item.rating == 5.0 # レートを検証
    assert first_item.page_type == "search"
    assert str(first_item.product_url).startswith("https://shopee.sg")
    assert first_item.location == "Japan"

def test_image_url_is_absolute_on_search_page():
    """T-010: 検索結果ページのimage_urlが常に絶対URLであることを検証する"""
    results = parse_from_file(str(SEARCH_HTML_PATH))
    assert len(results) > 0
    for item in results:
        assert str(item.image_url).startswith("https://")

def test_parse_from_string_search_page():
    """`parse_from_string` がキーワード検索結果ページを正しく解析することを確認する"""
    html_content = SEARCH_HTML_PATH.read_text(encoding="utf-8")
    results = parse_from_string(html_content)
    assert isinstance(results, list)
    assert len(results) == 60
    assert results[0].page_type == "search"
