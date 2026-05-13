from .base_agent import BaseAgent
from .competitive_research import CompetitiveResearchAgent
from .blog_generator import BlogGeneratorAgent
from .sns_post import SNSPostAgent
from .homepage_renewal import HomepageRenewalAgent
from .seminar_creator import SeminarCreatorAgent

SYSTEM_PROMPT = """あなたはマーケティング戦略のリーダーです。おうちCFO FP相談サービスの
総合的なマーケティング・コンテンツ戦略を統括します。

役割:
- 各専門エージェントの成果物を統合し、最高の結果を生み出す
- ゴールに対して最適なエージェントの組み合わせを判断する
- 各アウトプットの品質を評価し、統合的な提言をまとめる"""


class LeaderAgent(BaseAgent):
    """リーダーエージェント。ゴールに応じて専門エージェントを組み合わせて最高の成果を生み出す。"""

    AGENT_DESCRIPTIONS = {
        "competitive_research": "競合調査（FP市場・競合分析・差別化戦略）",
        "blog": "ブログ記事生成（SEO最適化コンテンツ）",
        "sns": "SNS投稿作成（Threads・Instagram）",
        "homepage": "ホームページリニューアル提案",
        "seminar": "セミナー資料作成（PPTX生成）",
    }

    def run(self, goal: str, agents: list[str] | None = None) -> dict:
        """
        goal: 達成したい目標
        agents: 使用するエージェントのリスト（None の場合は goal から自動判定）
        """
        if agents is None:
            agents = self._select_agents(goal)

        print(f"\n[リーダー] ゴール: {goal}")
        print(f"[リーダー] 実行エージェント: {', '.join(agents)}\n")

        results = {}

        if "competitive_research" in agents:
            print("[競合調査エージェント] 実行中...")
            agent = CompetitiveResearchAgent()
            results["competitive_research"] = agent.run(topic=goal)
            print("[競合調査エージェント] 完了\n")

        if "homepage" in agents:
            print("[ホームページリニューアルエージェント] 実行中...")
            agent = HomepageRenewalAgent()
            results["homepage"] = agent.run(focus=goal)
            print("[ホームページリニューアルエージェント] 完了\n")

        if "blog" in agents:
            print("[ブログ生成エージェント] 実行中...")
            agent = BlogGeneratorAgent()
            competitive_insights = results.get("competitive_research", {}).get("recommendations", [])
            keywords = competitive_insights[:3] if competitive_insights else None
            results["blog"] = agent.run(topic=goal, keywords=keywords)
            print("[ブログ生成エージェント] 完了\n")

        if "sns" in agents:
            print("[SNS投稿エージェント] 実行中...")
            agent = SNSPostAgent()
            blog_summary = results.get("blog", {}).get("summary", "")
            results["sns"] = agent.run(topic=goal, blog_summary=blog_summary)
            print("[SNS投稿エージェント] 完了\n")

        if "seminar" in agents:
            print("[セミナー作成エージェント] 実行中...")
            agent = SeminarCreatorAgent()
            results["seminar"] = agent.run(topic=goal)
            print("[セミナー作成エージェント] 完了\n")

        print("[リーダー] 統合サマリー生成中...")
        synthesis = self._synthesize(goal, agents, results)
        print("[リーダー] 完了\n")

        return {
            "goal": goal,
            "agents_used": agents,
            "results": results,
            "synthesis": synthesis,
        }

    def _select_agents(self, goal: str) -> list[str]:
        """ゴールのキーワードからエージェントを自動選択する。"""
        goal_lower = goal.lower()
        selected = []

        research_keywords = ["競合", "調査", "リサーチ", "市場", "分析", "compare", "research"]
        if any(k in goal_lower for k in research_keywords):
            selected.append("competitive_research")

        homepage_keywords = ["ホームページ", "hp", "サイト", "website", "web", "リニューアル", "seo"]
        if any(k in goal_lower for k in homepage_keywords):
            selected.append("homepage")

        blog_keywords = ["ブログ", "記事", "コンテンツ", "blog", "article", "column", "コラム"]
        if any(k in goal_lower for k in blog_keywords):
            selected.append("blog")

        sns_keywords = ["sns", "threads", "インスタ", "instagram", "投稿", "post", "ソーシャル"]
        if any(k in goal_lower for k in sns_keywords):
            selected.append("sns")

        seminar_keywords = ["セミナー", "パワポ", "pptx", "プレゼン", "資料", "seminar", "slide"]
        if any(k in goal_lower for k in seminar_keywords):
            selected.append("seminar")

        if not selected:
            selected = ["competitive_research", "blog", "sns"]

        return selected

    def _synthesize(self, goal: str, agents: list[str], results: dict) -> str:
        summaries = []
        for agent_key in agents:
            if agent_key not in results:
                continue
            r = results[agent_key]
            summary = r.get("summary", "")
            if summary:
                agent_name = self.AGENT_DESCRIPTIONS.get(agent_key, agent_key)
                summaries.append(f"【{agent_name}】{summary}")

        summaries_text = "\n".join(summaries) if summaries else "各エージェントの成果物を参照してください。"

        prompt = f"""以下のゴールと各エージェントの成果を統合し、おうちCFO FP相談サービスに向けた
総合的な戦略提言をまとめてください（300〜500文字程度）。

ゴール: {goal}

各エージェントのサマリー:
{summaries_text}

統合提言（日本語で簡潔に）:"""

        return self.call(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=2000,
        )
