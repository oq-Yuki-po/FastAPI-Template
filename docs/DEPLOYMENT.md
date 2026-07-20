# デプロイガイド

このリポジトリの `.docker/Dockerfile` は依存関係をbuilderで解決し、非rootユーザーで実行するマルチステージイメージです。アプリはポート8000で待ち受けます。

## ビルドと確認

```bash
docker build -f .docker/Dockerfile -t fastapi-template:local .
docker run --rm -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL='postgresql+asyncpg://app:password@db.example.com:5432/app' \
  -e SECRET_KEY='<32文字以上のランダム値>' \
  -e ALLOWED_HOSTS='["api.example.com"]' \
  -e CORS_ORIGINS='["https://app.example.com"]' \
  fastapi-template:local
```

上の値は例です。実際の秘密値はコマンド履歴やイメージへ埋め込まず、デプロイ先のSecret Managerを利用してください。

## リリース順序

1. 新しいイメージをビルドして脆弱性スキャンを行う
2. DBバックアップとマイグレーションの互換性を確認する
3. 同じイメージまたはリリースジョブで `alembic upgrade head` を一度だけ実行する
4. APIインスタンスを段階的に更新する
5. readiness、エラーレート、ログを確認する

複数のAPIインスタンスから同時にAlembicを実行しないでください。ローリング更新では、旧版と新版が一時的に同じDBを使えるよう、破壊的なスキーマ変更を複数リリースに分けます。

## プローブ

- liveness: `GET /api/v1/health/live`
- readiness: `GET /api/v1/health/ready`

liveness失敗はプロセス再起動、readiness失敗はロードバランサーからの切り離しに利用します。readinessはDBへ問い合わせるため、DB障害時は503になります。

## リバースプロキシ

TLSはロードバランサーまたはリバースプロキシで終端します。外部のAPIホスト名を `ALLOWED_HOSTS` に、ブラウザーから呼び出すフロントエンドの完全なオリジンを `CORS_ORIGINS` に設定してください。パスだけが違うURLは別オリジンではありませんが、スキーム・ホスト・ポートのいずれかが違えば別オリジンです。

staging / productionではAPIドキュメントが無効になります。必要な場合もアプリで全公開せず、認証された内部ネットワークへOpenAPI成果物を配布する運用を推奨します。

## 運用チェックリスト

- `ENVIRONMENT=production` と `DEBUG=false`
- 強い `SECRET_KEY` をSecret Managerから注入
- 専用DBユーザーとTLS接続を使用
- `ALLOWED_HOSTS` と `CORS_ORIGINS` を必要最小限に限定
- DBバックアップ、復元テスト、接続数上限を設定
- HTTPS、アクセスログ、アプリJSONログ、メトリクス、アラートを設定
- コンテナのCPU・メモリ上限と水平スケーリング方針を設定
- デプロイ前にCI、マイグレーション、ロールバック手順を確認

認証と追加対策は [SECURITY.md](../SECURITY.md)、全設定値は [設定リファレンス](CONFIGURATION.md) を参照してください。
