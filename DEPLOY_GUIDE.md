# 初心者向け：Claude Code × GitHub × Xサーバー ホームページ公開ガイド

---

## まず「リポジトリ」って何？

**リポジトリ（Repository）**とは、ファイルの「保存箱」のことです。

ホームページを作るときは、

- `index.html`（ページの内容）
- `style.css`（デザイン）
- `assets/`フォルダ（画像）

などのファイルが必要になります。これらをまとめて入れておく箱がリポジトリです。

GitHubはこの箱をインターネット上で保管してくれるサービスです。
自分のパソコンだけでなく、クラウド（インターネット上）にも保存されるため、
バックアップにもなり、変更履歴も全部残ります。

```
【イメージ図】

あなたのパソコン          GitHub（インターネット上）      Xサーバー（公開サーバー）
┌──────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  fp-project/ │  push   │  fp-project      │  自動転送 │  あなたのサイト  │
│  index.html  │ ──────→ │  リポジトリ      │ ────────→│  （世界に公開）  │
│  style.css   │         │  （保存箱）      │          │                  │
│  assets/     │         └──────────────────┘          └──────────────────┘
└──────────────┘
```

---

## 全体の流れ（まずここを把握してください）

```
① Claude Codeでファイルを編集する
        ↓
② GitHubにpush（送信）する
        ↓
③ GitHub Actionsが自動でXサーバーに転送する
        ↓
④ サイトに反映される
```

**ポイント：② をするだけで ③④ は自動です。**

---

## 【初回だけ】セットアップ手順

### ステップ1：GitHubアカウントを作る

