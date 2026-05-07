# Claude Code × GitHub × Xサーバー デプロイガイド

このリポジトリを例に、Claude Codeでホームページを編集し、GitHubを経由してXサーバーへ自動アップする流れをまとめます。

---

## 全体の流れ

```
Claude Code（編集）→ GitHub（push）→ GitHub Actions（自動FTP転送）→ Xサーバー（公開）
```

---

## 1. 事前準備

### Xサーバー側

1. Xサーバーのサーバーパネルにログイン
2. **FTP設定** → FTPアカウントを確認（またはサブFTPアカウントを作成）
   - FTPサーバー名（例：`sv****.xserver.jp`）
   - FTPユーザー名
   - FTPパスワード
   - アップロード先ディレクトリ（例：`/ドメイン名/public_html/`）

### GitHub側（Secretsの登録）

リポジトリの **Settings → Secrets and variables → Actions** に以下の4つを登録：

| Secret名 | 内容 |
|---|---|
| `FTP_SERVER` | XサーバーのFTPサーバー名 |
| `FTP_USERNAME` | FTPユーザー名 |
| `FTP_PASSWORD` | FTPパスワード |
| `FTP_SERVER_DIR` | アップロード先ディレクトリ（末尾に`/`） |

---

## 2. リポジトリの構成

```
fp-project/
├── index.html              # ホームページ本体
├── style.css               # スタイルシート
├── assets/                 # 画像ファイル
│   ├── hero-pc.png
│   └── hero-sp.png
└── .github/
    └── workflows/
        └── deploy.yml      # 自動デプロイの設定ファイル
```

---

## 3. GitHub Actionsの設定（deploy.yml）

`.github/workflows/deploy.yml` が自動デプロイの核心です。

```yaml
name: Deploy to Xserver

on:
  push:
    branches:
      - main          # mainブランチにpushされたら自動実行

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Deploy via FTP
        uses: SamKirkland/FTP-Deploy-Action@v4.3.5
        with:
          server: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          server-dir: ${{ secrets.FTP_SERVER_DIR }}
          protocol: ftps      # XサーバーはFTPS（暗号化FTP）を使用
          port: 21
```

**ポイント：** Xサーバーは暗号化FTP（FTPS）を使用するため `protocol: ftps` を指定します。

---

## 4. 日々の作業フロー（Claude Codeを使う場合）

### ステップ① Claude Codeでファイルを編集

Claude Codeのチャット欄に変更したい内容を日本語で指示するだけでOKです。

**指示の例：**
```
「ヒーロー画像の下にあるボタンのテキストを
 『初回相談を予約する』から『無料相談はこちら』に変えてください」
```

```
「CONCEPTセクションの背景色をベージュ（#f5f0e8）に変更してください」
```

Claude Codeが `index.html` や `style.css` を直接編集します。

### ステップ② 変更内容を確認

```bash
git diff
```

編集された箇所を確認します。問題なければ次のステップへ。

### ステップ③ mainブランチにpushする

```bash
git add .
git commit -m "ボタンテキストを変更"
git push origin main
```

**これだけでXサーバーへの反映が自動で始まります。**

### ステップ④ デプロイの状況を確認

GitHubリポジトリの **Actions** タブを開くと、デプロイの進行状況をリアルタイムで確認できます。

- 緑のチェックマーク ✅ → デプロイ成功
- 赤い × → エラーあり（ログを確認して原因を調査）

---

## 5. よくあるトラブルと対処法

### FTP接続エラー（Authentication failed）
- GitHub SecretsのFTPユーザー名・パスワードが正しいか確認
- XサーバーのFTPアカウントが有効になっているか確認

### ファイルは転送されたのにサイトに反映されない
- ブラウザのキャッシュをクリア（Ctrl+Shift+R）
- `FTP_SERVER_DIR` のパスが正しいか確認（`/ドメイン名/public_html/` 形式）

### pushしてもActionsが動かない
- `deploy.yml` の `branches: - main` が正しいブランチ名になっているか確認
- ファイルのインデントがYAML形式として正しいか確認

---

## 6. このプロジェクトで実際に使われているファイル

| ファイル | 役割 |
|---|---|
| `index.html` | ホームページ本体（SEO・OGP・セクション構成） |
| `style.css` | デザイン全般（レイアウト・色・フォント） |
| `assets/hero-pc.png` | PCサイズ用ヒーロー画像 |
| `assets/hero-sp.png` | スマホサイズ用ヒーロー画像 |
| `.github/workflows/deploy.yml` | 自動デプロイ設定 |

---

## まとめ

| 作業 | 担当 |
|---|---|
| HTMLやCSSの編集 | Claude Code（チャットで指示） |
| ファイルの管理・バージョン管理 | GitHub |
| Xサーバーへの転送 | GitHub Actions（自動） |

一度セットアップすれば、あとは **Claude Codeに指示 → push するだけ** でホームページが更新されます。
