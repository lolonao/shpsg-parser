"""
商品詳細ページのHTMLパーサー
"""
from typing import Optional, List, Dict, Any
import extruct
from bs4 import BeautifulSoup
from pydantic import ValidationError, HttpUrl

from .models_product import ProductDetailItem, ProductRating, ShippingInfo
from .parser_base import ParserError, to_absolute_url

def _extract_shipping_info(soup: BeautifulSoup) -> Optional[ShippingInfo]:
    """配送情報を抽出し、ShippingInfoオブジェクトとして返す"""
    shipping_container = soup.select_one("section.flex.KIoPj6.lkKD9l")
    if not shipping_container:
        return None

    guarantee_text = shipping_container.select_one("div.O3NAB1 > span")
    cost_text = shipping_container.select_one("div.O3NAB1.zRFiFo > span")
    voucher_text = shipping_container.select_one("div.O3NAB1.onPwxQ")

    return ShippingInfo(
        guarantee_text=guarantee_text.get_text(strip=True) if guarantee_text else None,
        cost_text=cost_text.get_text(strip=True) if cost_text else None,
        late_arrival_voucher_text=voucher_text.get_text(strip=True) if voucher_text else None,
    )

def _extract_detailed_ratings(soup: BeautifulSoup) -> List[ProductRating]:
    """詳細な商品レビューを抽出し、ProductRatingオブジェクトのリストとして返す"""
    ratings = []
    rating_elements = soup.select("div.shopee-product-comment-list > div.q2b7Oq")
    for elem in rating_elements:
        try:
            username = elem.select_one("a.InK5kS")
            # 星の数は、塗りつぶされた星アイコンの数で判断
            stars = len(elem.select("svg.shopee-svg-icon.YBGCRA.icon-rating-solid"))

            ts_var_elem = elem.select_one("div.j5ucs4 > div.XYk98l")
            timestamp = None
            variation = None
            if ts_var_elem:
                parts = ts_var_elem.get_text(strip=True).split('|')
                if len(parts) > 0:
                    timestamp = parts[0].strip()
                if len(parts) > 1:
                    variation = parts[1].replace("Variation:", "").strip()

            # コメント本文は特定のクラスを持つことが多い。このサンプルには存在しない。
            # 存在しないことを前提とした、より具体的なセレクタにすることで、誤って他のテキストを取得することを防ぐ。
            comment_elem = elem.select_one("div.shopee-product-rating__content")

            ratings.append(ProductRating(
                username=username.get_text(strip=True) if username else None,
                rating_stars=stars,
                timestamp=timestamp,
                variation=variation,
                comment=comment_elem.get_text(strip=True) if comment_elem else None,
            ))
        except Exception:
            continue
    return ratings

def _extract_specifications(soup: BeautifulSoup) -> Dict[str, str]:
    """商品仕様を抽出し、辞書として返す"""
    specs = {}
    spec_rows = soup.select("div.product-detail div.Gf4Ro0 > div.ybxj32")
    for row in spec_rows:
        try:
            key_element = row.find("h3", class_="VJOnTD")
            # The value is the text content of the div that is a sibling to the h3
            value_element = key_element.find_next_sibling("div")
            if key_element and value_element:
                key = key_element.get_text(strip=True)
                value = value_element.get_text(strip=True)
                if key and value:
                    specs[key] = value
        except AttributeError:
            continue
    return specs

