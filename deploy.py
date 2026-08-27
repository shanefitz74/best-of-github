#!/usr/bin/env python3
"""
deploy.py — one-command weekly publish for the Best of GitHub site.

What it does:
  1. (optional) python fetch.py        # refresh weekly snapshot data
  2. python build.py                   # regenerate index.html + data/*.json
  3. git add the published artifacts    # index.html is gitignored -> force-add
  4. git commit
  5. git push                           # GitHub Pages rebuilds automatically

Usage:
  python deploy.py                 # build + commit + push (assumes data already fetched)
  python deploy.py --fetch         # also run fetch.py first (needs network / optional GITHUB_TOKEN)
  python deploy.py --message "wk35"# custom commit message

The page is a static shell that loads data/week-N.json at runtime, so Pages
serves it with no build step. No secrets are embedded in the page.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, **kw):
    print("›", " ".join(cmd))
    r = subprocess.run(cmd, cwd=HERE, **kw)
    if r.returncode != 0:
        print(f"  ! command failed (exit {r.returncode}):", " ".join(cmd), file=sys.stderr)
        sys.exit(r.returncode)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="run fetch.py first to pull fresh data")
    ap.add_argument("--message", "-m", default=None, help="commit message")
    args = ap.parse_args()

    if args.fetch:
        if os.path.exists(os.path.join(HERE, "fetch.py")):
            run([sys.executable, "fetch.py"])
        else:
            print("! fetch.py not found; skipping fetch step", file=sys.stderr)

    # 1) build the static site
    run([sys.executable, "build.py"])

    # 2) stage the published artifacts (index.html is gitignored -> force-add)
    to_add = ["index.html", "data", "weeks", "assets", "translations.json", "build.py"]
    run(["git", "add", "-f", *to_add])

    # 3) commit (only if there is something to commit)
    out = subprocess.run(["git", "status", "--porcelain"], cwd=HERE,
                          capture_output=True, text=True)
    if not out.stdout.strip():
        print("· no changes to commit — already up to date.")
        return

    msg = args.message or "weekly update"
    run(["git", "commit", "-q", "-m", msg])

    # 4) push (updates GitHub Pages automatically)
    run(["git", "push"])

    print("\n✓ Deployed. GitHub Pages will rebuild in ~1 minute.")
    print("  Live at: https://shanefitz74.github.io/best-of-github/")


if __name__ == "__main__":
    main()
