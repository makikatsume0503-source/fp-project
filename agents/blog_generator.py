import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたはSEOに強いブログライターです。おうちCFO FP相談サービスのブログ記事を作成します。

記事の方針:
- ターゲット: 共働き・子育て世帯（30〜40代）
- トーン: 親しみやすく、専門的で信頼感がある
- SEO: 検索意図に合ったキーワードを自然に盛り込む
- 構成: 導入→本文（見出し付き）→まとめ→CTA
- 文字数: 1500〜2500文字程度
- 専門用語はわかりやすく解説する
- 読者の悩みに共感し、具体的な解決策を提示する"""


class BlogGeneratorAgent(BaseAgent):
    """ブログ生成エージェント。SEO最適化されたブログ記事を生成する。"""

    def run(self, topic: str, keywords: list[str] | None = None) -> dict:
        kw_str = "、".join(keywords) if keywords else "自動選定"
        prompt = f"""以下のテーマでブログ記事を作成してください：

テーマ: {topic}
SEOキーワード（参考）: {kw_str}

以下のJSON形式で回答してください:
{{
  "title": "記事タイトル（32文字以内、SEOキーワード含む）",
  "meta_description": "メタディスクリプション（120文字以内）",
  "seo_keywords": ["キーワード1", "キーワード2", "キーワード3"],
  "outline": [
    {{"heading": "見出し", "summary": "内容サマリー"}}
  ],
  "content": "## 見出し1\\n\\n本文...\\n\\n## 見出し2\\n\\n本文...（マークダウン形式の全文）",
  "cta": "記事末尾のCTAテキスト",
  "summary": "記事の要約（SNS投稿等に使用）"
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=10000,
        )

        result = self.extract_json(raw)
        if result:
            return result
        return {"raw_output": raw, "summary": "JSON解析に失敗しました。raw_outputを参照してください。"}
