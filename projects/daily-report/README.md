# Daily Report 📋

Your first tool! It takes a messy list of tasks and turns it into a clean, organized daily
report — grouped by status, with the most important tasks at the top.

## How to run it

Copy and run this one line:

```bash
python3 projects/daily-report/daily_report.py
```

That creates a file called `daily-report.md` in this folder. Open it to read your report.

## How to use your own tasks

Open `tasks.csv` (it's just a simple table) and edit it. It has three columns:

| Column | What to put | Allowed values |
|---|---|---|
| `task` | What needs doing | any text |
| `priority` | How important it is | `high`, `medium`, or `low` |
| `status` | Where it stands | `To Do`, `In Progress`, or `Done` |

Then run the command again. That's it!

> Tip: You don't have to edit the file yourself. Just tell Claude
> *"add these tasks to my daily report and run it"* and it'll do it for you.

## Good to know

- ✅ No installation needed — it uses only built-in Python.
- ✅ No internet or paid keys needed.
- It's safe to run as many times as you like; it just rewrites the report each time.
