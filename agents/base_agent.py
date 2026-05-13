import json
import re
import anthropic
from typing import Optional

# おうちCFO ビジネスコンテキスト（全エージェントで共有・キャッシュ）
BUSINESS_CONTEXT = """
あなたは「おうちCFO」FP相談サービスのマーケティング・コンテンツ制作アシスタントです。

## サービス概要
- サービス名: おうちCFO FP相談
- 担当者: 勝目麻希（ファイナンシャルプランナー）
- URL: https://fp-makikatsume.com/
- ターゲット: 共働き・子育て世帯
- 専門領域: 教育費・老後資金・家計設計・資産形成・NISA・iDeCo・クレジットカード/ポイント活用

## ブランドトーン
- 親しみやすく、専門的で信頼感がある
- 家庭の未来に寄り添う姿勢
- 専門用語をやさしく整理して伝える
- 共働き・子育て世帯の具体的な悩みに寄り添う
- 押しつけがましくなく、選択肢を整理するスタンス

## 競合との差別化ポイント
- 家庭単位で捉える「おうちCFO」というコンセプト
- 資産形成だけでなく日常家計も含めたトータルサポート
- クレジットカード・ポイント活用まで含む実践的アドバイス
"""

MODEL = "claude-opus-4-7"


class BaseAgent:
    """全エージェントの基底クラス。Claude API 呼び出しの共通ロジックを提供する。"""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def _system_blocks(self, agent_prompt: str) -> list:
        """ビジネスコンテキスト（キャッシュ対象）＋エージェント固有プロンプトを返す。"""
        return [
            {
                "type": "text",
                "text": BUSINESS_CONTEXT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": agent_prompt,
            },
        ]

    def call(
        self,
        prompt: str,
        system_prompt: str,
        tools: Optional[list] = None,
        max_tokens: int = 8000,
    ) -> str:
        """Claude を呼び出し、最終テキストを返す。サーバーサイドツールの pause_turn も処理する。"""
        params = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "thinking": {"type": "adaptive"},
            "system": self._system_blocks(system_prompt),
            "messages": [{"role": "user", "content": prompt}],
        }
        if tools:
            params["tools"] = tools

        messages = params["messages"].copy()

        while True:
            with self.client.messages.stream(**params) as stream:
                response = stream.get_final_message()

            if response.stop_reason in ("end_turn", "max_tokens"):
                break

            # サーバーサイドツールがイテレーション上限に達した場合は継続
            if response.stop_reason == "pause_turn":
                messages = messages + [
                    {"role": "assistant", "content": response.content}
                ]
                params["messages"] = messages
                continue

            break

        text_parts = [b.text for b in response.content if b.type == "text"]
        return "\n".join(text_parts).strip()

    @staticmethod
    def extract_json(raw: str) -> dict | None:
        """マークダウンコードブロックやテキストに埋め込まれたJSONを抽出してパースする。"""
        # そのままパース（Claude がクリーンなJSONを返した場合）
        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            pass
        # コードブロック内を試す
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 先頭の { から末尾の } を試す
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            candidate = raw[start:end]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # 文字列内の生の改行をエスケープして再試行
                fixed = re.sub(r'(?<!\\)\n', r'\\n', candidate)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        return None

    def call_json(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int = 8000,
    ) -> str:
        """JSON 形式で回答するよう指示して Claude を呼び出す。"""
        json_prompt = prompt + "\n\n必ずJSONのみを出力し、コードブロックや説明文は不要です。"
        return self.call(prompt=json_prompt, system_prompt=system_prompt, max_tokens=max_tokens)
