#!/usr/bin/env python3
"""
scrape_nasa.py — Download real NASA space imagery (no API key required) into
assets/space/ for use as the site's pannable background.

Sources: NASA Image and Video Library (images-api.nasa.gov), a public, key-free
endpoint. We search a handful of space queries, dedupe, and grab the largest
available rendition of each, then write a manifest the page reads.

Run:  python scrape_nasa.py
Output: assets/space/*.jpg  +  assets/space/manifest.json
"""
import json, os, sys, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "space")
os.makedirs(OUT, exist_ok=True)

QUERIES = [
    "nebula", "galaxy", "andromeda galaxy", "pillars of creation",
    "hubble deep field", "milky way", "supernova", "earth at night",
    "aurora", "star cluster", "carina nebula", "tarantula nebula",
]
MAX_IMAGES = 10
UA = {"User-Agent": "Mozilla/5.0 (best-of-github background scraper)"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def best_image(links):
    # prefer original > large > small; fall back to any jpg/png
    order = ["~orig", "~large", "~medium", "~small", ""]
    cands = [l["href"] for l in links if l.get("href", "").lower().endswith((".jpg", ".png"))]
    if not cands:
        return None
    for suf in order:
        for c in cands:
            if c.lower().endswith(suf + ".jpg") or c.lower().endswith(suf + ".png"):
                return c
    return cands[0]


def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    seen = set()
    manifest = []
    for q in QUERIES:
        if len(manifest) >= MAX_IMAGES:
            break
        try:
            u = "https://images-api.nasa.gov/search?" + urllib.parse.urlencode(
                {"q": q, "media_type": "image", "year_start": "2010"})
            d = get_json(u)
        except Exception as e:
            print("  query failed:", q, e, file=sys.stderr)
            continue
        items = d.get("collection", {}).get("items", [])
        for it in items:
            if len(manifest) >= MAX_IMAGES:
                break
            data = it.get("data", [{}])[0]
            title = data.get("title", "Untitled")
            img = best_image(it.get("links", []))
            if not img or img in seen:
                continue
            seen.add(img)
            slug = urllib.parse.quote(title[:40].strip().replace(" ", "_"), safe="")
            fname = f"{len(manifest)+1:02d}_{slug}.jpg"
            fpath = os.path.join(OUT, fname)
            try:
                size = download(img, fpath)
                manifest.append({"file": f"assets/space/{fname}", "title": title,
                                 "nasa_url": img, "bytes": size})
                print(f"  + {fname}  ({size//1024} KB)  {title}")
            except Exception as e:
                print("  download failed:", title, e, file=sys.stderr)

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(manifest), "images": manifest}, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(manifest)} NASA images to assets/space/ (manifest.json written).")


if __name__ == "__main__":
    main()
