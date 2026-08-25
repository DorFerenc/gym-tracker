# Gym Tracker
Personal workout tracker PWA (English UI) + MCP server for AI access.
- Deploy: push to GitHub, enable Pages, Add to Home Screen on the phone.
- AI access: mcp-server/server.py reads/updates gym-backup.json (exported from the app).
- Full setup is automated: open this folder in Claude Code and paste PROMPT.txt.

## How to use

### On the phone (the app)
1. Open the site (GitHub Pages URL) → browser menu → **Add to Home Screen**. It works offline from then on.
2. First time: go to **Manage → Workout Plans** and build your plan. The app ships with one empty
   routine **A** — give it a name in the editor and add exercises with **+ Exercise** (name · sets · reps ·
   weight · rest). **+ Routine** adds further routines (B/C…, named e.g. "Pull"); ✕ deletes one.
   Already have data? **Manage → Restore JSON** imports a `gym-backup.json` and replaces everything.
3. Training (**Workout** tab): the app suggests the next routine in rotation and pre-fills each exercise
   with what you lifted last time. Type weight/reps, hit **✓** per set — the rest timer starts itself
   (beep + vibration when done). **Finish & Save Workout** saves the session; an unfinished session survives
   closing the app and is restored on the next open.
4. **History** tab: every saved workout with all sets; expand to view or delete.
5. Backups (**Manage → Data**): **Backup JSON** = full export (plans + history), **Export CSV** = spreadsheet
   of all sets, **Import Hevy CSV** = migrate from the Hevy app.

### With AI (the MCP server)
1. In the app: **Manage → Backup JSON**, put the file at this repo's root as `gym-backup.json`.
2. Register `mcp-server/server.py` per CLAUDE.md Task 2 (`claude mcp add`, or create a local `.mcp.json`
   pointing your venv's python at the script — it's machine-specific, so it isn't committed) — the AI can then
   summarize progress, log workouts, and edit plans via tools like `get_summary`, `add_workout`, `exercise_progress`.
3. To get AI changes back on the phone: transfer the updated `gym-backup.json` to the phone and
   **Manage → Restore JSON**. (No auto-sync — the file is the bridge.)

### Local development
Serve the folder (`python -m http.server`) and open `http://localhost:8000` — it's a single
self-contained `index.html`, no build step.

## Privacy
- All workout data lives only in the user's own browser storage (localStorage) on their device.
  The site is static: no server, no accounts, no analytics, no cookies, no network calls with user data.
- The app ships with an empty plan — no personal data is embedded in the code or visible to other visitors.
  Each visitor's data is theirs alone; backup/restore is a local JSON file the user downloads/uploads.
- `gym-backup.json` (the exported data) is gitignored and must never be committed.
- Each exercise card has a **⇄** button: pick a recommended alternative that works the same muscles
  with a different angle or equipment. Swapping edits the routine in place (history is kept) and the
  same button swaps back.
- Each exercise card has an **i** button: a bottom sheet with an English how-to, the muscles worked,
  and a demo GIF (hotlinked from fitnessprogramer.com, fetched only when the sheet is opened, with
  referrer disabled; if it can't load, the sheet offers video/GIF search links instead).
- Everything you type is auto-saved in the background: the in-progress workout draft is written on
  every change and flushed the moment the app is hidden or closed, and a rolling safety snapshot is
  kept after every saved workout and before every restore/delete (Manage → Restore auto-backup).
- The service worker only handles same-origin GET requests; the CSP allows images only from
  fitnessprogramer.com (the exercise demo GIFs) and blocks all other external connections;
  the site sends no referrer and carries a `noindex` meta tag asking search engines not to index it.
  (robots.txt only takes effect if the app is ever hosted at a domain root — on a GitHub Pages
  project path crawlers don't read it, so the meta tag is what actually applies.)
