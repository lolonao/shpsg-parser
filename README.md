# shpsg-parser
Shopeeシンガポールの商品一覧ページをHTMLとして保存されたファイルを解析し、商品情報を抽出するPythonライブラリ

Shopee Singapoleの商品一覧、商品詳細ページをローカルに保存したHMLファイルを解析するPythonライブラリを提供します。

StreamlitやTyperなどのフロントエンドや、FastAPIなどのバックエンドで利用されることを想定しています。


## 要件:

Shopeeシンガポールの商品リストのページを、HTMLファイルとして保存されたファイルの内容を解析し、下記の商品情報を抽出する。今回は抽出結果はCSVファイルのみとするが、次回のバージョンアップではSQLite3をサポートする予定である。
また今後、多数のHTMLの解析を行うことを前提にした、`Streamlit`と`Typer`を利用した、クライアントアプリを成果物に加えること。
`Typer`アプリでは、指定されたフォルダ以下の全ての`*.html`ファイルを対象にするオプションを用意すること。Streamlitアプリでは、複数のHTMLファイルをドラッグ&ドロップで指定できること。


動作確認、


HTMLファイルは、`./data/categories/`フォルダの中に格納されている。   
    
## 取得する情報と変数名

- 商品名
  - product_name: str 
  - 取得必須
- 商品URL
  - product_url: str 
  - 取得必須
- 価格
  - price: float
  - `$32.58`などと表示されているので、`32.58`の部分を抽出し、`float`として格納する。
  - 取得必須
- 通貨
  - currency: str
  - `$32.58`などと表示されているので、通貨記号が`$`だった場合は、`SGD`として格納する。
  - 取得必須
- 商品画像URL
  - image_url: str
  - 画像URLをCDN形式に変換する。
  - 取得必須
- 出荷元
  - location: str 
- 販売数
  - sold: int 
  - 取得必須
- ショップタイプ
  - shop_type: str 
  - ショップ（セラー）のタイプ（Mall、Preferrdなど）
    - 画像として表示されており、画像が表示されていない場合は通常ランクのショップとして認識する（ページの画像を参照）。
  - 取得はオプション（できれば取得したい）
- ページタイプ
  - page_type: str
  - 解析したページのタイプ（ショップ、キーワード検索、カテゴリー、汎用、判定不可）などを判定して格納する。
- 各フィールドの抽出でエラーが発生しても、可能な限り処理を続行する。
- 評価
  - rating: int
  - 星の数として表示されているので、星の数またはキャプションで判定
  - 取得はオプション（できれば取得したい）
- ディスカウント
  - discount: flot
  - 常に表示されているわけではない
  - 取得はオプション（できれば取得したい）

## クライアントアプリケーションの使用方法

### Streamlit Web UI

以下のコマンドでWebアプリケーションを起動します。

```bash
streamlit run streamlit_app.py
```

ブラウザで表示されたページにHTMLファイルをアップロードすると、解析結果が表示されます。

### Typer CLI

以下のコマンドでCLIツールを使用できます。

```bash
# ヘルプ表示
uv run shpsg-parser --help

# サンプルデータを解析して 'products.csv' に出力
uv run shpsg-parser products.csv
```

---

## Pydanticを積極的に使用すること
下記のように、`Pydantic` の `BaseModel` を使用して、型付きのデータクラスとして管理すること。

```python
class ProductBasicItem(BaseModel):
    product_name: str
    product_url: HttpUrl
    price: float
    image_url: Optional[HttpUrl] = None
```


## HTMLファイルの解析に関する注意点など
- 解析対象のサンプルとして、`./data/samples/categories/`フォルダの中に、HTMLファイルが格納されています。   
- 同じ場所に、当該HTMLが出力するページ画面の画像があります。解析に役立ててください。
- HTMLの中には、JSON-LD形式のデータが含まれている可能性が高いので、JSON-LD形式のデータを、`extruct`ライブラリを使用して、抽出してください。またその場合は、スクレイピングによって抽出するデータはフォールバックとして利用してください。
- Shopeeはクラス名がランダムっぽく変わることがある。→ なので、soup.select("div.something") より、soup.find("span", string="₱") みたいに テキストベースで探す 方法も有効。
- 今回は、１つ（かつ１種類）だけのサンプルHTMLが対象ですが、今後は、複数種類の構成（大体は同じだが、細かい点で異なる）のHTMLをサンプルとして提供する予定です。 HTMLの構造が１種類ではないことを考慮して、設計してください。


## プロジェクト構成

```
[project]
name = "shpsg-parser"
version = "0.1.0"
description = "Shopeeシンガポールの商品一覧、商品詳細ページをローカルに保存したHMLファイルを解析するPythonライブラリ"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "beautifulsoup4>=4.13.5",
    "extruct>=0.18.0",
    "lxml>=6.0.1",
    "pydantic>=2.11.7",
    "pyyaml>=6.0.2",
    "requests>=2.32.5",
    "streamlit>=1.49.1",
    "typer>=0.17.4",
    "types-requests>=2.32.4.20250809",
]

[dependency-groups]
dev = [
    "pyright>=1.1.405",
    "pytest>=8.4.2",
    "ruff>=0.13.0",
]
```

## その他

- `./legacy_example_codes/`以下に、商品情報を抽出するために、実験的に制作されたスクリプトがありますので、**部分的な実装の参考**にしてください。
- 最初にHTMLが出力するページの画像を認識したほうが、HTMLの構造を把握しやすいと思います。
- ドキュメントには、詳細な日本語のコメントを添えてください。
- `AGENTS.md`に書かれているように、HTMLを解析後、必ずテスト仕様書から設計してください。これは、今後他のAIアシスタントが担当した場合でも、実装がぶれないための重要なルールです。
- 本プロジェクトのコードベースに変更を加えた場合は、必ず、関連ドキュメントも更新し、実装とドキュメントが乖離しないようにしてください。


