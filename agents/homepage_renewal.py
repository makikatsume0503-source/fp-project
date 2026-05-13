import json
from pathlib import Path
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたはWebデザインとSEOの専門家です。おうちCFO FP相談サービスの
ホームページのリニューアル提案を行います。

分析・提案のポイント:
- 現状のコンテンツ・構成・SEOの分析
- ターゲット（共働き・子育て世帯）への訴求力の評価
- UI/UX改善提案（情報設計・CTA配置・視覚的階層）
- SEO改善（タイトル・メタ・見出し・コンテンツ）
- 新規コンテンツセクションの提案
- コンバージョン率向上のための具体的な改善案"""

INDEX_HTML_PATH = Path(__file__).parent.parent / "index.html"


class HomepageRenewalAgent(BaseAgent):
    """ホームページリニューアルエージェント。現状のHTMLを分析し、改善提案と新HTMLを生成する。"""

    def run(self, focus: str = "総合リニューアル") -> dict:
        current_html = ""
        if INDEX_HTML_PATH.exists():
            current_html = INDEX_HTML_PATH.read_text(encoding="utf-8")

        html_section = f"\n\n現在のindex.html:\n```html\n{current_html}\n```" if current_html else ""

        prompt = f"""おうちCFO FP相談サービスのホームページをリニューアルしてください。

リニューアルフォーカス: {focus}{html_section}

以下のJSON形式で回答してください:
{{
  "current_analysis": {{
    "strengths": ["現状の強み1", "強み2"],
    "weaknesses": ["現状の課題1", "課題2"],
    "seo_score": "現状SEO評価（S/A/B/C）",
    "conversion_issues": ["コンバージョン課題1", "課題2"]
  }},
  "recommendations": [
    {{
      "area": "改善エリア",
      "priority": "高/中/低",
      "action": "具体的なアクション",
      "expected_impact": "期待される効果"
    }}
  ],
  "new_sections": [
    {{
      "section_name": "セクション名",
      "purpose": "目的",
      "content_concept": "コンテンツ概要"
    }}
  ],
  "seo_improvements": {{
    "title": "改善後タイトルタグ",
    "meta_description": "改善後メタディスクリプション",
    "h1": "改善後H1",
    "schema_additions": ["追加すべき構造化データ"]
  }},
  "new_html_sections": "追加・改善すべきHTMLセクションのコード（重要箇所のみ）",
  "copywriting_improvements": [
    {{
      "location": "箇所",
      "current": "現状のコピー",
      "improved": "改善案"
    }}
  ],
  "summary": "リニューアル提案の総括"
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=12000,
        )

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(raw[start:end])
                except json.JSONDecodeError:
                    pass
        return {"raw_output": raw, "summary": "JSON解析に失敗しました。raw_outputを参照してください。"}