def _extract_variations(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """商品のバリエーションを抽出し、辞書のリストとして返す"""
    variations = []
    # Find all buttons that represent a variation
    variation_buttons = soup.select("div.j7HL5Q button.sApkZm")
    for button in variation_buttons:
        try:
            name = button.get_text(strip=True)
            # Check if the variation is available (not disabled)
            is_available = not button.has_attr('aria-disabled') or button['aria-disabled'] == 'false'

            variation_data = {
                "name": name,
                "available": is_available
            }
            variations.append(variation_data)
        except Exception:
            continue
    return variations


def parse_from_string(html_content: str) -> Optional[ProductDetailItem]:
    """
    HTML文字列を直接解析し、商品情報の詳細を返す。
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "lxml")

    # 1. extructでJSON-LDデータを抽出
    try:
        data = extruct.extract(html_content, syntaxes=['json-ld'], uniform=True)
        product_data_list = [item for item in data.get('json-ld', []) if item.get('@type') == 'Product']
        if not product_data_list:
            # print("DEBUG: No JSON-LD product data found.")
            return None
        json_ld = product_data_list[0]
        # print(f"DEBUG: Found JSON-LD: {json_ld}")
    except Exception as e:
        # print(f"DEBUG: extruct failed: {e}")
        return None # extructが失敗した場合

    try:
        # 2. JSON-LDから基本情報を取得
        offers = json_ld.get("offers")
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        elif offers is None:
            offers = {}

        aggregate_rating = json_ld.get("aggregateRating", {})
        seller = offers.get("seller", {})

        # 3. BeautifulSoupで補完情報をスクレイピング
        sold_element = soup.select_one("div.mnzVGI")
        sold_count = None
        if sold_element:
            sold_count_text = sold_element.get_text(strip=True)
            if "sold" in sold_count_text.lower():
                sold_count = int("".join(filter(str.isdigit, sold_count_text)))

        shop_url_element = soup.select_one("div.page-product__shop a.lG5Xxv")
        shop_url = to_absolute_url(shop_url_element['href']) if shop_url_element else None

        # shop_idは商品URLから抽出するのが最も確実
        product_url_str = json_ld.get("url", "")
        shop_id = None
        if "-i." in product_url_str:
            parts = product_url_str.split('-i.')[-1].split('.')
            if len(parts) >= 2:
                shop_id = parts[0]

        # 画像URLの抽出ロジックを修正
        # 1. JSON-LDからメイン画像を取得
        main_image_url = json_ld.get("image")

        image_urls = []
        if main_image_url and isinstance(main_image_url, str):
            image_urls.append(main_image_url)

        # 2. HTMLから追加のサムネイル画像を取得
        thumbnail_urls = [img['src'] for img in soup.select("div.airUhU img.raRnQV") if img.get('src')]

        # すべてのURLを絶対パスに変換し、重複を排除して追加
        for url in thumbnail_urls:
            abs_url = to_absolute_url(url)
            if abs_url not in image_urls:
                image_urls.append(abs_url)

        quantity_element = soup.select_one("section.flex.items-center.OaFP0p > div > div:nth-of-type(2)")
        quantity = None
        if quantity_element:
            quantity_text = quantity_element.get_text(strip=True)
            quantity_parts = quantity_text.split()
            if len(quantity_parts) > 0 and quantity_parts[0].isdigit():
                quantity = int(quantity_parts[0])

        shopping_guarantee_element = soup.select_one("div._GVeNA > div.tUagTH")
        shopping_guarantee = shopping_guarantee_element.get_text(strip=True) if shopping_guarantee_element else None


        # 4. ProductDetailItemモデルにマッピング
        item = ProductDetailItem(
            product_id=json_ld.get("productID"),
            product_name=json_ld.get("name"),
            product_description=json_ld.get("description"),
            price=float(offers.get("price")) if offers.get("price") else None,
            original_price=None, # サンプルに元価格がないためNone
            currency=offers.get("priceCurrency"),
            product_url=HttpUrl(product_url_str),
            image_urls=[HttpUrl(url) for url in image_urls],
            quantity=quantity,
            rating=float(aggregate_rating.get("ratingValue")) if aggregate_rating.get("ratingValue") else None,
            rating_count=int(aggregate_rating.get("ratingCount")) if aggregate_rating.get("ratingCount") else None,
            sold=sold_count,
            detailed_ratings=_extract_detailed_ratings(soup),
            shop_id=shop_id,
            shop_name=seller.get("name"),
            shop_url=HttpUrl(shop_url) if shop_url else None,
            specifications=_extract_specifications(soup),
            variations=_extract_variations(soup),
            shipping_info=_extract_shipping_info(soup),
            shopping_guarantee=shopping_guarantee,
        )
        return item

    except (ValidationError, KeyError, TypeError, AttributeError, ValueError) as e:
        # Pydanticのバリデーションエラーやキーエラーは、構造が期待と異なることを示す
        # この場合、製品ページではないか、構造が大幅に変更された可能性があるためNoneを返す
        # import traceback
        # print(f"DEBUG: Parsing failed in the final block: {e}")
        # print(traceback.format_exc())
        return None


def parse_from_file(filepath: str) -> Optional[ProductDetailItem]:
    """
    指定されたパスのHTMLファイルを読み込み、商品情報の詳細を返す。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        return parse_from_string(html_content)
    except FileNotFoundError:
        raise
    except Exception as e:
        # 読み込みやその他の予期せぬエラー
        raise ParserError(f"Error reading or parsing file {filepath}: {e}")
