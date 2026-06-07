"""
Daily Report Generator
=======================

What it does (in plain English):
    Reads a simple list of tasks from `tasks.csv` and turns it into a tidy,
    easy-to-read daily report saved as `daily-report.md`.

    Tasks are grouped by their status (To Do / In Progress / Done) and, within
    each group, sorted so the most important ones are at the top.

How to run it:
    python3 projects/daily-report/daily_report.py

You don't need to install anything — this uses only tools that come with Python.
"""

import csv
import os
from datetime import date

# Where this script lives, so it can find its files no matter where you run it from.
HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(HERE, "tasks.csv")
OUTPUT_FILE = os.path.join(HERE, "daily-report.md")

# How we rank priorities (lower number = more important = shown first).
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# The order we want status groups to appear in the report.
STATUS_ORDER = ["To Do", "In Progress", "Done"]


def read_tasks(path):
    """Read tasks from the CSV file into a list of dictionaries."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Couldn't find your task list at: {path}\n"
            f"Create a tasks.csv there with columns: task, priority, status"
        )

    tasks = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up spacing and ignore completely blank rows.
            task = (row.get("task") or "").strip()
            if not task:
                continue
            tasks.append(
                {
                    "task": task,
                    "priority": (row.get("priority") or "medium").strip().lower(),
                    "status": (row.get("status") or "To Do").strip(),
                }
            )
    return tasks


def build_report(tasks):
    """Turn the list of tasks into a nicely formatted Markdown report."""
    lines = []
    lines.append(f"# Daily Report — {date.today().isoformat()}")
    lines.append("")
    lines.append(f"You have **{len(tasks)} task(s)** on the list.")
    lines.append("")

    # Group tasks by their status.
    for status in STATUS_ORDER:
        in_this_group = [t for t in tasks if t["status"].lower() == status.lower()]
        if not in_this_group:
            continue

        # Sort so high priority comes first. Unknown priorities go to the bottom.
        in_this_group.sort(key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))

        lines.append(f"## {status} ({len(in_this_group)})")
        for t in in_this_group:
            lines.append(f"- **[{t['priority'].upper()}]** {t['task']}")
        lines.append("")

    # Catch any tasks whose status wasn't one we recognized, so nothing is lost.
    known = {s.lower() for s in STATUS_ORDER}
    leftovers = [t for t in tasks if t["status"].lower() not in known]
    if leftovers:
        lines.append("## Other")
        for t in leftovers:
            lines.append(f"- **[{t['priority'].upper()}]** {t['task']} _(status: {t['status']})_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    tasks = read_tasks(INPUT_FILE)
    report = build_report(tasks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ Done! Your daily report is ready.")
    print(f"   Read {len(tasks)} task(s) from: {INPUT_FILE}")
    print(f"   Saved your report to:        {OUTPUT_FILE}")
    print()
    print("Open that file to see your tidy report. To use your own tasks,")
    print("edit tasks.csv and run this again.")


if __name__ == "__main__":
    main()
