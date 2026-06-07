"""
run.py — The one command that runs the whole Mnemo demo.

    python3 projects/knowledge-engine/run.py

What you'll watch happen, in order:
  1. We load a small starter knowledge base about a fictional invoicing app
     called "Billy" and print an opening dashboard.
  2. Q1 — a question the KB already knows → an INSTANT, cited answer.
  3. Q2 — a question the KB does NOT know → Mnemo resolves a new answer and,
     because it's confident, WRITES it into the KB. The KB grows by 1.
  4. We re-ask Q2 — now it's an INSTANT answer. It LEARNED.
  5. Q3 — a question with no supporting knowledge → the CONFIDENCE GATE blocks
     the write and flags it for a human. Mnemo refuses to learn garbage.
  6. A HEALER pass — it merges a duplicate article and flags a stale one.
  7. A closing dashboard showing the Instant-Answer Rate climbing and the
     Intelligence Score going up.

Outputs land in `projects/knowledge-engine/output/`:
  • kb_after.json   — the knowledge base after everything ran
  • demo_report.md  — a clean, plain-English summary of the run
"""

import json
import os

from kb import KnowledgeBase
from llm import get_client
from agents import CuratorAgent


# Resolve paths relative to THIS file so it runs from anywhere.
HERE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(HERE, "seed_kb.json")
OUTPUT_DIR = os.path.join(HERE, "output")


def banner(text: str) -> None:
    """Print a clear section header."""
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def main() -> None:
    banner("🧠  MNEMO — a Self-Improving, Self-Healing Knowledge Engine")
    print("An organization that teaches itself.\n")

    # The "brain": Gemini if a key is set, otherwise the zero-setup demo brain.
    llm = get_client()

    # Load the starter knowledge base about "Billy".
    kb = KnowledgeBase().load(SEED_PATH)
    curator = CuratorAgent(kb, llm)

    # Remember the starting size so we can show growth at the end.
    kb_size_before = kb.count_active()

    curator.dashboard("STARTING DASHBOARD")

    # ---- Q1: something the KB already knows → instant cited answer --------
    banner("STEP 1 — Ask something the KB already knows")
    curator.ask("How do I create and send an invoice in Billy?")

    # ---- Q2: a miss → Mnemo resolves and LEARNS a new article -------------
    banner("STEP 2 — Ask something NEW (the KB has to learn it)")
    curator.ask("How do I set up recurring invoices in Billy?")

    # ---- Re-ask Q2: now it's instant. It learned! -------------------------
    banner("STEP 3 — Re-ask the same question (did it learn?)")
    curator.ask("How do I set up recurring invoices in Billy?")

    # ---- Q3: low-confidence miss → CONFIDENCE GATE blocks the write -------
    banner("STEP 4 — Ask something with NO supporting knowledge")
    print("(Watch the confidence gate refuse to save a low-quality answer.)")
    curator.ask("What is the weather like in Tokyo today?")

    # ---- Healer pass: merge duplicate, flag stale -------------------------
    banner("STEP 5 — Run a self-healing pass over the KB")
    heal_report = curator.healer.heal()

    # ---- Closing dashboard ------------------------------------------------
    banner("FINAL RESULTS")
    print(f"📚 KB size: {kb_size_before} → {kb.count_active()} active "
          f"articles (after learning + healing)")
    curator.dashboard("CLOSING DASHBOARD")
    print("\n🎉 Mnemo got smarter on its own — and kept its library clean.")

    # ---- Save outputs -----------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    kb.save(os.path.join(OUTPUT_DIR, "kb_after.json"))
    write_report(curator, heal_report, kb_size_before, kb.count_active())
    print(f"\n💾 Saved: {os.path.join(OUTPUT_DIR, 'kb_after.json')}")
    print(f"💾 Saved: {os.path.join(OUTPUT_DIR, 'demo_report.md')}")


def write_report(curator, heal_report, size_before, size_after) -> None:
    """Write a clean markdown summary of what happened in the run."""
    lines = []
    lines.append("# Mnemo Demo Report")
    lines.append("")
    lines.append("_An organization that teaches itself — run summary._")
    lines.append("")

    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| KB size before | {size_before} active articles |")
    lines.append(f"| KB size after | {size_after} active articles |")
    lines.append(f"| Questions asked | {curator.questions_asked} |")
    lines.append(f"| Instant answers | {curator.instant_answers} |")
    lines.append(f"| Newly learned | {curator.learned} |")
    lines.append(f"| Flagged (gate blocked) | {curator.flagged} |")
    lines.append(f"| Instant-Answer Rate | "
                 f"{curator.instant_answer_rate():.0f}% |")
    lines.append(f"| Intelligence Score | {curator.intelligence_score()} |")
    lines.append("")

    lines.append("## What happened, question by question")
    lines.append("")
    labels = {
        "instant": "✅ INSTANT cited answer (already known)",
        "learned": "🧠 LEARNED — resolved a new answer and saved it to the KB",
        "flagged": "🚧 BLOCKED by confidence gate — flagged for human review",
    }
    for i, item in enumerate(curator.log, start=1):
        lines.append(f"**Q{i}: {item['question']}**")
        lines.append("")
        lines.append(f"- Outcome: {labels.get(item['action'], item['action'])}")
        lines.append(f"- Source: {item['source']}")
        lines.append(f"- Confidence: {item['confidence']:.2f}")
        lines.append(f"- Answer: {item['answer']}")
        lines.append("")

    lines.append("## Self-healing pass")
    lines.append("")
    if heal_report["merged"]:
        for m in heal_report["merged"]:
            lines.append(f"- 🔗 Merged Article #{m['merged']} into "
                         f"#{m['kept']} (similarity {m['similarity']}).")
    if heal_report["stale"]:
        for s in heal_report["stale"]:
            lines.append(f"- ⏳ Flagged stale Article #{s['id']} "
                         f"(created {s['created_at']}).")
    if heal_report["contradictions"]:
        for c in heal_report["contradictions"]:
            lines.append(f"- ⚔️ Flagged possible contradiction between "
                         f"#{c['a']} and #{c['b']}.")
    if not any(heal_report.values()):
        lines.append("- The KB was already healthy; nothing to fix.")
    lines.append("")

    lines.append("## Why this matters")
    lines.append("")
    lines.append("Every miss that Mnemo confidently resolves becomes a new "
                 "article, so the **Instant-Answer Rate climbs over time** and "
                 "the team self-serves more. The **confidence gate** keeps low "
                 "quality answers out, and the **healer** stops the library "
                 "from rotting with duplicates and stale pages.")
    lines.append("")

    path = os.path.join(OUTPUT_DIR, "demo_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
