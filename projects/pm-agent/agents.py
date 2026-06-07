"""
agents.py — The small "crew" of AI Product Manager agents.

Big picture
-----------
Think of this as a tiny product team where each member has ONE job:

  1. ResearcherAgent   🔎  reads all the messy feedback and groups it into themes.
  2. PrioritizerAgent  ⚖️  scores each theme with the RICE framework and ranks them.
  3. WriterAgent       ✍️  writes a one-page PRD and a Slack stakeholder update.
  4. LeadPMAgent       🧑‍💼 the manager who passes work between the others.

In "demo mode" (no API key) every agent uses simple, predictable built-in
logic (keyword matching, RICE math, and templates). Each agent also has clear
TODO comments showing exactly where a Gemini prompt could later replace the
heuristic — so upgrading to live AI is a clean, obvious next step.
"""

from dataclasses import dataclass, field
from datetime import date
import re
import textwrap
from collections import Counter


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------
# Dataclasses are just tidy little containers for data. They save us from
# juggling loose dictionaries and make the code easier to read.

@dataclass
class Feedback:
    """One single piece of user feedback (one row from the CSV)."""
    id: str
    source: str
    date: str
    text: str


@dataclass
class Theme:
    """A group of related feedback items that share a topic."""
    name: str              # short human label, e.g. "Slow Invoice Loading"
    description: str       # one-sentence summary of the pain
    items: list = field(default_factory=list)  # the Feedback objects inside it

    @property
    def count(self) -> int:
        """How many feedback items landed in this theme."""
        return len(self.items)


@dataclass
class RiceScore:
    """
    The RICE score for one theme.

    RICE is a classic product-management way to prioritize:
        Score = (Reach × Impact × Confidence) / Effort

      - Reach:      how many users this affects (we estimate from feedback volume)
      - Impact:     how much it moves the needle (0.25 / 0.5 / 1 / 2 / 3)
      - Confidence: how sure we are, as a fraction (0.5 = 50%, 1.0 = 100%)
      - Effort:     rough build cost in "person-weeks"
    """
    theme: Theme
    reach: int
    impact: float
    confidence: float       # stored as a fraction, e.g. 0.8 means 80%
    effort: float           # person-weeks
    score: float = 0.0
    this_sprint: bool = False  # set by the Prioritizer: build now vs. backlog

    def compute(self) -> float:
        """Do the RICE math and remember the result."""
        self.score = (self.reach * self.impact * self.confidence) / self.effort
        return self.score


