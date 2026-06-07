# Workspace — your shared brain 🧠🔄

This folder is a **mirror of the "Claude workspace" folder on your laptop** (the one
Claude Co-Work writes to). It's how your laptop and Claude Code (in the cloud) share the
same files — your 277 workflows, ideas, notes, and anything else worth keeping in one place.

## How the syncing works (the simple picture)

```
  YOUR LAPTOP                 GITHUB (the hub)              CLAUDE CODE (cloud)
  Co-Work writes   ──push──▶   xExtate repo    ◀──push──    I read & write here
  to this folder   ◀──pull──   (this folder)    ──pull──▶
```

**GitHub is the meeting point.** Both sides "push" (send changes up) and "pull" (get the
latest). I do this automatically. Your laptop does it with **GitHub Desktop** (or an
auto-sync script).

## The two golden rules ⭐

1. **Pull before you write, push after you write.** That keeps both sides current.
2. **Don't let Co-Work and Claude Code edit the *same file at the same moment*.** If it
   happens, GitHub flags a "conflict" — harmless, and Claude will help you fix it. Nothing
   is ever lost.

## What goes here

- Your 277-workflow list and architecture notes.
- Idea docs, brainstorms, research.
- Anything Co-Work produces that you want Claude Code to read or improve.

## ⚠️ Never put secrets here

No passwords, API keys, or tokens — this syncs to GitHub. If a secret is ever needed,
Claude will tell you the safe way to provide it.

## Setting it up

See the step-by-step recipe: `sops/sync-laptop-workspace-to-github.md`.
