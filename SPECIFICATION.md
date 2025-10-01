# 仕様書

## 1. 概要

提供されたHTMLファイルが、Shopeeのどのページタイプ（商品詳細、ショップ、カテゴリ、キーワード検索結果）に属するかを特定するロジックを実装する。

## 2. ページタイプの定義

- `PRODUCT_DETAIL`: 商品詳細ページ
- `SHOP`: ショップページ
- `CATEGORY`: カテゴリページ
- `KEYWORD_SEARCH_RESULT`: キーワード検索結果ページ
- `UNKNOWN`: 上記のいずれにも該当しないページ

## 3. ページタイプの判定ロジック

HTMLコンテンツを解析し、以下の優先順位でページタイプを判定する。

### 3.1. JSON-LD（構造化データ）による判定

HTML内に埋め込まれた `<script type="application/ld+json">` タグの内容を最優先の判定材料として使用する。JSON-LDはページの構造を明確に示しており、最も信頼性の高い情報源である。

1.  **商品詳細ページ (`PRODUCT_DETAIL`)**
    -   `"@type": "Product"` を含むJSON-LDオブジェクトが存在する場合。

2.  **ショップページ (`SHOP`)**
    -   `"@type": "Organization"` を含むJSON-LDオブジェクトが存在する場合。

3.  **カテゴリページ (`CATEGORY`)**
    -   `"@type": "BreadcrumbList"` を含むJSON-LDオブジェクトが存在し、かつURLに `/-cat.` のパターンが含まれる場合。
    -   `"@type": "Product"` が主要なエンティティとして定義されていないことを確認する。

4.  **キーワード検索結果ページ (`KEYWORD_SEARCH_RESULT`)**
    -   `"@type": "ItemList"` を含むJSON-LDオブジェクトが存在する場合。
    -   カテゴリページと区別するため、URLに `/search` のパターンが含まれることを確認する。

### 3.2. URLパターンによる判定（フォールバック）

JSON-LDが存在しない、または解析に失敗した場合の補助的な判定ロジックとしてURLパターンを使用する。

1.  **商品詳細ページ (`PRODUCT_DETAIL`)**
    -   URLのパスに `-i.{shop_id}.{item_id}` のパターンが含まれる場合。（例: `/product-i.12345.67890`）

2.  **ショップページ (`SHOP`)**
    -   URLのパスがショップのユーザー名と一致する場合。（例: `/shopusername`）

3.  **カテゴリページ (`CATEGORY`)**
    -   URLのパスに `/{category-name}-cat.{category_id}` のパターンが含まれる場合。

4.  **キーワード検索結果ページ (`KEYWORD_SEARCH_RESULT`)**
    -   URLのパスに `/search` が含まれ、`keyword=` のクエリパラメータが存在する場合。

### 3.3. 不明なページ

上記のいずれの条件にも一致しない場合は `UNKNOWN` として扱う。これには、エラーページ、予期せぬ構造のページ、またはHTML以外のファイルが含まれる。

## 4. 実装詳細

- Pythonの `BeautifulSoup` ライブラリを使用してHTMLを解析する。
- `json` ライブラリを使用してJSON-LDの内容を解析する。
- ページタイプは `enum` を使用して定義し、コードの可読性と保守性を高める。
- URLの解析にはPythonの `urllib.parse` モジュールを利用する。
- 判定ロジックは `get_page_type(html_content: str, url: str) -> PageType` のような関数にカプセル化する。

## 5. カテゴリページのパーサー仕様

カテゴリページから商品情報を抽出する際の仕様を定義する。

### 5.1. 商品情報コンテナ

- 各商品情報は、`li.shopee-search-item-result__item` または `div.h-full.duration-100...` (より具体的なTailwind CSSクラスを持つdiv) 内に存在する。

### 5.2. 抽出項目とセレクタ

各商品コンテナから以下の情報を抽出する。

- **商品名 (`product_name`)**:
    - セレクタ: `div.line-clamp-2`
    - 取得方法: 要素のテキストを取得する。

- **商品URL (`product_url`)**:
    - セレクタ: `a` タグ
    - 取得方法: `href` 属性の値を取得し、絶対URLに変換する。

- **画像URL (`image_url`)**:
    - セレクタ: `img` タグ
    - 取得方法: `src` 属性の値を取得し、絶対URLに変換する。

- **価格 (`price`)**:
    - セレクタ: `div.flex.items-baseline span`
    - 取得方法: 2番目の`span`要素のテキストから数値を抽出する。

- **レート (`rating`)**:
    - 新しいセレクタ: `div.flex.items-center.space-x-1.min-w-0` 内の `span`
    - 取得方法: `img[alt="rating-star"]` を持つ要素の兄弟`span`のテキストから浮動小数点数を抽出する。見つからない場合は `None` とする。
    - 備考: 新しいHTML構造に対応する。

- **販売数 (`sold`)**:
    - 新しいセレクタ: `div.flex.items-center.space-x-1.min-w-0` 内の `div`
    - 取得方法: "Sold/Month" または "sold/month" を含むテキストから数値を抽出する。見つからない場合は `0` とする。
    - 備考: 新しいHTML構造に対応する。

- **配送国 (`location`)**:
    - 新しいセレクタ: `img[alt="location-icon"]` を持つ要素の親要素のテキスト
    - 取得方法: `location-icon` の`alt`属性を持つ`img`タグを探し、その親要素のテキストを取得する。見つからない場合は `None` とする。
