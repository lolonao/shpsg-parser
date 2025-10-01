import enum
import json
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class PageType(enum.Enum):
    PRODUCT_DETAIL = "product_detail"
    SHOP = "shop"
    CATEGORY = "category"
    KEYWORD_SEARCH_RESULT = "keyword_search_result"
    UNKNOWN = "unknown"


def get_page_type(html_content: str, url: str) -> PageType:
    """
    Identifies the page type from the given HTML content and URL.
    The logic prioritizes distinct URL patterns first to disambiguate pages
    that might share JSON-LD types (e.g., Product and Category pages).

    Args:
        html_content: The HTML content of the page.
        url: The URL of the page.

    Returns:
        The identified page type.
    """
    if not html_content or not url:
        return PageType.UNKNOWN

    # 1. URL based identification (Primary for distinct patterns)
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path

        # Product: /...-i.{shop_id}.{item_id} (most specific)
        if "-i." in path and path.split('-i.')[-1].count('.') == 1:
            return PageType.PRODUCT_DETAIL

        # Category: /...-cat.{cat_id}
        if "-cat." in path:
            return PageType.CATEGORY

        # Search: /search?keyword=...
        if "/search" in path:
            return PageType.KEYWORD_SEARCH_RESULT

    except Exception:
        # Fall through to JSON-LD if URL parsing fails
        pass

    # 2. JSON-LD based identification (Primary for Shop, fallback for others)
    soup = BeautifulSoup(html_content, "html.parser")
    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "Organization":
                return PageType.SHOP
        except (json.JSONDecodeError, TypeError):
            continue

    # 3. Fallback URL check for shop pages with simple paths
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        # A simple path with one segment is likely a shop page.
        path_segments = path.strip('/').split('/')
        if len(path_segments) == 1 and path_segments[0]:
            # Exclude common non-shop paths
            if path_segments[0] not in ['cart', 'checkout', 'user', 'buyer', 'seller', 'search', 'mall', 'product', 'category', 'live', 'blog', 'events3']:
                 return PageType.SHOP
    except Exception:
        pass


    return PageType.UNKNOWN
