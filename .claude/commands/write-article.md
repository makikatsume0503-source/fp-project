# 記事執筆スキル（おうちCFO FP相談）

このスキルは `index.html` のCOLUMNセクションに追加するコラム記事を執筆します。

## 使い方

```
/write-article <テーマ> [タグ]
```

例:
- `/write-article 教育費の積み立て方法`
- `/write-article ふるさと納税の活用法 家計設計`

引数なしで実行すると、テーマとタグの入力を促します。

---

## 指示

ユーザーから記事テーマ（と任意でタグ）を受け取り、以下の形式でコラム記事を執筆してください。

### サイトのトーン・スタイル

- 対象読者: 共働き・子育て世帯。収入に余裕はあるが、お金の使い方・増やし方に迷いがある家庭
- 文体: 丁寧語（です・ます調）。押しつけがましくなく、寄り添うトーン
- キーワード: 教育費、老後資金、NISA、iDeCo、家計設計、資産形成、クレジットカード、ポイント活用
- ブランドカラー: ネイビー（#1a2e4a）・ゴールド（#b8973a）

### 既存タグ（いずれかを選ぶか、新規作成）

- 家計設計
- 資産形成
- ポイント活用

### 出力形式

以下の2つを出力してください。

#### 1. カード用スニペット（index.html に貼り付ける `<article>` タグ）

```html
<article class="column-card">
  <div class="column-card__meta">
    <span class="column-tag">{タグ}</span>
    <time datetime="{YYYY-MM-DD}">{YYYY.MM.DD}</time>
  </div>
  <h3 class="column-card__title">{タイトル（30文字以内）}</h3>
  <p class="column-card__excerpt">{本文抜粋（80〜100文字）}</p>
  <a href="#" class="column-link">続きを読む →</a>
</article>
```

#### 2. 記事本文（将来の記事ページ用・Markdown形式）

- 見出し（H2・H3）を使った読みやすい構成
- 800〜1200字程度
- 専門用語には簡単な補足を入れる
- 最後に「おうちCFOに相談する」への誘導文を1段落加える

---

出力後、`index.html` のCOLUMNセクション（`.column-grid` 内）に `<article>` スニペットを追加するか確認してください。OKなら `index.html` を編集し、コミットします。
