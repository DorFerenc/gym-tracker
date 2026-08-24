# Gym Tracker
Personal workout tracker PWA (Hebrew) + MCP server for AI access.
- Deploy: push to GitHub, enable Pages, Add to Home Screen on the phone.
- AI access: mcp-server/server.py reads/updates gym-backup.json (exported from the app).
- Full setup is automated: open this folder in Claude Code and paste PROMPT.txt.

## Privacy
- All workout data lives only in the user's own browser storage (localStorage) on their device.
  The site is static: no server, no accounts, no analytics, no cookies, no network calls with user data.
- The app ships with an empty plan — no personal data is embedded in the code or visible to other visitors.
  Each visitor's data is theirs alone; backup/restore is a local JSON file the user downloads/uploads.
- `gym-backup.json` (the exported data) is gitignored and must never be committed.
- The service worker only handles same-origin GET requests; a CSP meta tag blocks all external connections;
  the site sends no referrer and asks search engines not to index it (robots.txt + noindex).
