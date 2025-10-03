"""
Pydanticモデルを定義するモジュール
"""
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class ProductBasicItem(BaseModel):
    """
    抽出した商品情報を格納するPydanticモデル
    """
    product_id: Optional[int] = Field(None, description="商品ID")
    shop_id: Optional[int] = Field(None, description="ショップID")
    shop_name: Optional[str] = Field(None, description="ショップ名")
    product_name: str = Field(..., description="商品名")
    price: float = Field(..., description="価格")
    sold: int = Field(..., description="販売数")
    rating: float = Field(0.0, description="商品の評価 (5段階、0は評価なし)")
    location: Optional[str] = Field(None, description="出荷元")
    product_url: HttpUrl = Field(..., description="商品ページのURL")
    image_url: HttpUrl = Field(..., description="商品画像のURL")
    discount: Optional[float] = Field(None, description="割引率")
    shop_type: Optional[str] = Field(None, description="ショップのタイプ (Mall, Preferred, etc.)")
    currency: str = Field(..., description="通貨 (例: SGD)")
    page_type: str = Field(..., description="解析したHTMLのページタイプ")
