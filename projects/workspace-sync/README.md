# Workspace Auto-Sync (Windows) 🔄

Keeps your laptop's Claude workspace folder and the GitHub repo in sync **automatically** —
Co-Work's changes go up, Claude Code's changes come down, every few minutes, no clicking.

## What it does
Every run, the script: saves Co-Work's changes → pulls Claude Code's changes → pushes
everything to GitHub. You set it up once; then it just runs in the background.

## One-time setup (3 steps)

**Step 1 — Install GitHub Desktop and clone the repo.**
- Download **GitHub Desktop** (free): https://desktop.github.com — sign in.
- *File → Clone repository →* choose `faisalhamid6-cell/xExtate` → **Clone**.
  (This installs Git, handles your login, AND puts this script on your laptop.)
- Click the **"Current Branch"** dropdown and switch to **`claude/pensive-cori-ywRyY`**.

**Step 2 — Point Co-Work at the workspace folder.**
- Set Claude Co-Work to write into the `workspace\` folder inside your cloned `xExtate`
  folder (e.g. `C:\Users\You\Documents\GitHub\xExtate\workspace`). If Co-Work's folder
  can't be moved, just copy your files into that `workspace\` folder.

**Step 3 — Turn on automatic syncing.**
- In File Explorer, go to `xExtate\projects\workspace-sync`, right-click `sync.ps1` →
  **Copy as path**.
- Open **PowerShell** and paste this command (replace the path with the one you copied):

  ```powershell
  schtasks /Create /SC MINUTE /MO 5 /TN "ClaudeWorkspaceSync" `
    /TR "powershell -NoProfile -ExecutionPolicy Bypass -File \"PASTE_PATH_HERE\"" /F
  ```

  That runs the sync every 5 minutes, forever. Done! ✅

## How to check it's working
- Open `workspace\sync-log.txt` — you'll see timestamped "Sync complete" lines.
- Or look at the repo on github.com; your files appear under `workspace/`.

## To pause / stop it
```powershell
schtasks /Delete /TN "ClaudeWorkspaceSync" /F
```

## Good to know
- 💵 **Cost:** free.
- ⭐ **Golden rule:** if the log says "CONFLICT", it means the laptop and the cloud edited
  the same file at the same time. Nothing is lost — just tell Claude *"resolve the workspace
  conflict"* and it'll sort it out.
- 🔒 Never put passwords or API keys in the workspace folder — it's public on GitHub.
