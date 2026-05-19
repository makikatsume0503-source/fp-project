import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたは競合調査の専門家です。日本のFP（ファイナンシャルプランナー）相談市場を調査し、
おうちCFO FP相談サービスの競合分析・差別化戦略を提供します。

調査のポイント:
- 競合FPのサービス内容・料金・ターゲット層・強み
- おうちCFOとの差別化ポイントの発見
- 市場トレンドとターゲット層（共働き・子育て世帯）のニーズ
- 具体的な改善提案と戦略的推薦事項

必ず日本語で回答し、おうちCFO FP相談の視点で分析してください。"""

WEB_SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
}


class CompetitiveResearchAgent(BaseAgent):
    """競合調査エージェント。Web検索で日本のFP市場を調査し、戦略的インサイトを返す。"""

    def run(self, topic: str = "日本のFP相談サービス競合調査") -> dict:
        prompt = f"""以下のテーマで競合調査を実施してください：

テーマ: {topic}

調査内容:
1. 日本の主要FP相談サービス・競合他社（個人FP、法人FPサービス問わず）の調査
2. 各競合のサービス内容、料金体系、ターゲット層、強み・弱みの分析
3. 共働き・子育て世帯向けFP相談市場のトレンド
4. おうちCFO FP相談との差別化ポイントと改善機会

調査結果を以下のJSON形式で回答してください:
{{
  "competitors": [
    {{
      "name": "競合名",
      "service_overview": "サービス概要",
      "target_audience": "ターゲット層",
      "pricing": "料金体系",
      "strengths": ["強み1", "強み2"],
      "weaknesses": ["弱み1", "弱み2"]
    }}
  ],
  "market_trends": ["トレンド1", "トレンド2"],
  "differentiation_opportunities": ["差別化機会1", "差別化機会2"],
  "recommendations": ["推薦事項1", "推薦事項2"],
  "summary": "総合分析サマリー"
}}"""

        raw = self.call(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            tools=[WEB_SEARCH_TOOL],
            max_tokens=8000,
        )

        result = self.extract_json(raw)
        if result:
            return result
        return {"raw_output": raw, "summary": "JSON解析に失敗しました。raw_outputを参照してください。"}
