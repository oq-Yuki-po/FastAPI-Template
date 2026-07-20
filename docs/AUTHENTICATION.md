# 認証ガイド

このテンプレートは、メールアドレスとパスワードによるログインと、短時間有効なJWT Bearerトークンを使用します。この文書では個々のエンドポイント仕様ではなく、認証処理全体の流れと設計上の注意点を説明します。正確な入出力スキーマは開発環境のSwagger UI (`/docs`) またはReDoc (`/redoc`) を参照してください。

## 認証の流れ

1. クライアントがメールアドレスとパスワードでユーザーを登録する
2. パスワードをArgon2でハッシュ化し、ハッシュだけをDBへ保存する
3. クライアントがOAuth2 password formでログインする
4. メールアドレス、パスワード、ユーザーの有効状態を検証する
5. 成功時にユーザーIDをsubjectとする署名済みJWTを返す
6. クライアントが `Authorization: Bearer <token>` を保護されたAPIへ送る
7. APIが署名、必須claims、有効期限、issuer、audienceを検証し、DB上の有効なユーザーを取得する

メールアドレスは登録時とログイン時に小文字へ正規化されます。JWTには変更されうるメールアドレスではなく、DBのユーザーIDが格納されます。

## 動作確認

```bash
export API_URL=http://localhost:8000/api/v1

curl --fail-with-body -X POST "$API_URL/auth/register" \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@example.com","password":"a-secure-password"}'

curl --fail-with-body -X POST "$API_URL/auth/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'username=dev@example.com' \
  --data-urlencode 'password=a-secure-password'
```

OAuth2のフィールド名に合わせ、メールアドレスは `username` として送ります。ログインレスポンスから `access_token` を取り出し、保護されたAPIへ渡します。

```bash
export ACCESS_TOKEN='<取得したaccess_token>'

curl --fail-with-body "$API_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Swagger UIでは右上の **Authorize** から同じ認証フローを試せます。

## JWTの内容と検証

トークンは `HS256` と `SECRET_KEY` で署名され、次のclaimsを必須とします。

| Claim | 用途 |
| --- | --- |
| `sub` | ユーザーの正の整数ID |
| `exp` | 有効期限 |
| `iat` | 発行日時 |
| `nbf` | 利用開始日時 |
| `iss` | 発行者 (`JWT_ISSUER`) |
| `aud` | 対象サービス (`JWT_AUDIENCE`) |
| `jti` | トークンごとの一意なID |

有効期間は `ACCESS_TOKEN_EXPIRE_MINUTES` で設定します。署名が正しくても、対象ユーザーが存在しない、または `is_active=false` の場合は認証されません。

`SECRET_KEY`、`JWT_ISSUER`、`JWT_AUDIENCE` のいずれかを変更すると、以前の設定で発行したトークンは無効になります。複数インスタンスで運用する場合は、すべてに同じ値を配布してください。

## エラーの考え方

- ログイン情報が不正な場合は `401 Unauthorized`
- Bearerトークンがない、不正、期限切れの場合も `401 Unauthorized`
- 登録済みメールアドレスでの再登録は `409 Conflict`
- パスワードが12〜128文字の範囲外など、入力形式が不正な場合は `422 Unprocessable Entity`

存在しないメールアドレスでのログインでもArgon2検証を行い、応答時間からアカウントの存在を推測しにくくしています。クライアント側でも「メールが存在しない」「パスワードが違う」を区別して表示しないでください。

## 現在の範囲

アクセストークンはステートレスです。現時点では次の機能を実装していません。

- リフレッシュトークン
- サーバー側ログアウトまたは個別トークン失効
- メールアドレス確認
- パスワードリセット
- 多要素認証
- ログイン試行のレート制限

そのため、アクセストークンは期限まで有効です。即時失効が必要なサービスでは、`jti` のdenylist、ユーザー単位のtoken version、またはサーバー管理セッションなどを追加してください。登録・ログインのレート制限はAPI Gatewayやアプリケーション層で設定します。

## 本番運用

- 通信は必ずHTTPSで保護する
- 十分に長いランダムな `SECRET_KEY` をSecret Managerから注入する
- Bearerトークンをログ、URL、エラーレポートへ記録しない
- ブラウザーでの保存場所とXSS対策をフロントエンドの脅威モデルに合わせて決める
- 鍵のローテーション時は既存トークンが無効になることを考慮する
- 短い有効期限と、必要に応じた失効方式を組み合わせる

実装済みの防御策とデプロイ側の責務は [SECURITY.md](../SECURITY.md)、JWT関連の環境変数は [設定リファレンス](CONFIGURATION.md) を参照してください。
