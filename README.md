# Gym Tracker
Personal workout tracker PWA (Hebrew) + MCP server for AI access.
- Deploy: push to GitHub, enable Pages, Add to Home Screen on the phone.
- AI access: mcp-server/server.py reads/updates gym-backup.json (exported from the app).
- Full setup is automated: open this folder in Claude Code and paste PROMPT.txt.

## How to use

### On the phone (the app)
1. Open the site (GitHub Pages URL) → browser menu → **Add to Home Screen**. It works offline from then on.
2. First time: go to **ניהול → תוכניות אימון** and build your plan. The app ships with one empty
   routine **A** — give it a name in the editor and add exercises with **+ תרגיל** (name · sets · reps ·
   weight · rest). **+ אימון לתוכנית** adds further routines (B/C…, named e.g. "Pull"); ✕ deletes one.
   Already have data? **ניהול → שחזור JSON** imports a `gym-backup.json` and replaces everything.
3. Training (**אימון** tab): the app suggests the next routine in rotation and pre-fills each exercise
   with what you lifted last time. Type weight/reps, hit **✓** per set — the rest timer starts itself
   (beep + vibration when done). **סיים ושמור אימון** saves the session; an unfinished session survives
   closing the app and is restored on the next open.
4. **היסטוריה** tab: every saved workout with all sets; expand to view or delete.
5. Backups (**ניהול → נתונים**): **גיבוי JSON** = full export (plans + history), **ייצוא CSV** = spreadsheet
   of all sets, **ייבוא Hevy CSV** = migrate from the Hevy app.

### With AI (the MCP server)
1. In the app: **ניהול → גיבוי JSON**, put the file at this repo's root as `gym-backup.json`.
2. Register `mcp-server/server.py` per CLAUDE.md Task 2 (`claude mcp add`, or create a local `.mcp.json`
   pointing your venv's python at the script — it's machine-specific, so it isn't committed) — the AI can then
   summarize progress, log workouts, and edit plans via tools like `get_summary`, `add_workout`, `exercise_progress`.
3. To get AI changes back on the phone: transfer the updated `gym-backup.json` to the phone and
   **ניהול → שחזור JSON**. (No auto-sync — the file is the bridge.)

### Local development
Serve the folder (`python -m http.server`) and open `http://localhost:8000` — it's a single
self-contained `index.html`, no build step.

## Privacy
- All workout data lives only in the user's own browser storage (localStorage) on their device.
  The site is static: no server, no accounts, no analytics, no cookies, no network calls with user data.
- The app ships with an empty plan — no personal data is embedded in the code or visible to other visitors.
  Each visitor's data is theirs alone; backup/restore is a local JSON file the user downloads/uploads.
- `gym-backup.json` (the exported data) is gitignored and must never be committed.
- The service worker only handles same-origin GET requests; a CSP meta tag blocks all external connections;
  the site sends no referrer and carries a `noindex` meta tag asking search engines not to index it.
  (robots.txt only takes effect if the app is ever hosted at a domain root — on a GitHub Pages
  project path crawlers don't read it, so the meta tag is what actually applies.)
