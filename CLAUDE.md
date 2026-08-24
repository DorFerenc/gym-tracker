# Gym Tracker — instructions for Claude Code

Personal workout tracker PWA + MCP server. Owner: Dor. Do all steps without asking
unless a command fails or credentials are missing.

## Repo layout
- `index.html`, `manifest.json`, `sw.js`, `icon-*.png` — the PWA (single-file app, Hebrew RTL, localStorage).
- `mcp-server/server.py` — MCP server exposing the workout data to AI tools.
- Data file: `gym-backup.json` at repo root (exported from the app UI: ניהול → גיבוי JSON). Gitignored.

## Task 1 — Deploy the app to GitHub Pages
1. `git init` (if needed), create `.gitignore` containing `gym-backup.json` and `.venv/`.
2. Commit all files.
3. `gh repo create gym-tracker --public --source . --push` (ask the user only if `gh` is not authenticated).
4. Enable Pages from main branch root:
   `gh api repos/{owner}/gym-tracker/pages -X POST -f "source[branch]=main" -f "source[path]=/"`
   (if it already exists, use -X PUT).
5. Print the final URL: `https://<owner>.github.io/gym-tracker/` and tell the user:
   open it on the phone → browser menu → Add to Home Screen.

## Task 2 — Set up the MCP server
1. `python -m venv .venv && .venv/bin/pip install -r mcp-server/requirements.txt`
   (Windows: `.venv\Scripts\pip`).
2. Register for Claude Code:
   `claude mcp add gym -- <abs-path-to>/.venv/bin/python <abs-path-to>/mcp-server/server.py`
3. Also print the JSON snippet for Claude Desktop's `claude_desktop_config.json` (mcpServers entry) so the user can paste it there if they want it in Desktop too.
4. If `gym-backup.json` is missing, tell the user to export it from the app and drop it at repo root. Do not fabricate data.

## Task 3 — Verify
- Serve locally (`python -m http.server`) and confirm index.html loads without console errors.
- Run the MCP server once and confirm it starts; if `gym-backup.json` exists, call get_summary logic by importing the module and calling the underlying functions in a quick python -c check.

## Data flow (important)
Phone PWA (localStorage) and this repo do NOT auto-sync. Current loop:
app → "גיבוי JSON" → replace `gym-backup.json` here → AI reads/updates via MCP →
user re-imports the file in the app (ניהול → שחזור JSON).
A future task may add GitHub Gist sync inside the app to remove the manual step — do not build it unless asked.

## Conventions
- App is a single self-contained index.html — keep it that way (no build step, no frameworks).
- All history entries: {date: "YYYY-MM-DD", plan, routine, duration_min, entries: [{name, sets: [{w, r}]}]}.
- Hebrew UI strings; code and identifiers in English.
