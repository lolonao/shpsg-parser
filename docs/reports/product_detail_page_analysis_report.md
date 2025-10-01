# Shopeeシンガポール 商品詳細ページ分析レポート

## 1. 概要 (Overview)

- **対象ファイル (Target Files)**:
  - Image: `data/samples/product_detail_sample.png`
  - HTML: `data/samples/product_detail_sample.html`
- **ページタイプ (Page Type)**:
  - 分析の結果、これは単一の**商品詳細ページ (product_detail)**であることが確認された。

## 2. 画像分析 (Image Analysis)

- **ページレイアウト (Page Layout)**:
  - 左側に商品画像ギャラリー、中央に商品名、価格、評価、配送情報などの主要情報、右側にショップ情報が配置されている。
  - ページ下部には、商品説明、商品仕様、商品レビューのセクションが存在する。
- **主要な構成要素 (Key Components)**:
  - スクリーンショットから、以下の情報が視覚的に確認できた。
    - 商品画像（メイン画像とサムネイル）
    - 商品名: `Dr. Scholl Medi Qtto Outside Sheer Stockings...`
    - 評価: `4.0` スター、`1 rating`
    - 販売数: `10 Sold`
    - 価格: `$27.25`
    - サイズ選択: `M Size` / `L Size`
    - 数量選択
    - 商品仕様: カテゴリ、在庫、原産国（Japan）など
    - 商品説明

## 3. HTML分析 (HTML Analysis)

### 3.1. JSON-LD

- ページ内には、`@type: "Product"` を持つ `application/ld+json` スクリプトが1つ埋め込まれている。
- このJSON-LDには、以下の必須データが構造化された形式で含まれており、データ抽出の**主要な情報源**として利用すべきである。
  - `name` (商品名)
  - `description` (商品説明)
  - `url` (商品URL)
  - `image` (画像URL)
  - `offers.price` (価格)
  - `offers.priceCurrency` (通貨)
  - `aggregateRating.ratingValue` (評価)
  - `aggregateRating.ratingCount` (評価数)
- **結論**: ほとんどの重要データがJSON-LDから取得可能。`extruct`ライブラリの使用を強く推奨する。

### 3.2. スクレイピングのためのCSSセレクタ (CSS Selectors for Scraping)

JSON-LDから取得できない、または補完的に取得すべき情報のためのセレクタ。

- **商品名 (Product Name)**:
  - `h1.vR6K3w`
- **価格 (Price)**:
  - `div.IZPeQz`
- **販売数 (Sold Count)**:
  - `div.mnzVGI span.AcmPRb`
  - **後処理:** テキストから数値のみを抽出し、整数型に変換する必要がある。
- **評価 (Rating)**:
  - `div.F9RHbS.dQEiAI` (評価スコア `4.0`)
  - `div.flex.e2p50f > div.F9RHbS` (評価数 `1`)
- **出荷元 (Location / Ships From)**:
  - **XPath:** `//div[h3[text()='Ships From']]/div`
  - **説明:** 「Product Specifications」セクション内の「Ships From」ヘッダーに続く`div`要素からテキストを取得。
- **画像URL (Image URL)**:
  - `picture > source[type="image/webp"]` の `srcset` 属性から最初のURLを取得するのが望ましい。
- **ショップタイプ (Shop Type)**:
  - HTML内に明確なテキストやクラス名が存在しない。仕様書通り、これは画像バッジ（例: Mall, Preferred）の有無で判定する必要がある可能性が高い。存在しない場合は `Normal` または `None` とする。
- **ディスカウント (Discount)**:
  - このサンプルには割引情報が存在しない。オプション項目であるため、該当要素が見つからない場合は `None` とする。

## 4. 結論と今後の実装方針 (Conclusion and Future Implementation Policy)

- **抽出戦略**:
  1. **JSON-LDを優先:** まず `extruct` ライブラリでJSON-LDを解析し、取得可能な全てのデータを抽出する。
  2. **HTMLスクレイピングで補完:** JSON-LDで取得できない `sold`, `location` などの情報を、特定のCSSセレクタやXPathを用いて抽出する。
- **ページタイプ判定**: このパーサーは商品詳細ページ専用であるため、`page_type` には `'product_detail'` をハードコードで設定する。URLに `-i.` が含まれることも判定基準として利用可能。
- **堅牢性**: クラス名は変更されるリスクがあるため、`h1` タグやテキスト内容 (`Ships From`など) を組み合わせた、より堅牢なセレクタを用いる設計が望ましい。
- **実装**: 上記の分析に基づき、`shpsg_parser`に商品詳細ページ用の解析ロジックを追加する。
