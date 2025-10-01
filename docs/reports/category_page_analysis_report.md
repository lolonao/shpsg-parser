# カテゴリ別商品リストページ分析レポート

## 1. 概要 (Overview)

- **対象ファイル (Target Files)**:
  - Image: `data/samples/category_sample.png`
  - HTML: `data/samples/category_sample.html`
- **ページタイプ (Page Type)**:
  - URL (`.../Automotive-cat.11000002...`) とパンくずリストから、これは**カテゴリ別商品リスト (category)** ページであると判断できます。

## 2. 画像分析 (Image Analysis)

- **ページレイアウト (Page Layout)**:
  - 左側にカテゴリリストと絞り込みフィルター、中央に商品がグリッド形式で表示されています。
  - ヘッダーには「SHOPEE MALL」のロゴがあり、モールに出店しているショップの商品リストであることが示唆されます。
- **商品カードの構成要素 (Product Card Components)**:
  - 商品画像
  - 商品名
  - 価格（例: `$63.60`）
  - 割引率（例: `-12%`）
  - 販売数（例: `18 sold/month`）
  - 評価（星の数と評価件数）
  - 発送元（例: `Japan`）

## 3. HTML分析 (HTML Analysis)

### 3.1. JSON-LD

- ページ内に `application/ld+json` 形式のスクリプトが複数存在します。
  - `@type: "WebSite"`: サイト全体の情報。
  - `@type: "BreadcrumbList"`: パンくずリスト情報。「Shopee > Automotive」となっており、このページがカテゴリページであることを裏付けています。
  - `@type: "Product"`: ページ内の**最初の商品1件**の詳細情報が含まれています。`name`, `url`, `image`, `aggregateRating` などが取得可能です。
- **結論**: 全商品の情報を網羅していないため、メインの抽出方法としては利用できません。しかし、最初の1件のデータ取得や、他の方法が失敗した場合のフォールバックとして活用できる可能性があります。

### 3.2. スクレイピングのためのCSSセレクタ (CSS Selectors for Scraping)

- **商品アイテムのコンテナ (Item Container)**:
  - `ul.shopee-search-item-result__items > li.shopee-search-item-result__item`
  - 各 `li` 要素が1つの商品に対応します。

- **商品URL (Product URL)**:
  - アイテムコンテナ内の `a` タグの `href` 属性。

- **商品名 (Product Name)**:
  - `div.line-clamp-2` 内のテキスト。

- **画像URL (Image URL)**:
  - `img` タグの `src` 属性。 `div.relative > img` のようなセレクタで特定できます。

- **価格 (Price)**:
  - `div.truncate.flex.items-baseline` 内。
  - 通貨記号 `$` と価格 `63.60` は、それぞれ別の `span` タグに分かれています。親要素から両方の子要素を取得し、結合する必要があります。

- **販売数 (Sold Count)**:
  - `div.truncate.text-shopee-black87.text-xs` 内のテキスト（例: `18 sold/month`）。テキストから " sold/month" などの単位を除去し、数値を抽出する後処理が必要です。

- **発送元 (Location)**:
  - `div.flex-shrink.min-w-0.truncate.text-shopee-black54` 内のテキスト。

- **評価 (Rating)**:
  - `div.flex-none.flex.items-center.space-x-0.5` 内。星の画像と評価数が含まれています。`div.text-shopee-black87.text-xs` に具体的な数値（例: `4.9`）が記載されています。

## 4. 結論と今後の実装方針 (Conclusion and Future Implementation Policy)

- **抽出戦略**: 主にCSSセレクタを用いたスクレイピングで情報を抽出します。クラス名がランダムに変更される可能性を考慮し、DOM構造（親子関係）や `aria-label` 属性なども活用してセレクタの堅牢性を高めるべきです。
- **ページタイプ判定**: URLのパスに `-cat.` が含まれていることを基準に `category` と判定するのが有効そうです。
- **データの後処理**: 価格や販売数のように、抽出したテキストから不要な文字列（通貨記号、単位）を削除し、適切な型（`float`, `int`）に変換する処理が必須です。
- **実装**: 上記の分析に基づき、`shpsg_parser`にカテゴリページ用の解析ロジックを追加します。既存のパーサーとの共通点・相違点を考慮し、再利用可能なコンポーネントを設計することが望ましいです。

