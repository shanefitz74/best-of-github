#!/usr/bin/env python3
"""
Build index.html from _data.json — CYBERPUNK edition.
All 6 ChatGPT-generated assets used:
  hero.png    -> hero banner behind title
  hero2.png   -> banner divider after stats
  hero3.png   -> banner above repo grid
  divider.png -> thin sci-fi rule (footer / between sub-blocks)
  texture.png -> circuit/neural background tile
  seal.png    -> tech portal emblem (footer)
Live constellation canvas, scroll reveals, cursor-tilt, count-up, language chart.
Single self-contained HTML (images by relative path). No CDN.
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "_data.json"), encoding="utf-8") as f:
    data = json.load(f)

# --- Translation normalization (durable, no API key required) ---------------
# fetch.py may pull repos whose descriptions are non-English (CJK / Korean / ...).
# We apply curated English overrides from translations.json (repo name -> English
# description) so every weekly build stays English without any external API.
# To translate a future-language repo, add its "name": "English description"
# entry to translations.json; the next build rewrites it automatically.
def _has_cjk(s):
    if not s:
        return False
    return any(
        (0x3000 <= ord(c) <= 0x303F) or   # CJK punctuation
        (0x3040 <= ord(c) <= 0x30FF) or   # Hiragana / Katakana
        (0x3400 <= ord(c) <= 0x4DBF) or   # CJK Extension A
        (0x4E00 <= ord(c) <= 0x9FFF) or   # CJK Unified Ideographs
        (0xAC00 <= ord(c) <= 0xD7AF)      # Hangul Syllables
        for c in str(s)
    )

_trans_path = os.path.join(HERE, "translations.json")
_translations = {}
if os.path.exists(_trans_path):
    try:
        with open(_trans_path, encoding="utf-8") as tf:
            _translations = json.load(tf)
    except Exception as e:
        print("Warn: could not load translations.json:", e, file=sys.stderr)

_needs_translation = []
for _sec in ("fresh_this_week", "still_on_fire"):
    for _r in data.get(_sec, []):
        _n = _r.get("name")
        if _n in _translations:
            _r["description"] = _translations[_n]
        elif _has_cjk(_r.get("description", "")):
            _needs_translation.append(_n)

if _needs_translation:
    print("Warn: %d repo(s) still have non-English descriptions "
          "(add to translations.json): %s" % (len(_needs_translation),
          ", ".join(_needs_translation)), file=sys.stderr)
# ---------------------------------------------------------------------------

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Rust": "#dea584", "Go": "#00ADD8", "C": "#555555", "C++": "#f34b7d",
    "C#": "#178600", "Java": "#b07219", "Ruby": "#701516", "PHP": "#4F5D95",
    "Swift": "#F05138", "Kotlin": "#A97BFF", "Dart": "#00B4AB", "HTML": "#e34c26",
    "CSS": "#563d7c", "Shell": "#89e051", "Zig": "#ec915c", "Lua": "#000080",
    "Vue": "#41b883", "Elixir": "#6e4a7e", "Scala": "#c22d40", "OCaml": "#3be133",
    "Jupyter Notebook": "#DA5B0B", "Assembly": "#6E4C13", "Svelte": "#ff3e00",
    "R": "#198CE7", "Perl": "#0298c3", "Haskell": "#5e5086", "Cuda": "#3A4E3A",
}
LANG_COLORS_JS = json.dumps(LANG_COLORS, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Best of GitHub — Weekly Digest</title>
<meta name="description" content="Every week: the GitHub repositories that gained the most stars, ranked by signal and rendered in neon. Fresh this week, still on fire, and the neural map of code." />
<meta property="og:type" content="website" />
<meta property="og:title" content="Best of GitHub — The Week in Code" />
<meta property="og:description" content="The GitHub repositories that gained the most stars this week, ranked by signal and rendered in neon." />
<meta property="og:image" content="assets/og-image.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Best of GitHub — The Week in Code" />
<meta name="twitter:description" content="The GitHub repositories that gained the most stars this week, ranked by signal and rendered in neon." />
<meta name="twitter:image" content="assets/og-image.png" />
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg" />
<style>
  @font-face{
    font-family:"Orbitron";
    src:url("assets/fonts/Orbitron-Variable.ttf") format("truetype");
    font-weight:400 900; font-display:swap; font-style:normal;
  }
  :root{
    --bg:#05070d; --bg2:#080c16; --panel:#0b1120; --panel2:#0e1730;
    --cyan:#46e0ff; --cyan-soft:#3aa9d6; --cyan-deep:#1e6f9e;
    --violet:#a878ff; --ink:#dbe7ff; --ink-dim:#9fb2d6; --ink-faint:#5c7099;
    --line:rgba(70,224,255,.28); --line-soft:rgba(70,224,255,.12);
    --glow:rgba(70,224,255,.55);
    --radius:16px;
    --sans:"Avenir Next","Segoe UI",system-ui,sans-serif;
    --disp:"Eurostile","Bahnschrift","Segoe UI Semibold","Arial Narrow",var(--sans);
    --serif:"Iowan Old Style","Palatino Linotype",Georgia,serif;
    --ease:cubic-bezier(.16,1,.3,1);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; min-height:100vh; color:var(--ink); font-family:var(--sans); line-height:1.6;
    background-color:var(--bg);
    background-image:
      radial-gradient(1100px 700px at 50% -8%, rgba(70,224,255,.10), transparent 60%),
      radial-gradient(900px 600px at 88% 108%, rgba(168,120,255,.07), transparent 60%);
    background-attachment:fixed;
    -webkit-font-smoothing:antialiased; overflow-x:hidden;
  }
  body::before{
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.14;
    background-image:url("assets/texture.png"); background-size:480px 480px; background-repeat:repeat;
  }
  @media (prefers-reduced-motion:no-preference){ body::before{ animation:texDrift 120s linear infinite; }
    @keyframes texDrift{ from{background-position:0 0} to{background-position:480px 480px} } }
  ::selection{background:rgba(70,224,255,.28); color:#eafcff}
  a{color:inherit; text-decoration:none}

  /* ---------- STARFIELD (twinkling, drifting) — sits behind the constellation ---------- */
  #stars{ position:fixed; inset:0; width:100vw; height:100vh; z-index:0; display:block;
    background:transparent; pointer-events:none; }
  /* constellation canvas — must stay fixed/out-of-flow or it pushes content down */
  #sky{ position:fixed; inset:0; width:100vw; height:100vh; z-index:0; display:block;
    background:transparent; pointer-events:none; }
  /* deep-space nebula wash — soft palette clouds so the whole bg reads as space */
  .nebula{ position:fixed; inset:-10%; z-index:0; pointer-events:none; opacity:.5;
    background:
      radial-gradient(40% 50% at 18% 22%, rgba(70,224,255,.16), transparent 70%),
      radial-gradient(45% 55% at 82% 30%, rgba(168,120,255,.15), transparent 70%),
      radial-gradient(55% 60% at 50% 88%, rgba(57,230,168,.08), transparent 72%),
      radial-gradient(35% 40% at 70% 75%, rgba(120,160,255,.10), transparent 70%);
    filter:blur(30px); }
  /* keep paint order: stars (z0) < sky (z0, later in DOM) < vignette (z1) */
  .vignette{ position:fixed; inset:0; z-index:1; pointer-events:none;
    background:radial-gradient(120% 90% at 50% 30%, transparent 55%, rgba(2,4,9,.78) 100%); }
  .progress{ position:fixed; top:0; left:0; height:3px; width:0; z-index:60; pointer-events:none;
    background:linear-gradient(90deg,var(--cyan),var(--violet)); box-shadow:0 0 14px var(--glow); transition:width .12s linear; }


  .frame{ position:relative; z-index:2; max-width:1200px; margin:0 auto; padding:30px 22px 110px; }

  /* ---------- HERO ---------- */
  header.hero{ text-align:center; padding:70px 0 50px; position:relative; }
  .hero-frame{ position:absolute; inset:0; pointer-events:none; z-index:0;
    border:1px solid var(--line); border-radius:24px;
    box-shadow: inset 0 0 0 1px rgba(70,224,255,.08), 0 30px 90px rgba(0,0,0,.6), 0 0 60px rgba(70,224,255,.10);
    -webkit-mask-image: radial-gradient(120% 100% at 50% 30%, #000 62%, transparent 100%);
            mask-image: radial-gradient(120% 100% at 50% 30%, #000 62%, transparent 100%); }
  .hero-frame::before{ content:""; position:absolute; inset:7px; border:1px solid var(--line-soft); border-radius:18px; }

  /* top navigation bar */
  .topnav{ display:flex; align-items:center; justify-content:space-between; gap:16px;
    padding:18px 4px 6px; max-width:1200px; margin:0 auto; }
  .topnav .brand{ font-family:var(--sans); font-weight:800; letter-spacing:.02em; font-size:16px;
    color:#eafcff; text-decoration:none; text-shadow:0 0 18px rgba(70,224,255,.25); }
  .topnav .brand span{ color:var(--cyan); margin:0 2px; }
  .topnav .nav-links{ display:flex; gap:8px; }
  .topnav .nav-link{ font-family:var(--sans); font-size:12.5px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--cyan-soft); text-decoration:none; padding:8px 14px; border-radius:999px;
    border:1px solid var(--line); background:rgba(70,224,255,.05); transition:all .25s var(--ease); }
  .topnav .nav-link:hover{ color:var(--bg); background:var(--cyan); border-color:var(--cyan);
    box-shadow:0 0 18px rgba(70,224,255,.4); }
  .hero-art{ position:absolute; left:50%; top:48%; width:min(960px,94%); height:min(560px,72vw);
    transform:translate(-50%,-50%); border-radius:28px; overflow:hidden;
    background-color:#0a1426;
    /* CSS scene — the always-present, portable fallback when assets/hero.png 404s */
    background-image:
      radial-gradient(120% 120% at 30% 20%, rgba(70,224,255,.22), transparent 55%),
      radial-gradient(120% 120% at 80% 90%, rgba(168,120,255,.20), transparent 55%);
    background-size:cover, cover; background-position:center; background-repeat:no-repeat;
    filter:saturate(1.1) contrast(1.05) brightness(1.02); opacity:.92;
    -webkit-mask-image: radial-gradient(62% 56% at 50% 50%, #000 52%, transparent 100%);
            mask-image: radial-gradient(62% 56% at 50% 50%, #000 52%, transparent 100%);
    animation:heroDrift 26s ease-in-out infinite alternate; }
  /* PNG overlay — if assets/hero.png 404s it removes itself (onerror) and the
     CSS gradient scene above remains. Keeps the page portable with no image. */
  .hero-png{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
    filter:saturate(1.1) contrast(1.05) brightness(1.02);
    -webkit-mask-image: radial-gradient(62% 56% at 50% 50%, #000 52%, transparent 100%);
            mask-image: radial-gradient(62% 56% at 50% 50%, #000 52%, transparent 100%); }
  @keyframes heroDrift{ from{ background-position:48% 45%; transform:translate(-50%,-50%) scale(1.04); }
    to{ background-position:54% 55%; transform:translate(-50%,-50%) scale(1.12); } }
  /* scanning beam sweeping the hero like a sensor */
  .hero-art::after{ content:""; position:absolute; inset:0; border-radius:28px; pointer-events:none;
    background:linear-gradient(180deg, transparent 0%, rgba(70,224,255,.10) 46%, rgba(234,252,255,.22) 50%, rgba(70,224,255,.10) 54%, transparent 100%);
    background-size:100% 220%; mix-blend-mode:screen;
    animation:scan 6.5s linear infinite; }
  @keyframes scan{ from{ background-position:0 -110%; } to{ background-position:0 110%; } }

  /* faint radial plate behind the hero — grounds the title over the cityscape */
  .plate{ position:absolute; left:50%; top:46%; width:min(900px,92vw); height:min(520px,70vw);
    transform:translate(-50%,-50%); border-radius:50%; pointer-events:none;
    background: radial-gradient(closest-side, rgba(70,224,255,.10), rgba(168,120,255,.05) 55%, transparent 75%);
    filter: blur(4px); }

  /* HUD status ticker under the hero */
  .hud{ display:flex; align-items:center; justify-content:center; gap:12px; margin-top:8px;
    font-family:"Orbitron",var(--sans); font-size:11.5px; letter-spacing:.16em; text-transform:uppercase;
    color:var(--cyan-soft); opacity:0; animation:rise .9s var(--ease) .66s forwards; }
  .hud .dot{ width:8px;height:8px;border-radius:50%;background:var(--cyan); box-shadow:0 0 12px var(--cyan);
    animation:hudPulse 1.4s ease-in-out infinite; }
  @keyframes hudPulse{ 0%,100%{opacity:1; transform:scale(1)} 50%{opacity:.3; transform:scale(.7)} }
  .hud .msg{ min-width:280px; text-align:left; color:var(--cyan); text-shadow:0 0 12px rgba(70,224,255,.4); }
  .hud .arrow{ color:var(--violet); }
    transform:translate(-50%,-50%); border-radius:50%;
    background: radial-gradient(closest-side, rgba(70,224,255,.14), rgba(70,224,255,.04) 60%, transparent 78%);
    filter: blur(3px); }
  /* corner HUD brackets */
  .bracket{ position:absolute; width:46px; height:46px; border:2px solid var(--line); opacity:.8; }
  .bk-tl{ top:8px; left:8px; border-right:0; border-bottom:0; border-top-left-radius:14px; }
  .bk-tr{ top:8px; right:8px; border-left:0; border-bottom:0; border-top-right-radius:14px; }
  .bk-bl{ bottom:8px; left:8px; border-right:0; border-top:0; border-bottom-left-radius:14px; }
  .bk-br{ bottom:8px; right:8px; border-left:0; border-top:0; border-bottom-right-radius:14px; }

  .eyebrow{ position:relative; display:inline-block; font-family:var(--sans); letter-spacing:.46em; text-transform:uppercase;
    font-size:11px; margin:0 0 18px; opacity:0; animation:rise .9s var(--ease) .05s forwards;
    /* high-contrast white fill + matching palette-blue outline so it reads off the hero */
    color:#ffffff; -webkit-text-fill-color:#ffffff;
    -webkit-text-stroke:1px rgba(70,224,255,.75); paint-order:stroke fill;
    text-shadow:0 1px 1px rgba(0,0,0,.85), 0 0 10px rgba(70,224,255,.85), 0 0 22px rgba(70,224,255,.45);
    filter:drop-shadow(0 2px 6px rgba(0,0,0,.6)); }
  /* light reflection pass — flipped, faded copy beneath the text */
  .eyebrow::after{ content:attr(data-text); position:absolute; left:0; right:0; top:100%;
    transform:scaleY(-1); transform-origin:top; opacity:.32; pointer-events:none;
    -webkit-text-fill-color:rgba(220,245,255,.9); -webkit-text-stroke:0;
    text-shadow:0 0 8px rgba(70,224,255,.5);
    -webkit-mask-image:linear-gradient(180deg, rgba(0,0,0,.5), transparent 70%);
            mask-image:linear-gradient(180deg, rgba(0,0,0,.5), transparent 70%); }
  h1.title{ position:relative; font-family:"Orbitron", var(--disp); font-size:clamp(46px,9vw,104px); line-height:.92; margin:0; font-weight:800;
    letter-spacing:.02em; color:#eafcff; isolation:isolate;
    transform:perspective(700px) rotateX(14deg);
    text-shadow:
      0 1px 0 #b9e9fb, 0 2px 0 #8fd6f0, 0 3px 0 #5fb9de, 0 4px 0 #3f9ecb,
      0 5px 0 #2b86b4, 0 6px 0 #1f6f9e, 0 7px 0 #175a85, 0 8px 0 #0f476b,
      0 9px 1px rgba(0,0,0,.35), 0 11px 14px rgba(0,0,0,.55),
      0 0 26px rgba(70,224,255,.55), 0 0 54px rgba(70,224,255,.35);
    opacity:0; animation:rise3d 1.1s var(--ease) .12s forwards; }
  h1.title::before{ content:attr(data-text); position:absolute; inset:0; z-index:-1;
    color:transparent; -webkit-text-stroke:1.5px rgba(70,224,255,.6);
    text-shadow:0 0 30px rgba(70,224,255,.5); }
  @keyframes rise3d{ from{opacity:0} to{opacity:1} }
  h1.title .of{ display:block; font-family:"Orbitron", var(--sans); font-size:.26em; letter-spacing:.34em;
    color:#ffffff; -webkit-text-fill-color:#ffffff; -webkit-text-stroke:1.4px var(--cyan);
    paint-order:stroke fill; text-shadow:0 0 16px rgba(70,224,255,.55);
    font-weight:700; margin-top:18px; text-transform:uppercase;
    opacity:0; animation:rise .9s var(--ease) .32s forwards; }
  .subtitle{ font-style:italic; color:#ffffff; -webkit-text-fill-color:#ffffff; -webkit-text-stroke:.7px rgba(70,224,255,.55);
    paint-order:stroke fill; margin:22px auto 0; max-width:580px; font-size:18px;
    text-shadow:0 0 18px rgba(70,224,255,.35);
    opacity:0; animation:rise .9s var(--ease) .42s forwards; }
  @keyframes rise{ from{opacity:0; transform:translateY(26px)} to{opacity:1; transform:none} }

  /* neural-core glyph above title */
  .glyph{ position:relative; width:96px; height:96px; margin:0 auto 18px;
    opacity:0; animation:rise .9s var(--ease) .08s forwards, glyphPulse 3.2s ease-in-out 1s infinite; }
  .glyph svg{ width:100%; height:100%; filter:drop-shadow(0 0 14px rgba(70,224,255,.5)); }
  .glyph-node circle{ transform-origin:60px 60px; }
  @media (prefers-reduced-motion:no-preference){
    .glyph-link path{ stroke-dasharray:240; stroke-dashoffset:240; animation:trace 2.4s var(--ease) .3s forwards; }
    .glyph-node circle{ animation:nodepulse 2.6s ease-in-out infinite; }
    .glyph-node circle:nth-child(2){ animation-delay:.2s } .glyph-node circle:nth-child(3){ animation-delay:.4s }
    .glyph-node circle:nth-child(4){ animation-delay:.6s } .glyph-node circle:nth-child(5){ animation-delay:.8s }
    .glyph-node circle:nth-child(6){ animation-delay:1s } .glyph-node circle:nth-child(7){ animation-delay:1.2s }
    .glyph-node circle:nth-child(8){ animation-delay:1.4s } .glyph-node circle:nth-child(9){ animation-delay:1.6s }
  }
  @keyframes trace{ to{ stroke-dashoffset:0 } }
  @keyframes nodepulse{ 0%,100%{ opacity:.55; r:3 } 50%{ opacity:1; r:4.6 } }
  @keyframes glyphPulse{ 0%,100%{ transform:translateY(0) scale(1) } 50%{ transform:translateY(-4px) scale(1.04) } }

  /* neon scan sweep across the title */
  h1.title{ overflow:hidden; }
  h1.title::after{ content:""; position:absolute; top:0; left:-60%; width:55%; height:100%; z-index:-1;
    background:linear-gradient(105deg, transparent, rgba(234,252,255,.32), transparent);
    transform:skewX(-18deg); animation:sweep 5.5s ease-in-out 1.4s infinite; pointer-events:none; }
  @keyframes sweep{ 0%{ left:-60% } 55%{ left:130% } 100%{ left:130% } }

  .rule{ display:flex; align-items:center; justify-content:center; gap:16px; margin:30px 0 10px; color:var(--cyan-soft);
    opacity:0; animation:rise .9s var(--ease) .5s forwards; }
  .rule::before,.rule::after{ content:""; height:1px; width:min(34vw,360px);
    background:linear-gradient(90deg,transparent,var(--line),transparent); }
  .fleuron{ font-size:20px; color:var(--cyan); text-shadow:0 0 14px var(--glow); }

  .week-badge{ display:inline-flex; align-items:center; gap:11px; margin-top:8px;
    font-family:var(--sans); font-size:12.5px; letter-spacing:.18em; text-transform:uppercase;
    color:var(--cyan); border:1px solid var(--line); padding:9px 18px; border-radius:999px;
    background:rgba(70,224,255,.05); backdrop-filter:blur(4px);
    box-shadow:0 0 22px rgba(70,224,255,.12) inset, 0 0 18px rgba(70,224,255,.10);
    opacity:0; animation:rise .9s var(--ease) .58s forwards; }
  .week-badge .dot{ width:8px;height:8px;border-radius:50%;background:var(--cyan);
    box-shadow:0 0 14px var(--cyan); animation:pulse 2.4s ease-in-out infinite; }
  @keyframes pulse{ 0%,100%{opacity:1} 50%{opacity:.35} }

  /* ---------- AI BRIEFING ---------- */
  .briefing{ max-width:900px; margin:6px auto 0; padding:18px 22px; position:relative;
    border:1px solid var(--line); border-radius:var(--radius); backdrop-filter:blur(6px);
    background:linear-gradient(180deg,rgba(11,17,32,.78),rgba(8,12,22,.82));
    box-shadow:0 0 40px rgba(70,224,255,.08), inset 0 0 60px rgba(70,224,255,.04);
    display:flex; align-items:center; gap:16px; opacity:0; transform:translateY(18px); }
  .briefing.in{ animation:rise .9s var(--ease) .5s forwards; }
  .briefing .bdot{ flex:0 0 auto; width:9px;height:9px;border-radius:50%; background:var(--violet);
    box-shadow:0 0 14px var(--violet); animation:pulse 1.6s ease-in-out infinite; }
  .briefing .btxt{ font-family:var(--sans); font-size:13.5px; line-height:1.55; color:var(--ink); }
  .briefing .btxt b{ color:var(--cyan); font-weight:700; }
  .briefing .btxt .tag{ display:inline-block; font-family:var(--disp); font-size:10.5px; letter-spacing:.12em;
    text-transform:uppercase; color:var(--violet); border:1px solid rgba(168,120,255,.4); padding:2px 8px; border-radius:999px; margin-right:8px; }

  /* scroll reveal targets */
  #stats, .langchart, .banner.b2, .banner.b3, .divider-img, .controls{ opacity:0; transform:translateY(22px); }
  #stats.in, .langchart.in, .banner.in, .divider-img.in, .controls.in{ opacity:1; transform:none;
    transition:opacity .8s var(--ease), transform .8s var(--ease); }

  /* ---------- STATS ---------- */
  .stats{ display:flex; flex-wrap:wrap; justify-content:center; gap:0; margin:36px auto 8px;
    border:1px solid var(--line); border-radius:var(--radius); overflow:hidden; max-width:820px;
    background:linear-gradient(180deg,rgba(11,17,32,.85),rgba(8,12,22,.85)); backdrop-filter:blur(6px);
    box-shadow:0 0 40px rgba(70,224,255,.08); }
  .stat{ flex:1 1 0; min-width:128px; padding:20px 14px; text-align:center; position:relative; }
  .stat + .stat::before{ content:""; position:absolute; left:0; top:18%; height:64%; width:1px; background:var(--line-soft); }
  .stat .num{ font-family:var(--disp); font-size:32px; color:#eafcff; font-weight:700; line-height:1;
    font-variant-numeric:tabular-nums; text-shadow:0 0 18px var(--glow); }
  .stat .lbl{ font-family:var(--sans); font-size:10.5px; letter-spacing:.2em; text-transform:uppercase;
    color:var(--ink-faint); margin-top:9px; }

  /* ---------- BANNER IMAGES ---------- */
  .banner{ position:relative; width:100%; height:230px; margin:30px 0; border-radius:18px; overflow:hidden;
    border:1px solid var(--line); background-size:cover; background-position:center;
    box-shadow:0 0 50px rgba(70,224,255,.10), inset 0 0 90px rgba(2,4,9,.55);
    -webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);
            mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent); }
  .banner::after{ content:""; position:absolute; inset:0;
    background:linear-gradient(180deg,transparent,rgba(5,7,13,.25)); }
  .banner.b2{ background-color:#0a1426;
    background-image:
      linear-gradient(120deg, rgba(70,224,255,.18), rgba(168,120,255,.16)),
      url("assets/hero2.png");
    background-size:cover, cover; background-position:center; }
  .banner.b3{ background-color:#0a1426;
    background-image:
      linear-gradient(120deg, rgba(168,120,255,.16), rgba(70,224,255,.18)),
      url("assets/hero3.png");
    background-size:cover, cover; background-position:center; }

  /* thin divider */
  .divider-img{ display:block; width:min(680px,92%); height:60px; margin:34px auto;
    background-image:
      linear-gradient(90deg, transparent, rgba(70,224,255,.5) 20%, rgba(168,120,255,.5) 80%, transparent),
      url("assets/divider.png");
    background-size:100% 2px, 100% 60px; background-position:center, center; background-repeat:no-repeat, no-repeat;
    background-color:#05070d; opacity:.9; pointer-events:none;
    filter:drop-shadow(0 0 12px rgba(70,224,255,.2)); }

  /* ---------- CONTROLS ---------- */
  .controls{ display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin:30px 0 8px; }
  .skip-link{ position:absolute; left:-9999px; top:0; z-index:200; background:var(--cyan); color:#04121b;
    padding:10px 16px; border-radius:0 0 12px 0; font-family:var(--sans); font-weight:700; font-size:13px; }
  .skip-link:focus{ left:0; outline:2px solid #04121b; }
  .filter-toggle{ display:none; }
  .tabs{ display:flex; gap:0; border:1px solid var(--line); border-radius:999px; overflow:hidden; backdrop-filter:blur(6px); }
  .tab{ font-family:var(--sans); font-size:12.5px; letter-spacing:.1em; text-transform:uppercase;
    padding:11px 22px; cursor:pointer; color:var(--ink-dim); background:transparent; border:0;
    transition:color .3s var(--ease), background .3s var(--ease), box-shadow .3s; }
  .tab.active{ color:var(--bg); background:linear-gradient(180deg,#eafcff,var(--cyan)); font-weight:700;
    box-shadow:0 0 22px rgba(70,224,255,.45); }
  .tab:not(.active):hover{ color:#eafcff; }
  .search{ flex:1 1 220px; position:relative; min-width:200px; }
  .search input{ width:100%; padding:12px 14px 12px 40px; border-radius:999px;
    border:1px solid var(--line); background:rgba(11,17,32,.8); color:var(--ink); font-family:var(--sans);
    font-size:15px; outline:none; transition:border-color .3s, box-shadow .3s; backdrop-filter:blur(6px); }
  .search input:focus{ border-color:var(--cyan-soft); box-shadow:0 0 0 3px rgba(70,224,255,.14); }
  .search svg{ position:absolute; left:14px; top:50%; transform:translateY(-50%); width:16px; height:16px;
    stroke:var(--cyan-soft); fill:none; }
  select.sel{ appearance:none; padding:12px 34px 12px 15px; border-radius:999px;
    border:1px solid var(--line); background:rgba(11,17,32,.8); color:var(--ink); font-family:var(--sans);
    font-size:12.5px; cursor:pointer; outline:none; backdrop-filter:blur(6px);
    background-image:linear-gradient(45deg,transparent 50%,var(--cyan-soft) 50%),linear-gradient(135deg,var(--cyan-soft) 50%,transparent 50%);
    background-position:calc(100% - 16px) 50%, calc(100% - 11px) 50%; background-size:5px 5px,5px 5px; background-repeat:no-repeat; }
  select.sel:focus{ border-color:var(--cyan-soft); }
  .rand-btn{ font-family:var(--sans); font-size:12.5px; letter-spacing:.1em; text-transform:uppercase;
    padding:12px 20px; border-radius:999px; border:1px solid var(--line); background:transparent;
    color:var(--cyan-soft); cursor:pointer; transition:all .3s var(--ease); }
  .rand-btn:hover{ color:var(--bg); background:var(--cyan); border-color:var(--cyan); box-shadow:0 0 22px rgba(70,224,255,.4); }

  /* ---------- LANGUAGE CHART ---------- */
  .langchart{ margin:30px 0 6px; border:1px solid var(--line); border-radius:var(--radius);
    background:
      radial-gradient(120% 120% at 80% -10%, rgba(168,120,255,.10), transparent 60%),
      linear-gradient(180deg,rgba(11,17,32,.85),rgba(8,12,22,.85)); padding:24px 28px 26px; position:relative; backdrop-filter:blur(6px);
    box-shadow:0 0 40px rgba(70,224,255,.06); overflow:hidden; }
  .langchart::before{ content:""; position:absolute; inset:7px; border:1px solid var(--line-soft); border-radius:9px; pointer-events:none; }
  .langchart::after{ content:""; position:absolute; inset:0; pointer-events:none; opacity:.5;
    background-image:linear-gradient(rgba(70,224,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(70,224,255,.05) 1px,transparent 1px);
    background-size:26px 26px; -webkit-mask-image:radial-gradient(70% 70% at 30% 50%, #000, transparent 80%); mask-image:radial-gradient(70% 70% at 30% 50%, #000, transparent 80%); }
  .langchart h2{ margin:0 0 4px; font-family:var(--disp); font-size:clamp(22px,3vw,32px); color:#eafcff; font-weight:700; letter-spacing:.02em; position:relative; }
  .langchart .sub{ font-family:var(--sans); font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--ink-faint); margin:0 0 18px; position:relative; }
  .neural-wrap{ display:grid; grid-template-columns:minmax(280px,1fr) minmax(260px,360px); gap:22px; align-items:center; position:relative; }
  .neural-canvas-wrap{ position:relative; aspect-ratio:1/1; width:100%; max-width:460px; margin:0 auto; }
  #langCanvas{ width:100%; height:100%; display:block; }
  .neural-legend{ display:flex; flex-direction:column; gap:9px; }
  .neural-row{ display:grid; grid-template-columns:14px 1fr auto; align-items:center; gap:11px; padding:7px 10px; border-radius:9px;
    background:rgba(255,255,255,.02); border:1px solid var(--line-soft); }
  .neural-row .dot{ width:11px; height:11px; border-radius:50%; box-shadow:0 0 10px currentColor; }
  .neural-row .nm{ font-size:13.5px; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .neural-row .vl{ font-family:var(--sans); font-size:12.5px; color:var(--cyan-soft); text-align:right; white-space:nowrap; }
  .neural-row .vl b{ color:#eafcff; font-weight:700; }
  .neural-row .vl .pc{ color:var(--ink-faint); font-size:10px; letter-spacing:.08em; }
  @media (max-width:760px){ .neural-wrap{ grid-template-columns:1fr; } .neural-canvas-wrap{ max-width:360px; } }

  /* ---------- GRID ---------- */
  .grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:20px; margin-top:26px; }
  .card{ position:relative; border:1px solid var(--line); border-radius:var(--radius);
    background:linear-gradient(180deg,rgba(11,17,32,.88),rgba(8,12,22,.92)); padding:22px 24px 20px;
    backdrop-filter:blur(7px); transition:transform .5s var(--ease), box-shadow .5s var(--ease), border-color .5s var(--ease);
    overflow:hidden; transform-style:preserve-3d; will-change:transform;
    opacity:0; transform:translateY(34px); }
  .card.in{ opacity:1; transform:translateY(0) rotateX(0) rotateY(0); }
  .card::before{ content:""; position:absolute; inset:7px; border:1px solid var(--line-soft); border-radius:9px; pointer-events:none; }
  .card::after{ content:""; position:absolute; inset:0; border-radius:var(--radius);
    background:radial-gradient(360px 200px at var(--mx,50%) var(--my,0%), rgba(70,224,255,.12), transparent 70%);
    opacity:0; transition:opacity .5s var(--ease); pointer-events:none; }
  .card:hover{ transform:translateY(-6px); border-color:var(--cyan-soft);
    box-shadow:0 22px 60px rgba(0,0,0,.6), 0 0 0 1px rgba(70,224,255,.3), 0 0 40px rgba(70,224,255,.18); }
  .card:hover::after{ opacity:1; }
  .card.flash{ animation:flash 1.4s ease; }
  @keyframes flash{ 0%{box-shadow:0 0 0 3px var(--cyan),0 0 50px rgba(70,224,255,.5)} 100%{box-shadow:none} }
  .card-top{ display:flex; align-items:flex-start; gap:14px; position:relative; }
  .rank{ flex:0 0 auto; width:40px; height:40px; border-radius:50%; display:grid; place-items:center;
    font-family:var(--disp); font-weight:700; font-size:15px; color:var(--bg);
    background:linear-gradient(180deg,#eafcff,var(--cyan)); box-shadow:0 2px 10px rgba(0,0,0,.5),0 0 18px rgba(70,224,255,.4);
    transition:transform .5s var(--ease); }
  .card:hover .rank{ transform:scale(1.12) rotate(-6deg); }
  .avatar{ width:42px; height:42px; border-radius:10px; object-fit:cover; flex:0 0 auto;
    border:1px solid var(--line); background:var(--panel2); }
  .meta{ min-width:0; flex:1 1 auto; }
  .repo-name{ font-size:20px; font-weight:700; color:#eafcff; line-height:1.2; font-family:var(--disp);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-shadow:0 0 14px rgba(70,224,255,.2);
    transition:color .3s; }
  .card:hover .repo-name{ color:#fff; }
  .repo-owner{ font-family:var(--sans); font-size:11.5px; letter-spacing:.06em; color:var(--ink-faint); text-transform:uppercase; }
  .stars-row{ display:flex; align-items:center; gap:16px; margin:16px 0 12px; flex-wrap:wrap; }
  .star-big{ font-size:24px; color:var(--cyan); font-weight:700; display:flex; align-items:baseline; gap:6px; font-family:var(--disp);
    text-shadow:0 0 16px var(--glow); }
  .star-big .unit{ font-family:var(--sans); font-size:11px; letter-spacing:.14em; color:var(--ink-faint); text-transform:uppercase; }
  .metric{ font-family:var(--sans); font-size:12px; color:var(--ink-dim); display:flex; gap:5px; align-items:center; }
  .metric svg{ width:13px;height:13px; stroke:var(--cyan-soft); fill:none; }
  .bar{ height:6px; border-radius:3px; background:var(--line-soft); overflow:hidden; margin:4px 0 14px; }
  .bar > span{ display:block; height:100%; background:linear-gradient(90deg,var(--cyan-deep),var(--cyan));
    border-radius:3px; transform-origin:left; animation:grow 1s var(--ease) both; }
  .desc{ font-size:14.5px; color:var(--ink-dim); margin:2px 0 14px; min-height:42px; }
  .desc.empty{ font-style:italic; color:var(--ink-faint); }
  .tags{ display:flex; flex-wrap:wrap; gap:7px; margin-bottom:14px; }
  .chip{ font-family:var(--sans); font-size:10.5px; letter-spacing:.05em; padding:4px 10px; border-radius:999px;
    border:1px solid var(--line-soft); color:var(--ink-dim); background:rgba(70,224,255,.05); }
  .lang{ display:flex; align-items:center; gap:7px; font-family:var(--sans); font-size:11.5px; color:var(--ink-dim); }
  .lang .dot{ width:10px;height:10px;border-radius:50%; box-shadow:0 0 0 2px rgba(0,0,0,.3) inset; }
  .card-foot{ display:flex; align-items:center; justify-content:space-between; margin-top:14px;
    padding-top:14px; border-top:1px solid var(--line-soft); }
  .view-link{ font-family:var(--sans); font-size:11.5px; letter-spacing:.12em; text-transform:uppercase;
    color:var(--cyan); display:inline-flex; align-items:center; gap:7px; transition:gap .3s var(--ease),color .3s,text-shadow .3s; }
  .view-link:hover{ color:#eafcff; gap:11px; text-shadow:0 0 14px var(--glow); }
  .view-link svg{ width:14px;height:14px; stroke:currentColor; fill:none; }

  /* sparkline + trend badge */
  .trend-row{ display:flex; align-items:center; gap:12px; margin:2px 0 6px; }
  .spark{ flex:1 1 auto; height:30px; width:100%; min-width:0; overflow:visible; }
  .spark path.spark-line{ fill:none; stroke:var(--cyan); stroke-width:1.6; stroke-linejoin:round; stroke-linecap:round;
    filter:drop-shadow(0 0 4px rgba(70,224,255,.5)); }
  .spark path.spark-area{ fill:url(#sparkGrad); opacity:.5; }
  .trend{ display:inline-flex; align-items:center; gap:5px; flex:0 0 auto;
    font-family:var(--disp); font-size:12.5px; font-weight:700; padding:4px 9px; border-radius:999px;
    border:1px solid var(--line-soft); background:rgba(70,224,255,.06); }
  .trend.up{ color:#5cf2a8; border-color:rgba(92,242,168,.4); background:rgba(92,242,168,.1); }
  .trend.down{ color:#ff7a8a; border-color:rgba(255,122,138,.4); background:rgba(255,122,138,.1); }
  .trend.flat{ color:var(--ink-dim); }
  .trend.new{ color:var(--violet); border-color:rgba(168,120,255,.45); background:rgba(168,120,255,.12); }
  .trend .arw{ font-size:13px; line-height:1; }
  .trend .mag{ font-family:var(--sans); font-weight:600; font-size:11px; opacity:.85; }
  .rank-delta{ margin-left:7px; font-family:var(--sans); font-size:10.5px; font-weight:700; letter-spacing:.02em;
    padding:1px 7px; border-radius:999px; border:1px solid var(--line-soft); }
  .rank-delta.up{ color:#5cf2a8; border-color:rgba(92,242,168,.4); background:rgba(92,242,168,.1); }
  .rank-delta.down{ color:#ff7a8a; border-color:rgba(255,122,138,.4); background:rgba(255,122,138,.1); }
  .rank-delta.flat{ color:var(--ink-dim); }
  .created{ font-family:var(--sans); font-size:10.5px; color:var(--ink-faint); letter-spacing:.04em; }
  .empty-state{ text-align:center; color:var(--ink-faint); padding:60px 0; font-style:italic; }

  footer{ margin-top:60px; border-top:1px solid var(--line); padding-top:28px;
    font-family:var(--sans); font-size:12.5px; color:var(--ink-faint); line-height:1.7; position:relative; z-index:2; text-align:center; }
  footer h3{ font-family:var(--disp); color:var(--cyan-soft); font-size:16px; margin:0 0 8px; letter-spacing:.04em; }
  footer code{ color:var(--cyan-soft); background:rgba(70,224,255,.07); padding:1px 6px; border-radius:5px; }
  .seal{ display:block; width:96px; height:96px; margin:0 auto 12px; border-radius:50%;
    background:url("assets/seal.png") center/cover no-repeat;
    background-color:radial-gradient(circle at 50% 50%, rgba(70,224,255,.10), transparent 70%);
    box-shadow:0 0 0 1px var(--line), 0 0 26px rgba(70,224,255,.18) inset, 0 0 22px rgba(70,224,255,.25);
    filter:drop-shadow(0 0 18px rgba(70,224,255,.3)); }
  .err{ display:none; position:fixed; inset:auto 16px 16px auto; background:#2a1414; color:#ffb4a0;
    border:1px solid #6b2b2b; padding:10px 14px; border-radius:10px; font-family:var(--sans); font-size:12px; z-index:50; }

  @media (max-width:560px){
    .grid{grid-template-columns:1fr} .controls{gap:10px}
    .lang-row{ grid-template-columns:84px 1fr 64px; gap:9px } .banner{height:170px}
    /* collapse controls into a filter drawer */
    .filter-toggle{ display:inline-flex; align-items:center; gap:8px; font-family:var(--sans); font-size:12.5px;
      letter-spacing:.1em; text-transform:uppercase; padding:11px 18px; border-radius:999px; cursor:pointer;
      color:var(--bg); background:linear-gradient(180deg,#eafcff,var(--cyan)); border:0; font-weight:700;
      box-shadow:0 0 18px rgba(70,224,255,.4); }
    .controls{ position:fixed; left:0; right:0; bottom:0; z-index:120; margin:0; padding:16px 16px calc(16px + env(safe-area-inset-bottom));
      flex-direction:column; align-items:stretch; gap:10px; background:rgba(7,10,18,.96); backdrop-filter:blur(14px);
      border-top:1px solid var(--line); transform:translateY(110%); transition:transform .35s var(--ease); max-height:80vh; overflow:auto; }
    .controls.open{ transform:translateY(0); }
    .tabs{ width:100%; } .tab{ flex:1; padding:11px 10px; } .search{ min-width:0; } .sel{ width:100%; }
    .filter-toggle .count{ background:rgba(4,18,27,.25); border-radius:999px; padding:1px 8px; font-size:11px; }
  }
  @media (prefers-reduced-motion:reduce){
    *{animation-duration:.001ms!important; animation-iteration-count:1!important; transition:none!important}
    .card{opacity:1; transform:none}
  }

  /* ---------- DRAWER (repo detail) ---------- */
  .drawer-back{ position:fixed; inset:0; z-index:40; background:rgba(2,4,9,.72); backdrop-filter:blur(4px);
    opacity:0; pointer-events:none; transition:opacity .35s var(--ease); }
  .drawer-back.open{ opacity:1; pointer-events:auto; }
  .drawer{ position:fixed; top:0; right:0; height:100vh; width:min(430px,92vw); z-index:41;
    background:linear-gradient(180deg,#0b1120,#070b14); border-left:1px solid var(--line);
    box-shadow:-30px 0 80px rgba(0,0,0,.6), 0 0 60px rgba(70,224,255,.12);
    transform:translateX(102%); transition:transform .42s var(--ease); overflow-y:auto; padding:26px 28px 40px;
    -webkit-overflow-scrolling:touch; }
  .drawer.open{ transform:translateX(0); }
  .drawer .close{ position:absolute; top:16px; right:18px; width:34px;height:34px; border-radius:50%;
    border:1px solid var(--line); background:rgba(70,224,255,.06); color:var(--cyan); cursor:pointer; font-size:18px;
    display:grid; place-items:center; transition:all .3s var(--ease); }
  .drawer .close:hover{ background:var(--cyan); color:var(--bg); box-shadow:0 0 18px rgba(70,224,255,.5); }
  .drawer .d-avatar{ width:56px;height:56px;border-radius:12px;border:1px solid var(--line); background:var(--panel2); }
  .drawer .d-owner{ font-family:var(--sans); font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink-faint); }
  .drawer .d-name{ font-family:var(--disp); font-size:26px; color:#eafcff; margin:4px 0 2px; line-height:1.1;
    text-shadow:0 0 18px rgba(70,224,255,.3); }
  .drawer .d-lang{ display:inline-flex; align-items:center; gap:7px; font-family:var(--sans); font-size:12px; color:var(--ink-dim); margin:8px 0 16px; }
  .drawer .d-lang .dot{ width:11px;height:11px;border-radius:50%; }
  .drawer .d-stats{ display:flex; gap:10px; margin:0 0 18px; }
  .drawer .d-stat{ flex:1; border:1px solid var(--line-soft); border-radius:10px; padding:12px; text-align:center; background:rgba(70,224,255,.04); }
  .drawer .d-stat b{ display:block; font-family:var(--disp); font-size:22px; color:#eafcff; text-shadow:0 0 14px rgba(70,224,255,.35); }
  .drawer .d-stat span{ font-family:var(--sans); font-size:9.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-faint); }
  .drawer .d-desc{ font-family:var(--sans); font-size:15px; color:var(--ink-dim); line-height:1.6; margin:6px 0 18px; }
  .drawer .d-meta{ font-family:var(--sans); font-size:12px; color:var(--ink-faint); margin-bottom:16px; }
  .drawer .d-meta a{ color:var(--cyan-soft); }
  .drawer .d-topics{ display:flex; flex-wrap:wrap; gap:7px; margin-bottom:22px; }
  .drawer .d-topics .chip{ cursor:pointer; }
  .drawer .d-actions{ display:flex; gap:10px; }
  .drawer .btn{ flex:1; text-align:center; font-family:var(--sans); font-size:12px; letter-spacing:.08em; text-transform:uppercase;
    padding:12px; border-radius:999px; border:1px solid var(--line); cursor:pointer; transition:all .3s var(--ease); }
  .drawer .btn.primary{ background:linear-gradient(180deg,#eafcff,var(--cyan)); color:var(--bg); font-weight:700; border-color:var(--cyan); }
  .drawer .btn.primary:hover{ box-shadow:0 0 22px rgba(70,224,255,.5); }
  .drawer .btn.ghost{ background:transparent; color:var(--cyan-soft); }
  .drawer .btn.ghost:hover{ color:var(--bg); background:var(--cyan); border-color:var(--cyan); }

  /* topic chips as filter buttons */
  .chip[data-topic]{ cursor:pointer; transition:all .25s var(--ease); }
  .chip[data-topic]:hover{ color:var(--bg); background:var(--cyan); border-color:var(--cyan); box-shadow:0 0 14px rgba(70,224,255,.4); }
  .active-topic{ display:none; align-items:center; gap:8px; margin:0 0 0 4px; font-family:var(--sans); font-size:12px;
    color:var(--cyan); border:1px solid var(--line); padding:10px 14px; border-radius:999px; background:rgba(70,224,255,.07); }
  .active-topic.show{ display:inline-flex; }
  .active-topic b{ color:#eafcff; }
  .active-topic .x{ cursor:pointer; color:var(--cyan-soft); font-size:14px; }

  /* copy week-summary button */
  .sum-btn{ font-family:var(--sans); font-size:12.5px; letter-spacing:.1em; text-transform:uppercase;
    padding:12px 18px; border-radius:999px; border:1px solid var(--line); background:transparent; color:var(--cyan-soft);
    cursor:pointer; transition:all .3s var(--ease); }
  .sum-btn:hover{ color:var(--bg); background:var(--cyan); border-color:var(--cyan); box-shadow:0 0 22px rgba(70,224,255,.4); }

  /* toast */
  .toast{ position:fixed; left:50%; bottom:28px; transform:translateX(-50%) translateY(20px); z-index:60;
    background:#0e1730; border:1px solid var(--line); color:#eafcff; font-family:var(--sans); font-size:13px;
    padding:11px 18px; border-radius:999px; box-shadow:0 0 30px rgba(70,224,255,.2); opacity:0; pointer-events:none;
    transition:opacity .3s var(--ease), transform .3s var(--ease); }
  .toast.show{ opacity:1; transform:translateX(-50%) translateY(0); }

  /* focus ring + a11y */
  .card:focus-visible{ outline:2px solid var(--cyan); outline-offset:3px; box-shadow:0 0 0 4px rgba(70,224,255,.2),0 0 40px rgba(70,224,255,.3); }
  .tab:focus-visible,.btn:focus-visible,.sum-btn:focus-visible,.rand-btn:focus-visible,.chip:focus-visible,.close:focus-visible{ outline:2px solid var(--cyan); outline-offset:2px; }
</style>
</head>
<body>
<a class="skip-link" href="#grid">Skip to repositories</a>
<canvas id="stars" aria-hidden="true"></canvas>
<canvas id="sky" aria-hidden="true"></canvas>
<div class="nebula" aria-hidden="true"></div>
<div class="vignette"></div>
<div class="progress" id="progress"></div>

<div class="frame" id="frame">
  <nav class="topnav" aria-label="Primary">
    <a class="brand" href="./">Best<span>of</span>GitHub</a>
    <div class="nav-links">
      <a class="nav-link" href="./">Weekly</a>
      <a class="nav-link" href="hermes-tools.html">Hermes Tools</a>
    </div>
  </nav>
  <header class="hero">
    <div class="hero-frame" aria-hidden="true">
      <div class="hero-art">
        <img class="hero-png" src="assets/hero.png" alt="" onerror="this.remove()">
      </div>
      <div class="plate"></div>
      <div class="bracket bk-tl"></div><div class="bracket bk-tr"></div>
      <div class="bracket bk-bl"></div><div class="bracket bk-br"></div>
    </div>
    <div class="glyph" aria-hidden="true">
      <svg viewBox="0 0 120 120">
        <defs><radialGradient id="cg" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#eafcff"/><stop offset="55%" stop-color="#46e0ff"/><stop offset="100%" stop-color="#a878ff"/>
        </radialGradient></defs>
        <g class="glyph-node" fill="url(#cg)">
          <circle cx="60" cy="60" r="7"/><circle cx="60" cy="20" r="3.5"/><circle cx="60" cy="100" r="3.5"/>
          <circle cx="20" cy="60" r="3.5"/><circle cx="100" cy="60" r="3.5"/>
          <circle cx="30" cy="30" r="3"/><circle cx="90" cy="30" r="3"/><circle cx="30" cy="90" r="3"/><circle cx="90" cy="90" r="3"/>
        </g>
        <g class="glyph-link" stroke="url(#cg)" stroke-width="1.1" opacity=".55" fill="none">
          <path d="M60 60 L60 20 M60 60 L60 100 M60 60 L20 60 M60 60 L100 60 M60 60 L30 30 M60 60 L90 30 M60 60 L30 90 M60 60 L90 90
                   M30 30 L90 30 M30 30 L30 90 M90 30 L90 90 M30 90 L90 90 M20 60 L100 60"/>
        </g>
      </svg>
    </div>
    <p class="eyebrow" data-text="Repository Intelligence · Weekly Synthesis">Repository Intelligence · Weekly Synthesis</p>
    <h1 class="title" data-text="Best of GitHub">Best of GitHub<span class="of">The Week in Code</span></h1>
    <p class="subtitle">Every week we pull the repositories that gained the most stars on GitHub, ranked by how many they picked up in the last seven days.</p>
    <div class="rule"><span class="fleuron">&#9670;</span></div>
    <div class="week-badge"><span class="dot"></span><span id="weekLabel">—</span></div>
    <div class="hud" aria-live="polite"><span class="dot"></span><span class="msg" id="hudMsg">INITIALIZING</span><span class="arrow">▸</span></div>
  </header>


  <section class="briefing" id="briefing" aria-label="AI briefing"></section>

  <section class="stats" id="stats"></section>

  <div class="banner b2" aria-hidden="true"></div>

  <section class="langchart ai-neural">
    <h2>Neural Map of Code</h2>
    <p class="sub" id="langSub">Primary-language neurons, weighted by share of stars — currently showing Fresh This Week</p>
    <div class="neural-wrap">
      <div class="neural-canvas-wrap">
        <canvas id="langCanvas" aria-label="Neural map of programming languages by share of stars"></canvas>
      </div>
      <div class="neural-legend" id="langLegend"></div>
    </div>
  </section>

  <div class="divider-img" aria-hidden="true"></div>

  <div class="banner b3" aria-hidden="true"></div>

  <div class="controls">
    <button class="filter-toggle" id="filterToggle" aria-expanded="false" aria-controls="controls">&#9881; Filters <span class="count" id="filterCount"></span></button>
    <div class="tabs">
      <button class="tab active" data-tab="fresh">Fresh This Week</button>
      <button class="tab" data-tab="fire">Still On Fire</button>
      <button class="tab" data-tab="velocity">Velocity</button>
    </div>
    <div class="search">
      <svg viewBox="0 0 24 24" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
      <input id="search" type="text" placeholder="Search name, owner, topic…" />
    </div>
    <select class="sel" id="weekPick" title="Select a captured week"></select>
    <select class="sel" id="langFilter"><option value="">All languages</option></select>
    <select class="sel" id="sortBy">
      <option value="stars">Sort: Stars</option>
      <option value="delta">Sort: Star gain (Δ this week)</option>
      <option value="velocity">Sort: Velocity (Δ ÷ last-week stars)</option>
      <option value="forks">Sort: Forks</option>
      <option value="created">Sort: Newest</option>
      <option value="pushed">Sort: Recently active</option>
    </select>
    <button class="rand-btn" id="randBtn">&#10038; Surprise</button>
    <button class="sum-btn" id="sumBtn">&#10697; Copy View</button>
    <button class="sum-btn ghost" id="dlJson" title="Download current filtered view as JSON">&#11015; JSON</button>
    <button class="sum-btn ghost" id="dlMd" title="Download current filtered view as Markdown">&#11015; Markdown</button>
    <span class="active-topic" id="activeTopic"><span>Topic: <b></b></span><span class="x" id="topicClear" aria-label="Clear topic filter">✕</span></span>
  </div>

  <div class="grid" id="grid"></div>
  <div class="empty-state" id="emptyState" style="display:none">No repositories match your search.</div>

  <div class="divider-img" aria-hidden="true"></div>

  <footer>
    <div class="seal" aria-hidden="true"></div>
    <h3>Methodology &amp; Honesty</h3>
    <p id="methodText">—</p>
    <p>Source: <span id="srcText">—</span>. Generated <span id="genText">—</span>.
       Last updated <span id="pubText">—</span>.</p>
    <p>Snapshots are point-in-time; regenerate with <code>python fetch.py; python build.py</code> (optional: put a
       <code>GITHUB_TOKEN</code> in a local <code>.env</code> file in this folder for richer, higher-rate data).</p>
  </footer>
</div>
<div class="err" id="errBox"></div>
<div class="drawer-back" id="drawerBack" aria-hidden="true"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Repository details" tabindex="-1">
  <button class="close" id="drawerClose" aria-label="Close details">✕</button>
  <div id="drawerBody"></div>
</aside>
<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script src="__WEEK_JS_SRC__"></script>
<script>
window.__DEPLOY_AT__ = "__DEPLOY_AT_VALUE__";
// External week data — kept OUT of the page so an archive can host one shared
// blob instead of duplicating ~120KB in every page.
//   - Served over http://  -> fetch() the .json (single source of truth).
//   - Opened from disk (file://) -> the .js loader set window.__WEEK__ (fetch of
//     local files is blocked by CORS in most browsers).
// Integrity check: if the fresh-this-week payload is missing/totally empty,
// show the error box instead of a blank grid.
let DATA = null;

(function loadWeek(){
  if (typeof fetch === 'function') {
    fetch('__WEEK_JSON_SRC__')
      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(d => { DATA = d; boot(); })
      .catch(err => {
        // file:// fallback: the .js shim (if it loaded) sets window.__WEEK__
        if (window.__WEEK__) { DATA = window.__WEEK__; boot(); }
        else showError('Could not load week data (' + err.message + '). Serve over http:// or run: python build.py');
      });
  } else if (window.__WEEK__) {
    DATA = window.__WEEK__; boot();
  }
})();

function showError(msg){
  const eb = document.getElementById('errBox');
  if (eb) { eb.textContent = msg; eb.style.display = 'block'; }
  const g = document.getElementById('grid');
  if (g) g.innerHTML = '';
}

function boot(){
  if (!DATA || !DATA.fresh_this_week) { showError('Week data is missing or incomplete (no fresh_this_week). Run: python build.py'); return; }
  const $ = s => document.querySelector(s);
  const LANG_COLORS = __LANG_COLORS__;
  const grid = $('#grid'), emptyState = $('#emptyState'), errBox = $('#errBox');
  let activeTab = 'fresh';
  let searchTerm = '', langSel = '', sortBy = 'stars', topicSel = '';
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function fmt(n){ return n>=1000 ? (n/1000).toFixed(n>=10000?0:1)+'k' : ''+n; }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  let sparkSeq = 0;
  function langColor(l){ return LANG_COLORS[l] || '#46e0ff'; }
  function hashStr(s){ let h=2166136261; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619);} return (h>>>0); }
  function rng(seed){ let s=seed>>>0; return ()=>{ s=(Math.imul(s,1664525)+1013904223)>>>0; return s/4294967296; }; }

  // --- Trend Intelligence helpers ---
  function sparkline(series, w, h){
    const vals = (series||[]).filter(v=>typeof v==='number');
    if(vals.length < 2) return '';
    const min = Math.min(...vals), max = Math.max(...vals);
    const span = (max-min) || 1;
    const n = vals.length;
    const step = n>1 ? w/(n-1) : 0;
    const pts = vals.map((v,i)=>[i*step, h - ((v-min)/span)*(h-6) - 3]);
    const line = pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
    const area = line + ` L ${w} ${h} L 0 ${h} Z`;
    const gid = 'sparkGrad'+(++sparkSeq);
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(70,224,255,.5)"/><stop offset="100%" stop-color="rgba(70,224,255,0)"/>
      </linearGradient></defs>
      <path class="spark-area" style="fill:url(#${gid})" d="${area}"/><path class="spark-line" d="${line}"/></svg>`;
  }
  function trendBadge(name){
    const t = TRENDS[name];
    if(!t) return '';
    let rankPart = '';
    if(typeof t.rank_delta==='number'){
      if(t.rank_delta>0) rankPart = `<span class="rank-delta up" title="Rank up vs last week">▲${t.rank_delta}</span>`;
      else if(t.rank_delta<0) rankPart = `<span class="rank-delta down" title="Rank down vs last week">▼${-t.rank_delta}</span>`;
      else rankPart = `<span class="rank-delta flat" title="Rank unchanged">→0</span>`;
    }
    if(t.status==='new') return `<span class="trend new"><span class="arw">✦</span><span>NEW</span></span>${rankPart}`;
    if(t.delta===0 || t.delta===null) return `<span class="trend flat"><span class="arw">→</span><span class="mag">0</span></span>${rankPart}`;
    const up = t.delta>0;
    const mag = (Math.abs(t.delta)>=1000? (Math.abs(t.delta)/1000).toFixed(1)+'k' : Math.abs(t.delta));
    return `<span class="trend ${up?'up':'down'}"><span class="arw">${up?'▲':'▼'}</span><span class="mag">${mag}</span></span>${rankPart}`;
  }
  function trendRow(name, series){
    const nums = (series||[]).filter(v=>typeof v==='number');
    if(nums.length < 4) return '';  // only render sparklines once we have >=4 weeks of history
    return `<div class="trend-row">${sparkline(series, 220, 30)}${trendBadge(name)}</div>`;
  }

  $('#weekLabel').textContent = DATA.week_label;
  $('#methodText').textContent = DATA.methodology;
  $('#srcText').textContent = DATA.source + (DATA.authenticated ? ' (authenticated)' : ' (public, rate-limited)');
  $('#genText').textContent = DATA.generated_at.replace('T',' ').slice(0,16) + ' UTC';
  $('#pubText').textContent = (window.__DEPLOY_AT__ || DATA.generated_at).replace('T',' ').slice(0,16) + ' UTC';

  let fresh = DATA.fresh_this_week, fire = DATA.still_on_fire;
  let allRepos = fresh.concat(fire);
  let totalStars = allRepos.reduce((a,r)=>a+r.stars,0);
  let langs = new Set(allRepos.map(r=>r.language||'Docs / list').filter(Boolean));
  let TRENDS = DATA.trends || {};

  // language null (no primary language) → "Docs / list", counted as its own slice
  function langOf(r){ return r.language ? r.language : 'Docs / list'; }

  function median(arr){
    const a = arr.slice().sort((x,y)=>x-y); if(!a.length) return 0;
    const m = Math.floor(a.length/2);
    return a.length%2 ? a[m] : Math.round((a[m-1]+a[m])/2);
  }
  // weekly delta + velocity helpers (delta = stars gained vs previous captured week)
  function deltaOf(r){ const t = TRENDS[r.full_name]; return (t && typeof t.delta==='number') ? t.delta : -Infinity; }
  function prevStarsOf(r){ const s=(TRENDS[r.full_name]||{}).series||[]; const nums=s.filter(v=>typeof v==='number'); return nums.length>=2 ? nums[nums.length-2] : 0; }
  function velocityOf(r){ const d=deltaOf(r); if(d===-Infinity) return -Infinity; return d / Math.max(prevStarsOf(r),1); }

  // Neural-map language visualization (AI theme): central "AI core" hub + language
  // nodes on a ring, sized by share of stars, with pulses traveling along the links.
  let LANG_NODES = [];   // latest computed entries, shared with the canvas loop
  function renderLang(){
    const base = (activeTab==='fresh'?fresh:fire);
    const totals = {};
    base.forEach(r=>{ const l=langOf(r); totals[l]=(totals[l]||0)+r.stars; });
    const entries = Object.entries(totals).sort((a,b)=>b[1]-a[1]).slice(0,8);
    const starSum = base.reduce((a,r)=>a+r.stars,0) || 1;
    LANG_NODES = entries.map(([l,v])=>({ lang:l, stars:v, pct:Math.round(v/starSum*100) }));
    const sub = document.getElementById('langSub');
    if(sub) sub.textContent = `Primary-language neurons, weighted by share of stars — currently showing ${activeTab==='fresh'?'Fresh This Week':(activeTab==='fire'?'Still On Fire':'Velocity')}`;
    // legend
    $('#langLegend').innerHTML = LANG_NODES.map(n=>{
      const c = langColor(n.lang);
      return '<div class="neural-row"><span class="dot" style="background:'+c+';color:'+c+'"></span>'
        + '<span class="nm" title="'+esc(n.lang)+'">'+esc(n.lang)+'</span>'
        + '<span class="vl"><b>'+fmt(n.stars)+'</b> <span class="pc">'+n.pct+'%</span></span></div>';
    }).join('');
    drawLangCanvas();
  }

  // Canvas neural constellation ------------------------------------------------
  let langRAF=null, langRunning=false, langT=0;
  function initLangCanvas(){
    const cv=$('#langCanvas'); if(!cv) return; const ctx=cv.getContext('2d');
    let W,H,DPR;
    function size(){ DPR=Math.min(2,window.devicePixelRatio||1);
      const r=cv.getBoundingClientRect(); W=cv.width=Math.floor(r.width*DPR); H=cv.height=Math.floor(r.height*DPR);
      cv.style.width=r.width+'px'; cv.style.height=r.height+'px'; }
    window.__langT = ()=>langT;
    function nodes(){ const cx=W/2, cy=H/2; const R=Math.min(W,H)*0.34;
      const max=Math.max(1,...LANG_NODES.map(n=>n.stars));
      return LANG_NODES.map((n,i)=>{ const ang=(-Math.PI/2)+(i/LANG_NODES.length)*Math.PI*2;
        const rr=Math.sqrt(n.stars/max)*Math.min(W,H)*0.10 + Math.min(W,H)*0.018;
        return { x:cx+Math.cos(ang)*R, y:cy+Math.sin(ang)*R, r:rr, ang, color:langColor(n.lang), name:n.lang, pct:n.pct }; }); }
    function draw(){
      ctx.clearRect(0,0,W,H);
      const cx=W/2, cy=H/2; const ns=nodes();
      // links hub->node + traveling pulse
      ns.forEach((p,i)=>{
        const g=ctx.createLinearGradient(cx,cy,p.x,p.y);
        g.addColorStop(0,'rgba(120,200,255,.05)'); g.addColorStop(1,p.color);
        ctx.strokeStyle=g; ctx.globalAlpha=.35; ctx.lineWidth=Math.max(1,DPR);
        ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(p.x,p.y); ctx.stroke(); ctx.globalAlpha=1;
        if(!reduce){
          const t=(langT*0.012 + i*0.13)%1;   // pulse position 0..1
          const px=cx+(p.x-cx)*t, py=cy+(p.y-cy)*t;
          const pg=ctx.createRadialGradient(px,py,0,px,py,7*DPR);
          pg.addColorStop(0,p.color); pg.addColorStop(1,'rgba(0,0,0,0)');
          ctx.fillStyle=pg; ctx.beginPath(); ctx.arc(px,py,7*DPR,0,6.283); ctx.fill();
        }
      });
      // central AI core
      const coreR=Math.min(W,H)*0.07;
      const pulse = reduce?0:Math.sin(langT*0.05)*0.5+0.5;
      const cg=ctx.createRadialGradient(cx,cy,0,cx,cy,coreR*(2.2+pulse));
      cg.addColorStop(0,'rgba(150,225,255,.9)'); cg.addColorStop(.4,'rgba(70,224,255,.5)'); cg.addColorStop(1,'rgba(70,224,255,0)');
      ctx.fillStyle=cg; ctx.beginPath(); ctx.arc(cx,cy,coreR*(2.2+pulse),0,6.283); ctx.fill();
      ctx.fillStyle='rgba(234,252,255,.95)'; ctx.beginPath(); ctx.arc(cx,cy,coreR*0.55,0,6.283); ctx.fill();
      // language nodes
      ns.forEach(p=>{
        const ng=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*2.4);
        ng.addColorStop(0,p.color); ng.addColorStop(1,'rgba(0,0,0,0)');
        ctx.fillStyle=ng; ctx.beginPath(); ctx.arc(p.x,p.y,p.r*2.4,0,6.283); ctx.fill();
        ctx.fillStyle=p.color; ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,6.283); ctx.fill();
        ctx.fillStyle='rgba(234,252,255,.92)'; ctx.font=Math.max(9,12*DPR)+'px var(--sans),system-ui,sans-serif';
        ctx.textAlign='center'; ctx.textBaseline='middle';
        // place label just outside the node, nudged away from center
        const ox=Math.cos(p.ang), oy=Math.sin(p.ang);
        ctx.fillText(p.name, p.x+ox*p.r*0.2, p.y+oy*(p.r+13*DPR));
        ctx.fillStyle='rgba(180,210,235,.8)'; ctx.font=Math.max(8,10*DPR)+'px var(--sans),system-ui,sans-serif';
        ctx.fillText(p.pct+'%', p.x+ox*p.r*0.2, p.y+oy*(p.r+13*DPR)+13*DPR);
      });
      if(!reduce && langRunning){ langT++; langRAF=requestAnimationFrame(draw); }
    }
    function start(){ if(reduce||langRunning||document.hidden) return; langRunning=true; langRAF=requestAnimationFrame(draw); }
    function stop(){ langRunning=false; if(langRAF) cancelAnimationFrame(langRAF); langRAF=null; }
    window.__drawLang = draw;
    size(); draw(); if(!reduce) start();
    window.addEventListener('resize', ()=>{ size(); if(!langRunning) draw(); });
    document.addEventListener('visibilitychange', ()=>{ if(document.hidden) stop(); else start(); });
  }
  function drawLangCanvas(){ if(window.__drawLang) window.__drawLang(); }
  try{ initLangCanvas(); }catch(err){ }

  // Build/refresh everything that depends on the loaded week's data
  function applyData(d){
    DATA = d;
    TRENDS = DATA.trends || {};
    fresh = DATA.fresh_this_week; fire = DATA.still_on_fire;
    allRepos = fresh.concat(fire);
    totalStars = allRepos.reduce((a,r)=>a+r.stars,0);
    langs = new Set(allRepos.map(r=>r.language||'Docs / list').filter(Boolean));
    $('#weekLabel').textContent = DATA.week_label;
    $('#methodText').textContent = DATA.methodology;
    $('#srcText').textContent = DATA.source + (DATA.authenticated ? ' (authenticated)' : ' (public, rate-limited)');
    $('#genText').textContent = DATA.generated_at.replace('T',' ').slice(0,16) + ' UTC';
  $('#pubText').textContent = (window.__DEPLOY_AT__ || DATA.generated_at).replace('T',' ').slice(0,16) + ' UTC';
    // split stats: Fresh count / Fire count / median Fresh stars / biggest delta
    const deltas = allRepos.map(r=>({r, d:deltaOf(r)})).filter(x=>x.d!==-Infinity);
    let bigName='—', bigVal=0;
    deltas.forEach(x=>{ if(x.d>bigVal){ bigVal=x.d; bigName=x.r.name; } });
    const statNums = [
      ['Fresh this week', fresh.length, false],
      ['Still on fire', fire.length, false],
      ['Median fresh stars', median(fresh.map(r=>r.stars)), false],
      ['Biggest Δ (week)', bigVal, false, (bigVal>0?'+':'')+fmt(bigVal)+' · '+bigName],
    ];
    $('#stats').innerHTML = statNums.map(([lbl,num,_,disp])=>`<div class="stat"><div class="num" data-target="${num}" data-stars="${lbl==='Combined stars'}">${disp!==undefined?disp:(typeof num==='number'&&lbl!=='Combined stars'?num:'')}</div><div class="lbl">${lbl}</div></div>`).join('');
    renderLang();
    buildBriefing();
    render();
  }

  // HUD ticker — makes the hero read as a live "working" AI
  function startHud(){
    const el = document.getElementById('hudMsg'); if(!el) return;
    const top = allRepos.slice().sort((a,b)=>b.stars-a.stars);
    const lt = {};
    allRepos.forEach(r=>{ const l=langOf(r); lt[l]=(lt[l]||0)+r.stars; });
    const topLang = Object.entries(lt).sort((a,b)=>b[1]-a[1])[0];
    const topLangName = topLang ? topLang[0] : 'mixed';
    const msgs = [
      `SYNTHESIZING SIGNAL · ${allRepos.length} REPOS`,
      `RANKING BY STAR VELOCITY`,
      `TOP STACK · ${topLangName.toUpperCase()}`,
      `LEADER · ${top[0]?top[0].name.toUpperCase():'—'}`,
      `WINDOW ${DATA.date_range_start} → ${DATA.date_range_end}`,
      `RENDERING NEURAL DIGEST`,
    ];
    let i = 0;
    el.style.transition='opacity .22s ease';
    if(reduce){ el.textContent = msgs[0]; return; }
    setInterval(()=>{ i=(i+1)%msgs.length; el.style.opacity=0;
      setTimeout(()=>{ el.textContent=msgs[i]; el.style.opacity=1; }, 220); }, 2600);
  }

  function repoCard(r, idx){
    // NOTE: data fields are pre-HTML-escaped at build time (build.py). Do NOT
    // re-esc here — that double-escapes and corrupts text containing & < > " '.
    const topics = (r.topics||[]).slice(0,5).map(t=>`<span class="chip" data-topic="${t}" role="button" tabindex="0" aria-label="Filter by topic ${t}">${t}</span>`).join('');
    const desc = (r.description ? r.description : 'No description provided.');
    const descCls = r.description ? 'desc' : 'desc empty';
    const created = r.created_at ? r.created_at.slice(0,10) : '';
    const pushed = r.pushed_at ? r.pushed_at.slice(0,10) : '';
    const lang = r.language ? `<span class="lang"><span class="dot" style="background:${langColor(r.language)}"></span>${r.language}</span>` : `<span class="lang"><span class="dot" style="background:var(--violet)"></span>Docs / list</span>`;
    const owner = (r.owner||'');
    const repoName = (r.name||'');
    const fullName = (r.full_name||'');
    const lc = langColor(r.language);
    const avatar = r.owner_avatar
      ? `<img class="avatar" src="${r.owner_avatar||''}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'"><span class="avatar-fallback" aria-hidden="true" style="display:none;width:42px;height:42px;border-radius:10px;border:1px solid var(--line);background:var(--panel2);place-items:center;color:var(--cyan);font-family:var(--disp);font-weight:700">${owner.slice(0,1).toUpperCase()}</span>`
      : `<span class="avatar-fallback" aria-hidden="true" style="width:42px;height:42px;border-radius:10px;border:1px solid var(--line);background:var(--panel2);display:grid;place-items:center;color:var(--cyan);font-family:var(--disp);font-weight:700">${owner.slice(0,1).toUpperCase()}</span>`;
    return `<article class="card" data-name="${(r.full_name||'').toLowerCase()}" data-topics="${(r.topics||[]).join(' ').toLowerCase()}" data-lang="${r.language||''}" data-stars="${r.stars}" data-forks="${r.forks}" data-created="${r.created_at||''}" data-pushed="${r.pushed_at||''}" data-idx="${idx}" tabindex="0" role="button" aria-label="${fullName}, ${r.stars} stars. Open details.">
      <div class="card-top"><div class="rank">${idx+1}</div>${avatar}
        <div class="meta"><div class="repo-name" title="${fullName}">${repoName}</div><div class="repo-owner">${owner}</div></div>
      </div>
      <div class="stars-row"><div class="star-big">${fmt(r.stars)}<span class="unit">stars</span></div>
        <div class="metric"><svg viewBox="0 0 24 24" stroke-width="2"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="12" r="2.5"/><path d="M8.5 6h5a3 3 0 0 1 3 3v0M8.5 18h5a3 3 0 0 0 3-3v0"/></svg>${fmt(r.forks)} forks</div>
        <div class="metric"><svg viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>${fmt(r.open_issues)} issues</div>
      </div>
      ${ (TRENDS[r.full_name] ? trendRow(r.full_name, TRENDS[r.full_name].series) : '') }
      <div class="bar"><span style="width:${Math.max(4,(r.stars/(activeTab==='fresh'?DATA.fresh_this_week[0].stars:DATA.still_on_fire[0].stars))*100)}%"></span></div>
      <div class="${descCls}">${desc}</div>
      <div class="tags">${topics}${lang}</div>
      <div class="card-foot"><a class="view-link" href="${r.html_url}" target="_blank" rel="noopener">View on GitHub
        <svg viewBox="0 0 24 24" stroke-width="2"><path d="M7 17L17 7M9 7h8v8"/></svg></a>
        <span class="created">${activeTab==='fresh' ? 'created '+created : 'pushed '+pushed}</span></div>
    </article>`;
  }

  const repoIndex = {};
  allRepos.forEach(r => { repoIndex[(r.full_name||'').toLowerCase()] = r; });
  const topList = (activeTab==='fresh' ? DATA.fresh_this_week : DATA.still_on_fire);
  const maxStars = (topList[0] ? topList[0].stars : 1) || 1;

  function render(){
    const list = (activeTab==='fresh' ? fresh : fire).slice();
    const term = searchTerm.toLowerCase();
    let filtered = list.filter(r=>{
      const hay = ((r.full_name||'')+(r.owner||'')+(r.description||'')+(r.topics||[]).join(' ')).toLowerCase();
      return (!term || hay.includes(term)) && (!langSel || langOf(r)===langSel) && (!topicSel || (r.topics||[]).includes(topicSel));
    });
    const sorters = {
      stars:(a,b)=>b.stars-a.stars,
      forks:(a,b)=>b.forks-a.forks,
      created:(a,b)=>(b.created_at||'').localeCompare(a.created_at||''),
      pushed:(a,b)=>(b.pushed_at||'').localeCompare(a.pushed_at||''),
      delta:(a,b)=> (deltaOf(b)-deltaOf(a)) || (b.stars-a.stars),
      velocity:(a,b)=> (velocityOf(b)-velocityOf(a)) || (b.stars-a.stars),
    };
    // default sort per tab: Fire & Velocity lead with weekly momentum, Fresh leads with total stars
    const effectiveSort = sortBy || (activeTab==='fresh' ? 'stars' : (activeTab==='velocity' ? 'velocity' : 'delta'));
    filtered.sort(sorters[effectiveSort]||sorters.stars);
    if(!filtered.length){ grid.innerHTML=''; emptyState.style.display='block'; return; }
    emptyState.style.display='none';
    grid.innerHTML = filtered.map((r,i)=>repoCard(r,i)).join('');
    observeCards();
  }

  // Returns the current filtered + sorted list (mirrors render()), for export/copy
  function getCurrentView(){
    const list = (activeTab==='fresh' ? fresh : fire).slice();
    const term = searchTerm.toLowerCase();
    let filtered = list.filter(r=>{
      const hay = ((r.full_name||'')+(r.owner||'')+(r.description||'')+(r.topics||[]).join(' ')).toLowerCase();
      return (!term || hay.includes(term)) && (!langSel || langOf(r)===langSel) && (!topicSel || (r.topics||[]).includes(topicSel));
    });
    const sorters = {
      stars:(a,b)=>b.stars-a.stars, forks:(a,b)=>b.forks-a.forks,
      created:(a,b)=>(b.created_at||'').localeCompare(a.created_at||''),
      pushed:(a,b)=>(b.pushed_at||'').localeCompare(a.pushed_at||''),
      delta:(a,b)=> (deltaOf(b)-deltaOf(a)) || (b.stars-a.stars),
      velocity:(a,b)=> (velocityOf(b)-velocityOf(a)) || (b.stars-a.stars),
    };
    const effectiveSort = sortBy || (activeTab==='fresh' ? 'stars' : (activeTab==='velocity' ? 'velocity' : 'delta'));
    filtered.sort(sorters[effectiveSort]||sorters.stars);
    return filtered;
  }

  let io;
  if('IntersectionObserver' in window && !reduce){
    io = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold:0.12 });
  }
  function observeCards(){
    const cards=[...grid.querySelectorAll('.card')];
    cards.forEach((c,i)=>{
      c.style.transitionDelay = Math.min(i,12)*55 + 'ms';
      if(io) io.observe(c); else c.classList.add('in');
      c.addEventListener('mousemove', ev=>{
        const rect=c.getBoundingClientRect();
        const px=(ev.clientX-rect.left)/rect.width, py=(ev.clientY-rect.top)/rect.height;
        c.style.setProperty('--mx', (px*100)+'%');
        c.style.setProperty('--my', (py*100)+'%');
        if(!reduce){ c.style.transform = `translateY(-6px) rotateX(${(0.5-py)*7}deg) rotateY(${(px-0.5)*7}deg)`; }
      });
      c.addEventListener('mouseleave', ()=>{ c.style.transform=''; });
    });
  }

  function countUp(){
    if(reduce){ document.querySelectorAll('.stat .num').forEach(n=>{
      const t=+n.dataset.target; if(isNaN(t) || (t===0 && n.dataset.stars!=='true')) return;
      n.textContent = n.dataset.stars==='true'?fmt(t):t; }); return; }
    document.querySelectorAll('.stat .num').forEach(n=>{
      const target=+n.dataset.target;
      if(isNaN(target)) return;
      if(target===0 && n.dataset.stars!=='true') return;
      const dur=1400, t0=performance.now();
      function step(now){ const p=Math.min(1,(now-t0)/dur); const e=1-Math.pow(1-p,3);
        const val=Math.floor(e*target); n.textContent = n.dataset.stars==='true'?fmt(val):val;
        if(p<1) requestAnimationFrame(step); else n.textContent = n.dataset.stars==='true'?fmt(target):target; }
      requestAnimationFrame(step);
    });
  }
  setTimeout(countUp, 500);

  // ===========================================================================
  // Starfield — a living "deep space" background: larger glowing stars with soft
  // halos, a few bright hero stars, slow twinkle + drift. Cheap enough (cached
  // radial gradients per star) and respects reduced-motion / tab-hidden pause.
  // ===========================================================================
  function initStars(){
    const cv=$('#stars'), ctx=cv.getContext('2d'); let W,H,DPR,pts=[],rafId=null,running=false,starsRunning=false;
    window.__starsRunning = () => starsRunning;
    function build(){
      DPR=Math.min(2,window.devicePixelRatio||1);
      W=cv.width=Math.floor(innerWidth*DPR); H=cv.height=Math.floor(innerHeight*DPR);
      cv.style.width=innerWidth+'px'; cv.style.height=innerHeight+'px';
      const n=Math.min(260, Math.floor(innerWidth*innerHeight/7000));
      pts=[];
      for(let i=0;i<n;i++){
        const r=Math.random();
        // ~6% become large "hero" stars with a wide halo
        const hero = r>0.94;
        const rad = (hero ? (Math.random()*2.2+2.4) : (Math.random()*1.6+1.1)) * DPR;
        pts.push({
          x:Math.random()*W, y:Math.random()*H,
          rad,
          halo: hero ? (rad*7) : (rad*3.4),        // glow radius
          base:Math.random()*0.45+0.4,
          amp:Math.random()*0.4+0.25,
          ph:Math.random()*6.28,
          sp:Math.random()*0.018+0.004,
          vx:(Math.random()-0.5)*0.05*DPR,
          vy:(Math.random()*0.09+0.015)*DPR,
          cross: hero || Math.random()<0.12,       // 4-point sparkle on bright stars
          hue:Math.random()<0.16 ? '255,255,255' : (Math.random()<0.5?'190,225,255':'130,205,255')
        });
      }
    }
    function star(x,y,rad,halo,hue,a,cross){
      // soft halo
      const g=ctx.createRadialGradient(x,y,0,x,y,halo);
      g.addColorStop(0,'rgba('+hue+','+(0.9*a).toFixed(3)+')');
      g.addColorStop(0.25,'rgba('+hue+','+(0.35*a).toFixed(3)+')');
      g.addColorStop(1,'rgba('+hue+',0)');
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,halo,0,6.283); ctx.fill();
      // bright core
      ctx.fillStyle='rgba(255,255,255,'+(0.85*a+0.15).toFixed(3)+')';
      ctx.beginPath(); ctx.arc(x,y,rad,0,6.283); ctx.fill();
      // 4-point sparkle for the brighter stars
      if(cross){
        const L=halo*0.9, w=Math.max(0.6,rad*0.5);
        ctx.strokeStyle='rgba('+hue+','+(0.5*a).toFixed(3)+')'; ctx.lineWidth=w;
        ctx.beginPath();
        ctx.moveTo(x-L,y); ctx.lineTo(x+L,y); ctx.moveTo(x,y-L); ctx.lineTo(x,y+L);
        ctx.stroke();
      }
    }
    function draw(){
      ctx.clearRect(0,0,W,H);
      for(const p of pts){
        const a = reduce ? p.base : (p.base + p.amp*Math.sin(t*p.sp + p.ph));
        star(p.x,p.y,p.rad,p.halo,p.hue,Math.max(0.08,a),p.cross);
      }
      if(!reduce && running){
        t++;
        for(const p of pts){
          p.x+=p.vx; p.y+=p.vy;
          if(p.y>H){ p.y=-p.halo; p.x=Math.random()*W; }
          if(p.x<0) p.x+=W; else if(p.x>W) p.x-=W;
        }
        rafId=requestAnimationFrame(draw);
      }
    }
    let t=0;
    window.__starsT = () => t;
    function start(){ if(reduce || running || document.hidden) return; running=true; starsRunning=true; rafId=requestAnimationFrame(draw); }
    function stop(){ running=false; starsRunning=false; if(rafId) cancelAnimationFrame(rafId); rafId=null; }
    build(); draw();
    if(!reduce) start();
    window.addEventListener('resize', ()=>{ build(); if(!running) draw(); });
    document.addEventListener('visibilitychange', ()=>{ if(document.hidden) stop(); else start(); });
  }
  try{ initStars(); }catch(err){ }

  function initSky(){
    const cv=$('#sky'), ctx=cv.getContext('2d'); let W,H,DPR,stars=[],mx=0,my=0,t=0;
    const reduced = reduce;
    let rafId = null, running = false, skyRunning = false;
    window.__skyRunning = () => skyRunning;   // inspectable: false when paused/hidden
    function build(){
      DPR=Math.min(2,window.devicePixelRatio||1);
      W=cv.width=Math.floor(innerWidth*DPR); H=cv.height=Math.floor(innerHeight*DPR);
      cv.style.width=innerWidth+'px'; cv.style.height=innerHeight+'px';
      const top = allRepos.slice().sort((a,b)=>b.stars-a.stars).slice(0,80);
      stars = top.map(r=>{ const h=hashStr(r.full_name); const rn=rng(h);
        const max=top[0].stars||1; const s=Math.sqrt(r.stars)/Math.sqrt(max);
        return { x:rn()*W, y:rn()*H*0.92+0.04*H, r:(1.4+s*5)*DPR, tw:rn()*6.28, sp:0.3+rn()*0.7, top:r.stars===top[0].stars, vx:(rn()-0.5)*0.05*DPR, vy:(rn()-0.5)*0.05*DPR }; });
    }
    function draw(){
      ctx.clearRect(0,0,W,H);
      // Nearest-8 neighbor links: cap each star's connections instead of drawing
      // every pair inside 150px (keeps the web light and the lines readable).
      for(let i=0;i<stars.length;i++){
        const a=stars[i]; const near=[];
        for(let j=0;j<stars.length;j++){ if(j===i) continue;
          const b=stars[j]; const dx=a.x-b.x, dy=a.y-b.y; near.push({b, d:Math.hypot(dx,dy)}); }
        near.sort((p,q)=>p.d-q.d);
        for(let k=0;k<Math.min(8,near.length);k++){
          const b=near[k].b, d=near[k].d;
          if(d<150*DPR){ const al=(1-d/(150*DPR))*0.12; ctx.strokeStyle='rgba(70,224,255,'+al.toFixed(3)+')';
            ctx.lineWidth=0.6*DPR; ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }
        }
      }
      for(const s of stars){
        const tw = reduced?1 : (0.6+0.4*Math.sin(t*0.02*s.sp + s.tw));
        const r = s.top ? s.r*1.8*(reduced?1:(0.85+0.15*Math.sin(t*0.05))) : s.r;
        const g=ctx.createRadialGradient(s.x,s.y,0,s.x,s.y,r*4);
        g.addColorStop(0,'rgba(234,252,255,'+(0.9*tw).toFixed(3)+')');
        g.addColorStop(0.4,'rgba(70,224,255,'+(0.35*tw).toFixed(3)+')');
        g.addColorStop(1,'rgba(70,224,255,0)');
        ctx.fillStyle=g; ctx.beginPath(); ctx.arc(s.x,s.y,r*4,0,6.283); ctx.fill();
      }
      if(!reduced && running){
        t++;
        for(const s of stars){ s.x+=s.vx; s.y+=s.vy; if(s.x<0||s.x>W) s.vx*=-1; if(s.y<0||s.y>H) s.vy*=-1;
          s.x += mx*0.6*DPR*0.04*(s.top?1:0.4); s.y += my*0.6*DPR*0.04*(s.top?1:0.4); }
        mx*=0.94; my*=0.94;
        rafId=requestAnimationFrame(draw);
      }
    }
    function start(){ if(reduced || running || document.hidden) return; running=true; skyRunning=true; rafId=requestAnimationFrame(draw); }
    function stop(){ running=false; skyRunning=false; if(rafId) cancelAnimationFrame(rafId); rafId=null; }
    build(); draw();                       // always paint one static frame
    if(!reduced) start();                  // then animate only when visible
    window.addEventListener('resize', ()=>{ build(); if(!running) draw(); });
    if(!reduced) window.addEventListener('mousemove', e=>{ mx=(e.clientX/innerWidth-0.5)*2; my=(e.clientY/innerHeight-0.5)*2; });
    // Pause the rAF loop when the tab is hidden (visibilitychange) to save CPU/GPU.
    document.addEventListener('visibilitychange', ()=>{ if(document.hidden) stop(); else start(); });
  }
  try{ initSky(); }catch(err){ }

  // Week picker — reload a captured week (separate generated file in weeks/)
  const weekPick = $('#weekPick');
  function safeName(w){ return (w||'').replace(/[^\w\-]+/g,'_'); }
  function populateWeeks(){
    const weeks = DATA.history_weeks || [];
    weekPick.innerHTML = weeks.map(w=>`<option value="${esc(safeName(w))}">${esc(w)}</option>`).join('')
      || '<option value="">No history yet</option>';
    const cur = safeName(DATA.week_label);
    if([...weekPick.options].some(o=>o.value===cur)) weekPick.value = cur;
  }
  // Mobile: collapse controls into a filter drawer
  const filterToggle = $('#filterToggle'), controlsEl = $('.controls');
  function updateFilterCount(){
    let n = 0;
    if(searchTerm) n++; if(langSel) n++; if(topicSel) n++;
    if(sortBy && !(activeTab==='fresh'?'stars':(activeTab==='velocity'?'velocity':'delta'))===sortBy) n++;
    const c = $('#filterCount'); if(c) c.textContent = n ? '('+n+')' : '';
  }
  if(filterToggle && controlsEl){
    filterToggle.addEventListener('click', ()=>{
      const open = controlsEl.classList.toggle('open');
      filterToggle.setAttribute('aria-expanded', open?'true':'false');
      if(open) filterToggle.setAttribute('aria-label','Close filters');
      else filterToggle.setAttribute('aria-label','Open filters');
    });
  }
  populateWeeks();
  weekPick.addEventListener('change', e=>{
    const f = 'weeks/week_'+e.target.value+'.json';
    fetch(f).then(r=>{ if(!r.ok) throw new Error('missing'); return r.json(); })
      .then(d=>{ applyData(d); populateWeeks(); })
      .catch(()=>{ toast('Week file not found: '+e.target.value); });
  });

  document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    t.classList.add('active'); activeTab=t.dataset.tab;
    // sensible default sort per tab
    const def = activeTab==='fresh' ? 'stars' : (activeTab==='velocity' ? 'velocity' : 'delta');
    sortBy = def; const sb=$('#sortBy'); if(sb) sb.value = def;
    render(); renderLang(); updateFilterCount();
  }));
  let st; $('#search').addEventListener('input',e=>{ clearTimeout(st); st=setTimeout(()=>{ searchTerm=e.target.value; render(); updateFilterCount(); },120); });
  $('#langFilter').addEventListener('change',e=>{ langSel=e.target.value; render(); updateFilterCount(); });
  $('#sortBy').addEventListener('change',e=>{ sortBy=e.target.value; render(); updateFilterCount(); });
  $('#randBtn').addEventListener('click',()=>{
    const cards=[...grid.querySelectorAll('.card')]; if(!cards.length) return;
    const c=cards[Math.floor(Math.random()*cards.length)];
    c.scrollIntoView({behavior:'smooth',block:'center'});
    c.classList.remove('flash'); void c.offsetWidth; c.classList.add('flash');
  });

  /* ---- SHARE / COPY helpers ---- */
  const toastEl = $('#toast'); let toastT;
  function toast(msg){ toastEl.textContent=msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT=setTimeout(()=>toastEl.classList.remove('show'),2200); }
  function copyText(txt){ if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(()=>toast('Copied to clipboard')).catch(()=>toast('Copy failed'));
    } else { const ta=document.createElement('textarea'); ta.value=txt; document.body.appendChild(ta); ta.select();
      try{ document.execCommand('copy'); toast('Copied to clipboard'); }catch(e){ toast('Copy failed'); } ta.remove(); } }
  function exportData(){
    // current filtered + sorted view (respects tab/search/lang/topic/sort)
    const view = getCurrentView();
    const meta = {
      week_label: DATA.week_label,
      date_range: [DATA.date_range_start, DATA.date_range_end],
      tab: activeTab,
      query: searchTerm || null,
      language: langSel || null,
      topic: topicSel || null,
      sort: sortBy || (activeTab==='fresh'?'stars':(activeTab==='velocity'?'velocity':'delta')),
      count: view.length,
      exported_at: new Date().toISOString(),
    };
    // slim each repo to useful fields (include trend delta/velocity if present)
    const rows = view.map(r=>{
      const t = TRENDS[r.full_name];
      return {
        rank: view.indexOf(r)+1,
        full_name: r.full_name, name: r.name, owner: r.owner,
        stars: r.stars, forks: r.forks, open_issues: r.open_issues,
        language: r.language || 'Docs / list', topics: r.topics || [],
        url: r.html_url,
        weekly_delta: (t && typeof t.delta==='number') ? t.delta : null,
        status: (t && t.status) || null,
      };
    });
    return { meta, repos: rows };
  }
  function download(filename, text, type){
    const blob = new Blob([text], {type: type+';charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download=filename; document.body.appendChild(a); a.click();
    setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 100);
  }
  $('#sumBtn').addEventListener('click',()=>{
    const {meta, repos} = exportData();
    const NL='\n';
    const head = `Best of GitHub — ${meta.week_label} (${meta.date_range[0]} → ${meta.date_range[1]})`;
    const filt = [meta.tab, meta.query&&('q='+meta.query), meta.language&&('lang='+meta.language), meta.topic&&('topic='+meta.topic)].filter(Boolean).join(' · ');
    let md = `# ${head}` + NL + (filt?`*Filtered: ${filt}*`+NL:'') + NL + `Showing ${repos.length} repos (sorted by ${meta.sort}):` + NL + NL;
    md += repos.map(r=>`${r.rank}. **${r.full_name}** — ${r.stars.toLocaleString()}★${(r.weekly_delta!=null)?` (${r.weekly_delta>=0?'+':''}${r.weekly_delta} this week)`:''} (${r.language})`+NL+`   ${r.url}`).join(NL);
    copyText(md);
  });
  $('#dlJson').addEventListener('click',()=>{ const {meta,repos}=exportData(); download(`best-of-github_${meta.tab}_${meta.date_range[0]}.json`, JSON.stringify({meta, repos}, null, 2), 'application/json'); toast('Downloaded JSON'); });
  $('#dlMd').addEventListener('click',()=>{ const {meta,repos}=exportData();
    let md = `# Best of GitHub — ${meta.week_label} (${meta.date_range[0]} → ${meta.date_range[1]})\n\n| # | Repo | Stars | Δ this wk | Lang | Topics |\n|---|------|------:|---------:|------|--------|\n`;
    md += repos.map(r=>`| ${r.rank} | [${r.full_name}](${r.url}) | ${r.stars.toLocaleString()} | ${(r.weekly_delta!=null)?(r.weekly_delta>=0?'+':'')+r.weekly_delta:'—'} | ${r.language} | ${(r.topics||[]).join(', ')} |`).join('\n');
    download(`best-of-github_${meta.tab}_${meta.date_range[0]}.md`, md, 'text/markdown'); toast('Downloaded Markdown'); });


  /* ---- DEEP LINKS: ?tab=fresh&q=mcp&lang=TypeScript&repo=owner/name ---- */
  function applyDeepLink(){
    const p = new URLSearchParams(location.search);
    if(p.has('tab')){ const t=p.get('tab'); if(['fresh','fire','velocity'].includes(t)){ activeTab=t;
      document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active', x.dataset.tab===t)); } }
    if(p.has('q')){ const q=p.get('q'); const sEl=$('#search'); if(sEl){ sEl.value=q; searchTerm=q; } }
    if(p.has('lang')){ const l=p.get('lang'); const lEl=$('#langFilter'); if(lEl && [...lEl.options].some(o=>o.value===l)){ lEl.value=l; langSel=l; } }
    let sortForTab = activeTab==='fresh'?'stars':(activeTab==='velocity'?'velocity':'delta');
    if(p.has('sort') && ['stars','delta','velocity','forks','created','pushed'].includes(p.get('sort'))) sortForTab=p.get('sort');
    sortBy = sortForTab; const sb=$('#sortBy'); if(sb) sb.value=sortForTab;
    render(); renderLang(); updateFilterCount();
    if(p.has('repo')){ const rn=(p.get('repo')||'').toLowerCase();
      // wait a tick for the grid to render, then open the matching card
      setTimeout(()=>{ const card=grid.querySelector(`.card[data-name="${CSS.escape(rn)}"]`); if(card) openDrawer(rn); }, 60); }
  }
  function syncURL(){
    const p = new URLSearchParams();
    if(activeTab!=='fresh') p.set('tab', activeTab);
    if(searchTerm) p.set('q', searchTerm);
    if(langSel) p.set('lang', langSel);
    const def = activeTab==='fresh'?'stars':(activeTab==='velocity'?'velocity':'delta');
    if(sortBy && sortBy!==def) p.set('sort', sortBy);
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs?'?'+qs:''));
  }
  /* ---- TOPIC FILTER ---- */
  const activeTopicEl = $('#activeTopic'), topicClear = $('#topicClear');
  function setTopic(t){ topicSel=t;
    if(t){ activeTopicEl.classList.add('show'); activeTopicEl.querySelector('b').textContent=t; }
    else { activeTopicEl.classList.remove('show'); }
    render(); updateFilterCount(); syncURL();
  }
  topicClear.addEventListener('click',()=>setTopic(''));

  /* ---- DRAWER ---- */
  const drawer = $('#drawer'), drawerBack = $('#drawerBack'), drawerBody = $('#drawerBody'), drawerClose = $('#drawerClose');
  let lastFocus = null;
  function openDrawer(fullName){
    const r = repoIndex[fullName]; if(!r) return;
    lastFocus = document.activeElement;
    const lc = langColor(r.language);
    const topics = (r.topics||[]).map(t=>`<span class="chip" data-topic="${t}">${t}</span>`).join('') || '<span class="chip">no topics</span>';
    drawerBody.innerHTML = `
      <img class="d-avatar" src="${r.owner_avatar||''}" alt="" referrerpolicy="no-referrer" onerror="this.style.visibility='hidden'">
      <div class="d-owner">${r.owner}</div>
      <div class="d-name">${r.name}</div>
      ${r.language?`<div class="d-lang"><span class="dot" style="background:${lc}"></span>${r.language}</div>`:''}
      <div class="d-stats">
        <div class="d-stat"><b>${fmt(r.stars)}</b><span>Stars</span></div>
        <div class="d-stat"><b>${fmt(r.forks)}</b><span>Forks</span></div>
        <div class="d-stat"><b>${fmt(r.open_issues)}</b><span>Issues</span></div>
      </div>
      ${ (TRENDS[r.full_name] ? `<div class="trend-row" style="margin:0 0 16px">${sparkline(TRENDS[r.full_name].series, 360, 40)}${trendBadge(r.full_name)}</div>` : '') }
      <div class="d-desc">${r.description?r.description:'No description provided.'}</div>
      <div class="d-meta">Created ${r.created_at?r.created_at.slice(0,10):'—'} · Last push ${r.pushed_at?r.pushed_at.slice(0,10):'—'}<br>Home: <a href="${r.html_url}" target="_blank" rel="noopener">${r.html_url}</a></div>
      <div class="d-topics">${topics}</div>
      <div class="d-actions">
        <a class="btn primary" href="${r.html_url}" target="_blank" rel="noopener">Open on GitHub</a>
        <button class="btn ghost" id="copyLink">Copy Link</button>
      </div>`;
    drawerBack.classList.add('open'); drawer.classList.add('open');
    drawer.setAttribute('aria-hidden','false');
    const frameEl = document.getElementById('frame'); if(frameEl) frameEl.inert = true;
    drawer.querySelector('#copyLink').addEventListener('click',()=>copyText(r.html_url));
    drawer.querySelectorAll('.d-topics .chip[data-topic]').forEach(c=>c.addEventListener('click',()=>setTopic(c.dataset.topic)));
    drawerClose.focus();
    trapFocus(drawer);
  }
  function trapFocus(container){
    const sel = 'a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])';
    function onKey(e){
      if(e.key!=='Tab') return;
      const f = [...container.querySelectorAll(sel)].filter(el=>el.offsetParent!==null);
      if(!f.length) return;
      const first=f[0], last=f[f.length-1];
      if(e.shiftKey && document.activeElement===first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement===last){ e.preventDefault(); first.focus(); }
    }
    container._trap = onKey; container.addEventListener('keydown', onKey);
  }
  function closeDrawer(){ drawer.classList.remove('open'); drawerBack.classList.remove('open');
    drawer.setAttribute('aria-hidden','true');
    const frameEl = document.getElementById('frame'); if(frameEl) frameEl.inert = false;
    if(drawer._trap) drawer.removeEventListener('keydown', drawer._trap);
    if(lastFocus&&lastFocus.focus) lastFocus.focus(); }

  drawerBack.addEventListener('click', closeDrawer);
  drawerClose.addEventListener('click', closeDrawer);

  /* grid-level delegation: card click / Enter -> drawer; topic chip -> filter */
  grid.addEventListener('click', e=>{
    const chip = e.target.closest('.chip[data-topic]');
    if(chip){ e.stopPropagation(); setTopic(chip.dataset.topic); return; }
    const card = e.target.closest('.card');
    if(card && !e.target.closest('a')) openDrawer(card.dataset.name);
  });
  grid.addEventListener('keydown', e=>{
    if(e.key==='Enter'||e.key===' '){
      const card = e.target.closest('.card'); const chip = e.target.closest('.chip[data-topic]');
      if(chip){ e.preventDefault(); setTopic(chip.dataset.topic); }
      else if(card){ e.preventDefault(); openDrawer(card.dataset.name); }
    }
  });
  document.addEventListener('keydown', e=>{ if(e.key==='Escape'){ if(drawer.classList.contains('open')) closeDrawer(); } });

  const langSelEl = $('#langFilter');
  [...langs].sort().forEach(l=>{ const o=document.createElement('option'); o.value=l; o.textContent=l; langSelEl.appendChild(o); });

  window.addEventListener('error',e=>{ errBox.style.display='block'; errBox.textContent='Error: '+e.message; });

  // --- AI Briefing: computed insight panel from real data (no external LLM) ---
  function buildBriefing(){
    const el = document.getElementById('briefing'); if(!el) return;
    const ranked = allRepos.slice().sort((a,b)=>b.stars-a.stars);
    const top1 = ranked[0], top2 = ranked[1];
    const newCount = fresh.length; // repos created this week (the Fresh-This-Week set)
    const trulyNew = Object.values(TRENDS).filter(t=>t.status==='new').length;
    const leaders = ranked.slice(0,3);
    const leadStr = leaders.map(r=>r.name).join(', ');
    const langTot = {};
    allRepos.forEach(r=>{ const l=r.language||'Docs / list'; langTot[l]=(langTot[l]||0)+r.stars; });
    const langTop = Object.entries(langTot).sort((a,b)=>b[1]-a[1])[0];
    const comboUp = (window.__momentum && window.__momentum.up) || Object.values(TRENDS).filter(t=>t.status==='up').length;
    el.innerHTML = `<span class="bdot"></span><span class="btxt"><span class="tag">AI Briefing</span>`
      + `This cycle surfaced <b>${allRepos.length}</b> repositories — led by <b>${top1?top1.name:'—'}</b> at <b>${top1?fmt(top1.stars):0}★</b>. `
      + `Dominant stack is <b>${langTop?langTop[0]:'mixed'}</b>; <b>${newCount}</b> repos were created this week and <b>${comboUp}</b> gained stars week-over-week. `
      + `Momentum leaders: ${leadStr}.</span>`;
    el.classList.add('in');
    if(reduce) el.style.opacity=1, el.style.transform='none';
  }

  // --- Scroll progress bar ---
  const prog = document.getElementById('progress');
  function onScroll(){
    const h = document.documentElement.scrollHeight - window.innerHeight;
    const p = h>0 ? (window.scrollY/h*100) : 0;
    prog.style.width = p.toFixed(2)+'%';
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();

  // --- Title cursor-tilt + hero parallax (respect reduced motion) ---
  const titleEl = document.querySelector('.title');
  const heroArtEl = document.querySelector('.hero-art');
  if(!reduce){
    window.addEventListener('mousemove', e=>{
      const nx = (e.clientX/window.innerWidth)-0.5, ny = (e.clientY/window.innerHeight)-0.5;
      if(titleEl) titleEl.style.transform = `perspective(700px) rotateX(${(14 - ny*7).toFixed(2)}deg) rotateY(${(nx*8).toFixed(2)}deg)`;
      if(heroArtEl) heroArtEl.style.transform = `translate(-50%,-50%) scale(1.08) translate(${(nx*14).toFixed(1)}px, ${(ny*14).toFixed(1)}px)`;
    });
  }

  // --- Reveal on scroll for stats / langchart / banners / controls ---
  if('IntersectionObserver' in window && !reduce){
    const io = new IntersectionObserver((ents)=>{
      ents.forEach(en=>{ if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
    }, {threshold:0.12});
    ['#stats','.langchart','.banner.b2','.banner.b3','.divider-img','.controls'].forEach(s=>{
      const t = document.querySelector(s); if(t) io.observe(t);
    });
  } else {
    ['#stats','.langchart','.banner.b2','.banner.b3','.divider-img','.controls'].forEach(s=>{
      const t = document.querySelector(s); if(t) t.classList.add('in');
    });
  }
  // failsafe: never leave content hidden if IO/scroll misbehaves
  setTimeout(()=>{ ['#stats','.langchart','.banner.b2','.banner.b3','.divider-img','.controls'].forEach(s=>{
    const t = document.querySelector(s); if(t) t.classList.add('in'); }); }, 4000);

  startHud();
  applyData(DATA);  // initial render of all data-dependent UI
}

</script>
</body>
</html>
"""

