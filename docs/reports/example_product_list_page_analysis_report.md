# Shopeeシンガポール ショップ別商品リストページ分析レポート

## 1. 概要 (Overview)

- **対象ファイル (Target Files)**:
  - Image: `data/samples/sample.png`
  - HTML: `data/samples/sample_tem.html`
- **ページタイプ (Page Type)**:
  - 分析の結果、これは`nobistar.sg`という特定の**ショップページ (shop)**であることが確認された。

## 2. 画像分析 (Image Analysis)

- **ページレイアウト (Page Layout)**:
  - ヘッダーにショップ情報、左側にカテゴリリスト、中央に商品リストが表示される典型的なショップページの構成。
  - 「Recommended For You」「Best Price」など、複数の商品推薦セクションが存在する。
  - メインの商品リストはグリッドレイアウトで表示され、ページネーション機能を持つ。
- **商品カードの構成要素 (Product Card Components)**:
  - 各商品カードには以下の情報が含まれていることを視覚的に確認した。
    - 商品画像
    - 商品名
    - 価格 (例: `$27.25`)
    - 販売数 (例: `10 sold`)
    - 評価 (星の数と評価件数)
    - 発送元は商品カードには表示されていない。

## 3. HTML分析 (HTML Analysis)

### 3.1. JSON-LD

- ページ内には複数の `application/ld+json` スクリプトが埋め込まれている。
  - `@type: "WebSite"`: サイト全体の情報。
  - `@type: "BreadcrumbList"`: パンくずリスト情報。
  - `@type: "Organization"`: ショップ情報 (`nobistar.sg`)。
  - `@type: "Product"`: **表示されている商品のうち1件**の情報が含まれている。`name`, `url`, `image`, `aggregateRating` などが取得可能。
- **結論**: JSON-LDは一部の商品の情報しか含まないため、全商品リストの抽出には不向き。HTMLの直接スクレイピングを主軸とする。

### 3.2. スクレイピングのためのCSSセレクタ (CSS Selectors for Scraping)

- **商品アイテムコンテナ (Item Container)**:
  - `div.shop-search-result-view__item`
- **商品URL (Product URL)**:
  - `a`タグ (コンテナ全体をラップしている) の `href` 属性
- **商品名 (Product Name)**:
  - `div.line-clamp-2` (アイテムコンテナ内の子孫要素)
- **画像URL (Image URL)**:
  - `img` タグの `src` 属性。 `div[style*="padding-top: 100%"] > img` のようなセレクタで特定可能。
- **価格 (Price)**:
  - `div` > `span` > `span`。 `$` と価格が別の `span` に分かれているため、親要素から両方の子要素を取得する必要がある。具体的なセレクタは `div.truncate.flex.items-baseline > span`。
- **販売数 (Sold Count)**:
  - `div.truncate.text-shopee-black87.text-xs`。`10 sold` のようにテキストが含まれるため、数値部分を抽出する後処理が必要。
- **評価 (Rating)**:
  - `div[style*="background-color: rgb(255, 248, 228)"] > span`。評価値と評価件数が含まれる。

## 4. 結論と今後の実装方針 (Conclusion and Future Implementation Policy)

- **抽出戦略**: 主にCSSセレクタを用いたスクレイピングで情報を抽出する。JSON-LDは補助的な情報源として、またはフォールバックとして利用を検討する。
- **ページタイプ判定**: このページはショップページであるため、`page_type`には`shop`を格納する。URLにショップ名が含まれていること(`shopee.sg/nobistar.sg`)を判定基準とすることができる。
- **堅牢性**: クラス名は変更される可能性を考慮し、テキスト内容（"sold"など）やDOM構造（親子関係）を組み合わせたセレクタを用いることで、パーサーの堅牢性を高める。
- **実装**: 上記の分析に基づき、`shpsg_parser`にショップページ用の解析ロジックを追加する。
