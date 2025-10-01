import pytest
import os
from shpsg_parser.page_type_identifier import get_page_type, PageType

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'samples')

def load_sample(filename):
    """Helper function to load a sample HTML file."""
    with open(os.path.join(SAMPLES_DIR, filename), 'r', encoding='utf-8') as f:
        return f.read()

# URLs extracted from the saved from comments in the sample files
URLS = {
    "product_detail_sample.html": "https://shopee.sg/Dr.-Scholl-Medi-Qtto-Outside-Sheer-Stockings-Nature-Nude-%E2%98%85Direct-From-Japan%E2%98%85-i.672907573.19445913336",
    "shop_sample.html": "https://shopee.sg/nobistar.sg",
    "category_sample.html": "https://shopee.sg/Ankle-socks-cat.11012819.11012954.11012956",
    "keyword_search_result_sample.html": "https://shopee.sg/search?keyword=direct+from+japan+demon+slayer+figure"
}

@pytest.mark.parametrize("filename, expected_type", [
    ("product_detail_sample.html", PageType.PRODUCT_DETAIL),
    ("shop_sample.html", PageType.SHOP),
    ("category_sample.html", PageType.CATEGORY),
    ("keyword_search_result_sample.html", PageType.KEYWORD_SEARCH_RESULT),
])
def test_get_page_type_with_samples(filename, expected_type):
    """Tests the get_page_type function with the provided sample HTML files."""
    html_content = load_sample(filename)
    url = URLS[filename]
    assert get_page_type(html_content, url) == expected_type

def test_get_page_type_unknown_html():
    """Tests with a generic HTML that doesn't match any criteria."""
    html_content = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
    url = "http://example.com/some/path"
    assert get_page_type(html_content, url) == PageType.UNKNOWN

def test_get_page_type_empty_content():
    """Tests with empty HTML content."""
    assert get_page_type("", "http://example.com") == PageType.UNKNOWN

def test_get_page_type_no_url():
    """Tests with no URL provided."""
    html_content = load_sample("product_detail_sample.html")
    assert get_page_type(html_content, "") == PageType.UNKNOWN

def test_get_page_type_plain_text():
    """Tests with non-HTML plain text."""
    assert get_page_type("this is not html", "http://example.com") == PageType.UNKNOWN

def test_get_page_type_broken_json_ld():
    """Tests with malformed JSON-LD, relying on URL fallback."""
    html_content = """
    <html>
      <head>
        <script type="application/ld+json">
          {"@type": "Product", "name": "Test"  // Missing closing brace
        </script>
      </head>
      <body>Product page</body>
    </html>
    """
    # Fallback to URL should still identify it as a product page
    url = "https://shopee.sg/Test-Product-i.123.456"
    assert get_page_type(html_content, url) == PageType.PRODUCT_DETAIL