# ----------------------------------------------------------------------------
# Schema validation — required fields, ISO dates, star >= 0.
# Fail loudly at build time so a broken snapshot never reaches the page.
# ----------------------------------------------------------------------------
def is_iso_date(s):
    if not isinstance(s, str):
        return False
    try:
        datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False

REPO_REQUIRED = {
    "name": str, "full_name": str, "owner": str, "html_url": str,
    "description": str, "stars": int, "forks": int, "open_issues": int,
    "language": (str, type(None)), "topics": list,
    "created_at": str, "pushed_at": str, "license": (str, type(None)),
}

def validate_repo(r, where):
    if not isinstance(r, dict):
        raise ValueError(f"{where}: repo entry is not an object: {r!r}")
    for k, t in REPO_REQUIRED.items():
        if k not in r:
            raise ValueError(f"{where}: repo {r.get('full_name','?')!r} missing required field {k!r}")
        v = r[k]
        ok = isinstance(v, t) if isinstance(t, tuple) else isinstance(v, t)
        if not ok:
            raise ValueError(f"{where}: repo {r.get('full_name','?')!r} field {k!r} has wrong type "
                             f"(expected {t.__name__}, got {type(v).__name__})")
    if r["stars"] < 0:
        raise ValueError(f"{where}: repo {r['full_name']!r} has negative stars ({r['stars']})")
    # ISO date sanity for the two date fields we sort/display
    if not is_iso_date(r["created_at"]):
        raise ValueError(f"{where}: repo {r['full_name']!r} created_at is not ISO-8601: {r['created_at']!r}")
    if not is_iso_date(r["pushed_at"]):
        raise ValueError(f"{where}: repo {r['full_name']!r} pushed_at is not ISO-8601: {r['pushed_at']!r}")

