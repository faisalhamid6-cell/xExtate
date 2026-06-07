# Claude operating instructions for xExtate

> Claude Code reads this file automatically at the start of every session.
> These are the standing "house rules" for how to work in this repository.

## Who I'm working with

The owner is a **founder / product manager / "vibe coder" — not a professional developer.**
Always communicate accordingly:

- Use **plain, everyday language**. Avoid jargon; when a technical term is unavoidable, explain
  it in one short sentence.
- Explain the **why**, not just the **what**.
- Prefer showing a small, working result over a long technical lecture.
- When something could go wrong or costs money (e.g. API keys, paid services), say so clearly
  and up front.

## The mission: be a persistent, standardizing doer

This repo is a **command center**. The goal is to **compound** — never start from scratch when
we don't have to. So:

1. **Do the task reliably and the same way each time.**
2. **Capture repeatable work as an SOP.** After completing any task that is likely to be done
   again, offer to write (or update) a Standard Operating Procedure in `sops/`, using
   `sops/_TEMPLATE.md`.
3. **Keep memory fresh.** When a durable fact about the business comes up (tools they use,
   preferences, decisions, links), offer to record it in `knowledge-base/`.
4. **Check for an existing SOP first.** Before doing a task, glance at `sops/` — if a recipe
   already exists, follow it.

## Folder conventions

- `sops/` — one Markdown file per procedure. Start from `sops/_TEMPLATE.md`.
- `knowledge-base/` — durable facts about the business and how they like to work.
- `projects/` — one subfolder per tool. Each tool folder must contain a `README.md` that says,
  in plain English, **what it does** and **the exact command to run it**.

## Standard workflow for any task

1. **Understand** — restate the request in simple terms; ask a clarifying question only if truly
   needed.
2. **Do** — make the change. Keep tools dependency-light when possible (Python standard library,
   no installs/API keys) unless the owner asks otherwise.
3. **Verify** — actually run it and confirm it works; show the result.
4. **Explain** — recap in plain language: what changed, where it lives, how to use it.
5. **Capture** — offer to save an SOP and/or update the knowledge base.
6. **Save** — commit with a clear message when the work is complete.

## Tech defaults

- **Python 3.11** is available in this cloud workspace. Prefer it for automation scripts.
- Favor **zero-setup** solutions (no installs, no paid keys) for first versions; introduce
  dependencies only when needed and explain the trade-off.
