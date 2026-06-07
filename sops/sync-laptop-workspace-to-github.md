# SOP: Sync my laptop "Claude workspace" folder with GitHub

## Goal
Keep the files on my laptop (where Claude Co-Work writes) and the files in the GitHub
`xExtate` repo (where Claude Code writes) in sync, using GitHub as the shared hub — so both
"Claudes" can read and build on the same brain.

## When to do it
- Once, to set it up.
- Then: **pull** before you start a work session, and **push** after Co-Work (or you) makes changes.

## What you need first
- A free **GitHub Desktop** app (Mac or Windows): https://desktop.github.com
- Your GitHub login (the account `faisalhamid6-cell`).
- The folder on your laptop where Claude Co-Work writes its files.

## One-time setup
1. Install and open **GitHub Desktop**; sign in to GitHub.
2. **Clone** the `xExtate` repo to your laptop: *File → Clone repository →* pick
   `faisalhamid6-cell/xExtate` → choose where to save it → **Clone**.
3. You now have an `xExtate` folder on your laptop with a `workspace/` subfolder inside it.
4. **Switch to the working branch:** in GitHub Desktop, click the **"Current Branch"**
   dropdown at the top and choose **`claude/pensive-cori-ywRyY`** (this is the branch Claude
   Code is working on, so both sides share the exact same files). Later, once we merge this
   into `main`, we'll both switch to `main` as the permanent shared brain.
5. **Point Co-Work at that `workspace/` folder** (if Co-Work lets you choose its folder),
   OR copy your existing workspace files into `xExtate/workspace/`.
6. In GitHub Desktop you'll see the new files listed. Type a short summary (e.g. "Add my
   277 workflows"), click **Commit**, then click **Push origin**. Done — they're on GitHub,
   and Claude Code can now read them.

## Everyday use
- **Before working:** open GitHub Desktop → click **Fetch/Pull** (gets Claude Code's latest).
- **After changes:** type a summary → **Commit** → **Push** (sends your latest up).

## How to do it with Claude
> "Pull the latest workspace files and tell me what changed."
> or
> "Read my workspace folder and use it for the next task."

## How you know it worked
- The files appear in the repo on github.com under the `workspace/` folder.
- Claude Code can read them and refer to their contents.

## Notes
- **Golden rule:** pull before you write, push after. Avoid Co-Work and Claude Code editing
  the *same file at once* (GitHub will flag a "conflict" — Claude will help resolve it).
- **Want zero clicking?** Claude can write you a small auto-sync script that pushes changes
  the moment Co-Work saves them. Ask for it once the manual version feels comfortable.
- **Never commit secrets** (passwords, API keys) — this folder is public on GitHub.