TOP_REQUIRED = {
    "generated_at": str, "week_label": str,
    "date_range_start": str, "date_range_end": str,
    "fresh_this_week": list, "still_on_fire": list,
    "history_weeks": list, "trends": dict,
    "methodology": str, "source": str, "authenticated": bool,
}
for k, t in TOP_REQUIRED.items():
    if k not in data:
        raise ValueError(f"top-level payload missing required field {k!r}")
    if k == "generated_at" and not is_iso_date(data[k]):
        raise ValueError(f"top-level payload field {k!r} is not ISO-8601: {data[k]!r}")
    if not isinstance(data[k], t):
        raise ValueError(f"top-level payload field {k!r} has wrong type "
                         f"(expected {t.__name__}, got {type(data[k]).__name__})")

for i, r in enumerate(data["fresh_this_week"]):
    validate_repo(r, f"fresh_this_week[{i}]")
for i, r in enumerate(data["still_on_fire"]):
    validate_repo(r, f"still_on_fire[{i}]")

# ----------------------------------------------------------------------------
# HTML escaping at build time — the client can never forget.
# Every repo field that lands in the DOM is pre-escaped here, so even if GitHub
# returns <script> in a description, the page renders it inert. The inline esc()
# in the page is now a belt-and-braces fallback (defense in depth), not the
# primary guard.
# ----------------------------------------------------------------------------
def htmlesc(v):
    if v is None:
        return ""
    s = str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))

