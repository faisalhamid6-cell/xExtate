# Getting Started — explained like you're 10 🧒

Hi! This guide assumes you know **nothing** about coding. That's totally fine. Read it once,
top to bottom. It takes about 10 minutes.

---

## 1. What is this place?

Think of this project as a **kitchen**. 🍳

- **You** are the person who says *"I'd like a sandwich."*
- **Claude Code** (me) is the chef who actually makes it.
- The **folders** are where we keep ingredients, recipes, and finished dishes.

You don't cook. You just say what you want, taste the result, and say "yes, perfect" or
"a bit more salt." That's the whole job.

---

## 2. The folders (where stuff lives)

- **`projects/`** = your **tools** (finished dishes). Each tool gets its own little folder.
- **`sops/`** = your **recipes**. When we figure out how to do something, we write it down here
  so it can be repeated perfectly next time. ("SOP" just means *Standard Operating Procedure* —
  a fancy phrase for *recipe*.)
- **`knowledge-base/`** = my **memory** about your business. Facts you tell me once get saved
  here so I don't forget them.
- **`CLAUDE.md`** = the **house rules** I read automatically every single time we start. It's
  what makes me behave the same reliable way every time.

---

## 3. How to talk to me (prompting)

"Prompting" is a scary word that just means **asking**. Two simple tips:

**👍 Good asks are specific and say the goal:**
> "Make me a script that reads my list of tasks and gives me a clean daily report, sorted by
> what's most important."

**👎 Vague asks make me guess:**
> "Do something with my tasks."

You don't need perfect words. If you're unsure, just describe the *outcome you want* and I'll
ask you questions to fill in the gaps. **You can't break anything by asking.**

---

## 4. The everyday loop (this is the whole rhythm)

```
   You ask  →  I do it  →  I run it & show you  →  you check  →  we save it
        ▲                                                            │
        └────────────────  ask for the next thing  ◀────────────────┘
```

That's it. Ask → I do → you check → we save → repeat. Every loop, your command center gets a
little more powerful.

---

## 5. Cloud vs. your own computer (don't worry about installing anything yet)

Right now you're using **Claude Code on the web**. That means everything runs on a computer
**in the cloud** — not on your laptop. ☁️

- ✅ You do **NOT** need to install anything to start.
- ✅ Your work is saved to GitHub (an online locker for code) when we "commit" it.
- ℹ️ *Later*, if you ever want to run things directly on your own laptop, you can install Claude
  Code there too — but that's a "someday" thing, not a "today" thing. Ask me when you're ready
  and I'll walk you through it.

**One word you'll hear: "commit."** Committing just means **saving a snapshot** of your work to
the online locker so it's safe and you can always go back. I'll do this for you and tell you when.

---

## 6. Run your first tool right now ✅

You already have a working tool. Let's prove it. Copy this line and run it:

```bash
python3 projects/daily-report/daily_report.py
```

It reads a sample task list (`projects/daily-report/tasks.csv`) and creates a tidy report file
called `daily-report.md` in that same folder. Open it and you'll see your tasks neatly organized
by priority. 🎉

Want it to use *your* real tasks? Just open `projects/daily-report/tasks.csv`, type your tasks
in, and run the line again. Or simpler: tell me *"update my tasks"* and I'll do it.

---

## 7. Three things to try next

1. Ask me: *"Add my real tasks to the daily report and run it."*
2. Ask me: *"Turn that into an SOP so we can do it the same way every Monday."*
3. Ask me: *"Save these facts about my business to the knowledge base: ..."*

Welcome aboard. You're the founder. I'm your doer. Let's compound. 💪
