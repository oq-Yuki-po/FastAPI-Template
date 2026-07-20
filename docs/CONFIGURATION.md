# 設定リファレンス

設定は環境変数から読み込まれます。変数名は大文字・小文字を区別しません。

## 読み込み順序

優先順位は高い順に次の通りです。

1. プロセスまたはコンテナへ直接渡した環境変数
2. `ENV_FILE` で指定した単一のdotenvファイル
3. `config/env/base.env`、続いて `config/env/${ENVIRONMENT}.env`
4. アプリケーション内の既定値

`ENV_FILE` を指定した場合、環境別ファイルとの自動マージは行われません。リポジトリには `.example` のみを置き、秘密値を含む `.env` はコミットしないでください。

## 変数一覧

| 変数 | 既定値 | 説明 |
| --- | --- | --- |
| `APP_NAME` | `FastAPI Template` | OpenAPIとアプリケーションの表示名 |
| `ENVIRONMENT` | `development` | `development`, `test`, `staging`, `production` のいずれか |
| `DEBUG` | `false` | FastAPIのデバッグモード |
| `API_V1_PREFIX` | `/api/v1` | 全APIルートの接頭辞 |
| `DATABASE_URL` | ローカルPostgreSQL URL | SQLAlchemy async接続URL |
| `SECRET_KEY` | 開発用プレースホルダー | JWT署名鍵（32文字以上） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | アクセストークンの有効期間（分） |
| `JWT_ISSUER` | `fastapi-template` | JWTのissuer |
| `JWT_AUDIENCE` | `fastapi-template-api` | JWTのaudience |
| `CORS_ORIGINS` | ローカル2オリジン | 許可する完全なオリジンのJSON配列 |
| `ALLOWED_HOSTS` | ローカル用ホスト | 許可するHostヘッダーのJSON配列 |
| `LOG_LEVEL` | `INFO` | Pythonログレベル |
| `TEST_DATABASE_URL` | SQLite（テスト側の既定） | pytestが利用する専用DB URL |
| `POSTGRES_DB` | なし | ComposeのPostgreSQL DB名 |
| `POSTGRES_USER` | なし | ComposeのPostgreSQLユーザー |
| `POSTGRES_PASSWORD` | なし | ComposeのPostgreSQLパスワード |

リスト値は `CORS_ORIGINS=["https://app.example.com"]` のようなJSON配列で指定します。`DATABASE_URL` は非同期ドライバーを含む `postgresql+asyncpg://...` 形式にしてください。

## ローカル設定

```bash
cp config/env/development.example config/env/development.env
```

Compose内のAPIからDBへ接続する場合のホスト名は `db` です。ホストOSからAPIを起動する場合は `DATABASE_URL` のホストを `localhost` に変更します。

## staging / productionの制約

起動時に次を検証し、安全でない設定では起動を中止します。

- プレースホルダーの `SECRET_KEY` は使用不可
- `DEBUG=true` は使用不可
- `CORS_ORIGINS` の `*` は全環境で使用不可
- `ALLOWED_HOSTS` の `*` はstaging / productionで使用不可
- productionでは既定の `postgres:postgres` DB認証情報を使用不可

本番の秘密値は環境変数またはSecret Managerから注入してください。安全な鍵は例えば `openssl rand -hex 32` で生成できます。`JWT_ISSUER` や `JWT_AUDIENCE` を変更すると、変更前に発行したトークンは受理されなくなります。