def _esc_value(v):
    # Only escape strings. Lists keep their shape (each element escaped), numbers
    # and null pass through untouched — the client expects r.topics to stay an array.
    if isinstance(v, str):
        return htmlesc(v)
    if isinstance(v, list):
        return [_esc_value(x) for x in v]
    return v

def esc_repo(r):
    return {k: _esc_value(v) for k, v in r.items()}

sane = dict(data)
sane["fresh_this_week"] = [esc_repo(r) for r in data["fresh_this_week"]]
sane["still_on_fire"] = [esc_repo(r) for r in data["still_on_fire"]]
# build-time escaping means the page's esc() never has anything to do, but the
# post-escape blob still must not break out of a <script> context:
raw = json.dumps(sane, ensure_ascii=False)
raw = raw.replace("</", "<\\/")

# Derive a stable week file name (e.g. data/week-34.json)
m = re.search(r"Week (\d+)", data.get("week_label", ""))
week_no = m.group(1) if m else "current"
week_file = f"week-{week_no}.json"

HTML = HTML.replace("__WEEK_JSON_SRC__", f"data/{week_file}")
HTML = HTML.replace("__WEEK_JS_SRC__", f"data/{week_file}.js")
HTML = HTML.replace("__LANG_COLORS__", LANG_COLORS_JS)

