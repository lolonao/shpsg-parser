
# Releasing a New Version

This project uses GitHub Actions to automate the release process. New releases are created by pushing a version tag to the repository.

## Release Steps

1.  **Update Version Number:**
    In `pyproject.toml`, update the `version` number under the `[project]` section following [Semantic Versioning](https://semver.org/).

    ```toml
    [project]
    name = "shpsg-parser"
    version = "0.7.0" # Update this line
    ```

2.  **Update Lockfile:**
    Run `uv lock` to update `uv.lock` with the new version.

3.  **Commit Changes:**
    Commit the updated `pyproject.toml` and `uv.lock` files.

    ```bash
    git add pyproject.toml uv.lock
    git commit -m "feat: Bump version to 0.7.0"
    ```

4.  **Create and Push Tag:**
    Create a git tag that matches the version in `pyproject.toml` (prefixed with a `v`) and push it to GitHub.

    ```bash
    # Create the tag
    git tag v0.7.0

    # Push the commit and the tag
    git push
    git push origin v0.7.0
    ```

5.  **Automatic Release:**
    Pushing the tag will automatically trigger the [Create GitHub Release](https://github.com/lolonao/shpsg-parser/actions/workflows/create-release.yml) workflow. This workflow will:
    *   Build the package.
    *   Create a new GitHub Release.
    *   Attach the built `.whl` and `.tar.gz` files to the release as assets.

## Installation

Once the release is created, the package can be installed from the private repository using the following command. Remember to replace `<YOUR_PAT_HERE>` with a valid Personal Access Token and `<TAG_NAME>` with the new version tag.

```bash
uv pip install git+https://<YOUR_PAT_HERE>@github.com/lolonao/shpsg-parser.git@<TAG_NAME>
```
