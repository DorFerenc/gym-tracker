"""Gym Tracker MCP server — reads/updates gym-backup.json exported from the PWA.

Register (Claude Code):   claude mcp add gym -- python /path/to/mcp-server/server.py
Register (Claude Desktop): add to claude_desktop_config.json mcpServers.
Data file: env GYM_DATA, or ../gym-backup.json next to this repo.
"""
import json
import os
from datetime import date as _date

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("GYM_DATA", os.path.join(HERE, "..", "gym-backup.json"))

mcp = FastMCP("gym-tracker")


def _load() -> dict:
    if not os.path.exists(DATA):
        raise FileNotFoundError(
            f"Data file not found: {DATA}. Export 'gym-backup.json' from the app "
            "(ניהול → גיבוי JSON) and place it there, or set env GYM_DATA."
        )
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def _save(d: dict) -> None:
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA)


def _fmt_set(s: dict) -> str:
    w = s.get("w") or "BW"
    return f"{w}x{s.get('r')}"


@mcp.tool()
def get_summary() -> str:
    """Overview: workout count, last workout, available plans and routines."""
    d = _load()
    hist = d.get("history", [])
    plans = d.get("plans", {})
    lines = [f"Workouts logged: {len(hist)}", f"Active plan: {d.get('activePlan')}"]
    for pid, p in plans.items():
        routines = ", ".join(f"{r}({len(rt.get('ex', []))} ex)" for r, rt in p.get("routines", {}).items())
        lines.append(f"Plan {pid}: {p.get('name')} — {routines}")
    if hist:
        last = hist[-1]
        lines.append(f"Last workout: {last['date']} routine {last['routine']} "
                     f"({len(last.get('entries', []))} exercises)")
    return "\n".join(lines)


@mcp.tool()
def list_workouts(limit: int = 10, exercise: str = "") -> str:
    """Recent workouts, newest first. Optional case-insensitive exercise name filter."""
    d = _load()
    out = []
    for w in reversed(d.get("history", [])):
        entries = w.get("entries", [])
        if exercise:
            entries = [e for e in entries if exercise.lower() in e["name"].lower()]
            if not entries:
                continue
        body = "; ".join(f"{e['name']}: {', '.join(_fmt_set(s) for s in e['sets'])}" for e in entries)
        dur = f" [{w['duration_min']}min]" if w.get("duration_min") else ""
        out.append(f"{w['date']} {w.get('routine', '?')}{dur} — {body}")
        if len(out) >= limit:
            break
    return "\n".join(out) or "No matching workouts."


@mcp.tool()
def exercise_progress(exercise: str) -> str:
    """Progression for one exercise: date, top-set weight, total volume (kg*reps)."""
    d = _load()
    rows = []
    for w in d.get("history", []):
        for e in w.get("entries", []):
            if exercise.lower() in e["name"].lower():
                sets = e.get("sets", [])
                try:
                    top = max(float(s.get("w") or 0) for s in sets)
                    vol = sum(float(s.get("w") or 0) * float(s.get("r") or 0) for s in sets)
                except (TypeError, ValueError):
                    top, vol = 0, 0
                rows.append(f"{w['date']}: top {top:g} kg, {len(sets)} sets, volume {vol:g}")
    return "\n".join(rows) or f"No history for '{exercise}'."


@mcp.tool()
def add_workout(routine: str, entries_json: str, plan: str = "", day: str = "", duration_min: int = 0) -> str:
    """Log a workout. entries_json: [{"name": "...", "sets": [{"w": 24, "r": 10}, ...]}, ...].
    day defaults to today (YYYY-MM-DD); plan defaults to the active plan."""
    d = _load()
    entries = json.loads(entries_json)
    if not isinstance(entries, list) or not entries:
        return "entries_json must be a non-empty JSON list."
    w = {
        "date": day or _date.today().isoformat(),
        "plan": plan or d.get("activePlan", "2"),
        "routine": routine,
        "duration_min": duration_min or "",
        "entries": entries,
    }
    d.setdefault("history", []).append(w)
    d["history"].sort(key=lambda x: x.get("date", ""))
    _save(d)
    return f"Saved workout {w['date']} routine {routine} ({len(entries)} exercises)."


@mcp.tool()
def get_plan(plan_id: str = "") -> str:
    """Full definition of a plan (default: active plan): routines, exercises, targets."""
    d = _load()
    pid = plan_id or d.get("activePlan")
    p = d.get("plans", {}).get(pid)
    if not p:
        return f"No plan '{pid}'. Available: {', '.join(d.get('plans', {}))}"
    lines = [f"Plan {pid}: {p.get('name')}"]
    for r, rt in p.get("routines", {}).items():
        lines.append(f"  {r} ({rt.get('name', '')}):")
        for ex in rt.get("ex", []):
            lines.append(f"    - {ex['n']}: {ex.get('sets')}x{ex.get('reps')} @ {ex.get('w')}kg, "
                         f"rest {ex.get('rest')}s. {ex.get('note', '')}")
    return "\n".join(lines)


@mcp.tool()
def update_exercise(routine: str, exercise_name: str, field: str, value: str, plan_id: str = "") -> str:
    """Update one field of an exercise. field: n|sets|reps|w|rep|rest|note. Matches name case-insensitively."""
    d = _load()
    pid = plan_id or d.get("activePlan")
    rt = d.get("plans", {}).get(pid, {}).get("routines", {}).get(routine)
    if rt is None:
        return f"No routine '{routine}' in plan '{pid}'."
    for ex in rt.get("ex", []):
        if exercise_name.lower() in ex["n"].lower():
            if field in ("sets", "rep", "rest"):
                ex[field] = int(value)
            elif field == "w":
                ex[field] = float(value)
            elif field in ("n", "reps", "note"):
                ex[field] = value
            else:
                return f"Unknown field '{field}'."
            _save(d)
            return f"Updated {ex['n']}.{field} = {value}"
    return f"No exercise matching '{exercise_name}' in {pid}/{routine}."


@mcp.tool()
def add_exercise(routine: str, name: str, sets: int = 3, reps: str = "10", weight: float = 20,
                 rest: int = 90, note: str = "", plan_id: str = "") -> str:
    """Add an exercise to a routine in a plan (default: active plan)."""
    d = _load()
    pid = plan_id or d.get("activePlan")
    rt = d.get("plans", {}).get(pid, {}).get("routines", {}).get(routine)
    if rt is None:
        return f"No routine '{routine}' in plan '{pid}'."
    rep = int("".join(ch for ch in reps if ch.isdigit()) or 10)
    rt.setdefault("ex", []).append(
        {"n": name, "sets": sets, "reps": reps, "w": weight, "rep": rep, "rest": rest, "note": note}
    )
    _save(d)
    return f"Added '{name}' to {pid}/{routine}."


if __name__ == "__main__":
    mcp.run()