# Inject the "Last updated" deploy timestamp (written by deploy.py at publish time)
_deploy_json = os.path.join(HERE, "deploy.json")
_deploy_at = ""
if os.path.exists(_deploy_json):
    try:
        _deploy_at = json.load(open(_deploy_json, encoding="utf-8")).get("deployed_at", "")
    except Exception:
        _deploy_at = ""
HTML = HTML.replace("__DEPLOY_AT_VALUE__", _deploy_at)

# Regenerate favicon + OG social-share image (pure PIL, no network)
try:
    import subprocess as _sp
    _sp.run([sys.executable, os.path.join(HERE, "gen_assets.py")], check=False)
except Exception:
    pass

# Write the shell page (no inline data blob)
out = os.path.join(HERE, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print("Wrote", out, "(%d bytes)" % len(HTML))

# Write the external week data file (the 120KB blob now lives here, shared by
# index.html and any archive page — not duplicated into every page).
data_dir = os.path.join(HERE, "data")
os.makedirs(data_dir, exist_ok=True)
week_json_path = os.path.join(data_dir, week_file)
with open(week_json_path, "w", encoding="utf-8") as f:
    json.dump(sane, f, ensure_ascii=False, indent=2)
# .js shim so the page works when opened directly from disk (file://) where
# fetch() of a local file is blocked by CORS.
with open(os.path.join(data_dir, week_file + ".js"), "w", encoding="utf-8") as f:
    f.write("window.__WEEK__ = ")
    json.dump(sane, f, ensure_ascii=False)
    f.write(";\n")
print("Wrote", week_json_path, "(%d bytes)" % os.path.getsize(week_json_path))

# Refresh the matching weeks/ snapshot (this is what the week picker loads) so it
# carries the same build-time-escaped, validated data — the picker no longer pulls
# the raw, unescaped weeks/*.json.
try:
    safe = re.sub(r"[^\w\-]+", "_", data.get("week_label", "")).strip("_")
    wk_dir = os.path.join(HERE, "weeks")
    os.makedirs(wk_dir, exist_ok=True)
    wk_path = os.path.join(wk_dir, f"week_{safe}.json")
    with open(wk_path, "w", encoding="utf-8") as f:
        json.dump(sane, f, ensure_ascii=False, indent=2)
    print("Refreshed", wk_path)
except Exception as e:
    print("Warn: could not refresh weeks/ snapshot:", e, file=sys.stderr)
