import json
import re
from .base_agent import BaseAgent

WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search"}

SYSTEM_PROMPT = """あなたは金融専門メディアのSEOライター兼ファクトチェッカーです。
おうちCFO FP相談の勝目麻希さんが執筆するブログ記事を代筆します。

## 文体・トーン（厳守）
- 親しみやすく、専門的で信頼感がある
- 「〜ですね」「〜でしょう」など読者に語りかける文体
- 専門用語は必ず直後にカッコ書きで補足
- 難しい内容も具体的な数字・事例・比較表でわかりやすく伝える
- 共働き・子育て世帯の日常にひきつけた具体例を必ず入れる

## 禁止事項（絶対に使わない）
- 「絶対に」「最強の」「必ず儲かる」「間違いない」「確実に」などの断定表現
- 根拠のない数字や事実
- 出典のないデータ・統計
- 一方的なメリット訴求（必ずデメリット・注意点もセットで書く）

## SEO要件
- タイトル（H1）: 検索意図に合った主要キーワードをタイトル前半に配置、32文字以内
- H2見出し: 副キーワード・関連語を自然に含む、疑問形や数字入りで興味を引く
- H3見出し: 具体的・簡潔に
- 導入文: 最初の100文字以内に主要キーワードを自然に含める
- FAQセクション: 検索される質問形式で3〜5問（PAA対策）
- 内部リンク提案: 関連コンテンツへの自然な誘導

## 記事構成
導入（読者の悩みに共感）→ 本論（H2×3〜4、各H2にH3×2〜3）→ FAQ → まとめ → CTA

## 見出し構造ルール（厳守）
- H1（記事タイトル）の直後にH2を置かない。H1直後は必ずリード文（p要素）から始める
- 「はじめに」「〜そんな悩みありませんか？」などのイントロH2は作らない
- リード文（2〜3段落）のあとに最初のH2（本論第1章）を置く

## データ・引用表記ルール（メディア業界標準）
- 金融庁・国税庁・厚生労働省・総務省統計局・文部科学省・こども家庭庁などの官公庁一次資料のみ使用
- 民間メディア（ダイヤモンドZAi・東洋経済・日経等）は参照元として使用禁止
- 数字・統計を参照した場合: 文中に「（参照：発行機関名｜資料名）」を明記
- 図・表・画像を転載・直接引用した場合: キャプションに「出典：発行機関名｜資料名」を明記
- 筆者が独自に作成した図解: キャプションに「筆者作成」と明記
- 情報の鮮度を明示（「〇〇年〇月時点」）"""


STYLE_ANALYSIS_PROMPT = """以下の検索結果を参考に、勝目麻希さんの文体・記事スタイルを分析してください。

分析ポイント:
1. 導入文のパターン（どう読者の共感を掴むか）
2. 専門用語の説明スタイル
3. 具体例・数字の使い方
4. 段落の長さ・テンポ
5. CTAや締めくくりのパターン

分析結果を100文字程度で簡潔にまとめてください。"""


