"""
キーワード検索結果ページのHTMLパーサー
"""
from typing import List
import re
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

def _parse_search_page_by_scraping(soup: BeautifulSoup) -> List[ProductBasicItem]:
    """
    BeautifulSoupを使用してキーワード検索結果ページをスクレイピングする。
    """
    products = []
    item_containers = soup.select('li.shopee-search-item-result__item')

    for container in item_containers:
        if not isinstance(container, Tag):
            continue

        try:
            name_div = container.select_one('div.line-clamp-2')
            name = name_div.get_text(strip=True) if name_div else ''
            if not name:
                continue

            a_tag = container.find('a', href=True)
            product_url = to_absolute_url(a_tag['href']) if a_tag else ''

            shop_id, product_id = extract_ids_from_url(product_url)

            img_tag = container.select_one('img[src]')
            image_url = to_absolute_image_url(img_tag['src']) if img_tag and img_tag.has_attr('src') else ''

            price = 0.0
            price_dollar_span = container.find("span", string="$")
            if price_dollar_span:
                price_value_span = price_dollar_span.find_next_sibling("span")
                if price_value_span:
                    price = extract_price(price_value_span.text)

            if price == 0.0:
                price_div = container.select_one("div[class*='_3_FVSo']")
                if price_div:
                    price = extract_price(price_div.text)

            rating = None
            sold = 0
            location = None

            # 複数のHTML構造パターンに対応するため、各情報を個別に探索する

            # 【レート抽出】
            rating_star_img = container.select_one('img[alt="rating-star-full"]')
            if rating_star_img:
                rating_div = rating_star_img.find_next_sibling('div')
                if rating_div:
                    rating = extract_rating(rating_div.text)

            if rating is None:
                rating_star_img_alt = container.select_one('img[alt="rating-star"]')
                if rating_star_img_alt:
                    rating_span = rating_star_img_alt.find_next_sibling('span')
                    if rating_span:
                        rating = extract_rating(rating_span.text)

            # 【販売数抽出】
            sold_div = container.find("div", string=re.compile(r"sold/month|sold", re.IGNORECASE))
            if sold_div:
                sold = extract_sold(sold_div.text)

            # 【配送国抽出】
            location_img = container.select_one('img[alt="location-icon"]')
            if location_img:
                if location_img.parent and location_img.parent.get_text(strip=True):
                    location = location_img.parent.get_text(strip=True)
                else:
                    location_span = location_img.find_next_sibling('span')
                    if location_span:
                        location = location_span.get_text(strip=True)

            product_data = {
                "product_id": product_id,
                "shop_id": shop_id,
                "product_name": name,
                "product_url": product_url,
                "price": price,
                "currency": "SGD",
                "image_url": image_url,
                "sold": sold,
                "page_type": "search",
                "location": location,
            }
            # レートが取得できた場合（Noneでない場合）のみ辞書に追加する
            if rating is not None:
                product_data['rating'] = rating

            products.append(ProductBasicItem(**product_data))
        except (ValidationError, Exception) as e:
            print(f"Error processing item '{name}': {e}")
            continue

    return products

def parse_from_string(html_content: str) -> List[ProductBasicItem]:
    """
    キーワード検索結果ページのHTML文字列を解析し、商品情報のリストを返す。
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    products = _parse_search_page_by_scraping(soup)
    return products