# ---------------------------------------------------------------------------
# 1) ResearcherAgent  🔎
# ---------------------------------------------------------------------------
class ResearcherAgent:
    """
    Reads every feedback item and clusters them into themes.

    Demo logic: we keep a small dictionary of known topics, each with a list of
    keywords. Every feedback item is matched to the topic whose keywords it hits
    most often. This is simple, fast, and needs no AI.
    """

    # Each theme is: a friendly name, a one-line description, and trigger keywords.
    # The order matters only for tidy output; matching is by keyword hit count.
    THEME_LIBRARY = [
        {
            "name": "Slow Invoice Loading",
            "description": "Users say the invoice list/dashboard is slow to load.",
            "keywords": ["slow", "lag", "sluggish", "loading", "load", "speed",
                         "performance", "spins", "spinning", "ages", "forever"],
        },
        {
            "name": "Recurring Invoices",
            "description": "Users want invoices that repeat/auto-send on a schedule.",
            "keywords": ["recurring", "repeat", "repeating", "subscription",
                         "monthly", "auto-send", "automatic", "schedule",
                         "retainer", "every month"],
        },
        {
            "name": "Confusing Tax Settings",
            "description": "Tax/VAT configuration is unclear and hard to trust.",
            "keywords": ["tax", "taxes", "vat", "sales tax"],
        },
        {
            "name": "Mobile App Crashes",
            "description": "The phone app crashes, freezes, or force-closes.",
            "keywords": ["crash", "crashes", "crashing", "freezes", "force-close",
                         "force-closes", "closes", "unstable", "mobile", "android",
                         "ios", "iphone", "pixel", "phone app"],
        },
        {
            "name": "Stripe / Card Payments",
            "description": "Users want to collect online card payments via Stripe.",
            "keywords": ["stripe", "card", "credit card", "payment processor",
                         "pay online", "online card"],
        },
        {
            "name": "Accounting Software Export",
            "description": "Users want to export/sync data to QuickBooks or Xero.",
            "keywords": ["quickbooks", "xero", "accounting", "export", "sync",
                         "reconciliation", "bookkeeper", "month-end"],
        },
        {
            "name": "Dark Mode",
            "description": "Users want a darker color theme, especially at night.",
            "keywords": ["dark mode", "dark theme", "dark", "color scheme",
                         "white background", "white screen"],
        },
        {
            "name": "Multi-Currency Support",
            "description": "Users need to invoice in multiple currencies.",
            "keywords": ["currency", "currencies", "multi-currency", "euros",
                         "usd", "gbp", "eur", "conversion", "international"],
        },
        {
            "name": "Better Payment Reminders",
            "description": "Users want stronger, scheduled overdue-payment reminders.",
            "keywords": ["reminder", "reminders", "nudge", "overdue", "follow-up",
                         "follow-ups", "late", "paid on time", "cash flow"],
        },
    ]

    def cluster(self, feedback_items: list) -> list:
        """
        Group feedback into themes and return the non-empty ones.

        TODO (Gemini mode): instead of keyword matching, we could send all the
        feedback text to Gemini with a prompt like "Cluster these comments into
        themes and name each theme", then parse the JSON it returns. The demo
        heuristic below is the zero-setup stand-in.
        """
        # Start with one empty Theme per library entry.
        themes = [
            Theme(name=t["name"], description=t["description"])
            for t in self.THEME_LIBRARY
        ]

        # Assign each feedback item to its best-matching theme.
        for fb in feedback_items:
            best_index = self._best_theme_index(fb.text)
            if best_index is not None:
                themes[best_index].items.append(fb)

        # Only keep themes that actually caught at least one item.
        return [theme for theme in themes if theme.count > 0]

    def _best_theme_index(self, text: str):
        """Return the index of the theme whose keywords match this text most."""
        lowered = text.lower()
        best_index = None
        best_hits = 0

        for index, topic in enumerate(self.THEME_LIBRARY):
            # Count how many of this topic's keywords appear in the text.
            hits = sum(1 for kw in topic["keywords"] if kw in lowered)
            if hits > best_hits:
                best_hits = hits
                best_index = index

        return best_index


