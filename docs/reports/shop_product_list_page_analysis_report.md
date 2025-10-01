# Shopeeシンガポール ショップ別商品リストページ分析レポート (shop_sample.html)

## 1. 概要 (Overview)

- **対象ファイル (Target Files)**:
  - Image: `data/samples/shop_sample.png`
  - HTML: `data/samples/shop_sample.html`
- **ページタイプ (Page Type)**:
  - 分析の結果、これは`nobistar.sg`という特定の**ショップページ (shop)**であることが確認された。

## 2. 画像分析 (Image Analysis)

- **ページレイアウト (Page Layout)**:
  - ヘッダーにショップ情報、左側にカテゴリリスト、中央に商品リストが表示される典型的なショップページの構成。
  - メインの商品リストはグリッドレイアウトで表示され、ページネーション機能を持つ。
- **商品カードの構成要素 (Product Card Components)**:
  - 各商品カードには以下の情報が含まれていることを視覚的に確認した。
    - 商品画像
    - 商品名
    - 価格 (例: `$27.25`)
    - 販売数 (例: `10 sold`)
    - 評価 (星の数と評価件数、例: `4.0`, `10 sold`)
    - "Mall"や"Preferred"のようなショップタイプを示す特別なバッジは見当たらないため、ショップタイプは `Normal` と判断できる。
    - 発送元は商品カードには表示されていない。

## 3. HTML分析 (HTML Analysis)

### 3.1. JSON-LD

- ページ内には複数の `application/ld+json` スクリプトが埋め込まれている。
  - `@type: "WebSite"`: サイト全体の情報。
  - `@type: "BreadcrumbList"`: パンくずリスト情報。
  - `@type: "Organization"`: ショップ情報 (`nobistar.sg`)。
  - `@type: "Product"`: **表示されている商品のうち1件**の情報が含まれている。
- **結論**: JSON-LDは一部の商品の情報しか含まないため、全商品リストの抽出にはHTMLの直接スクレイピングが必須となる。

### 3.2. スクレイピングのためのCSSセレクタ (CSS Selectors for Scraping)

- **商品アイテムコンテナ (Item Container)**:
  - `div.shop-search-result-view__item`
  - このコンテナが、個々の商品カード全体をラップしている。
- **商品URL (Product URL)**:
  - アイテムコンテナ内の `a` タグの `href` 属性。
- **商品名 (Product Name)**:
  - `div.line-clamp-2` (アイテムコンテナ内の子孫要素)。テキストコンテンツが商品名に相当する。
- **画像URL (Image URL)**:
  - アイテムコンテナ内の `img` タグの `src` 属性。セレクタは `img.inset-y-0` などが利用可能。
- **価格 (Price)**:
  - `div.truncate.flex.items-baseline` 内の `span` 要素。通貨記号 `$` と価格 `27.25` が別々の `span` に分かれている場合があるため、親要素からテキストをまとめて取得し、数値部分を抽出する必要がある。
- **販売数 (Sold Count)**:
  - `div.truncate.text-shopee-black87.text-xs`。 `10 sold` のようにテキストが含まれるため、数値部分を抽出する後処理が必要。
- **評価 (Rating)**:
  - `div[style*="background-color: rgb(255, 248, 228)"]` のようなスタイルを持つdiv内の `span`。評価値テキストが含まれる。セレクタは不安定な可能性があるため、`div.flex.items-center.space-x-1.min-w-0` のような構造的なセレクタも検討する。

## 4. 結論と今後の実装方針 (Conclusion and Future Implementation Policy)

- **抽出戦略**: 主にCSSセレクタを用いたスクレイピングで情報を抽出する。クラス名が複雑で自動生成されている可能性が高いため、DOM構造（親子関係）やテキスト内容（"sold"など）を組み合わせた、より堅牢なセレクタの設計が求められる。
- **ページタイプ判定**: このページはショップページであるため、`page_type`には`shop`を格納する。URLにショップ名が含まれていること (`shopee.sg/nobistar.sg`) や、ページの `title` タグの内容から判定が可能。
- **データの後処理**: 価格や販売数のように、テキストから特定の数値や単位を抽出する後処理が必要となる。
- **実装**: 上記の分析に基づき、`shpsg_parser`にこのパターンのショップページを解析するためのロジックを追加する。
