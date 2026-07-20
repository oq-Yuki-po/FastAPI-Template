# FastAPI Production Template

非同期PostgreSQL、JWT認証、マイグレーション、Docker、CIを備えた、実運用向けFastAPIテンプレートです。Book/Author APIは実装例として含まれています。

## 主な機能

- FastAPI 0.139 / Pydantic v2
- SQLAlchemy 2 async + PostgreSQL 18 + Alembic
- JWT Bearer認証とArgon2パスワードハッシュ
- lifespan、CORS、環境変数設定、JSONログ
- Service / Repository層による業務ロジックとDBアクセスの分離
- development / test / staging / production別のdotenv設定
- liveness/readiness probe
- pytest + SQLiteによる高速テスト、PostgreSQLによるDB統合テスト
- Ruff、mypy、pre-commit、GitHub Actions
- マルチステージDockerイメージとCompose開発環境

## クイックスタート

必要なものはPython 3.12以上とuv 0.11.29以上です。

```bash
cp config/env/development.example config/env/development.env
uv sync
docker compose --env-file config/env/development.env -f .docker/compose.yaml run --rm api alembic upgrade head
docker compose --env-file config/env/development.env -f .docker/compose.yaml up --build
```

- API: <http://localhost:8000/api/v1>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

より詳しい手順は次のガイドを参照してください。

- [認証ガイド](docs/AUTHENTICATION.md) — 登録、ログイン、JWT検証の流れと運用上の注意
- [設定リファレンス](docs/CONFIGURATION.md) — 全環境変数、dotenvの優先順位、安全な本番設定
- [開発ガイド](docs/DEVELOPMENT.md) — Dev Container、テスト、マイグレーション、変更の追加方法
- [デプロイガイド](docs/DEPLOYMENT.md) — コンテナ、起動順序、ヘルスチェック、運用チェックリスト
- [トラブルシューティング](docs/TROUBLESHOOTING.md) — 起動、DB接続、認証でよくある問題

ホスト側でAPIを起動する場合は、`config/env/development.env` のDBホストを `db` から `localhost` へ変更し、次を実行します。

```bash
docker compose --env-file config/env/development.env -f .docker/compose.yaml up -d db
ENV_FILE=config/env/development.env uv run alembic upgrade head
ENV_FILE=config/env/development.env uv run fastapi dev app/main.py
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
make security   # Bandit + 依存関係の脆弱性監査
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
├── api/          # HTTPルーターとFastAPI依存性
├── core/         # 設定、認証、ログ
├── db/           # Baseと非同期セッション
├── migration/    # Alembic migrations
├── models/       # SQLAlchemy models
├── repositories/ # DBクエリと永続化
├── schemas/      # Pydantic API schemas
├── services/     # 業務ロジックとトランザクション境界
└── main.py       # application factory
config/
└── env/          # 環境別dotenvテンプレートとローカル設定
tests/            # app/と対応するテスト構成
├── api/          # app/api/の依存性・ルーターテスト
│   └── routes/   # app/api/routes/のAPIテスト
├── core/         # app/core/の単体テスト
├── db/           # app/db/のDBセッションテスト
├── migration/    # app/migration/の履歴テスト
├── models/       # app/models/の統合テスト
├── repositories/ # app/repositories/のDBテスト
├── schemas/      # app/schemas/のバリデーションテスト
├── services/     # app/services/の単体テスト
└── test_main.py  # app/main.pyのアプリ構成テスト
.docker/
├── Dockerfile
├── Dockerfile.dockerignore
└── compose.yaml
docs/
└── database/     # SQLAlchemyモデルから生成するSVGのER図
tools/
└── database/     # DB可視化などの開発支援ツール
```

依存方向は `api -> services -> repositories -> db/models` です。RouterはHTTP入出力、Serviceは業務判断、RepositoryはSQLAlchemy操作に責務を限定しています。

## 環境別設定

環境ごとのサンプルは `config/env/` に集約しています。実値を含む `*.env` はGit管理外です。

```bash
cp config/env/development.example config/env/development.env
cp config/env/test.example config/env/test.env
```

`ENVIRONMENT=test` を指定すると `config/env/base.env` と `config/env/test.env` を順番に読み、後者で上書きします。任意のファイルを使う場合は `ENV_FILE` を指定できます。OS環境変数やコンテナから注入した値はdotenvより優先されます。

```bash
ENVIRONMENT=test uv run pytest
ENV_FILE=/run/secrets/app.env fastapi run app/main.py
docker compose --env-file config/env/development.env -f .docker/compose.yaml up
```

staging / productionではサンプル値をそのまま使わず、デプロイ先のSecret Manager等から `DATABASE_URL` と `SECRET_KEY` を注入してください。
`ALLOWED_HOSTS` にはAPIのホスト名、`CORS_ORIGINS` には許可するフロントエンドの完全なオリジンだけを列挙します。本番ではSwagger、ReDoc、OpenAPI JSONは公開されません。

## DB構造の可視化

[ERAlchemy2](https://pypi.org/project/eralchemy2/)でSQLAlchemyの `Base.metadata` を直接読み取ります。PostgreSQLの起動、接続情報、Alembicの実行は不要です。

```bash
make db-docs
```

ER図は `docs/database/schema.svg` と `docs/database/schema.png` に生成されます。生成物はモデルから再作成できるためGit管理外です。

画像生成にはGraphvizが必要です。Dev Containerには導入済みです。ホストで実行する場合はOSに合わせてGraphvizをインストールしてください。

```bash
# macOS
brew install graphviz

# Debian / Ubuntu
sudo apt-get install graphviz libgraphviz-dev
```

## テスト用データベース

ローカルの通常テストは、外部サービスなしで高速かつ独立して実行できるようSQLiteを使います。
一方、SQLiteだけではPostgreSQL固有の型・制約・SQL・トランザクション差異を検出できません。そのためCIでは同じテストスイートをPostgreSQL 18でも実行し、Alembicマイグレーションも検証します。

ローカルでPostgreSQLに対して実行する場合:

```bash
docker compose --env-file config/env/test.env -f .docker/compose.yaml --profile test up -d test-db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/app_test \
  uv run pytest
```

テストは対象DBのテーブルを作り直すため、開発用・本番用DBではなく必ず専用の `app_test` を指定してください。

## 本番運用時の注意

- `config/env/production.env` の `SECRET_KEY` を十分長いランダム値に変更してください。
- HTTPS終端、シークレット管理、DBバックアップはデプロイ先で設定してください。
- デプロイ時はアプリ起動前に `alembic upgrade head` を一度実行してください。
- レート制限やトークン失効など、デプロイ側で必要な対策は [SECURITY.md](SECURITY.md) を参照してください。