class ArticleGeneratorAgent(BaseAgent):
    """高品質記事生成エージェント。文体分析・最新データ収集・SEO最適化・SVG図解生成を一括で行う。"""

    def run(self, topic: str, primary_keyword: str = "", target_length: int = 3500) -> dict:
        if not primary_keyword:
            primary_keyword = topic[:20]

        print("  [1/3] 文体分析・最新データ収集中...")
        research = self._research(topic, primary_keyword)

        print("  [2/3] 記事本文生成中（3,000〜4,000文字）...")
        article = self._generate_article(topic, primary_keyword, research, target_length)

        print("  [3/3] アイキャッチ・図解・HTMLページ生成中...")
        result = self._build_output(topic, primary_keyword, article)

        return result

    # ------------------------------------------------------------------ #
    # Step 1: 文体分析 + 最新データ収集
    # ------------------------------------------------------------------ #
    def _research(self, topic: str, keyword: str) -> dict:
        prompt = f"""以下の2つを順番にWeb検索してください。

【検索1】勝目麻希 マネイロ OR LIMO FP 記事
→ 記事の文体・構成・トーンを分析する

【検索2】{topic} 金融庁 OR 国税庁 OR 厚生労働省 OR 総務省 2024 OR 2025
→ 最新の公的データ・統計・制度情報を収集する

収集後、以下のJSON形式でまとめてください:
{{
  "style_notes": "文体の特徴（100文字程度）",
  "key_data": [
    {{"fact": "データ・数字・制度内容", "source": "出典機関名", "year": "年度"}}
  ],
  "related_laws": ["関連する法律・制度名"],
  "caution_points": ["読者が誤解しやすいポイント"]
}}"""

        raw = self.call(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            tools=[WEB_SEARCH_TOOL],
            max_tokens=4000,
        )
        result = self.extract_json(raw)
        return result if result else {"style_notes": "", "key_data": [], "related_laws": [], "caution_points": []}

    # ------------------------------------------------------------------ #
    # Step 2: 記事本文生成
    # ------------------------------------------------------------------ #
    def _generate_article(self, topic: str, keyword: str, research: dict, target_length: int) -> dict:
        style_notes = research.get("style_notes", "")
        key_data = json.dumps(research.get("key_data", []), ensure_ascii=False)
        cautions = "、".join(research.get("caution_points", []))

        prompt = f"""以下の条件で記事を執筆してください。

【テーマ】{topic}
【主要キーワード】{keyword}
【目標文字数】{target_length}文字（3,000〜4,000文字）
【文体参考】{style_notes}
【使用すべきデータ】{key_data}
【注意すべき誤解】{cautions}

【SEO要件】
- タイトル（H1）: 「{keyword}」を前半に入れ、32文字以内で検索意図に刺さるタイトル
- メタディスクリプション: 120文字以内、キーワード含む
- H2見出し: 3〜4個、副キーワード・数字・疑問形を活用
- H3見出し: 各H2に2〜3個

【必須要素】
1. 導入文: 読者の悩みに共感する問いかけから始める（100文字以内に主要KW含む）
2. 本論: メリットとデメリット・注意点を必ずセットで記述
3. 数字・統計を文中で使った場合: 「（参照：発行機関名｜資料名）」を直後に明記
   図・表を転載した場合: キャプションに「出典：発行機関名｜資料名」を明記
   筆者作成の図解: キャプションに「筆者作成」のみ（出典・参照は不要）
4. FAQセクション: 検索されやすい質問形式で3問
5. まとめ: 行動を促す締めくくり
6. SVG図解: 記事内に必ず2〜3箇所、以下のいずれかを視覚化する図解をSVGで生成
   - 数字の比較表（例：制度ごとの上限額、コースA/B/Cの違い）
   - 時系列・ステップフロー（例：手続きの流れ、年代別の積み立て推移）
   - 割合・構成（例：費用の内訳、節税効果のイメージ）
   各図解はキャプションに「筆者作成」を明記すること
7. アイキャッチ画像プロンプト: DALL-E/Midjourney用の英語プロンプト

以下のJSON形式で出力してください:
{{
  "title": "SEO最適化タイトル（H1、32文字以内）",
  "meta_description": "メタディスクリプション（120文字以内）",
  "seo_keywords": ["主要KW", "副KW1", "副KW2", "副KW3", "副KW4"],
  "eyecatch_prompt": "DALL-E/Midjourney用英語プロンプト（スタイル・構図・カラー指定含む）",
  "content_markdown": "## 見出し\\n\\n本文...（マークダウン形式、3000〜4000文字）",
  "svg_diagrams": [
    {{
      "insert_after": "挿入する見出しテキスト（H2またはH3）",
      "caption": "図のキャプション（筆者作成は不要、自動付与）",
      "alt": "alt属性テキスト",
      "svg": "<svg>...</svg>"
    }},
    {{省略せず必ず2個目も生成}},
    {{可能であれば3個目も生成}}
  ],
  "faq": [
    {{"question": "Q: 質問文", "answer": "A: 回答文（100〜150文字）"}}
  ],
  "sources": [
    {{"type": "参照 or 出典", "name": "資料名", "organization": "発行機関", "year": "年度", "url": "公式URL（わかる場合）"}}
  ],
  "internal_link_suggestions": [
    {{"anchor": "リンクテキスト", "target_topic": "リンク先記事テーマ"}}
  ],
  "word_count_estimate": 3500
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=12000,
        )
        result = self.extract_json(raw)
        return result if result else {"content_markdown": raw}

    # ------------------------------------------------------------------ #
    # Step 3: HTMLページ生成
    # ------------------------------------------------------------------ #
    def _build_output(self, topic: str, keyword: str, article: dict) -> dict:
        slug = self._make_slug(article.get("title", topic))
        html = self._render_html(article, slug)

        out_path = f"/home/user/fp-project/blog/{slug}.html"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            article["html_path"] = out_path
        except Exception as e:
            article["html_error"] = str(e)

        article["slug"] = slug
        article["summary"] = article.get("meta_description", "")
        return article

    # ------------------------------------------------------------------ #
    # HTML レンダリング
    # ------------------------------------------------------------------ #
    def _render_html(self, article: dict, slug: str) -> str:
        title = article.get("title", "")
        meta_desc = article.get("meta_description", "")
        keywords_str = ", ".join(article.get("seo_keywords", []))
        content_md = article.get("content_markdown", "")
        svg_diagrams = article.get("svg_diagrams", [])
        faq_items = article.get("faq", [])
        sources = article.get("sources", [])
        eyecatch_prompt = article.get("eyecatch_prompt", "")

        content_html = self._md_to_html(content_md, svg_diagrams)

        faq_html = ""
        if faq_items:
            faq_html = '<section class="article-faq"><h2>よくある質問</h2>'
            for item in faq_items:
                q = item.get("question", "")
                a = item.get("answer", "")
                faq_html += f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>'
            faq_html += "</section>"

        sources_html = ""
        if sources:
            items_html = []
            for s in sources:
                stype = s.get("type", "参照")
                org   = s.get("organization", "")
                name  = s.get("name", "")
                year  = s.get("year", "")
                url   = s.get("url", "")
                label = f"{stype}：{org}｜{name}"
                if year:
                    label += f"（{year}）"
                if url:
                    items_html.append(f'<li><a href="{url}" target="_blank" rel="noopener">{label}</a></li>')
                else:
                    items_html.append(f'<li>{label}</li>')
            sources_html = f'<section class="article-sources"><h2>参考資料・出典</h2><ul>{"".join(items_html)}</ul></section>'

        eyecatch_note = f'<!-- アイキャッチ画像プロンプト（DALL-E/Midjourney用）:\n{eyecatch_prompt}\n-->' if eyecatch_prompt else ""

        return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}｜おうちCFO FP相談</title>
  <meta name="description" content="{meta_desc}" />
  <meta name="keywords" content="{keywords_str}" />
  <link rel="canonical" href="https://fp-makikatsume.com/blog/{slug}.html" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{title}｜おうちCFO FP相談" />
  <meta property="og:description" content="{meta_desc}" />
  <meta property="og:url" content="https://fp-makikatsume.com/blog/{slug}.html" />
  <meta property="og:image" content="https://fp-makikatsume.com/assets/hero-pc.png" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "description": "{meta_desc}",
    "author": {{"@type": "Person", "name": "勝目麻希"}},
    "publisher": {{"@type": "Organization", "name": "おうちCFO FP相談"}}
  }}
  </script>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../style.css?v=10" />
  <style>
    .article-wrap {{ max-width: 780px; margin: 0 auto; padding: 56px 24px 80px; }}
    .article-meta {{ display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
    .article-wrap h1 {{ font-size: clamp(1.4rem, 3vw, 1.95rem); line-height: 1.5; margin-bottom: 36px; color: #1a2b4a; }}
    .article-wrap h2 {{ font-size: 1.3rem; font-weight: 700; color: #1a2b4a; margin: 52px 0 16px; padding: 10px 16px; background: #f7f4ef; border-left: 4px solid #c8a96e; border-radius: 0 4px 4px 0; }}
    .article-wrap h3 {{ font-size: 1.05rem; font-weight: 700; color: #1a2b4a; margin: 32px 0 10px; padding-left: 10px; border-left: 2px solid #c8a96e; }}
    .article-wrap p {{ line-height: 1.95; margin-bottom: 18px; color: #333; }}
    .article-wrap ul, .article-wrap ol {{ padding-left: 1.5em; margin-bottom: 18px; }}
    .article-wrap li {{ line-height: 1.85; margin-bottom: 8px; color: #333; }}
    .article-wrap .svg-block {{ margin: 32px 0; text-align: center; }}
    .article-wrap .svg-block svg {{ max-width: 100%; height: auto; }}
    .article-wrap .svg-caption {{ font-size: 0.85rem; color: #666; margin-top: 8px; }}
    .article-faq {{ margin-top: 56px; }}
    .article-faq h2 {{ font-size: 1.3rem; }}
    .faq-item {{ border: 1px solid #e8e0d0; border-radius: 6px; margin-bottom: 12px; overflow: hidden; }}
    .faq-item summary {{ padding: 14px 18px; font-weight: 500; cursor: pointer; color: #1a2b4a; list-style: none; position: relative; padding-right: 40px; }}
    .faq-item summary::after {{ content: '+'; position: absolute; right: 18px; top: 50%; transform: translateY(-50%); font-size: 1.2rem; color: #c8a96e; }}
    .faq-item[open] summary::after {{ content: '−'; }}
    .faq-item p {{ padding: 0 18px 14px; margin: 0; }}
    .article-sources {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #e8e0d0; }}
    .article-sources h2 {{ font-size: 1rem; color: #666; background: none; border: none; padding: 0; margin-bottom: 8px; }}
    .article-sources ul {{ font-size: 0.85rem; color: #888; }}
    .article-cta {{ background: #f7f4ef; border-radius: 8px; padding: 32px 28px; margin-top: 64px; text-align: center; }}
    .article-cta p {{ margin-bottom: 20px; font-weight: 500; color: #1a2b4a; }}
    .article-back {{ display: inline-block; margin-bottom: 28px; color: #c8a96e; text-decoration: none; font-size: 0.9rem; }}
    .article-back:hover {{ opacity: 0.7; }}
    .point-box {{ background: #f0f7ff; border-radius: 6px; padding: 20px 22px; margin: 24px 0; border-left: 3px solid #4a90d9; }}
    .caution-box {{ background: #fff8f0; border-radius: 6px; padding: 20px 22px; margin: 24px 0; border-left: 3px solid #e8944a; }}
  </style>
</head>
<body>
  {eyecatch_note}
  <main>
    <div class="article-wrap">
      <a href="../index.html#column" class="article-back">← コラム一覧に戻る</a>
      <div class="article-meta">
        <span class="column-tag">FP解説</span>
        <time>2026.05.13</time>
        <span style="font-size:0.8rem;color:#888;">監修：勝目麻希（FP）</span>
      </div>
      <h1>{title}</h1>
      <div class="article-content">
{content_html}
      </div>
      {faq_html}
      {sources_html}
      <div class="article-cta">
        <p>記事の内容について、もっと詳しく相談したいですか？<br>おうちCFO FP相談では、共働き・子育て世帯の家計設計を<br>ファイナンシャルプランナー 勝目麻希が丁寧にサポートします。</p>
        <a href="../index.html#contact" class="btn large">初回相談のお申し込み →</a>
      </div>
    </div>
  </main>
  <footer>
    <p>© 2026 おうちCFO FP相談｜勝目麻希</p>
  </footer>
</body>
</html>'''

    # ------------------------------------------------------------------ #
    # Markdown → HTML（SVG挿入対応）
    # ------------------------------------------------------------------ #
    def _md_to_html(self, md: str, svg_diagrams: list) -> str:
        svg_map = {d.get("insert_after", ""): d for d in svg_diagrams}
        lines = md.split("\n")
        html_parts = []
        in_ul = False
        in_ol = False
        last_heading = ""

        def close_list():
            nonlocal in_ul, in_ol
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            if in_ol:
                html_parts.append("</ol>")
                in_ol = False

        def insert_svg_if_any(heading_text: str):
            clean = heading_text.strip()
            for key, diagram in svg_map.items():
                if key and key in clean:
                    svg_code = diagram.get("svg", "")
                    caption = diagram.get("caption", "")
                    alt = diagram.get("alt", "")
                    if svg_code:
                        caption_text = f"{caption}（筆者作成）" if caption else "筆者作成"
                        html_parts.append(
                            f'<div class="svg-block" role="img" aria-label="{alt}">'
                            f'{svg_code}'
                            f'<p class="svg-caption">{caption_text}</p></div>'
                        )
                    break

        for line in lines:
            stripped = line.rstrip()

            if stripped.startswith("### "):
                close_list()
                text = self._inline(stripped[4:])
                html_parts.append(f"<h3>{text}</h3>")
                insert_svg_if_any(stripped[4:])

            elif stripped.startswith("## "):
                close_list()
                text = self._inline(stripped[3:])
                html_parts.append(f"<h2>{text}</h2>")
                insert_svg_if_any(stripped[3:])

            elif stripped.startswith("# "):
                close_list()
                text = self._inline(stripped[2:])
                html_parts.append(f"<h2>{text}</h2>")

            elif re.match(r"^\d+\. ", stripped):
                if in_ul:
                    html_parts.append("</ul>")
                    in_ul = False
                if not in_ol:
                    html_parts.append("<ol>")
                    in_ol = True
                text = self._inline(re.sub(r"^\d+\. ", "", stripped))
                html_parts.append(f"<li>{text}</li>")

            elif stripped.startswith("- ") or stripped.startswith("* "):
                if in_ol:
                    html_parts.append("</ol>")
                    in_ol = False
                if not in_ul:
                    html_parts.append("<ul>")
                    in_ul = True
                text = self._inline(stripped[2:])
                html_parts.append(f"<li>{text}</li>")

            elif stripped.startswith("> "):
                close_list()
                text = self._inline(stripped[2:])
                html_parts.append(f'<div class="point-box"><p>{text}</p></div>')

            elif stripped == "---" or stripped == "***":
                close_list()
                html_parts.append("<hr />")

            elif stripped == "":
                close_list()

            else:
                close_list()
                text = self._inline(stripped)
                html_parts.append(f"<p>{text}</p>")

        close_list()
        return "\n".join(html_parts)

    def _inline(self, text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
        return text

    def _make_slug(self, title: str) -> str:
        import unicodedata
        from datetime import datetime
        normalized = unicodedata.normalize("NFKC", title)
        # ASCII文字・数字・ハイフンのみ残す
        ascii_only = re.sub(r"[^a-zA-Z0-9\s-]", "", normalized)
        slug = re.sub(r"[\s_]+", "-", ascii_only).strip("-").lower()
        slug = slug[:50] if len(slug) > 50 else slug
        if not slug or all(c == "-" for c in slug):
            slug = f"article-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return slug
