import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたはSNSマーケティングの専門家です。おうちCFO FP相談サービスの
ThreadsとInstagram向け投稿を作成します。

Threads投稿のポイント:
- 500文字以内
- 共感を呼ぶ導入文から始める
- 有益な情報・気づきを提供する
- 親しみやすいトーン
- CTAは控えめに（押しつけない）

Instagram投稿のポイント:
- キャプション: 共感→価値提供→行動促進の流れ
- ハッシュタグ: 15〜30個、日本語と英語ミックス
- 絵文字を適度に使用（多用しない）
- 保存・シェアされやすい有益な内容"""


class SNSPostAgent(BaseAgent):
    """SNS投稿エージェント。Threads・Instagram向けの投稿文とハッシュタグを生成する。"""

    def run(self, topic: str, blog_summary: str = "") -> dict:
        context = f"\n参考（ブログ記事サマリー）: {blog_summary}" if blog_summary else ""
        prompt = f"""以下のテーマでThreadsとInstagram向けの投稿を作成してください：

テーマ: {topic}{context}

以下のJSON形式で回答してください:
{{
  "threads_post": "Threads投稿文（500文字以内、改行あり）",
  "instagram_caption": "Instagramキャプション（絵文字含む、改行あり）",
  "instagram_hashtags": ["#ハッシュタグ1", "#ハッシュタグ2"],
  "image_concept": "投稿に合う画像のコンセプト説明",
  "best_posting_time": "おすすめ投稿時間帯",
  "engagement_tips": ["エンゲージメント向上のヒント1", "ヒント2"]
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=4000,
        )

        result = self.extract_json(raw)
        if result:
            return result
        return {"raw_output": raw, "summary": "JSON解析に失敗しました。raw_outputを参照してください。"}
