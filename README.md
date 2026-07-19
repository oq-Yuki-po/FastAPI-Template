# FastAPI Production Template

非同期PostgreSQL、JWT認証、マイグレーション、Docker、CIを備えた、実運用向けFastAPIテンプレートです。Book/Author APIは実装例として含まれています。

## 主な機能

- FastAPI 0.139 / Pydantic v2
- SQLAlchemy 2 async + PostgreSQL 18 + Alembic
- JWT Bearer認証とArgon2パスワードハッシュ
- lifespan、CORS、環境変数設定、JSONログ
- liveness/readiness probe
- pytest + SQLiteによる高速テスト、PostgreSQLによるDB統合テスト
- Ruff、mypy、pre-commit、GitHub Actions
- マルチステージDockerイメージとCompose開発環境

## クイックスタート

必要なものはPython 3.12以上とuv 0.11.29以上です。

```bash
cp .env.example .env
uv sync
docker compose -f .docker/compose.yaml up -d db
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

- API: <http://localhost:8000/api/v1>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Dockerだけで起動する場合は、初回にマイグレーションを実行してからAPIを起動します。

```bash
cp .env.example .env
docker compose -f .docker/compose.yaml run --rm api alembic upgrade head
docker compose -f .docker/compose.yaml up --build
```

## API利用例

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@example.com","password":"a-secure-password"}'

curl -X POST http://localhost:8000/api/v1/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=dev@example.com&password=a-secure-password'
```

取得したトークンを `Authorization: Bearer <token>` に指定すると、保護されたBook作成APIを利用できます。読み取りAPIは公開されています。

## 開発コマンド

```bash
make test       # テストとカバレッジ
make lint       # Ruff + mypy
make format     # 自動整形
make migrate    # DBを最新へ更新
```

新しいマイグレーションは次のように作成します。

```bash
uv run alembic revision --autogenerate -m "describe change"
```

## ディレクトリ構成

```text
app/
├── api/          # ルーターとFastAPI依存性
├── core/         # 設定、認証、ログ
├── db/           # Baseと非同期セッション
├── migration/    # Alembic migrations
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic API schemas
└── main.py       # application factory
tests/            # app/と対応するテスト構成
├── api/          # app/api/の依存性・ルーターテスト
│   └── routes/   # app/api/routes/のAPIテスト
├── core/         # app/core/の単体テスト
├── db/           # app/db/のDBセッションテスト
├── migration/    # app/migration/の履歴テスト
├── models/       # app/models/の統合テスト
├── schemas/      # app/schemas/のバリデーションテスト
└── test_main.py  # app/main.pyのアプリ構成テスト
.docker/
├── Dockerfile
├── Dockerfile.dockerignore
└── compose.yaml
```

## テスト用データベース

ローカルの通常テストは、外部サービスなしで高速かつ独立して実行できるようSQLiteを使います。
一方、SQLiteだけではPostgreSQL固有の型・制約・SQL・トランザクション差異を検出できません。そのためCIでは同じテストスイートをPostgreSQL 18でも実行し、Alembicマイグレーションも検証します。

ローカルでPostgreSQLに対して実行する場合:

```bash
docker compose -f .docker/compose.yaml --profile test up -d test-db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/app_test \
  uv run pytest
```

テストは対象DBのテーブルを作り直すため、開発用・本番用DBではなく必ず専用の `app_test` を指定してください。

## 本番運用時の注意

- `.env` の `SECRET_KEY` を十分長いランダム値に変更してください。
- HTTPS終端、シークレット管理、DBバックアップはデプロイ先で設定してください。
- デプロイ時はアプリ起動前に `alembic upgrade head` を一度実行してください。
