# 🧠 Mnemo — a Self-Improving, Self-Healing Knowledge Engine

**"An organization that teaches itself."**

You ask Mnemo a question. It searches your knowledge base:

- If it's **confident it already knows**, it answers **instantly — with a citation**
  (so you can trust where the answer came from).
- If it **doesn't know**, it figures out the answer and — **only when it's
  confident the answer is good** — writes a brand-new article back into the
  knowledge base. Next time, that question is **instant**.
- It also **heals itself**: it spots **duplicate**, **stale**, and
  **contradictory** articles and merges or flags them, so the library stays
  clean instead of rotting over time.

As it runs, a live dashboard shows the **Instant-Answer Rate** and the
**knowledge-base size** climbing. The system literally gets smarter on its own.

## ▶️ The one command to run it

```bash
python3 projects/knowledge-engine/run.py
```

That's it. **Demo mode needs zero setup** — no installs, no API keys, no
internet. It uses only the Python 3.11 standard library. Run the command, watch
the agents work in your terminal, and find your results in the
`projects/knowledge-engine/output/` folder.

## 🤖 The crew (who does what)

Mnemo is a small team of four agents, each with one job:

| Agent | Emoji | Job |
|-------|-------|-----|
| **LibrarianAgent** | 🔎 | Semantically searches the knowledge base and reports how confident it is. |
| **ResolverAgent** | ✍️ | Answers from a found article (with a citation), or resolves a new answer and — past a confidence gate — saves it. |
| **HealerAgent** | 🩹 | Merges duplicate articles, flags stale ones, and flags likely contradictions. |
| **CuratorAgent** | 🧑‍🏫 | The lead. Runs the show and tracks the metrics. |

### 🚧 The confidence gate (an important feature)

When Mnemo has to invent a new answer, it scores its own confidence. It **only
writes the answer into the knowledge base if that score clears a threshold**.
If not, it **refuses to learn it** and flags it for a human instead. This is
what stops the library from filling up with confident-sounding garbage.

## 📄 What a knowledge-base article looks like

Each article is one simple record (a future MongoDB document):

| Field | Meaning |
|-------|---------|
| `id` | A unique number for the article. |
| `title` | The short headline / topic. |
| `body` | The actual answer text. |
| `tags` | A few keywords for the article. |
| `source` | Where it came from (e.g. `handbook`, `resolver`). |
| `created_at` | The date it was written (used to spot stale articles). |
| `confidence` | How sure we are it's correct, from 0 to 1. |
| `status` | `active`, `merged` (folded into another), or `flagged` (needs review). |

## 🧪 Demo mode vs. 🤖 live (Gemini + MongoDB) mode

**Demo mode (default).** Everything runs locally with the Python standard
library. Search uses a classic "bag-of-words cosine similarity" — it counts the
meaningful words in your question and each article and measures how much they
overlap. Answers are produced from clear templates. No installs, no keys, no
internet. Perfect for a demo video.

**Live mode (the upgrade path).** Set a `GEMINI_API_KEY` and connect a MongoDB
Atlas database and Mnemo gets a real brain:

- The **Librarian's** word-overlap search becomes **MongoDB Atlas
  `$vectorSearch`** over **Gemini embeddings** — true *meaning-based* search.
- The **Resolver's** templated answers become **real Gemini 3** answers, and
  the model's own grounding becomes the confidence score on the gate.
- The **Healer's** keyword checks become **Gemini-powered** semantic
  de-duplication and contradiction detection.

The code is structured so this swap is clean: every place that would call
Gemini or MongoDB is marked with a `TODO` comment, and those libraries are
imported **lazily** (only when actually used) so a missing package can never
break demo mode. To try live mode:

```bash
pip install -r projects/knowledge-engine/requirements.txt   # only for live mode
export GEMINI_API_KEY=your_key_here
python3 projects/knowledge-engine/run.py
```

## ♻️ Dual-use

This isn't just a demo trick. Point Mnemo at **any team's real knowledge base**
— support docs, an internal wiki, an FAQ — and it makes that knowledge base
**improve itself**: answering instantly with citations, learning the gaps it
finds, and quietly cleaning out duplicates and stale pages.

## 📂 What the demo produces

Running the command writes two files into
`projects/knowledge-engine/output/`:

- **`kb_after.json`** — the full knowledge base after learning + healing.
- **`demo_report.md`** — a clean, plain-English summary of the run (metrics,
  every question's outcome, and what the healer fixed).

## 🗂️ Files in this project

| File | What it is |
|------|-----------|
| `run.py` | The one entry point — runs the scripted demo. |
| `kb.py` | The `KnowledgeBase` (JSON-backed) and the cosine-similarity search. |
| `agents.py` | The four agents (Librarian, Resolver, Healer, Curator). |
| `llm.py` | The swappable "brain" — demo stub today, Gemini tomorrow. |
| `seed_kb.json` | Six starter articles about a fictional invoicing app, "Billy". |
| `requirements.txt` | Packages for **live mode only** — demo mode needs none. |
