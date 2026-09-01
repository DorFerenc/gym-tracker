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
   (beep + vibration when done). **+ Set** adds a set for the session and **− Set** takes the last one
   back (it asks first if that set is already checked off); neither changes the plan itself.
   A progress bar tracks the sets left in the routine.
   **Finish & Save Workout** saves the session; an unfinished session survives closing the app and is
   restored on the next open.
4. **History** tab: every saved workout with all sets; expand to view or delete.
5. Backups (**Manage → Data**): **Backup JSON** = full export (plans + history), **Export CSV** = spreadsheet
   of all sets, **Import Hevy CSV** = migrate from the Hevy app.

### During a workout
- **Coach** sits at the top of the workout: tap it for today's call, read from your own logged
  history — go up in weight where you cleared every rep last time, add volume where a lift has
  stalled, hold and chase reps where you didn't. Each suggestion has an **Approve** button that
  applies it to today's session only (never to your plan), plus a motivation line based on your
  streak and time off. This part runs entirely on the phone — no network, no key, works offline.
- **Ask the coach** (optional): add your own Anthropic API key in **Manage → AI Coach** and the
  coach sheet gains a question box and quick chips (pep talk / my progress / focus today). Your
  question plus a digest of your training log goes to the Claude API and the reply comes back in
  the sheet. Details in Privacy below — read them before you turn it on.
- **i** on any exercise opens a guide: the muscles worked, step-by-step form cues, and a photo demo
  of the movement (two frames cross-faded, so you see the start and end position). Links to
  video/GIF searches are there for full-motion footage.
- **⇄** suggests alternatives that train the same muscles a different way (different angle or
  equipment), each with a one-line reason, ranked so the **top three picks** come first — closest
  stimulus, then general quality, then whether it uses the station you're already at and whether
  you've lifted it before. Swapping edits the routine in place — history is kept under the old
  name, and the same button swaps back.
- **+ Add exercise** adds one mid-session, from the 62-exercise catalog (searchable, grouped by
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
  The site is static: no server, no accounts, no analytics, no cookies. The only time workout data
  leaves the device is when you opt into the AI coach and press Ask — see below.
- The app ships with an empty plan — no personal data is embedded in the code or visible to other visitors.
  Each visitor's data is theirs alone; backup/restore is a local JSON file the user downloads/uploads.
- `gym-backup.json` (the exported data) is gitignored and must never be committed.
- Everything you type is auto-saved in the background: the in-progress workout draft is written on
  every change and flushed the moment the app is hidden or closed, and a rolling safety snapshot is
  kept after every saved workout and before every restore/delete (Manage → Restore auto-backup).
- The only external requests are the exercise demo photos, fetched from the open-source
  `yuhonas/free-exercise-db` repository on GitHub, pinned to one immutable commit so the image
  bytes can't be changed later (every URL was verified before shipping). They
  load only when you open a guide sheet, are sent with no referrer, and the CSP pins images to
  `'self' data: https://raw.githubusercontent.com` — nothing else can be loaded. `connect-src` is
  `'self' https://api.anthropic.com`, so the only scripted request the page can make is the opt-in
  coach call below; every other origin is blocked. If the photos can't load (offline,
  or a slow link — there's a 6s timeout), the sheet falls back to an inline-SVG animation the app
  draws itself, so the guide still works with no network at all.
- The service worker only handles same-origin GET requests, so neither the photos nor the API call
  are cached or intercepted by it.
- **The AI coach is off by default and opt-in.** With no key, nothing is ever sent anywhere and the
  rules-based coach works offline. If you add a key:
  - The key is stored in this browser's localStorage only. It is never put in a URL, never written
    to the JSON/CSV exports or the auto-backup snapshot, and never shown on screen after saving.
    Anyone with the unlocked phone (or a browser exploit on this origin) could read it — treat it
    like any password on the device, and remove it from **Manage → AI Coach** when you're done.
  - **Worth knowing about GitHub Pages:** browser storage is scoped to the whole origin
    (`<owner>.github.io`), not to the `/gym-tracker/` path. Any *other* Pages site published under
    the same GitHub account can therefore read this key. If you host other Pages projects, either
    put this app on its own custom domain or skip the key and use the MCP server instead.
  - Prefer a key scoped to its own Anthropic workspace with a spend limit, so a leak is bounded.
  - Requests go straight from the phone to `api.anthropic.com` with your key, so they are billed to
    **your** Anthropic account, not to any server of mine — there is no server.
  - Each question sends a digest of your log: the current routine and its planned exercises, your
    total workout count, and your last 12 workouts with weights and reps. That is workout data
    leaving the device — the one place in this app where that happens.
  - The model's reply is inserted as plain text, never as HTML, and the system prompt tells it to
    treat the log as data rather than instructions.
- The only outbound links are the optional "Video demos"/"More GIFs" buttons in the guide sheet,
  which open a YouTube/Google search in a new tab and are never loaded automatically.
- The site sends no referrer and carries a `noindex` meta tag asking search engines not to index it.
  (robots.txt only takes effect if the app is ever hosted at a domain root — on a GitHub Pages
  project path crawlers don't read it, so the meta tag is what actually applies.)
- Untrusted input (imported backups, Hevy CSVs, typed names) is escaped before it reaches the DOM,
  CSV cells are quoted and formula-injection-neutralized on export, and imports are structure-validated.
