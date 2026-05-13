import json
from datetime import datetime
from pathlib import Path
from .base_agent import BaseAgent

SYSTEM_PROMPT = """あなたはセミナー講師とプレゼンテーションデザインの専門家です。
おうちCFO FP相談サービスのセミナー資料（パワーポイント）を作成します。

スライド設計の方針:
- 対象: 共働き・子育て世帯（30〜40代）
- 構成: タイトル→アジェンダ→本編（各トピック）→まとめ→CTA
- 1スライドに1メッセージ
- 具体的な数字・事例を活用
- 行動を促す締めくくり
- 視覚的にわかりやすい図解・箇条書き"""

OUTPUT_DIR = Path(__file__).parent.parent / "output"


class SeminarCreatorAgent(BaseAgent):
    """セミナー作成エージェント。Claude でスライド構成を生成し、python-pptx で実際のPPTXを作成する。"""

    def run(self, topic: str, slide_count: int = 15) -> dict:
        prompt = f"""以下のテーマでセミナー用スライド構成を作成してください：

テーマ: {topic}
スライド枚数: 約{slide_count}枚

以下のJSON形式で回答してください:
{{
  "title": "セミナータイトル",
  "subtitle": "サブタイトル",
  "target_audience": "想定参加者",
  "duration_minutes": 60,
  "learning_objectives": ["学習目標1", "学習目標2", "学習目標3"],
  "slides": [
    {{
      "slide_number": 1,
      "type": "title",
      "title": "スライドタイトル",
      "content": ["本文1", "本文2"],
      "speaker_notes": "講師メモ",
      "visual_suggestion": "視覚要素の提案"
    }}
  ],
  "summary": "セミナー概要"
}}"""

        raw = self.call_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=12000,
        )

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    data = json.loads(raw[start:end])
                except json.JSONDecodeError:
                    return {"raw_output": raw, "summary": "JSON解析に失敗しました。"}
            else:
                return {"raw_output": raw, "summary": "JSON解析に失敗しました。"}

        pptx_path = self._build_pptx(data)
        data["pptx_path"] = str(pptx_path)
        return data

    def _build_pptx(self, data: dict) -> Path:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        NAVY = RGBColor(0x1A, 0x2B, 0x4A)
        WHITE = RGBColor(0xFF, 0xFF, 0xFF)
        ACCENT = RGBColor(0xC8, 0xA96E, 0x00) if False else RGBColor(0xC8, 0xA9, 0x6E)

        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        blank_layout = prs.slide_layouts[6]

        for slide_data in data.get("slides", []):
            slide = prs.slides.add_slide(blank_layout)

            bg = slide.background
            fill = bg.fill
            fill.solid()
            fill.fore_color.rgb = WHITE

            title_text = slide_data.get("title", "")
            content_items = slide_data.get("content", [])
            notes_text = slide_data.get("speaker_notes", "")
            slide_type = slide_data.get("type", "content")

            if slide_type == "title":
                fill.fore_color.rgb = NAVY
                title_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.33), Inches(2))
                tf = title_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                run = p.add_run()
                run.text = data.get("title", title_text)
                run.font.size = Pt(40)
                run.font.bold = True
                run.font.color.rgb = WHITE

                if data.get("subtitle"):
                    sub_box = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11.33), Inches(1))
                    tf2 = sub_box.text_frame
                    p2 = tf2.paragraphs[0]
                    p2.alignment = PP_ALIGN.CENTER
                    r2 = p2.add_run()
                    r2.text = data["subtitle"]
                    r2.font.size = Pt(22)
                    r2.font.color.rgb = ACCENT
            else:
                title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.33), Inches(1))
                tf = title_box.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = title_text
                run.font.size = Pt(28)
                run.font.bold = True
                run.font.color.rgb = NAVY

                line = slide.shapes.add_shape(
                    1, Inches(0.5), Inches(1.35), Inches(12.33), Inches(0.05)
                )
                line.fill.solid()
                line.fill.fore_color.rgb = ACCENT
                line.line.fill.background()

                if content_items:
                    content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(11.93), Inches(5.3))
                    tf2 = content_box.text_frame
                    tf2.word_wrap = True
                    for i, item in enumerate(content_items):
                        p2 = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
                        p2.space_before = Pt(6)
                        run2 = p2.add_run()
                        run2.text = f"• {item}" if not item.startswith("•") else item
                        run2.font.size = Pt(20)
                        run2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

            if notes_text:
                notes_slide = slide.notes_slide
                tf_notes = notes_slide.notes_text_frame
                tf_notes.text = notes_text

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = data.get("title", "seminar")[:30].replace("/", "_").replace(" ", "_")
        filename = f"seminar_{safe_title}_{timestamp}.pptx"
        path = OUTPUT_DIR / filename
        prs.save(str(path))
        return path
