import streamlit as st
import pandas as pd
from typing import List
from datetime import datetime

# 既存のパーサーとモデル
from shpsg_parser.parser_category import parse_from_string as parse_from_string_category
from shpsg_parser.parser_search import parse_from_string as parse_from_string_search
from shpsg_parser.parser_shop import parse_from_string as parse_from_string_shop
from shpsg_parser.models import ProductBasicItem

# 新しく追加したパーサーとモデル
from shpsg_parser.parser_product import parse_from_string as parse_product_from_string
from shpsg_parser.models_product import ProductDetailItem

st.set_page_config(layout="wide")

def list_page_view():
    """
    商品一覧ページ（カテゴリ、検索、ショップ）用のビュー
    """
    st.header("商品一覧ページパーサー")
    st.write(
        "パーサーの種類を選択し、Shopeeシンガポールの商品一覧ページのHTMLファイルをアップロードしてください。"
        "複数ファイルのアップロードに対応しています。"
    )

    parser_type = st.selectbox(
        "パーサーの種類を選択してください:",
        ("カテゴリページ", "検索結果ページ", "ショップページ")
    )

    if parser_type == "カテゴリページ":
        parse_function = parse_from_string_category
        st.info("カテゴリページのHTMLファイルをアップロードしてください。")
    elif parser_type == "検索結果ページ":
        parse_function = parse_from_string_search
        st.info("検索結果ページのHTMLファイルをアップロードしてください。")
    else:
        parse_function = parse_from_string_shop
        st.info("ショップページのHTMLファイルをアップロードしてください。")

    uploaded_files = st.file_uploader(
        "HTMLファイルをドラッグ＆ドロップするか、ボタンをクリックして選択してください。",
        type=["html", "htm"],
        accept_multiple_files=True,
        key="list_page_uploader" # uploaderにユニークなキーを付与
    )

    if uploaded_files:
        all_products: List[ProductBasicItem] = []
        progress_bar = st.progress(0)
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                html_content = uploaded_file.getvalue().decode("utf-8")
                products = parse_function(html_content)
                if products:
                    all_products.extend(products)
            except Exception as e:
                st.error(f"{uploaded_file.name} の処理中にエラーが発生しました: {e}")
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_products:
            st.success(f"合計 {len(all_products)} 件の商品情報を抽出しました。")
            dict_products = [p.model_dump() for p in all_products]
            df = pd.DataFrame(dict_products)
            df['product_url'] = df['product_url'].astype(str)
            df['image_url'] = df['image_url'].astype(str)

            # 表示するカラムの順番を調整
            display_columns = [
                'product_name', 'price', 'rating', 'sold', 'location',
                'product_url', 'image_url', 'page_type', 'currency'
            ]
            # 存在するカラムのみ表示
            df_display = df[[col for col in display_columns if col in df.columns]]

            st.dataframe(df_display)

            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="結果をCSVとしてダウンロード",
                data=csv,
                file_name='shopee_list_products.csv',
                mime='text/csv',
            )
        else:
            st.warning("アップロードされたファイルから商品情報を抽出できませんでした。")


def product_detail_view():
    """
    商品詳細ページ用のビュー
    """
    st.header("商品詳細ページパーサー")
    st.write(
        "Shopeeシンガポールの商品詳細ページのHTMLファイルをアップロードしてください。"
        "複数ファイルのアップロードに対応しています。"
    )

    uploaded_files = st.file_uploader(
        "HTMLファイルをドラッグ＆ドロップするか、ボタンをクリックして選択してください。",
        type=["html", "htm"],
        accept_multiple_files=True,
        key="product_detail_uploader" # uploaderにユニークなキーを付与
    )

    if uploaded_files:
        all_products: List[ProductDetailItem] = []
        progress_bar = st.progress(0)

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                html_content = uploaded_file.getvalue().decode("utf-8")
                item = parse_product_from_string(html_content)
                if item:
                    all_products.append(item)
            except Exception as e:
                st.error(f"{uploaded_file.name} の処理中にエラーが発生しました: {e}")
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_products:
            st.success(f"合計 {len(all_products)} 件の商品情報を抽出しました。")

            for item in all_products:
                with st.expander(f"{item.product_name} (ID: {item.product_id})", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        if item.image_urls:
                            st.image(str(item.image_urls[0]), caption="メイン画像", use_container_width=True)
                        st.metric(label="価格", value=f"{item.currency} {item.price}")
                        st.metric(label="評価", value=f"{item.rating} / 5 ({item.rating_count}件)")
                        st.metric(label="販売数", value=f"{item.sold or 'N/A'}")
                        st.metric(label="在庫数", value=f"{item.quantity or 'N/A'}")

                    with col2:
                        st.subheader("ショップ情報")
                        st.text(f"ショップ名: {item.shop_name}")
                        st.text(f"ショップID: {item.shop_id}")
                        if item.shop_url:
                            st.markdown(f"[ショップページへ]({item.shop_url})")

                        st.subheader("配送と保証")
                        if item.shipping_info:
                            if item.shipping_info.cost_text:
                                st.markdown(f"- **送料:** {item.shipping_info.cost_text}")
                            if item.shipping_info.guarantee_text:
                                st.markdown(f"- **配送保証:** {item.shipping_info.guarantee_text}")
                        if item.shopping_guarantee:
                             st.markdown(f"- **ショッピング保証:** {item.shopping_guarantee}")

                    st.subheader("商品説明")
                    st.markdown(item.product_description)

                    st.subheader("商品仕様")
                    st.json(item.specifications)

                    st.subheader("バリエーション")
                    st.json(item.variations)

                    st.subheader("レビュー詳細")
                    if item.detailed_ratings:
                        for rating in item.detailed_ratings:
                            st.text(f"⭐️ {rating.rating_stars}/5 by {rating.username or 'Anonymous'} ({rating.timestamp})")
                            if rating.variation:
                                st.text(f"購入バリエーション: {rating.variation}")
                            if rating.comment:
                                st.info(rating.comment)
                            st.divider()
                    else:
                        st.text("詳細なレビューはありません。")

            # ダウンロード用にDataFrameを作成
            dict_products = [p.model_dump() for p in all_products]
            df = pd.DataFrame(dict_products)
            # URLとリスト/辞書を文字列に変換
            for col in ['product_url', 'shop_url', 'image_urls', 'specifications', 'variations', 'shipping_info', 'detailed_ratings']:
                 if col in df.columns:
                    df[col] = df[col].astype(str)

            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="全結果をCSVとしてダウンロード",
                data=csv,
                file_name='shopee_product_details.csv',
                mime='text/csv',
            )

        else:
            st.warning("アップロードされたファイルから商品情報を抽出できませんでした。")


def main():
    """
    メインアプリケーション
    """
    st.sidebar.title("Shopee Parser")
    app_mode = st.sidebar.selectbox(
        "解析したいページの種類を選択してください",
        ["商品一覧ページ", "商品詳細ページ"]
    )

    if app_mode == "商品一覧ページ":
        list_page_view()
    elif app_mode == "商品詳細ページ":
        product_detail_view()

if __name__ == "__main__":
    main()