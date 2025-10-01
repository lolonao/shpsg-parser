"""
商品詳細ページパーサー (`parser_product`) のテスト
"""
import pytest
from pathlib import Path
from pydantic import HttpUrl

# TDD: Implement tests before the actual parser module exists.
# These imports will fail until the files are created.
from shpsg_parser.models_product import ProductDetailItem
from shpsg_parser.parser_product import parse_from_file, parse_from_string, ParserError

# --- テスト用のフィクスチャ ---

@pytest.fixture
def product_detail_html_path() -> str:
    """正常な商品詳細ページのサンプルHTMLファイルへのパスを返す"""
    return "data/samples/product_detail_sample.html"

@pytest.fixture
def product_detail_html_content(product_detail_html_path: str) -> str:
    """正常な商品詳細ページのHTMLコンテンツを返す"""
    with open(product_detail_html_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def category_page_html_content() -> str:
    """カテゴリページのHTMLコンテンツを返す"""
    with open("data/samples/category_sample.html", "r", encoding="utf-8") as f:
        return f.read()

# --- 正常系テスト (T-011, T-012, T-013) ---

def test_parse_from_file_success(product_detail_html_path: str):
    """
    T-011: `parse_from_file` が正常な商品詳細HTMLを正しく解析することを確認する
    """
    item = parse_from_file(product_detail_html_path)

    assert item is not None
    assert isinstance(item, ProductDetailItem)

    # --- JSON-LDから取得すべき主要な値の検証 ---
    assert item.product_id == "19445913336"
    assert item.product_name == "Dr. Scholl Medi Qtto  Outside Sheer Stockings Nature Nude ★Direct From Japan★"
    assert item.price == 27.25
    assert item.currency == "SGD"
    assert item.rating == 4.0
    assert item.rating_count == 1
    assert item.shop_name == "nobistar.sg"
    assert item.page_type == "product_detail"

    # --- HTMLから補完的に取得する値の検証 ---
    assert item.sold == 10

    # --- URLとリストの検証 ---
    assert isinstance(item.product_url, HttpUrl)
    assert "i.672907573.19445913336" in str(item.product_url)
    assert isinstance(item.image_urls, list)
    assert len(item.image_urls) > 0
    assert isinstance(item.image_urls[0], HttpUrl)

    # --- 辞書とリスト形式のフィールドの検証 ---
    assert isinstance(item.specifications, dict)
    assert item.specifications.get("Country of Origin") == "Japan"
    assert item.specifications.get("Stock") == "10"

    assert isinstance(item.variations, list)
    assert len(item.variations) > 0

    # --- 新しく追加されたフィールドの検証 ---
    assert item.quantity == 10
    assert item.shopping_guarantee == "15-Day Free Returns"

    assert item.shipping_info is not None
    assert item.shipping_info.cost_text == "Free shipping"
    assert "Guaranteed to get by" in item.shipping_info.guarantee_text

    assert len(item.detailed_ratings) == 1
    rating = item.detailed_ratings[0]
    assert rating.username == "ahyan1989"
    assert rating.rating_stars == 4
    assert rating.variation == "L Size"
    assert rating.comment is None


def test_parse_from_string_success(product_detail_html_content: str):
    """
    T-012: `parse_from_string` が正常な商品詳細HTMLを正しく解析することを確認する
    """
    item = parse_from_string(product_detail_html_content)

    # Assertions are the same as in test_parse_from_file_success
    assert item is not None
    assert isinstance(item, ProductDetailItem)
    assert item.product_id == "19445913336"
    assert item.price == 27.25
    assert item.sold == 10

# T-013 (データ型の検証) はPydanticモデルのインスタンス化が成功することで暗黙的に検証される

# --- 異常系・エッジケーステスト (T-014, T-015, T-016) ---

def test_parse_file_not_found():
    """
    T-014: 存在しないファイルを指定した場合に FileNotFoundError が発生することを確認する
    """
    with pytest.raises(FileNotFoundError):
        parse_from_file("non_existent_file.html")

def test_parse_invalid_html():
    """
    T-015: 不正なHTMLコンテンツを渡した際にNoneが返されることを確認する
    """
    assert parse_from_string("this is not valid html") is None

def test_parse_non_product_page(category_page_html_content: str):
    """
    T-016: 商品情報を含まないHTML（カテゴリページ）を渡した際にNoneが返されることを確認する
    """
    assert parse_from_string(category_page_html_content) is None
