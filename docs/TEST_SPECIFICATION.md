# テスト仕様書

## 1. 概要

`page_type_identifier` モジュールの `get_page_type` 関数が、仕様書通りに正しくページタイプを判定できることを確認するためのテストを定義する。

## 2. テスト対象

- `page_type_identifier.get_page_type(html_content: str, url: str)` 関数

## 3. テスト環境

- Python 3.x
- `pytest` フレームワーク

## 4. テストケース

### 4.1. 正常系テスト：サンプルHTMLファイル

提供された4つのサンプルHTMLファイルを使用して、各ページタイプが正しく判定されることを確認する。

| テストケースID | テスト内容 | 入力ファイル | 期待される返り値 |
| :--- | :--- | :--- | :--- |
| TC-001 | 商品詳細ページの判定 | `product_detail_sample.html` | `PageType.PRODUCT_DETAIL` |
| TC-002 | ショップページの判定 | `shop_sample.html` | `PageType.SHOP` |
| TC-003 | カテゴリページの判定 | `category_sample.html` | `PageType.CATEGORY` |
| TC-004 | キーワード検索結果ページの判定 | `keyword_search_result_sample.html` | `PageType.KEYWORD_SEARCH_RESULT`|

### 4.2. 異常系テスト

予期せぬ入力に対して、関数が適切に `PageType.UNKNOWN` を返すか、またはエラーを発生させずに処理を完了できることを確認する。

| テストケースID | テスト内容 | 入力 | 期待される返り値 |
| :--- | :--- | :--- | :--- |
| TC-005 | 空のHTMLコンテンツ | `html_content=""`, `url="http://example.com"` | `PageType.UNKNOWN` |
| TC-006 | JSON-LDを含まないHTML | 判定ロジックに合致しないHTML | `PageType.UNKNOWN` |
| TC-007 | 破損したJSON-LD | 不正な形式のJSONデータを含むHTML | `PageType.UNKNOWN` |
| TC-008 | HTMLではないプレーンテキスト | `html_content="This is a test."` | `PageType.UNKNOWN` |
| TC-009 | URL情報がない場合 | `url=None` または `url=""` | `PageType.UNKNOWN`（URLに依存するロジックが正しくフォールバックすることを確認） |

## 5. テストの実施方法

- `pytest` を使用してテストを自動実行する。
- テスト用のHTMLファイルは `data/samples/` ディレクトリから読み込む。
- 各テストケースは独立したテスト関数として実装する。
- `assert` 文を使用して、`get_page_type` の返り値が期待通りであることを検証する。

## 6. カテゴリページパーサーのテスト仕様

### 6.1. テスト対象
- `parser_category.parse_from_file`
- `parser_category.parse_from_string`

### 6.2. テストデータ
- `data/samples/category_sample.html`

### 6.3. 検証項目

`category_sample.html` を入力として、以下の項目を検証する。

1.  **抽出件数**:
    - HTML内に存在するすべての商品アイテムが、`ProductBasicItem` オブジェクトのリストとして返されることを確認する。

2.  **各項目の正確性**:
    - リストの先頭、中間、末尾のアイテムをサンプリングし、各フィールドが正しく抽出されていることを検証する。
    - **レート (`rating`)**:
        - 期待される浮動小数点数が正しく抽出されていること。
        - レート情報が存在しない商品では `None` が設定されていること。
    - **販売数 (`sold`)**:
        - "k" や "m" を含む文字列（例: `1.2k sold`）が正しく整数に変換されていること。
        - 販売数情報が存在しない商品では `0` が設定されていること。
    - **配送国 (`location`)**:
        - "Japan", "Singapore" などの文字列が正しく抽出されていること。
        - 配送国情報が存在しない商品では `None` が設定されていること。
    - **リグレッション防止**:
        - 商品名、価格、URLなどの既存項目が、変更後も正しく抽出されていることを確認する。
