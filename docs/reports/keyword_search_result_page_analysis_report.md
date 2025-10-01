# Shopeeシンガポール キーワード検索結果ページ分析レポート

## 1. 概要 (Overview)

- **対象ファイル (Target Files)**:
  - Image: `data/samples/keyword_search_result_sample.png`
  - HTML: `data/samples/keyword_search_result_sample.html`
- **ページタイプ (Page Type)**:
  - 分析の結果、これは「iphone case」というキーワードの**検索結果ページ (keyword_search)**であることが確認された。

## 2. 画像分析 (Image Analysis)

- **ページレイアウト (Page Layout)**:
  - ページ上部に検索バー、左側に絞り込み用のフィルターパネル、中央に商品リストがグリッド形式で表示される、典型的な検索結果ページの構成。
  - ページ下部にはページネーション機能が存在する。
- **商品カードの構成要素 (Product Card Components)**:
  - 各商品カードには以下の情報が視覚的に含まれていることを確認した。
    - 商品画像
    - 商品名（複数行にわたる場合がある）
    - 価格 (例: `$3.99 - $5.25` のように範囲指定の場合もある)
    - 販売数 (例: `3.8k sold`)
    - 発送元 (例: `Singapore`)
    - ショップタイプ (「Mall」タグ)
    - 割引率 (「10% off」バッジ)
    - 評価 (星)

## 3. HTML分析 (HTML Analysis)

### 3.1. JSON-LD

- ページ内には、構造化データとして複数の `application/ld+json` スクリプトが埋め込まれている。
  - `@type: "WebSite"`: サイト全体の情報。
  - `@type: "ItemList"`: **ページ内に表示されている商品リストの情報**。各商品 (`itemListElement`) の `name`, `url`, `image` が含まれており、主要な情報の抽出に最適。
  - `@type: "Product"`: 商品のうち1件のみの詳細情報。`aggregateRating`（評価）などが含まれる。
- **結論**: `README.md` の推奨通り、`extruct` ライブラリを用いて `ItemList` を抽出する方法を第一優先とする。これにより、必須情報の多くを安定して取得可能。

### 3.2. スクレイピングのためのCSSセレクタ (CSS Selectors for Scraping)

JSON-LDが利用できない場合のフォールバックとして、以下のCSSセレクタを利用する。クラス名が動的に生成される傾向があるため、構造やテキスト内容を組み合わせたセレクタが望ましい。

- **商品アイテムコンテナ (Item Container)**:
  - `li.shopee-search-item-result__item`
  - 各アイテムは `<a>` タグで囲まれている。
- **商品URL (Product URL)**:
  - 上記コンテナ内の `a` タグの `href` 属性。
- **商品名 (Product Name)**:
  - `div.line-clamp-2` (アイテムコンテナ内の子孫要素)
- **画像URL (Image URL)**:
  - `div.w-full.pt-full + img` タグの `src` 属性。
- **価格 (Price)**:
  - 価格は通貨記号と数値が別の `<span>` に分かれている。`$` と `58.32` など。
  - 親要素 `div.flex.items-center` 内の `span` 要素から取得する。
- **販売数 (Sold Count)**:
  - `div.truncate.text-shopee-black87.text-xs`。`3 sold/month` のようにテキストが含まれるため、数値部分を抽出する後処理が必要。「sold/month」でのテキスト検索が堅牢。
- **評価 (Rating)**:
  - `div.flex-none.flex.items-center.space-x-0.5` 内に星の `img` と評価値の `div` が含まれる。
- **発送元 (Location)**:
  - `div` > `span.ml-[3px]`。`Japan` などのテキストが含まれる。

## 4. 結論と今後の実装方針 (Conclusion and Future Implementation Policy)

- **抽出戦略**:
  1. **Primary**: `extruct` を使用して `application/ld+json` から `ItemList` データを抽出する。
  2. **Fallback**: JSON-LDの解析に失敗した場合、または追加情報（販売数、発送元など）が必要な場合に、上記CSSセレクタを用いたスクレイピングで情報を補完する。
- **ページタイプ判定**: `h1` タグに「Search result for」の文字列が含まれるか、またはURLに `/search?keyword=` が含まれるかで `keyword_search` タイプと判定する。
- **堅牢性**: クラス名に依存しすぎず、DOM構造（親子関係）や `aria-label` 属性、テキスト内容を積極的に利用して、将来のHTML変更に対する耐性を高める。
- **実装**: 上記の分析に基づき、`shpsg_parser` にキーワード検索結果ページ用の解析ロジックを追加する。