# ---------------------------------------------------------------------------
# 2) PrioritizerAgent  ⚖️
# ---------------------------------------------------------------------------
class PrioritizerAgent:
    """
    Scores every theme with RICE and decides what to build this sprint.

    Demo logic uses deterministic heuristics so the demo gives the SAME answer
    every time:
      - Reach is estimated from how many feedback items mention the theme.
      - Impact / Effort are looked up from a small, sensible table per theme.
      - Confidence rises with the amount of evidence (more feedback = surer).
    """

    # Sensible, hand-tuned Impact (0.25–3 scale) and Effort (person-weeks)
    # estimates per theme. In real life a PM would set these with the team.
    ESTIMATES = {
        "Slow Invoice Loading":      {"impact": 3.0, "effort": 2.0},
        "Recurring Invoices":        {"impact": 3.0, "effort": 4.0},
        "Confusing Tax Settings":    {"impact": 2.0, "effort": 3.0},
        "Mobile App Crashes":        {"impact": 3.0, "effort": 3.0},
        "Stripe / Card Payments":    {"impact": 3.0, "effort": 5.0},
        "Accounting Software Export":{"impact": 2.0, "effort": 4.0},
        "Dark Mode":                 {"impact": 0.5, "effort": 1.0},
        "Multi-Currency Support":    {"impact": 2.0, "effort": 5.0},
        "Better Payment Reminders":  {"impact": 2.0, "effort": 2.0},
    }

    # How many real users we guess each feedback item represents. (For every
    # person who writes in, many more feel the same but stay silent.)
    USERS_PER_FEEDBACK_ITEM = 40

    # Default fallback estimates if a theme isn't in the table above.
    DEFAULT_IMPACT = 1.0
    DEFAULT_EFFORT = 3.0

    def __init__(self, effort_budget: float = 6.0):
        # The "This Sprint" set must fit inside this many person-weeks.
        self.effort_budget = effort_budget

    def score_all(self, themes: list) -> list:
        """
        Turn a list of Themes into a ranked list of RiceScores.

        TODO (Gemini mode): we could ask Gemini to estimate Impact/Effort and
        explain its reasoning for each theme, instead of the lookup table.
        """
        scores = [self._score_one(theme) for theme in themes]

        # Rank highest RICE score first.
        scores.sort(key=lambda s: s.score, reverse=True)

        # Greedily fill the sprint: take the best themes until the effort
        # budget runs out. This is a simple, explainable planning rule.
        remaining_budget = self.effort_budget
        for rice in scores:
            if rice.effort <= remaining_budget:
                rice.this_sprint = True
                remaining_budget -= rice.effort

        return scores

    def _score_one(self, theme: Theme) -> RiceScore:
        """Build and compute a single RICE score for one theme."""
        estimate = self.ESTIMATES.get(theme.name, {})
        impact = estimate.get("impact", self.DEFAULT_IMPACT)
        effort = estimate.get("effort", self.DEFAULT_EFFORT)

        # Reach: scale the number of mentions into an estimated user count.
        reach = theme.count * self.USERS_PER_FEEDBACK_ITEM

        # Confidence: more feedback = more confident, capped between 50% and 100%.
        # 1 mention -> 0.5, and each extra mention adds 0.1 up to 1.0.
        confidence = min(1.0, 0.5 + (theme.count - 1) * 0.1)

        rice = RiceScore(
            theme=theme,
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
        )
        rice.compute()
        return rice


