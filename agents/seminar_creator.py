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

        data = self.extract_json(raw)
        if not data:
            return {"raw_output": raw, "summary": "JSON解析に失敗しました。"}

        pptx_path = self._build_pptx(data)
        data["pptx_path"] = str(pptx_path)
        return data

    def _build_pptx(self, data: dict) -> Path:
        from pptx import Presentation
        from pptx.util import Inches, Pt, Emu
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches

        # カラーパレット
        NAVY    = RGBColor(0x1A, 0x2B, 0x4A)
        NAVY2   = RGBColor(0x22, 0x3A, 0x5E)
        GOLD    = RGBColor(0xC8, 0xA9, 0x6E)
        WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
        LGRAY   = RGBColor(0xF7, 0xF4, 0xEF)
        DGRAY   = RGBColor(0x44, 0x44, 0x44)
        MGRAY   = RGBColor(0x88, 0x88, 0x88)
        ACCENT2 = RGBColor(0x4A, 0x90, 0xD9)

        W = Inches(13.33)
        H = Inches(7.5)

        prs = Presentation()
        prs.slide_width = W
        prs.slide_height = H
        blank = prs.slide_layouts[6]
        slides_data = data.get("slides", [])
        total = len(slides_data)

        def add_rect(slide, x, y, w, h, color, line=False):
            from pptx.util import Emu
            s = slide.shapes.add_shape(1, x, y, w, h)
            s.fill.solid()
            s.fill.fore_color.rgb = color
            if line:
                s.line.color.rgb = color
                s.line.width = Pt(0.5)
            else:
                s.line.fill.background()
            return s

        def add_text(slide, text, x, y, w, h, size, bold=False, color=None, align=PP_ALIGN.LEFT, wrap=True):
            tb = slide.shapes.add_textbox(x, y, w, h)
            tf = tb.text_frame
            tf.word_wrap = wrap
            p = tf.paragraphs[0]
            p.alignment = align
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color or DGRAY
            return tb

        def add_para(tf, text, size, bold=False, color=None, align=PP_ALIGN.LEFT, space_before=4):
            from pptx.util import Pt as pt2
            p = tf.add_paragraph()
            p.alignment = align
            p.space_before = pt2(space_before)
            r = p.add_run()
            r.text = text
            r.font.size = pt2(size)
            r.font.bold = bold
            r.font.color.rgb = color or DGRAY
            return p

        def add_footer(slide, slide_num, total_num, title_text="おうちCFO FP相談"):
            # フッターライン
            add_rect(slide, Inches(0), Inches(7.15), W, Inches(0.04), GOLD)
            # スライド番号
            add_text(slide, f"{slide_num} / {total_num}", Inches(12.3), Inches(7.2),
                     Inches(0.9), Inches(0.28), 9, color=MGRAY, align=PP_ALIGN.RIGHT)
            # フッターテキスト
            add_text(slide, title_text, Inches(0.3), Inches(7.2),
                     Inches(5), Inches(0.28), 9, color=MGRAY)

        for idx, sd in enumerate(slides_data, 1):
            slide = prs.slides.add_slide(blank)
            slide_type  = sd.get("type", "content")
            title_text  = sd.get("title", "")
            content     = sd.get("content", [])
            notes_text  = sd.get("speaker_notes", "")

            # ======================================================
            # タイトルスライド
            # ======================================================
            if slide_type == "title":
                # 背景全面ネイビー
                add_rect(slide, Inches(0), Inches(0), W, H, NAVY)
                # 左側ゴールドアクセントバー
                add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, GOLD)
                # 右下装飾三角形代わりのゴールドブロック
                add_rect(slide, Inches(10.5), Inches(5.8), Inches(2.83), Inches(1.7), NAVY2)
                add_rect(slide, Inches(12.0), Inches(6.5), Inches(1.33), Inches(1.0), GOLD)

                # サービスタグライン
                tag = data.get("target_audience", "共働き・子育て世帯向け")[:30]
                add_text(slide, tag, Inches(0.7), Inches(1.6), Inches(10), Inches(0.5),
                         12, color=GOLD, align=PP_ALIGN.LEFT)

                # メインタイトル
                tb = slide.shapes.add_textbox(Inches(0.7), Inches(2.1), Inches(11.5), Inches(2.2))
                tf = tb.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT
                r = p.add_run()
                r.text = data.get("title", title_text)
                r.font.size = Pt(42)
                r.font.bold = True
                r.font.color.rgb = WHITE

                # ゴールド区切りライン
                add_rect(slide, Inches(0.7), Inches(4.45), Inches(3.5), Inches(0.06), GOLD)

                # サブタイトル
                if data.get("subtitle"):
                    add_text(slide, data["subtitle"], Inches(0.7), Inches(4.65),
                             Inches(11), Inches(0.7), 20, color=GOLD)

                # 発表者名
                presenter = "ファイナンシャルプランナー　勝目麻希"
                add_text(slide, presenter, Inches(0.7), Inches(5.6),
                         Inches(8), Inches(0.5), 14, color=RGBColor(0xCC, 0xCC, 0xCC))

            # ======================================================
            # アジェンダスライド
            # ======================================================
            elif slide_type == "agenda":
                add_rect(slide, Inches(0), Inches(0), W, H, LGRAY)
                add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, NAVY)
                # ヘッダー帯
                add_rect(slide, Inches(0.18), Inches(0), W, Inches(1.4), NAVY)
                add_text(slide, "AGENDA", Inches(0.5), Inches(0.1), Inches(3), Inches(0.5),
                         11, color=GOLD, bold=True)
                add_text(slide, title_text, Inches(0.5), Inches(0.55), Inches(12), Inches(0.75),
                         26, bold=True, color=WHITE)

                # アジェンダ番号付きリスト
                cols = (content[:len(content)//2 + len(content)%2],
                        content[len(content)//2 + len(content)%2:])
                circle_colors = [NAVY, NAVY2, GOLD, ACCENT2, NAVY, NAVY2]
                for ci, col in enumerate(cols):
                    x = Inches(0.7 + ci * 6.3)
                    for ri, item in enumerate(col):
                        y = Inches(1.7 + ri * 0.92)
                        num = ri + 1 + ci * len(cols[0])
                        # 丸ナンバー
                        add_rect(slide, x, y + Inches(0.03), Inches(0.52), Inches(0.52),
                                 circle_colors[(num-1) % len(circle_colors)])
                        add_text(slide, str(num), x, y, Inches(0.52), Inches(0.58),
                                 16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
                        # テキスト
                        add_text(slide, item, x + Inches(0.62), y + Inches(0.04),
                                 Inches(5.5), Inches(0.5), 15, color=NAVY, bold=(ri == 0))
                add_footer(slide, idx, total)

            # ======================================================
            # コンテンツスライド（汎用）
            # ======================================================
            else:
                bg_color = LGRAY if slide_type not in ("summary", "cta") else NAVY
                add_rect(slide, Inches(0), Inches(0), W, H, bg_color)

                if slide_type in ("summary", "cta"):
                    # ===== まとめ・CTA スライド =====
                    add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, GOLD)
                    add_rect(slide, Inches(0.18), Inches(0), W, Inches(1.4), NAVY2)
                    add_text(slide, "SUMMARY" if slide_type == "summary" else "NEXT STEP",
                             Inches(0.5), Inches(0.1), Inches(4), Inches(0.5),
                             11, color=GOLD, bold=True)
                    add_text(slide, title_text, Inches(0.5), Inches(0.55),
                             Inches(12), Inches(0.75), 26, bold=True, color=WHITE)

                    # カードレイアウト
                    card_colors = [RGBColor(0x22, 0x3A, 0x5E), RGBColor(0x1E, 0x35, 0x58),
                                   RGBColor(0x26, 0x40, 0x66), RGBColor(0x1A, 0x30, 0x52)]
                    per_row = 3 if len(content) >= 5 else 2
                    for ci, item in enumerate(content):
                        row, col = ci // per_row, ci % per_row
                        cw = Inches(12.5 / per_row)
                        cx = Inches(0.4) + col * (cw + Inches(0.15))
                        cy = Inches(1.65) + row * Inches(2.3)
                        add_rect(slide, cx, cy, cw, Inches(2.1), card_colors[ci % 4])
                        # カード番号
                        add_rect(slide, cx, cy, Inches(0.45), Inches(0.45), GOLD)
                        add_text(slide, str(ci + 1), cx, cy, Inches(0.45), Inches(0.45),
                                 13, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
                        # カードテキスト
                        tb = slide.shapes.add_textbox(cx + Inches(0.1), cy + Inches(0.55),
                                                      cw - Inches(0.2), Inches(1.45))
                        tf = tb.text_frame
                        tf.word_wrap = True
                        p = tf.paragraphs[0]
                        p.alignment = PP_ALIGN.LEFT
                        r = p.add_run()
                        r.text = item
                        r.font.size = Pt(14)
                        r.font.color.rgb = WHITE
                else:
                    # ===== 通常コンテンツスライド =====
                    # ヘッダーバー（ネイビー）
                    add_rect(slide, Inches(0), Inches(0), W, Inches(1.3), NAVY)
                    # 左アクセントバー
                    add_rect(slide, Inches(0), Inches(0), Inches(0.18), H, GOLD)
                    # スライドタイプラベル
                    type_label = {"content": "POINT", "step": "STEP",
                                  "comparison": "CHECK", "case": "CASE"}.get(slide_type, "INFO")
                    add_text(slide, type_label, Inches(0.4), Inches(0.08),
                             Inches(2), Inches(0.4), 10, color=GOLD, bold=True)
                    # タイトル
                    add_text(slide, title_text, Inches(0.4), Inches(0.48),
                             Inches(12.5), Inches(0.75), 26, bold=True, color=WHITE)

                    # コンテンツエリア
                    if len(content) <= 4:
                        # ポイントカード形式
                        for ci, item in enumerate(content):
                            cy = Inches(1.5) + ci * Inches(1.35)
                            # 左ゴールドナンバーバー
                            add_rect(slide, Inches(0.4), cy, Inches(0.6), Inches(1.1),
                                     GOLD if ci % 2 == 0 else NAVY)
                            add_text(slide, str(ci + 1), Inches(0.4), cy + Inches(0.22),
                                     Inches(0.6), Inches(0.65), 22, bold=True,
                                     color=NAVY if ci % 2 == 0 else WHITE,
                                     align=PP_ALIGN.CENTER)
                            # テキストボックス
                            add_rect(slide, Inches(1.1), cy, Inches(11.8), Inches(1.1),
                                     WHITE)
                            tb = slide.shapes.add_textbox(
                                Inches(1.25), cy + Inches(0.18), Inches(11.5), Inches(0.8))
                            tf = tb.text_frame
                            tf.word_wrap = True
                            p = tf.paragraphs[0]
                            r = p.add_run()
                            r.text = item
                            r.font.size = Pt(18)
                            r.font.color.rgb = NAVY
                    else:
                        # 箇条書き形式（5項目以上）
                        tb = slide.shapes.add_textbox(
                            Inches(0.55), Inches(1.5), Inches(12.4), Inches(5.7))
                        tf = tb.text_frame
                        tf.word_wrap = True
                        for ci, item in enumerate(content):
                            p = tf.paragraphs[0] if ci == 0 else tf.add_paragraph()
                            p.space_before = Pt(8)
                            r = p.add_run()
                            r.text = f"▶  {item}"
                            r.font.size = Pt(18)
                            r.font.color.rgb = NAVY if ci % 2 == 0 else NAVY2

                add_footer(slide, idx, total)

            # 講師メモ
            if notes_text:
                slide.notes_slide.notes_text_frame.text = notes_text

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = data.get("title", "seminar")[:30].replace("/", "_").replace(" ", "_")
        filename = f"seminar_{safe_title}_{timestamp}.pptx"
        path = OUTPUT_DIR / filename
        prs.save(str(path))
        return path
