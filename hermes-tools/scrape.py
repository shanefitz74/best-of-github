#!/usr/bin/env python3
"""
scrape.py — Collect Hermes-agent-related tools, addons, and skills from the
real public sources:

  1. skills.sh  (canonical Hermes skill hub)  -> api/search?q=...
  2. GitHub      topic:hermes-agent + best-of-llm-agent repos (no token needed)
  3. Local       installed skills in this Hermes profile (so your own show up)

Output: hermes-tools/_catalog.json  (merged, de-duplicated, classified)

No API token is required or embedded. GitHub unauthenticated rate limit
(~60 req/min) is fine for the few calls we make; if it 429s we degrade
gracefully and keep what we got.
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_catalog.json")
LOCAL_SKILLS = os.path.join(os.path.expanduser("~"),
                            "AppData", "Local", "hermes", "skills")

def http_json(url, timeout=20, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "hermes-tools-aggregator"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.stderr.write(f"Rate limited by {url}; skipping.\n")
            return None
        sys.stderr.write(f"HTTP {e.code} for {url}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"Fetch error {url}: {e}\n")
        return None

def classify(name, desc, source):
    n = (name or "").lower()
    d = (desc or "").lower()
    blob = n + " " + d
    if any(k in blob for k in ("plugin", "addon", "add-on", "extension", "theme")):
        return "Addon"
    if any(k in blob for k in ("tool", "cli", "binary", "app", "client", "wrapper")):
        return "Tool"
    if any(k in blob for k in ("mcp", "server", "integration", "bridge")):
        return "Integration"
    return "Skill"

seen = {}  # dedup key -> record

def add(rec):
    key = (rec.get("source", "") + "/" + rec.get("name", "")).lower()
    if key in seen:
        # merge: keep the higher installs/stars signal
        prev = seen[key]
        prev["installs"] = max(prev.get("installs", 0), rec.get("installs", 0))
        prev["stars"] = max(prev.get("stars", 0), rec.get("stars", 0))
        prev["sources"] = sorted(set(prev.get("sources", []) + rec.get("sources", [])))
        return
    seen[key] = rec

# ---------------------------------------------------------------- skills.sh
SKILLS_QUERIES = ["hermes", "agent", "mcp", "automation", "claude", "llm"]
for q in SKILLS_QUERIES:
    data = http_json("https://skills.sh/api/search?" +
                     urllib.parse.urlencode({"q": q, "searchVersion": "legacy"}))
    if not data:
        continue
    for s in data.get("skills", []):
        name = s.get("name") or s.get("skillId") or ""
        sid = s.get("id") or s.get("installId") or ""
        desc = s.get("description") or ""
        add({
            "name": name,
            "source": "skills.sh/" + (s.get("source") or sid),
            "installSource": "skills-sh/" + sid if sid else "skills-sh/" + name,
            "installs": int(s.get("installs") or 0),
            "stars": 0,
            "type": classify(name, desc, "skills.sh"),
            "description": desc,
            "url": "https://skills.sh/skill/" + sid if sid else "",
            "sources": ["skills.sh"],
        })
    time.sleep(0.2)

# ---------------------------------------------------------------- GitHub
gh_url = ("https://api.github.com/search/repositories?q="
          + urllib.parse.quote("topic:hermes-agent") + "&per_page=40&sort=stars")
gh = http_json(gh_url)
if gh and gh.get("items"):
    for r in gh["items"]:
        name = r["name"]
        desc = r.get("description") or ""
        add({
            "name": name,
            "source": "github/" + r["full_name"],
            "installSource": "",  # installed via gh clone, not hermes skills
            "installs": 0,
            "stars": int(r.get("stargazers_count") or 0),
            "type": classify(name, desc, "github"),
            "description": desc,
            "url": r.get("html_url", ""),
            "sources": ["github"],
        })

# ---------------------------------------------------------------- Local
if os.path.isdir(LOCAL_SKILLS):
    for root, dirs, files in os.walk(LOCAL_SKILLS):
        if "SKILL.md" in files:
            rel = os.path.relpath(root, LOCAL_SKILLS)
            name = os.path.basename(root)
            # read the first line that has a description
            desc = ""
            try:
                with open(os.path.join(root, "SKILL.md"), encoding="utf-8") as f:
                    for line in f:
                        if line.lower().startswith("description:"):
                            desc = line.split(":", 1)[1].strip()
                            break
            except Exception:
                pass
            rec = {
                "name": name,
                "source": "local/" + rel.replace("\\", "/"),
                "installSource": "",
                "installs": 0,
                "stars": 0,
                "type": classify(name, desc, "local"),
                "description": desc,
                "url": "",
                "sources": ["local"],
                "installed": True,
            }
            key = ("local/" + rel.replace("\\", "/") + "/" + name).lower()
            seen[key] = rec  # local always wins (it's yours)

catalog = {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "counts": {},
    "items": sorted(seen.values(), key=lambda r: (-r.get("installs", 0), -r.get("stars", 0), r["name"].lower())),
}
for t in ("Skill", "Tool", "Addon", "Integration"):
    catalog["counts"][t] = sum(1 for r in catalog["items"] if r["type"] == t)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
print(f"Scraped {len(catalog['items'])} items "
      f"(Skill={catalog['counts']['Skill']}, Tool={catalog['counts']['Tool']}, "
      f"Addon={catalog['counts']['Addon']}, Integration={catalog['counts']['Integration']}) -> {OUT}")
