import pytest
from pathlib import Path

# Try to import the module to be tested, and skip all tests in this file if it fails.
parser_shop = pytest.importorskip("shpsg_parser.parser_shop")
ProductBasicItem = pytest.importorskip("shpsg_parser.models").ProductBasicItem

SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
SHOP_HTML_PATH = SAMPLES_DIR / "shop_sample.html"

@pytest.fixture
def products():
    """Fixture to parse the shop sample HTML and return the products."""
    return parser_shop.parse_from_file(str(SHOP_HTML_PATH))


def test_parse_shop_page_from_file(products):
    """T-009: `parse_from_file` がショップページを正しく解析することを確認する"""
    assert isinstance(products, list)
    # The sample HTML file has 30 product items.
    assert len(products) == 30

    first_item = products[0]
    assert isinstance(first_item, ProductBasicItem)
    assert first_item.page_type == "shop"

def test_first_product_data(products):
    """最初の商品のデータが正しく抽出されていることを確認する"""
    first_item = products[0]
    # Based on shop_product_list_page_analysis_report.md and manual inspection
    assert "Dr. Scholl Medi Qtto" in first_item.product_name
    assert first_item.price == 27.25
    assert first_item.sold == 10
    assert first_item.rating == 4.0
    assert first_item.location == "Japan"
    assert str(first_item.product_url).startswith("https://shopee.sg")
    assert "i.672907573.19445913336" in str(first_item.product_url)

def test_image_url_is_absolute_on_shop_page(products):
    """T-010: ショップページのimage_urlが常に絶対URLであることを検証する"""
    for item in products:
        assert str(item.image_url).startswith("https://")

def test_parse_from_string_shop_page():
    """`parse_from_string` がショップページのHTMLを正しく解析することを確認する"""
    html_content = SHOP_HTML_PATH.read_text(encoding="utf-8")
    results = parser_shop.parse_from_string(html_content)
    assert isinstance(results, list)
    assert len(results) == 30
    assert results[0].page_type == "shop"
