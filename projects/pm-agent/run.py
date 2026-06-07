"""
run.py — The single entry point for the AI Product Manager Agent.

Run it with ZERO setup:

    python3 projects/pm-agent/run.py

What it does, in plain English:
  1. Reads a pile of messy user feedback from a CSV.
  2. Hands it to a small crew of AI agents (Researcher → Prioritizer → Writer).
  3. Saves three ready-to-use documents into the `output/` folder:
       - roadmap.md       (a prioritized, RICE-scored roadmap table)
       - prd.md           (a one-page PRD for the #1 feature)
       - slack_update.md  (a Slack-ready stakeholder update)

By default it uses the bundled `sample_feedback.csv`. Point it at your own data
with `--input path/to/your_feedback.csv`.
"""

import argparse
import csv
import os
import sys

# Make sure we can import the sibling files (agents.py, llm.py) no matter what
# directory the user runs this from. We add THIS script's folder to the path.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from agents import Feedback, LeadPMAgent  # noqa: E402  (import after path tweak)
from llm import get_client                # noqa: E402


# Default locations, resolved relative to THIS file so it works from anywhere.
DEFAULT_INPUT = os.path.join(SCRIPT_DIR, "sample_feedback.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def load_feedback(csv_path: str) -> list:
    """Read the feedback CSV into a list of Feedback objects."""
    items = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(
                Feedback(
                    id=row.get("id", "").strip(),
                    source=row.get("source", "").strip(),
                    date=row.get("date", "").strip(),
                    text=row.get("text", "").strip(),
                )
            )
    return items


def save(path: str, content: str) -> None:
    """Write text to a file, creating the folder if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")


def main() -> None:
    # --- Parse the optional --input flag --------------------------------
    parser = argparse.ArgumentParser(
        description="AI Product Manager Agent: feedback in → roadmap out."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Path to a feedback CSV (columns: id, source, date, text). "
             "Defaults to the bundled sample_feedback.csv.",
    )
    args = parser.parse_args()

    # --- Friendly banner ------------------------------------------------
    print("=" * 64)
    print("🧑‍💼  AI PRODUCT MANAGER AGENT — Feedback In → Roadmap Out")
    print("=" * 64)

    # Decide demo vs. Gemini mode (prints which one it picked).
    # The client is created here so future Gemini upgrades have it ready to use.
    get_client()
    print()

    # --- Load the feedback ----------------------------------------------
    if not os.path.exists(args.input):
        print(f"❌ Could not find feedback file: {args.input}")
        sys.exit(1)

    feedback = load_feedback(args.input)
    print(f"📥 Loaded {len(feedback)} feedback items from "
          f"{os.path.basename(args.input)}\n")

    # --- Run the crew ----------------------------------------------------
    lead = LeadPMAgent(effort_budget=6.0)
    result = lead.run(feedback)

    # --- Save the documents ---------------------------------------------
    roadmap_path = os.path.join(OUTPUT_DIR, "roadmap.md")
    prd_path = os.path.join(OUTPUT_DIR, "prd.md")
    slack_path = os.path.join(OUTPUT_DIR, "slack_update.md")

    save(roadmap_path, result["roadmap"])
    save(prd_path, result["prd"])
    save(slack_path, result["slack"])

    # --- Final summary ---------------------------------------------------
    ranked = result["ranked"]
    top = ranked[0]
    sprint = [r for r in ranked if r.this_sprint]

    print("=" * 64)
    print("✅ DONE — your PM documents are ready!")
    print("=" * 64)
    print(f"🏆 Top priority : {top.theme.name} (RICE {top.score:,.0f})")
    print(f"🏃 This sprint  : {', '.join(r.theme.name for r in sprint)}")
    print(f"📊 Themes ranked: {len(ranked)}")
    print()
    print("📁 Files written:")
    print(f"   • {roadmap_path}")
    print(f"   • {prd_path}")
    print(f"   • {slack_path}")
    print("=" * 64)


if __name__ == "__main__":
    main()
