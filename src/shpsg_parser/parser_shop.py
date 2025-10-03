"""
ショップページのHTMLパーサー
"""
from typing import List
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from pydantic import ValidationError

from .models import ProductBasicItem
from .parser_base import (
    ParserError,
    to_absolute_url,
    to_absolute_image_url,
    extract_price,
    extract_sold,
    extract_rating,
    extract_ids_from_url,
    extract_shop_name_from_url,
)


def parse_from_file(filepath: str) -> List[ProductBasicItem]:
    """
    指定されたパスのHTMLファイルを読み込み、商品情報のリストを返す。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return parse_from_string(html_content)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ParserError(f"Error reading or parsing file {filepath}: {e}")

def _parse_shop_page(soup: BeautifulSoup) -> List[ProductBasicItem]:
    """
    BeautifulSoupを使用してショップページをスクレイピングする。
    """
    products = []
    # ショップページの商品コンテナセレクタ
    item_containers = soup.select('div.shop-search-result-view__item')

    # canonical URLからショップ名を取得
    canonical_link = soup.find("link", {"rel": "canonical"})
    shop_url = canonical_link['href'] if canonical_link and canonical_link.has_attr('href') else ''
    shop_name = extract_shop_name_from_url(shop_url)

    # ショップの配送国はページ全体で共通の可能性が高いため、最初に一度だけ取得する
    location = None
    location_div = soup.select_one('div.shop-page-shop-description > span')
    if location_div and "Japan" in location_div.get_text():
         location = "Japan"

    for container in item_containers:
        if not isinstance(container, Tag):
            continue

        try:
            a_tag = container.find('a', href=True)
            if not a_tag:
                continue
            product_url = to_absolute_url(a_tag['href'])
            shop_id, product_id = extract_ids_from_url(product_url)

            name_div = a_tag.select_one('div.line-clamp-2')
            name = name_div.get_text(strip=True) if name_div else ''
            if not name:
                continue

            img_tag = a_tag.select_one('img.inset-y-0')
            image_url = to_absolute_image_url(img_tag['src']) if img_tag and img_tag.has_attr('src') else ''

            price_container = a_tag.select_one('div.truncate.flex.items-baseline')
            price = extract_price(price_container.text) if price_container else 0.0

            rating = None
            sold = 0

            # 【レート抽出】ショップページのHTML構造に合わせる
            rating_star_img = container.select_one('img[alt="rating-star"]')
            if rating_star_img:
                rating_span = rating_star_img.find_next_sibling('span')
                if rating_span:
                    rating = extract_rating(rating_span.text)

            # 【販売数抽出】
            sold_div = container.find("div", string=re.compile(r" sold$")) # "10 sold" のような形式
            if sold_div:
                sold = extract_sold(sold_div.text)

            product_data = {
                "product_id": product_id,
                "shop_id": shop_id,
                "shop_name": shop_name,
                "product_name": name,
                "product_url": product_url,
                "price": price,
                "currency": "SGD",
                "image_url": image_url,
                "sold": sold,
                "location": location, # 最初に取得した共通のlocationを設定
                "page_type": "shop",
            }
            if rating is not None:
                product_data['rating'] = rating
            products.append(ProductBasicItem(**product_data))
        except (ValidationError, Exception) as e:
            print(f"Error processing a shop item '{name}': {e}")
            continue

    return products

def parse_from_string(html_content: str) -> List[ProductBasicItem]:
    """
    ショップページのHTML文字列を解析し、商品情報のリストを返す。
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')

    # Check if it's a shop page
    if soup.select_one('div.shop-search-result-view'):
        return _parse_shop_page(soup)

    return []