1. [https://github.com](https://github.com) を開く
2. 「Sign up」からアカウントを作成する
   - メールアドレス・パスワード・ユーザー名を決める

---

### ステップ2：GitHubにリポジトリを作る

1. GitHubにログインする
2. 右上の「＋」ボタン → 「New repository」をクリック
3. 以下を入力する

   | 項目 | 入力内容 |
   |---|---|
   | Repository name | `fp-project`（なんでもOK） |
   | Public / Private | Private（非公開）を選ぶ |

4. 「Create repository」ボタンをクリック

これでGitHub上に空の保存箱ができました。

---

### ステップ3：XサーバーのFTP情報を調べる

FTPとは「ファイルを転送するための仕組み」です。
GitHub→Xサーバーへファイルを送るために必要な情報を調べます。

1. Xサーバーの**サーバーパネル**にログインする
2. 「FTPソフト設定」または「FTPアカウント」のメニューを開く
3. 以下の情報をメモする

   | 項目 | 例 |
   |---|---|
   | FTPサーバー名 | `sv12345.xserver.jp` |
   | FTPユーザー名 | `example_user` |
   | FTPパスワード | （設定したパスワード） |
   | アップロード先 | `/example.com/public_html/` |

   ※ アップロード先は「ドメイン名/public_html/」が基本です。
   　 末尾の `/` を忘れないようにしてください。

---

### ステップ4：GitHubにFTP情報を登録する（Secrets）

FTPのパスワードなどをそのままファイルに書くのは危険です。
GitHubには「Secrets（シークレット）」という、外から見えない安全な保管場所があります。

1. GitHubのリポジトリページを開く
2. 上のメニューから「**Settings**」をクリック
3. 左のメニューから「**Secrets and variables**」→「**Actions**」をクリック
4. 「**New repository secret**」ボタンをクリック
5. 以下の4つを1つずつ登録する

   **登録①**
   - Name（名前）: `FTP_SERVER`
   - Secret（値）: `sv12345.xserver.jp`（メモしたサーバー名）

   **登録②**
   - Name: `FTP_USERNAME`
   - Secret: `example_user`（メモしたユーザー名）

   **登録③**
   - Name: `FTP_PASSWORD`
   - Secret: `（メモしたパスワード）`

   **登録④**
   - Name: `FTP_SERVER_DIR`
   - Secret: `/example.com/public_html/`（メモしたアップロード先）

---

### ステップ5：自動デプロイの設定ファイルを用意する

`.github/workflows/deploy.yml` というファイルが「GitHubに push したら自動でXサーバーに転送する」という命令書です。

このプロジェクトにはすでに用意されています（中身は以下）。

```yaml
name: Deploy to Xserver

on:
  push:
    branches:
      - main        # ← mainブランチにpushされたら自動実行

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Deploy via FTP
        uses: SamKirkland/FTP-Deploy-Action@v4.3.5
        with:
          server: ${{ secrets.FTP_SERVER }}        # ← Secretsから読み込む
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          server-dir: ${{ secrets.FTP_SERVER_DIR }}
          protocol: ftps    # ← Xサーバーはftpsを使う
          port: 21
```

`${{ secrets.FTP_SERVER }}` という書き方で、ステップ4で登録したシークレットを安全に読み込んでいます。

---

### ステップ6：ファイルをGitHubに初回アップロードする

パソコンのターミナル（またはClaude Codeのターミナル）で、以下のコマンドを順に実行します。

```bash
# GitHubのリポジトリと接続する（URLは自分のものに変える）
git remote add origin https://github.com/あなたのユーザー名/fp-project.git

# mainブランチに切り替える
git branch -M main

# GitHubに送信する（初回）
git push -u origin main
```

これで初回セットアップは完了です。

---

## 【毎回】ホームページを更新するときの手順

セットアップが終わったあとは、毎回この流れだけでOKです。

---

### 1. Claude Codeに変更を指示する

Claude Codeのチャット欄に、日本語で指示するだけです。

**指示の例：**

> 「ヒーロー画像の下のボタンを『無料相談はこちら』に変えてください」

> 「CONCEPTセクションの背景色をやさしいベージュにしてください」

> 「フッターに『プライバシーポリシー』のリンクを追加してください」

Claude Codeが `index.html` や `style.css` を直接編集してくれます。

---

### 2. 変更内容を確認する（任意）

```bash
git diff
```

このコマンドで、何が変わったか確認できます。
問題なければ次のステップへ。

---

### 3. GitHubに送信する（push）

以下の3行を実行します。

```bash
git add .
git commit -m "ボタンのテキストを変更した"
git push origin main
```

**各コマンドの意味：**

| コマンド | 意味 |
|---|---|
| `git add .` | 変更したファイルを「送る準備」にする |
| `git commit -m "..."` | 変更に名前（メモ）をつけて記録する |
| `git push origin main` | GitHubに送信する |

**pushした瞬間に、GitHub Actionsが自動で動き始めます。**

---

### 4. デプロイが成功したか確認する

1. GitHubのリポジトリページを開く
2. 上のメニューから「**Actions**」をクリック
3. 一番上にある実行履歴を見る

   - **黄色のぐるぐる** → 実行中（少し待つ）
   - **緑のチェックマーク ✅** → 成功！サイトに反映されました
   - **赤の ✗** → エラー（クリックしてログを確認）

---

## よくあるトラブルと対処法

### サイトにアクセスしても変わっていない

→ ブラウザのキャッシュが残っている可能性があります。  
　`Ctrl + Shift + R`（Macは `Cmd + Shift + R`）で強制リロードしてください。

### Actionsで赤い ✗ が出た

→ Actionsのログをクリックして「Deploy via FTP」のところを確認します。  
　よくある原因：
- Secretsの入力ミス（スペースが入っているなど）
- `FTP_SERVER_DIR` の末尾の `/` が抜けている

### `git push` でエラーが出た

→ 以下を確認してください。
- インターネットに繋がっているか
- GitHubにログインしているか（認証エラーの場合）

---

## このプロジェクトのファイル構成

```
fp-project/
├── index.html                  # ホームページ本体
├── style.css                   # デザイン（色・レイアウト・フォントなど）
├── assets/
│   ├── hero-pc.png             # PCサイズのヒーロー画像
│   └── hero-sp.png             # スマホサイズのヒーロー画像
└── .github/
    └── workflows/
        └── deploy.yml          # 自動デプロイの命令書（初回以降は触らない）
```

---

## まとめ：覚えておくことは3つだけ

1. **Claude Codeに指示する** → ファイルが自動で書き変わる
2. **3行のコマンドを実行する** → GitHubに送信される
3. **Actionsのタブで確認する** → ✅ が出ればサイトに反映済み

セットアップさえ済んでいれば、**毎回の作業はこの3ステップだけ**です。