# ---------------------------------------------------------------------------
# 3) WriterAgent  ✍️
# ---------------------------------------------------------------------------
class WriterAgent:
    """
    Turns the ranked themes into human-ready documents:
      - a roadmap table (markdown),
      - a one-page PRD for the #1 theme,
      - a short Slack-style stakeholder update.

    Demo logic uses clean templates. Each method has a TODO showing where a
    Gemini prompt would write richer prose.
    """

    def write_roadmap(self, ranked_scores: list) -> str:
        """Build a markdown roadmap with a ranked RICE table."""
        lines = []
        lines.append("# 🗺️ Billy Product Roadmap")
        lines.append("")
        lines.append(f"_Generated by the PM Agent crew on {date.today().isoformat()}._")
        lines.append("")
        lines.append("Themes are ranked by their **RICE score** "
                     "`(Reach × Impact × Confidence) / Effort`. "
                     "The **This Sprint** set fits within the team's effort budget.")
        lines.append("")

        # Markdown table header.
        lines.append("| Rank | Theme | Mentions | Reach | Impact | Confidence | Effort (wks) | RICE Score | Plan |")
        lines.append("|-----:|-------|---------:|------:|-------:|-----------:|-------------:|-----------:|------|")

        for rank, rice in enumerate(ranked_scores, start=1):
            plan = "✅ This Sprint" if rice.this_sprint else "📋 Backlog"
            lines.append(
                f"| {rank} "
                f"| {rice.theme.name} "
                f"| {rice.theme.count} "
                f"| {rice.reach:,} "
                f"| {rice.impact:g} "
                f"| {int(rice.confidence * 100)}% "
                f"| {rice.effort:g} "
                f"| {rice.score:,.0f} "
                f"| {plan} |"
            )

        lines.append("")
        sprint = [r for r in ranked_scores if r.this_sprint]
        sprint_effort = sum(r.effort for r in sprint)
        lines.append(f"**This Sprint:** {len(sprint)} themes, "
                     f"{sprint_effort:g} person-weeks of effort.")
        lines.append("")

        # TODO (Gemini mode): ask Gemini to add a short narrative paragraph
        # explaining the strategic story behind these rankings.
        return "\n".join(lines)

    def write_prd(self, top_rice: RiceScore) -> str:
        """Write a one-page PRD (product requirements doc) for the #1 theme."""
        theme = top_rice.theme

        # Pull a few real user quotes to make the PRD feel grounded.
        quotes = [f'  - "{item.text}" — _{item.source}_'
                  for item in theme.items[:3]]
        quotes_block = "\n".join(quotes) if quotes else "  - (no quotes)"

        # TODO (Gemini mode): replace this template with a Gemini prompt such as
        # "Write a one-page PRD for <theme> given these user quotes ...".
        prd = f"""# 📄 PRD: {theme.name}

_One-page product requirements document. Auto-drafted by the PM Agent crew on {date.today().isoformat()}._

## Problem
{theme.description} This was the **#1 prioritized theme**, appearing in
**{theme.count} pieces of feedback** across multiple channels. Representative voices:

{quotes_block}

## Goal
Resolve "{theme.name}" so that affected users (an estimated **{top_rice.reach:,} people**)
have a noticeably better experience, directly addressing the most-mentioned pain point
in our current feedback.

## User Stories
- As a Billy user, I want this pain point fixed so my invoicing workflow is smooth.
- As a small-business owner, I want to trust the product so I can recommend it to peers.
- As a busy founder, I want fewer manual workarounds so I can spend time on my business.

## Success Metrics
- Reduce related support tickets/complaints about "{theme.name}" by 60% within 30 days.
- Improve overall satisfaction (CSAT) for affected users by at least 10 points.
- Confirm the fix with a follow-up survey to the {theme.count}+ users who reported it.

## Scope (In)
- Directly address the core problem described above for the primary platforms.
- Add lightweight in-app messaging so users know the issue was fixed.

## Out of Scope
- Unrelated feature requests from other themes (tracked separately in the roadmap).
- A full redesign — this PRD targets the specific pain point only.

## Effort & Confidence
- Estimated effort: **{top_rice.effort:g} person-weeks**.
- Confidence: **{int(top_rice.confidence * 100)}%** (based on volume of consistent feedback).
- RICE score: **{top_rice.score:,.0f}** (highest of all themes).
"""
        return prd

    def write_slack_update(self, ranked_scores: list, total_feedback: int) -> str:
        """Write a punchy 4-6 line Slack-style stakeholder update."""
        sprint = [r for r in ranked_scores if r.this_sprint]
        top = ranked_scores[0]

        # Build a comma list of the sprint theme names.
        sprint_names = ", ".join(r.theme.name for r in sprint)

        # TODO (Gemini mode): ask Gemini to rewrite this in the founder's voice.
        update = f""":rocket: *Billy Roadmap Update — {date.today().isoformat()}*

We just turned *{total_feedback} pieces of user feedback* into a plan. :tada:
:dart: *Top priority:* {top.theme.name} (RICE {top.score:,.0f}) — a PRD is ready for review.
:hammer_and_wrench: *This sprint:* {sprint_names}.
:bar_chart: We ranked *{len(ranked_scores)} themes* with the RICE framework; everything else is in the backlog.
Full roadmap + PRD attached. Feedback welcome before we kick off! :pray:"""
        return update

    def build_gitlab_issues(self, ranked_scores: list) -> list:
        """
        Turn the "This Sprint" themes into GitLab-ready issue payloads.

        This is the magic final step that CLOSES THE LOOP: the agent doesn't
        just recommend work, it produces the exact engineering tickets. In the
        live hackathon build, this same list is what we hand to GitLab's MCP
        server to actually CREATE the issues in your project — automatically.

        TODO (GitLab MCP mode): send each dict to the GitLab MCP "create issue"
        tool. The fields below map directly onto real GitLab issue fields.
        """
        milestone = f"Sprint — week of {date.today().isoformat()}"
        issues = []
        for rice in ranked_scores:
            if not rice.this_sprint:
                continue
            theme = rice.theme
            quotes = "\n".join(f"> {item.text}  \n> — _{item.source}_"
                               for item in theme.items[:3])
            description = (
                f"**Why this matters:** {theme.description}\n\n"
                f"Raised in **{theme.count} pieces of user feedback**, representing an "
                f"estimated **{rice.reach:,} users**. RICE score **{rice.score:,.0f}**.\n\n"
                f"**What users said:**\n{quotes}\n\n"
                f"**Definition of done:** the pain point above is resolved and "
                f"verified with the users who reported it."
            )
            issues.append({
                "title": f"[Sprint] {theme.name}",
                "description": description,
                "labels": ["from-user-feedback", "pm-agent", "sprint"],
                "weight": int(round(rice.effort)),   # GitLab "weight" == effort
                "milestone": milestone,
            })
        return issues

    def render_gitlab_issues_md(self, issues: list) -> str:
        """A human-readable preview of the GitLab issues we will create."""
        lines = ["# 🦊 GitLab Issues — ready to create", ""]
        lines.append(f"_Auto-prepared by the PM Agent crew on {date.today().isoformat()}._")
        lines.append("")
        lines.append(f"These **{len(issues)}** issues map to the *This Sprint* themes. "
                     "In the live build, the agent creates them directly in GitLab "
                     "via the GitLab MCP server — no copy-paste needed.")
        lines.append("")
        for i, issue in enumerate(issues, start=1):
            lines.append(f"## {i}. {issue['title']}")
            lines.append(f"- **Labels:** {', '.join(issue['labels'])}")
            lines.append(f"- **Weight (effort):** {issue['weight']} person-weeks")
            lines.append(f"- **Milestone:** {issue['milestone']}")
            lines.append("")
            lines.append(issue["description"])
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# 4) LeadPMAgent  🧑‍💼
# ---------------------------------------------------------------------------
class LeadPMAgent:
    """
    The orchestrator / manager. It owns the whole pipeline and narrates each
    handoff with friendly console logs so a live demo is fun to watch:

        feedback -> Researcher -> Prioritizer -> Writer -> finished documents
    """

    def __init__(self, effort_budget: float = 6.0):
        # Hire the crew.
        self.researcher = ResearcherAgent()
        self.prioritizer = PrioritizerAgent(effort_budget=effort_budget)
        self.writer = WriterAgent()

    def run(self, feedback_items: list) -> dict:
        """
        Run the full crew and return a dict of finished documents plus the
        ranked scores (handy for the console summary).
        """
        total = len(feedback_items)

        # --- Step 1: Research ------------------------------------------------
        print(f"🔎 Researcher: clustering {total} feedback items into themes...")
        themes = self.researcher.cluster(feedback_items)
        print(f"   → Found {len(themes)} themes.")
        for theme in themes:
            print(f"      • {theme.name} ({theme.count} mentions)")
        print()

        # --- Step 2: Prioritize ---------------------------------------------
        print(f"⚖️  Prioritizer: scoring {len(themes)} themes with the RICE framework...")
        ranked = self.prioritizer.score_all(themes)
        for rank, rice in enumerate(ranked, start=1):
            tag = "✅ This Sprint" if rice.this_sprint else "📋 Backlog"
            print(f"   {rank}. {rice.theme.name:<28} RICE {rice.score:>8,.0f}  {tag}")
        print()

        # --- Step 3: Write ---------------------------------------------------
        top = ranked[0]
        print(f"✍️  Writer: drafting roadmap, PRD for '{top.theme.name}', "
              f"and Slack update...")
        roadmap = self.writer.write_roadmap(ranked)
        prd = self.writer.write_prd(top)
        slack = self.writer.write_slack_update(ranked, total)
        gitlab_issues = self.writer.build_gitlab_issues(ranked)
        gitlab_md = self.writer.render_gitlab_issues_md(gitlab_issues)
        print("   → Documents drafted.")

        # --- Step 4: Close the loop -> GitLab tickets -----------------------
        print(f"🦊 Lead: {len(gitlab_issues)} GitLab issue(s) queued for the sprint "
              f"(ready to auto-create via GitLab MCP).\n")

        return {
            "ranked": ranked,
            "roadmap": roadmap,
            "prd": prd,
            "slack": slack,
            "gitlab_issues": gitlab_issues,
            "gitlab_md": gitlab_md,
        }
