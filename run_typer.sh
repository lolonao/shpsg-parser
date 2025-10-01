#!/usr/bin/env bash

PARSER_TYPE="category"
# パース対象のHTMLファイルが保存されているフォルダー
HTML_DIR="/home/nao/Public/github/naokitsutsui/WIP/shpsg-parser-api/data/samples/"
OUTPUT_FILE="./typer_output.csv"

uv run shpsg-parser --parser-type "${PARSER_TYPE}" --html-dir "${HTML_DIR}" "${OUTPUT_FILE}" 


