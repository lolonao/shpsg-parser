import typer
import pathlib
import pandas as pd
from typing_extensions import Annotated
from enum import Enum
from typing import List

from shpsg_parser.parser_category import parse_from_file as parse_from_file_category
from shpsg_parser.parser_search import parse_from_file as parse_from_file_search
from shpsg_parser.parser_shop import parse_from_file as parse_from_file_shop
from shpsg_parser.parser_product import parse_from_file as parse_from_file_product
from shpsg_parser.models import ProductBasicItem
from shpsg_parser.models_product import ProductDetailItem


class ParserType(str, Enum):
    category = "category"
    search = "search"
    shop = "shop"
    product = "product"

app = typer.Typer()

@app.command()
def parse(
    output_csv: Annotated[pathlib.Path, typer.Argument(help="出力するCSVファイルのパス")],
    parser_type: Annotated[ParserType, typer.Option(help="使用するパーサーを選択します ('category', 'search', 'shop', 'product')")] = ParserType.category,
    html_dir: Annotated[pathlib.Path, typer.Option(help="解析対象のHTMLファイルが含まれるディレクトリ")] = None,
):
    """
    指定されたディレクトリ内のHTMLファイルを解析し、結果をCSVファイルに出力します。
    """
    if html_dir is None:
        # If no directory is specified, use the default samples directory
        html_dir = pathlib.Path("./data/samples/")

    if not html_dir.is_dir():
        typer.echo(f"エラー: 指定されたディレクトリが見つかりません: {html_dir}", err=True)
        raise typer.Exit(code=1)

    html_files = list(html_dir.glob("*.html"))
    if not html_files:
        typer.echo(f"エラー: 指定されたディレクトリにHTMLファイルが見つかりませんでした: {html_dir}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"{len(html_files)}個のHTMLファイルを解析します...")

    all_items = []
    with typer.progressbar(html_files, label="ファイルを解析中") as progress:
        for file_path in progress:
            try:
                if parser_type == ParserType.category:
                    items = parse_from_file_category(str(file_path))
                    if items:
                        all_items.extend(items)
                elif parser_type == ParserType.search:
                    items = parse_from_file_search(str(file_path))
                    if items:
                        all_items.extend(items)
                elif parser_type == ParserType.shop:
                    items = parse_from_file_shop(str(file_path))
                    if items:
                        all_items.extend(items)
                elif parser_type == ParserType.product:
                    # 商品詳細パーサーは単一のアイテムまたはNoneを返す
                    item = parse_from_file_product(str(file_path))
                    if item:
                        all_items.append(item)

            except Exception as e:
                typer.echo(f"\nファイル解析中にエラーが発生しました: {file_path}, エラー: {e}", err=True)

    if not all_items:
        typer.echo("商品情報が見つかりませんでした。", err=True)
        raise typer.Exit()

    df = pd.DataFrame([p.model_dump() for p in all_items])

    # Ensure URL fields are strings for CSV output
    if 'product_url' in df.columns:
        df['product_url'] = df['product_url'].astype(str)
    if 'image_url' in df.columns:
        df['image_url'] = df['image_url'].astype(str)
    if 'image_urls' in df.columns:
        # リストをカンマ区切りの文字列に変換
        df['image_urls'] = df['image_urls'].apply(lambda urls: ','.join(map(str, urls)) if isinstance(urls, list) else urls)
    if 'shop_url' in df.columns:
        df['shop_url'] = df['shop_url'].astype(str)
    if 'specifications' in df.columns:
        df['specifications'] = df['specifications'].astype(str)
    if 'variations' in df.columns:
        df['variations'] = df['variations'].astype(str)


    try:
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        typer.echo(f"成功: 解析結果を {output_csv} に保存しました。")
        typer.echo(f"合計 {len(all_items)} 件の商品情報を抽出しました。")
    except Exception as e:
        typer.echo(f"エラー: CSVファイルへの書き込み中にエラーが発生しました: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
