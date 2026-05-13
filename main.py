#!/usr/bin/env python3
"""おうちCFO マルチエージェントシステム CLI"""
import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def print_result(result: dict, agent_name: str):
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax

        console = Console()
        console.print(f"\n[bold green]✓ {agent_name} 完了[/bold green]\n")
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
        console.print(Panel(syntax, title=agent_name, border_style="blue"))
    except ImportError:
        print(f"\n=== {agent_name} ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_research(args):
    from agents import CompetitiveResearchAgent
    agent = CompetitiveResearchAgent()
    result = agent.run(topic=args.topic)
    print_result(result, "競合調査エージェント")
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n結果を保存しました: {args.output}")


def cmd_blog(args):
    from agents import BlogGeneratorAgent
    keywords = args.keywords.split(",") if args.keywords else None
    agent = BlogGeneratorAgent()
    result = agent.run(topic=args.topic, keywords=keywords)
    print_result(result, "ブログ生成エージェント")
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n結果を保存しました: {args.output}")


def cmd_sns(args):
    from agents import SNSPostAgent
    agent = SNSPostAgent()
    result = agent.run(topic=args.topic, blog_summary=args.blog_summary or "")
    print_result(result, "SNS投稿エージェント")
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n結果を保存しました: {args.output}")


def cmd_homepage(args):
    from agents import HomepageRenewalAgent
    agent = HomepageRenewalAgent()
    result = agent.run(focus=args.focus or "総合リニューアル")
    print_result(result, "ホームページリニューアルエージェント")
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n結果を保存しました: {args.output}")


def cmd_seminar(args):
    from agents import SeminarCreatorAgent
    agent = SeminarCreatorAgent()
    result = agent.run(topic=args.topic, slide_count=args.slides)
    print_result(result, "セミナー作成エージェント")
    if result.get("pptx_path"):
        print(f"\nPPTXファイル: {result['pptx_path']}")
    if args.output:
        result_copy = {k: v for k, v in result.items() if k != "pptx_path"}
        Path(args.output).write_text(json.dumps(result_copy, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON結果を保存しました: {args.output}")


def cmd_leader(args):
    from agents import LeaderAgent
    agent_list = args.agents.split(",") if args.agents else None
    agent = LeaderAgent()
    result = agent.run(goal=args.goal, agents=agent_list)

    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print("\n[bold magenta]★ リーダーエージェント 統合結果 ★[/bold magenta]\n")
        console.print(f"[bold]ゴール:[/bold] {result['goal']}")
        console.print(f"[bold]使用エージェント:[/bold] {', '.join(result['agents_used'])}\n")
        console.print(Panel(result.get("synthesis", ""), title="統合提言", border_style="magenta"))
    except ImportError:
        print(f"\n=== リーダーエージェント統合結果 ===")
        print(f"ゴール: {result['goal']}")
        print(f"使用エージェント: {', '.join(result['agents_used'])}")
        print(f"\n統合提言:\n{result.get('synthesis', '')}")

    if args.output:
        synthesis = result.pop("synthesis", "")
        result["synthesis"] = synthesis
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n結果を保存しました: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="おうちCFO マルチエージェントシステム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py research --topic "共働き家庭向けFP相談市場"
  python main.py blog --topic "NISAを始める前に確認すべき3つのこと"
  python main.py sns --topic "教育費の積み立て方"
  python main.py homepage --focus "コンバージョン率改善"
  python main.py seminar --topic "共働き家庭のお金の設計図" --slides 15
  python main.py leader --goal "共働き家庭向けNISA活用コンテンツ戦略" --agents blog,sns
  python main.py leader --goal "サービス全体のマーケティング強化"
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_research = sub.add_parser("research", help="競合調査")
    p_research.add_argument("--topic", default="日本のFP相談サービス競合調査", help="調査テーマ")
    p_research.add_argument("--output", help="結果のJSON出力先ファイルパス")
    p_research.set_defaults(func=cmd_research)

    p_blog = sub.add_parser("blog", help="ブログ記事生成")
    p_blog.add_argument("--topic", required=True, help="記事テーマ")
    p_blog.add_argument("--keywords", help="SEOキーワード（カンマ区切り）")
    p_blog.add_argument("--output", help="結果のJSON出力先ファイルパス")
    p_blog.set_defaults(func=cmd_blog)

    p_sns = sub.add_parser("sns", help="SNS投稿作成")
    p_sns.add_argument("--topic", required=True, help="投稿テーマ")
    p_sns.add_argument("--blog-summary", help="参考にするブログ記事のサマリー")
    p_sns.add_argument("--output", help="結果のJSON出力先ファイルパス")
    p_sns.set_defaults(func=cmd_sns)

    p_hp = sub.add_parser("homepage", help="ホームページリニューアル提案")
    p_hp.add_argument("--focus", help="リニューアルのフォーカスエリア")
    p_hp.add_argument("--output", help="結果のJSON出力先ファイルパス")
    p_hp.set_defaults(func=cmd_homepage)

    p_seminar = sub.add_parser("seminar", help="セミナー資料作成（PPTX）")
    p_seminar.add_argument("--topic", required=True, help="セミナーテーマ")
    p_seminar.add_argument("--slides", type=int, default=15, help="スライド枚数（デフォルト: 15）")
    p_seminar.add_argument("--output", help="スライド構成のJSON出力先ファイルパス")
    p_seminar.set_defaults(func=cmd_seminar)

    p_leader = sub.add_parser("leader", help="リーダーエージェント（全エージェント統合）")
    p_leader.add_argument("--goal", required=True, help="達成したいゴール")
    p_leader.add_argument(
        "--agents",
        help="使用エージェント（カンマ区切り: competitive_research,blog,sns,homepage,seminar）",
    )
    p_leader.add_argument("--output", help="結果のJSON出力先ファイルパス")
    p_leader.set_defaults(func=cmd_leader)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
