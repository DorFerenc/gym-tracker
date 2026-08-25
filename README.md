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
   (beep + vibration when done). A progress bar tracks the sets left in the routine.
   **Finish & Save Workout** saves the session; an unfinished session survives closing the app and is
   restored on the next open.
4. **History** tab: every saved workout with all sets; expand to view or delete.
5. Backups (**Manage → Data**): **Backup JSON** = full export (plans + history), **Export CSV** = spreadsheet
   of all sets, **Import Hevy CSV** = migrate from the Hevy app.

### During a workout
- **i** on any exercise opens a guide: the muscles worked, step-by-step form cues, and a built-in
  animated demo of the movement. Links to video/GIF searches are there for a real-footage demo.
- **⇄** suggests alternatives that train the same muscles a different way (different angle or
  equipment), each with a one-line reason. Swapping edits the routine in place — history is kept
  under the old name, and the same button swaps back.
- **+ Add exercise** adds one mid-session, from the 44-exercise catalog (searchable, grouped by
  equipment) or as a custom name. It stays in the routine; remove it later in Manage.
- **⇅ Plan order / Gym order** regroups the routine by equipment zone — barbell & rack, dumbbells,
  machines, cables, pull-up & bodyweight, mat & core — so you finish one station before moving on
  instead of criss-crossing the gym floor. The order is a view only: your plan is untouched.

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
- Everything you type is auto-saved in the background: the in-progress workout draft is written on
  every change and flushed the moment the app is hidden or closed, and a rolling safety snapshot is
  kept after every saved workout and before every restore/delete (Manage → Restore auto-backup).
- The exercise demo animations are drawn by the app itself (inline SVG), not fetched. Nothing is
  hotlinked, so the app makes **zero** external requests: the CSP is `default-src 'none'` with
  images limited to `'self' data:`, and the service worker only handles same-origin GET requests.
  Earlier versions hotlinked GIFs from a fitness site; that needed an external origin in the CSP and
  broke whenever a URL moved, so the animations were brought in-house.
- The only outbound links are the optional "Video demos"/"More GIFs" buttons in the guide sheet,
  which open a YouTube/Google search in a new tab and are never loaded automatically.
- The site sends no referrer and carries a `noindex` meta tag asking search engines not to index it.
  (robots.txt only takes effect if the app is ever hosted at a domain root — on a GitHub Pages
  project path crawlers don't read it, so the meta tag is what actually applies.)
- Untrusted input (imported backups, Hevy CSVs, typed names) is escaped before it reaches the DOM,
  CSV cells are quoted and formula-injection-neutralized on export, and imports are structure-validated.
