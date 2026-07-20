# 開発ガイド

## 開発環境

Python 3.12〜3.14、uv 0.11.29以上、Docker Composeを利用します。ER図を生成する場合はGraphvizも必要です。

```bash
cp config/env/development.example config/env/development.env
uv sync --locked
```

VS Code / Dev Containerを使う場合、依存関係の同期とpre-commitの導入はコンテナ作成後に自動実行されます。DBホストもあらかじめ `db` に設定されています。

## 起動方法

すべてComposeで起動する方法:

```bash
docker compose --env-file config/env/development.env -f .docker/compose.yaml up --build
docker compose --env-file config/env/development.env -f .docker/compose.yaml run --rm api alembic upgrade head
```

APIをホスト側で起動する方法（`development.env` のDBホストを `localhost` に変更）:

```bash
docker compose --env-file config/env/development.env -f .docker/compose.yaml up -d db
ENV_FILE=config/env/development.env uv run alembic upgrade head
ENV_FILE=config/env/development.env uv run fastapi dev app/main.py
```

初回はAPI起動前にマイグレーションを実行してください。

## 品質チェック

```bash
make format    # Ruffによる修正と整形
make lint      # Ruff、フォーマット確認、mypy
make test      # pytestとカバレッジ
make security  # Banditと依存関係監査
```

CIは上記に加え、PostgreSQL 18でマイグレーションとテストを実行し、Dockerイメージをビルドします。

## テスト

通常のローカルテストはSQLiteを使い、外部DBを必要としません。

```bash
uv run pytest
uv run pytest tests/api/routes/test_catalog.py
uv run pytest -k create_book
```

PostgreSQLとの差異も確認する場合は専用のテストDBを起動します。

```bash
cp config/env/test.example config/env/test.env
docker compose --env-file config/env/test.env -f .docker/compose.yaml --profile test up -d test-db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/app_test uv run pytest
```

テストはスキーマを作り直します。`TEST_DATABASE_URL` に開発DBや本番DBを指定しないでください。

## マイグレーション

モデル変更後にリビジョンを作成し、生成されたファイルを必ずレビューします。

```bash
ENV_FILE=config/env/development.env uv run alembic revision --autogenerate -m "add book field"
ENV_FILE=config/env/development.env uv run alembic upgrade head
ENV_FILE=config/env/development.env uv run alembic downgrade -1
```

特に型変更、データ移行、制約の追加はautogenerateだけでは完結しない場合があります。upgrade / downgradeの両方向と、既存データがある状態を確認してください。

## 機能追加の流れ

このテンプレートの依存方向は `api → services → repositories → db/models` です。

1. `app/models/` と `app/schemas/` に永続化モデルと入出力を追加
2. `app/repositories/` にDB操作を追加
3. `app/services/` に業務ルールとトランザクション境界を追加
4. `app/api/routes/` にHTTPルートを追加し、`app/api/router.py` へ登録
5. `tests/` の対応する階層にテストを追加
6. DB変更があればAlembicリビジョンを追加

RouterにSQLAlchemyクエリを置かず、RepositoryにHTTP例外を持ち込まないことで、各層を独立してテストしやすく保ちます。

## ER図

```bash
make db-docs
```

`docs/database/schema.svg` と `schema.png` が生成されます。モデルを直接読み取るため、DB接続やマイグレーションは不要です。
