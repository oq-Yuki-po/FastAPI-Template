# トラブルシューティング

## Composeがenvファイルを見つけられない

リポジトリのルートでサンプルをコピーし、すべてのComposeコマンドに同じファイルを指定します。

```bash
cp config/env/development.example config/env/development.env
docker compose --env-file config/env/development.env -f .docker/compose.yaml config
```

## DBへ接続できない

APIをどこで実行しているかでホスト名が変わります。

- Compose内のAPI: `...@db:5432/app`
- ホストOS上のAPI: `...@localhost:5432/app`
- ホストOSからtest-db: `...@localhost:5433/app_test`

まず `docker compose -f .docker/compose.yaml ps` でDBがhealthyか確認し、次に `DATABASE_URL` が実行場所と一致するか確認してください。

## `relation ... does not exist` が出る

対象環境のDBへマイグレーションを適用します。

```bash
ENV_FILE=config/env/development.env uv run alembic current
ENV_FILE=config/env/development.env uv run alembic upgrade head
```

## staging / production設定で起動しない

安全性検証により、プレースホルダー鍵、`DEBUG=true`、ワイルドカードのHost/CORS、productionの既定DB認証情報は拒否されます。例外メッセージと [設定リファレンス](CONFIGURATION.md) を確認してください。

## `401 Unauthorized` になる

- `Authorization: Bearer <token>` の形式を確認
- トークンの有効期限を確認
- 発行時と検証時の `SECRET_KEY`、`JWT_ISSUER`、`JWT_AUDIENCE` が同じか確認
- `/auth/token` の `username` にユーザー名ではなくメールアドレスを指定

設定変更や再デプロイでJWT設定が変わると、以前のトークンは使えません。

## `422 Unprocessable Entity` になる

レスポンスの `detail` で対象フィールドを確認します。代表的な制約は次の通りです。

- パスワード: 12〜128文字
- ISBN: 13桁の数字
- `published_at`: `YYYY-MM-DD`
- 一覧の `offset`: 0以上
- 一覧の `limit`: 1〜100
- `/auth/token`: JSONではなくform-urlencoded

## ポートが使用中

既定ではAPIが8000、開発DBが5432、テストDBが5433を使用します。使用中のプロセスを停止するか、Composeのホスト側ポート割り当てを変更してください。DB URL側のポートも合わせて変更します。

## テストが開発DBを消しそうになる

直ちにテストを止め、`TEST_DATABASE_URL` を確認してください。PostgreSQLテストはテーブルを作り直すため、名前だけで判断せず接続先ホスト、ポート、DB名、ユーザーをすべて専用にします。通常のローカルテストは `TEST_DATABASE_URL` を指定せずSQLiteで実行できます。
