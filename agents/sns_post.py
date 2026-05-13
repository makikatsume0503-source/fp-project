import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたはSNSマーケティングの専門家です。おうちCFO FP相談サービスの
Threads投稿と、Instagram投稿をChatGPTで作成するための設計図を提供します。

Threads投稿のポイント:
- 500文字以内
- 共感を呼ぶ導入文から始める
- 有益な情報・気づきを提供する
- 親しみやすいトーン
- CTAは控えめに（押しつけない）

Instagram設計図のポイント:
- ChatGPTがすぐに使えるプロンプトを生成する
- 投稿の目的・感情・構成・文体を具体的に指示する
- カルーセル投稿（複数枚）か単枚かを明示する
- ハッシュタグは日本語・英語ミックスで25〜30個"""


class SNSPostAgent(BaseAgent):
    """SNS投稿エージェント。Threads投稿文とInstagram用ChatGPTプロンプト設計図を生成する。"""

    def run(self, topic: str, blog_summary: str = "") -> dict:
        context = f"\n参考（ブログ記事サマリー）: {blog_summary}" if blog_summary else ""
        prompt = f"""以下のテーマでSNS投稿素材を作成してください：

テーマ: {topic}{context}

以下のJSON形式で回答してください:
{{
  "threads_post": "Threads投稿文（500文字以内、改行あり、そのまま投稿できる完成形）",
  "instagram_design": {{
    "format": "カルーセル（○枚）または 単枚",
    "goal": "この投稿で達成したいゴール（保存・シェア・コメント・フォローなど）",
    "target_emotion": "読者に感じてほしい感情（例：共感・安心・驚き・納得）",
    "core_message": "この投稿で伝える1つのメッセージ（1文で）",
    "slide_structure": [
      {{"slide": 1, "role": "表紙", "content": "ここに表示するテキスト・コンセプト"}},
      {{"slide": 2, "role": "問題提起", "content": "内容"}}
    ],
    "tone": "文体・トーンの指示（例：親しみやすい・専門的・体験談風）",
    "must_include": ["必ず含めるキーワードや要素1", "要素2"],
    "avoid": ["避けるべき表現や内容1", "内容2"],
    "visual_direction": "デザイン・配色・フォントの方向性"
  }},
  "chatgpt_prompt": "このInstagram投稿をChatGPTで作成するためのプロンプト（コピペしてそのまま使える完成形）",
  "instagram_hashtags": ["#ハッシュタグ1", "#ハッシュタグ2"],
  "best_posting_time": "おすすめ投稿時間帯と理由",
  "engagement_tips": ["エンゲージメント向上のヒント1", "ヒント2", "ヒント3"]
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=6000,
        )

        result = self.extract_json(raw)
        if result:
            return result
        return {"raw_output": raw, "summary": "JSON解析に失敗しました。raw_outputを参照してください。"}
