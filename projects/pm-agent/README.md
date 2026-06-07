# 🧑‍💼 AI Product Manager Agent — "Feedback In → Roadmap Out"

Give it a messy pile of user feedback. Get back a real product plan.

This is a small **crew of AI agents** that act like a tiny product team. You
hand them raw, unstructured user feedback (support tickets, app reviews, Slack
messages, emails, surveys) and they hand you back three things:

1. **A prioritized roadmap** — every theme ranked with the RICE framework, and a
   clear "build this sprint" vs. "backlog" call.
2. **A one-page PRD** (product requirements doc) for the #1 feature.
3. **A Slack-ready stakeholder update** — 5 punchy lines you could post today.

## ▶️ The one command to run it

```bash
python3 projects/pm-agent/run.py
```

That's it. **Demo mode needs zero setup** — no installs, no API keys, no
internet. It uses only the Python 3.11 standard library. Run the command, watch
the agents work in your terminal, and find your finished documents in the
`projects/pm-agent/output/` folder.

## 🤖 The crew (who does what)

The work is split between four agents, each with one job:

| Agent | Emoji | Job |
|-------|-------|-----|
| **ResearcherAgent** | 🔎 | Reads all feedback and clusters it into themes. |
| **PrioritizerAgent** | ⚖️ | Scores each theme with **RICE** and ranks them. |
| **WriterAgent** | ✍️ | Writes the roadmap, the PRD, and the Slack update. |
| **LeadPMAgent** | 🧑‍💼 | The manager — passes work between the others. |

**RICE** is a standard product-prioritization formula:
`Score = (Reach × Impact × Confidence) ÷ Effort`. Higher score = build it sooner.

## 🧪 Demo mode vs. 🤖 Gemini mode

- **Demo mode (default):** No API key. The agents use smart built-in rules
  (keyword clustering, RICE math, and clean templates). Perfect for a live demo —
  it always works and always gives the same result. **This needs zero setup.**
- **Gemini mode (optional upgrade):** Set a `GEMINI_API_KEY` environment
  variable and install the one package in `requirements.txt`. The agents then
  call Google's Gemini for richer clustering and writing. The code is already
  wired for this (see `llm.py`), with `TODO` comments in `agents.py` marking
  exactly where a Gemini prompt slots in. ⚠️ A real API key may cost money.

To turn on Gemini mode later:

```bash
pip install -r projects/pm-agent/requirements.txt
export GEMINI_API_KEY="your-key-here"
python3 projects/pm-agent/run.py
```

## 📄 Using your own feedback

Bring your own CSV and point the tool at it:

```bash
python3 projects/pm-agent/run.py --input path/to/your_feedback.csv
```

Your CSV needs these columns:

| Column | Meaning | Example |
|--------|---------|---------|
| `id` | A unique number/label for the row | `1` |
| `source` | Where it came from | `support_ticket`, `app_review`, `slack`, `email`, `survey` |
| `date` | When it arrived (`YYYY-MM-DD`) | `2026-05-12` |
| `text` | The actual feedback in the user's words | `"The app is so slow to load."` |

A ready-made example, `sample_feedback.csv`, ships with the tool (~45 realistic
comments for a fictional invoicing app called **Billy**).

## 📁 What you get (outputs)

After a run, look in `projects/pm-agent/output/`:

- `roadmap.md` — the ranked RICE table + the sprint plan.
- `prd.md` — a one-page PRD for the top-ranked feature.
- `slack_update.md` — the stakeholder update, ready to paste into Slack.

## 🗂️ Files in this folder

- `run.py` — the entry point you run.
- `agents.py` — the four agents and their logic.
- `llm.py` — the tiny "brain" abstraction (Demo + Gemini clients).
- `sample_feedback.csv` — example feedback to play with.
- `requirements.txt` — the one package needed *only* for Gemini mode.
- `output/` — where the generated documents are saved.
