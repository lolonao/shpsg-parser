"""
商品詳細ページ用のPydanticモデルを定義するモジュール
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class ProductRating(BaseModel):
    """
    個別の商品レビュー情報を格納するPydanticモデル
    """
    username: Optional[str] = Field(None, description="レビュー投稿者のユーザー名")
    rating_stars: int = Field(..., description="レビューの星の数 (1-5)")
    timestamp: Optional[str] = Field(None, description="レビュー投稿日時")
    variation: Optional[str] = Field(None, description="購入した商品のバリエーション")
    comment: Optional[str] = Field(None, description="レビューのコメント本文")

class ShippingInfo(BaseModel):
    """
    配送情報を格納するPydanticモデル
    """
    guarantee_text: Optional[str] = Field(None, description="配送保証に関する文言")
    cost_text: Optional[str] = Field(None, description="配送料に関する文言")
    late_arrival_voucher_text: Optional[str] = Field(None, description="配送遅延時のバウチャーに関する文言")

class ProductDetailItem(BaseModel):
    """
    商品詳細ページから抽出した情報を格納するPydanticモデル。
    既存のProductBasicItemとは独立しており、より詳細な情報を含む。
    """
    # 基本情報
    product_id: str = Field(..., description="プラットフォーム固有の商品ID")
    product_name: str = Field(..., description="商品名")
    product_description: str = Field(..., description="商品の説明文")
    price: float = Field(..., description="現在の販売価格")
    original_price: Optional[float] = Field(None, description="割引前の元価格")
    currency: str = Field("SGD", description="価格の通貨")
    product_url: HttpUrl = Field(..., description="商品ページの正規URL")
    image_urls: List[HttpUrl] = Field(..., description="商品画像のURLリスト")
    quantity: Optional[int] = Field(None, description="利用可能な在庫数")

    # 評価情報
    rating: Optional[float] = Field(None, description="商品の平均評価 (5段階)")
    rating_count: Optional[int] = Field(None, description="評価の総数")
    sold: Optional[int] = Field(None, description="販売数")
    detailed_ratings: List[ProductRating] = Field([], description="詳細な商品レビューのリスト")

    # ショップ情報
    shop_id: str = Field(..., description="ショップのID")
    shop_name: str = Field(..., description="ショップ名")
    shop_url: Optional[HttpUrl] = Field(None, description="ショップページのURL")
    shop_vouchers: List[Dict[str, Any]] = Field([], description="ショップバウチャーのリスト（サンプルにないため現時点では空）")

    # 仕様とバリエーション
    specifications: Dict[str, str] = Field({}, description="商品の仕様（例: {'ブランド': 'X', '在庫': '123'}）")
    variations: List[Dict[str, Any]] = Field([], description="商品のバリエーション（例: [{'name': 'Mサイズ', 'price': 10.0}]）")

    # その他
    shipping_info: Optional[ShippingInfo] = Field(None, description="配送情報")
    shopping_guarantee: Optional[str] = Field(None, description="ショッピング保証（例: 15-Day Free Returns）")
    page_type: str = Field("product_detail", description="解析したHTMLのページタイプ（固定）")
