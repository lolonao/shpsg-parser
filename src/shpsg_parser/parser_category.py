"""
カテゴリページのHTMLパーサー
"""
from typing import List
import re
import json
from bs4 import BeautifulSoup
from pydantic import ValidationError

from .models import ProductBasicItem
from .parser_base import (
    ParserError,
    to_absolute_url,
    to_absolute_image_url,
    extract_price,
    extract_sold,
    extract_rating,
)


def parse_from_file(filepath: str) -> List[ProductBasicItem]:
    """
    指定されたパスのHTMLファイルを読み込み、商品情報のリストを返す。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        return parse_from_string(html_content)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ParserError(f"Error reading or parsing file {filepath}: {e}")


def _parse_item_page(soup: BeautifulSoup) -> List[ProductBasicItem]:
    """商品詳細ページのHTMLを解析する"""
    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    if not json_ld_scripts:
        return []

    product_json_ld = None
    for script in json_ld_scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                product_json_ld = next(
                    (item for item in data if item.get("@type") == "Product"), None
                )
                if product_json_ld:
                    break
            elif isinstance(data, dict) and data.get("@type") == "Product":
                product_json_ld = data
                break
        except json.JSONDecodeError:
            continue

    if not product_json_ld:
        return []

    try:
        name = product_json_ld.get("name")
        if not name:
            return []

        offers_data = product_json_ld.get("offers", {})
        if isinstance(offers_data, list):
            offers = offers_data[0] if offers_data else {}
        else:
            offers = offers_data

        price = float(offers.get("price", 0))
        currency = offers.get("priceCurrency", "SGD")

        rating_info = product_json_ld.get("aggregateRating", {})
        rating_value = rating_info.get("ratingValue")
        rating = float(rating_value) if rating_value is not None else None

        sold_count_text_elem = soup.select_one("div.aleSBU")
        sold = extract_sold(sold_count_text_elem.text) if sold_count_text_elem else 0

        product_data = {
            "product_name": name,
            "product_url": to_absolute_url(product_json_ld.get("url", "")),
            "price": price,
            "currency": currency,
            "image_url": to_absolute_image_url(product_json_ld.get("image", "")),
            "sold": sold,
            "page_type": "item",
            "rating": rating,
        }
        return [ProductBasicItem(**product_data)]
    except (KeyError, IndexError, ValidationError) as e:
        print(f"Error processing item page: {e}")
        return []


def _parse_category_page(
    soup: BeautifulSoup
) -> List[ProductBasicItem]:
    """カテゴリページのHTMLを解析する"""
    products = []
    # 商品アイテムのコンテナは 'div.col-xs-2-4' または 'li.shopee-search-item-result__item'
    item_containers = soup.select("div.col-xs-2-4, li.shopee-search-item-result__item")

    for container in item_containers:
        try:
            name_div = container.select_one("div.line-clamp-2")
            name = name_div.get_text(separator=" ", strip=True) if name_div else ""
            if not name:
                continue

            a_tag = container.find("a", href=True)
            product_url = to_absolute_url(a_tag["href"]) if a_tag else ""

            img_tag = container.find("img", alt=True)
            image_url = to_absolute_image_url(img_tag["src"]) if img_tag and img_tag.has_attr("src") else ""

            price_spans = container.select("div.flex.items-baseline span")
            price = 0.0
            if len(price_spans) > 1:
                price = extract_price(price_spans[1].text)

            rating = None
            sold = 0
            location = None

            # --- ▼▼▼ここからが最終修正箇所▼▼▼ ---
            # 複数のHTML構造パターンに対応するため、各情報を個別に探索する

            # 【レート抽出】
            # パターン1: <img alt="rating-star-full"> の隣の <div>
            rating_star_img = container.select_one('img[alt="rating-star-full"]')
            if rating_star_img:
                rating_div = rating_star_img.find_next_sibling('div')
                if rating_div:
                    rating = extract_rating(rating_div.text)

            # パターン2: <img alt="rating-star"> の隣の <span>
            if rating is None:
                rating_star_img_alt = container.select_one('img[alt="rating-star"]')
                if rating_star_img_alt:
                    rating_span = rating_star_img_alt.find_next_sibling('span')
                    if rating_span:
                        rating = extract_rating(rating_span.text)

            # 【販売数抽出】
            # "sold" または "sold/month" を含むテキストを持つdivを探す
            sold_div = container.find("div", string=re.compile(r"sold/month|sold", re.IGNORECASE))
            if sold_div:
                sold = extract_sold(sold_div.text)

            # 【配送国抽出】
            # 'location-icon' のalt属性を持つimgを探す
            location_img = container.select_one('img[alt="location-icon"]')
            if location_img:
                # 親要素からテキストを取得する方が確実な場合がある
                if location_img.parent and location_img.parent.get_text(strip=True):
                    location = location_img.parent.get_text(strip=True)
                else:
                    # 親要素がダメなら、次のspanを試す
                    location_span = location_img.find_next_sibling('span')
                    if location_span:
                        location = location_span.get_text(strip=True)

            # --- ▲▲▲ここまでが最終修正箇所▲▲▲ ---

            product_data = {
                "product_name": name,
                "product_url": product_url,
                "price": price,
                "currency": "SGD",
                "image_url": image_url,
                "sold": sold,
                "page_type": "category",
                "location": location,
            }
            # レートが取得できた場合（Noneでない場合）のみ辞書に追加する
            # これにより、Noneの場合はPydanticモデルのデフォルト値(0.0)が使用される
            if rating is not None:
                product_data['rating'] = rating

            products.append(ProductBasicItem(**product_data))
        except (ValidationError, Exception) as e:
            print(f"Error processing item '{name}': {e}")
            continue
    return products


def parse_from_string(html_content: str) -> List[ProductBasicItem]:
    """
    HTML文字列を直接解析し、商品情報のリストを返す。
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "lxml")

    if soup.select("li.shopee-search-item-result__item"):
        return _parse_category_page(soup)
    # Heuristic to detect item page. A product page has a div with a class like "page-product"
    elif soup.select_one("div.page-product"):
        return _parse_item_page(soup)

    return []
