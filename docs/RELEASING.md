
# 新しいバージョンのリリース手順

このプロジェクトでは、リリースプロセスを自動化するためにGitHub Actionsを使用しています。新しいバージョンタグをリポジトリにプッシュすることで、新しいリリースが作成されます。

## リリース手順

1.  **バージョン番号の更新:**
    `pyproject.toml` ファイル内の `[project]` セクションにある `version` を、[セマンティック バージョニング](https://semver.org/lang/ja/)に従って更新します。

    ```toml
    [project]
    name = "shpsg-parser"
    version = "0.7.0" # この行を更新
    ```

2.  **ロックファイルの更新:**
    `uv lock` を実行して、新しいバージョンを `uv.lock` ファイルに反映させます。

3.  **変更のコミット:**
    更新した `pyproject.toml` と `uv.lock` ファイルをコミットします。

    ```bash
    git add pyproject.toml uv.lock
    git commit -m "feat: Bump version to 0.7.0"
    ```

4.  **タグの作成とプッシュ:**
    `pyproject.toml` のバージョンと一致するGitタグ（先頭に `v` を付ける）を作成し、GitHubにプッシュします。

    ```bash
    # タグを作成
    git tag v0.7.0

    # コミットとタグをプッシュ
    git push
    git push origin v0.7.0
    ```

5.  **自動リリース:**
    **タグをプッシュすると**、[Create GitHub Release](https://github.com/lolonao/shpsg-parser/actions/workflows/create-release.yml) ワークフローが自動的にトリガーされます。**注意：コミットをプッシュしただけでは起動しません。必ず `git push origin <タグ名>` を実行してください。** このワークフローは以下の処理を行います:
    *   パッケージをビルドします。
    *   新しいGitHubリリースを作成します。
    *   ビルドされた `.whl` と `.tar.gz` ファイルをリリースのアセットとして添付します。

## インストール方法

リリースが作成された後、以下のコマンドで非公開リポジトリからパッケージをインストールできます。`<YOUR_PAT_HERE>` を有効なPersonal Access Tokenに、`<TAG_NAME>` を新しいバージョンタグに置き換えることを忘れないでください。

```bash
uv pip install git+https://<YOUR_PAT_HERE>@github.com/lolonao/shpsg-parser.git@<TAG_NAME>
```

---

## パッケージの利用方法（更新と依存関係の記録）

リリースしたパッケージを他のプロジェクト（例: `packagedemo`）で利用する方法です。

### 新しいバージョンへの更新

新しいバージョンがリリースされたら、利用側のプロジェクトで以下のコマンドを実行してパッケージを更新します。

`@<TAG_NAME>` の部分を、新しいバージョンタグ（例: `@v0.7.2`）に置き換えてください。

```bash
uv pip install --upgrade git+https://<YOUR_PAT_HERE>@github.com/lolonao/shpsg-parser.git@<TAG_NAME>
```

### 依存関係を `pyproject.toml` に記録する

`uv pip install` コマンドはパッケージをインストールするだけで、`pyproject.toml` には何も書き込みません。依存関係をプロジェクトに記録するには、手動で `pyproject.toml` を編集する必要があります。

利用側プロジェクトの `pyproject.toml` を開き、`[project.dependencies]` リストに以下のように追記します。

```toml
[project]
# ...
dependencies = [
    # "@<TAG_NAME>" の部分をインストールしたいバージョンに合わせる
    "shpsg-parser @ git+https://github.com/lolonao/shpsg-parser.git@v0.7.2"
]
```

**【重要】** このファイルに **Personal Access Token (PAT) を絶対に含めないでください**。このファイルはGitで管理されるため、秘密情報が漏洩する危険があります。

`pyproject.toml` に依存関係を記録した後は、インストール自体は上記のPAT付きのコマンドで手動実行するのが、最もシンプルで安全な運用です。
