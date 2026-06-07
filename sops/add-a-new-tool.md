# SOP: Add a new tool to the command center

## Goal
Add a new little tool (a script, dashboard, or agent) to `projects/` in a consistent way.

## When to do it
Whenever you want Claude to build you a new tool.

## What you need first
- A plain-English description of what you want the tool to do.
- Any sample data or examples (optional, but helpful).

## Steps
1. Decide what the tool should do (the outcome you want).
2. Ask Claude to build it (see below).
3. Claude creates a new folder under `projects/` (e.g. `projects/your-tool-name/`).
4. That folder gets: the code, a `README.md` explaining it, and sample input if needed.
5. Claude runs it to prove it works and shows you the result.
6. Claude commits (saves) it.

## How to do it with Claude
> "Build me a new tool that [describe what you want]. Put it in its own folder under projects/,
> keep it simple with no installs if possible, run it to show me it works, then save it."

## How you know it worked
- There's a new folder in `projects/`.
- It has a `README.md` with the exact command to run it.
- Claude showed you a real result from running it.

## Notes
- Prefer "no installs, no paid keys" for first versions. If a tool truly needs a paid AI key or
  an installed program, Claude will tell you clearly before going ahead.
