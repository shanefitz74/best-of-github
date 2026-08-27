#!/usr/bin/env python3
"""
Fetch a real weekly snapshot of notable GitHub repositories and write _data.json.

Methodology (honest about GitHub API limits):
  - "Fresh this week": repos CREATED in the last 7 days, ranked by current stars.
  - "Still on fire": popular repos (>=5k stars) PUSHED in the last 7 days, ranked by stars.
  - GitHub has NO "stars gained this week" field, so we use creation/update windows.

Unauthenticated: ~10 search req/min. Paces requests with a simple limiter.
With GITHUB_TOKEN set: 30 req/min + richer data (topics, etc).
"""
import json, os, sys, time, urllib.parse, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def load_dotenv(path):
    """Minimal .env reader. Token stays local on disk — never printed, never logged."""
    env = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                env[k.strip()] = v
    except FileNotFoundError:
        pass
    return env

dot = load_dotenv(os.path.join(HERE, ".env"))
TOKEN = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
         or dot.get("GITHUB_TOKEN") or dot.get("GH_TOKEN") or "").strip()

def token_valid(tok):
    if not tok:
        return False
    req = urllib.request.Request("https://api.github.com/user", headers={
        "User-Agent": "best-of-github-weekly",
        "Authorization": f"Bearer {tok}",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False

AUTH = bool(TOKEN) and token_valid(TOKEN)
if TOKEN and not AUTH:
    print("WARNING: GITHUB_TOKEN present but rejected by GitHub (401). Falling back to unauthenticated.", file=sys.stderr)
    TOKEN = None
RATE_MIN = 30 if AUTH else 10  # requests per minute we self-limit to
PER = 60.0 / RATE_MIN
_last = [0.0]

def pace():
    now = time.time()
    wait = _last[0] + PER - now
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()

def api_get(url):
    pace()
    req = urllib.request.Request(url, headers={
        "User-Agent": "best-of-github-weekly",
        "Accept": "application/vnd.github+json",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                remain = r.headers.get("X-RateLimit-Remaining")
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise

def search(q, sort="stars", order="desc", per_page=30):
    base = "https://api.github.com/search/repositories"
    params = urllib.parse.urlencode({"q": q, "sort": sort, "order": order, "per_page": per_page})
    return api_get(f"{base}?{params}")

def days_ago_iso(d):
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ")

def clean(item):
    return {
        "name": item["name"],
        "full_name": item["full_name"],
        "owner": item["owner"]["login"],
        "owner_avatar": item["owner"].get("avatar_url", ""),
        "html_url": item["html_url"],
        "description": (item.get("description") or "").strip(),
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "open_issues": item.get("open_issues_count", 0),
        "language": item.get("language"),
        "topics": item.get("topics", [])[:8],
        "created_at": item.get("created_at"),
        "pushed_at": item.get("pushed_at"),
        "license": (item.get("license") or {}).get("spdx_id"),
    }

def load_history():
    """Return list of weekly snapshots: [{week, date, repos:{full_name:stars}}, ...] (oldest first)."""
    p = os.path.join(HERE, "_history.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(week_label, date_start, fresh_items, fire_items):
    """Append (or replace) this week's snapshot so build.py can show rank deltas + sparklines."""
    hist = load_history()
    snap = {
        "week": week_label,
        "date": date_start,
        "repos": {r["full_name"]: r["stars"] for r in (fresh_items + fire_items) if r.get("full_name")},
    }
    # replace any existing snapshot for the same week label
    hist = [h for h in hist if h.get("week") != week_label]
    hist.append(snap)
    # keep at most 12 weeks
    hist = hist[-12:]
    with open(os.path.join(HERE, "_history.json"), "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)
    print(f"Wrote _history.json: {len(hist)} weekly snapshots", file=sys.stderr)

def compute_trends(hist):
    """Build per-repo trend info from history.
    Returns dict full_name -> {series:[stars per week], delta:int|None, status:'up'|'down'|'new'|'flat'}"""
    if len(hist) < 2:
        return {}
    prev, cur = hist[-2], hist[-1]
    prev_repos = prev.get("repos", {})
    cur_repos = cur.get("repos", {})
    # rank delta within current week's ordering (by stars)
    cur_sorted = sorted(cur_repos.items(), key=lambda kv: kv[1], reverse=True)
    prev_sorted = sorted(prev_repos.items(), key=lambda kv: kv[1], reverse=True)
    prev_rank = {name: i + 1 for i, (name, _) in enumerate(prev_sorted)}
    # build series per repo across all weeks
    weeks = [h.get("repos", {}) for h in hist]
    series = {}
    names = set()
    for w in weeks:
        names.update(w.keys())
    for name in names:
        series[name] = [w.get(name) for w in weeks]  # None where absent
    trends = {}
    for name, stars in cur_repos.items():
        s = series.get(name, [])
        clean = [v for v in s if v is not None]
        prev_stars = prev_repos.get(name)
        if prev_stars is None:
            status = "new"
            delta = None
        else:
            delta = stars - prev_stars
            status = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        rank = cur_sorted.index((name, stars)) + 1 if (name, stars) in cur_sorted else None
        prev_r = prev_rank.get(name)
        rank_delta = (prev_r - rank) if (prev_r and rank) else None
        trends[name] = {
            "series": s,
            "delta": delta,
            "status": status,
            "rank_delta": rank_delta,
        }
    return trends

def main():
    since = days_ago_iso(7)
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("Fetching 'fresh this week' (created in last 7 days)...", file=sys.stderr)
    fresh_per = 50 if AUTH else 40
    fresh = search(f"created:>{since}", per_page=fresh_per)
    fresh_items = [clean(i) for i in fresh.get("items", [])]
    fresh_items.sort(key=lambda x: x["stars"], reverse=True)
    fresh_items = fresh_items[:50 if AUTH else 30]

    print("Fetching 'still on fire' (popular, pushed in last 7 days)...", file=sys.stderr)
    fire_per = 50 if AUTH else 40
    fire_threshold = "stars:>1000" if AUTH else "stars:>5000"
    fire = search(f"pushed:>{since} {fire_threshold}", per_page=fire_per)
    fire_items = [clean(i) for i in fire.get("items", [])]
    fire_items.sort(key=lambda x: x["stars"], reverse=True)
    fire_items = fire_items[:40 if AUTH else 20]

    date_range_start = since[:10]
    date_range_end = now_iso[:10]
    # week label
    wk_start = datetime.datetime.strptime(date_range_start, "%Y-%m-%d")
    wk_end = datetime.datetime.strptime(date_range_end, "%Y-%m-%d")
    iso_week = wk_start.isocalendar()[1]
    week_label = f"Week {iso_week} · {date_range_start} — {date_range_end}"

    # --- Trend Intelligence: persist a weekly snapshot for delta/sparkline ---
    save_history(week_label, date_range_start, fresh_items, fire_items)

    hist = load_history()
    trends = compute_trends(hist)
    out = {
        "generated_at": now_iso,
        "week_label": week_label,
        "date_range_start": date_range_start,
        "date_range_end": date_range_end,
        "history_weeks": [h.get("week") for h in hist],
        "trends": trends,
        "methodology": (
            "GitHub's API exposes no 'stars gained this week' metric, so this digest ranks two honest slices: "
            "(1) repositories CREATED in the last 7 days by current star count, and "
            "(2) established repositories (>=5k stars) PUSHED in the last 7 days by total stars. "
            "Star counts are a live snapshot at generation time."
        ),
        "source": "GitHub REST API (api.github.com)",
        "authenticated": AUTH,
        "fresh_this_week": fresh_items,
        "still_on_fire": fire_items,
    }

    with open(os.path.join(os.path.dirname(__file__), "_data.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # --- Persist a full per-week snapshot so the site's week picker can reload history ---
    try:
        import re as _re
        safe = _re.sub(r"[^\w\-]+", "_", week_label).strip("_")
        wk_dir = os.path.join(os.path.dirname(__file__), "weeks")
        os.makedirs(wk_dir, exist_ok=True)
        with open(os.path.join(wk_dir, f"week_{safe}.json"), "w", encoding="utf-8") as wf:
            json.dump(out, wf, ensure_ascii=False, indent=2)
        # manifest of available week files (so the site's picker only offers loadable weeks)
        man_path = os.path.join(wk_dir, "manifest.json")
        try:
            man = json.load(open(man_path, encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            man = []
        man = [m for m in man if m.get("file") != f"week_{safe}.json"]
        man.append({"file": f"week_{safe}.json", "week": week_label,
                    "start": date_range_start, "end": date_range_end})
        man.sort(key=lambda m: m.get("start", ""))
        json.dump(man, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Wrote weeks/week_{safe}.json + manifest ({len(man)} weeks)", file=sys.stderr)
    except Exception as e:
        print(f"Warn: could not write per-week file: {e}", file=sys.stderr)
    print(f"Wrote _data.json: {len(fresh_items)} fresh + {len(fire_items)} on-fire repos", file=sys.stderr)

if __name__ == "__main__":
    main()
