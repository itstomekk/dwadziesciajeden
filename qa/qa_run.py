"""QA gates for the built site. Needs qa/serve.py running on :8721.

Run from the qa folder with an interpreter that has Playwright (Firefox):
    C:/Python314/python.exe qa_run.py
Writes qa/report.md (PASS/FAIL with evidence) and screenshots to qa/shots/.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
BASE = "http://127.0.0.1:8721" + os.environ.get("DJ_BASE", "/dwadziesciajeden").rstrip("/")
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

PAGES = ["/", "/kim-jestesmy/", "/dolacz-do-nas/", "/zasady/", "/miasta/", "/warszawa/", "/poznan/", "/wroclaw/",
         "/bitcoinowa-mapa-polski/", "/projekty/", "/inicjatywy/", "/biblioteka/", "/kronika/", "/artykuly/",
         "/standard-bitcoina-w-polskim-parlamencie/", "/proof-of-keys-3-stycznia-doroczny-test-zaufania-dla-bitcoina-i-dla-ciebie/",
         "/zbieramy-satki-na-wosp/", "/bitcoin-whitepaper/", "/slowniczek/", "/tag/zbiorki/"]

OLD_URLS = ["/", "/dolacz-do-nas/", "/miasta/", "/bitcoinowa-mapa-polski/", "/projekty/", "/bitcoin-whitepaper/",
            "/kim-jestesmy/", "/standard-bitcoina-w-polskim-parlamencie/",
            "/proof-of-keys-3-stycznia-doroczny-test-zaufania-dla-bitcoina-i-dla-ciebie/", "/poznan/", "/krakow/",
            "/warszawa/", "/author/jesterhodl/", "/tag/miasta/", "/tag/zbiorki/", "/tag/artykuly/", "/tag/zasoby/",
            "/tag/meetupy/", "/meetup-w-warszawie-17-ii-2023/", "/meetup-w-warszawie-2-xii-2022/",
            "/meetup-w-warszawie-4-xi-2022/", "/meetup-we-wroclawiu-12-i-2023/", "/zbieramy-satki-na-wosp/", "/mapa/",
            "/meetupy/", "/slowniczek/"]

results = []


def gate(name, ok, evidence):
    results.append((name, ok, evidence))
    print(("PASS " if ok else "FAIL ") + name + ": " + evidence)


def status(url):
    try:
        return urllib.request.urlopen(url, timeout=10).status
    except urllib.error.HTTPError as ex:
        return ex.code


# 1. every old URL still resolves
bad = [u for u in OLD_URLS if status(BASE + u) != 200]
gate("old-urls", not bad, f"{len(OLD_URLS) - len(bad)}/{len(OLD_URLS)} old dwadziesciajeden.pl paths return 200" + (f"; failing {bad}" if bad else ""))

# 2. internal links and assets resolve (static scan of every built page)
missing = set()
files = list(DOCS.rglob("*.html"))
for f in files:
    h = f.read_text(encoding="utf-8")
    for ref in re.findall(r'(?:href|src)="(/dwadziesciajeden/[^"#?]*)', h):
        p = DOCS / ref[len("/dwadziesciajeden/"):]
        if ref.endswith("/"):
            p = p / "index.html"
        if not p.exists():
            missing.add(ref)
gate("internal-links", not missing, f"{len(files)} pages scanned; missing targets: {sorted(missing)[:10] if missing else 0}")

# 3. no leftover Ghost markup, old-host media, or tracking scripts
leftover = []
for f in files:
    h = f.read_text(encoding="utf-8")
    for pat in ("kg-card", "twitter-tweet", "platform.twitter.com", "dwadziesciajeden.pl/content/", "google.com/maps", "ref=dwadziesciajeden"):
        if pat in h:
            leftover.append(f"{f.relative_to(DOCS)}:{pat}")
gate("clean-markup", not leftover, f"leftovers: {leftover[:8] if leftover else 'none'}")

# 4. noindex while in preview
robots = (DOCS / "robots.txt").read_text()
noidx = all('name="robots" content="noindex,nofollow"' in f.read_text(encoding="utf-8") for f in files if f.name == "index.html" and "http-equiv" not in f.read_text(encoding="utf-8"))
gate("preview-noindex", "Disallow: /" in robots and noidx, "robots.txt Disallow all + meta noindex on every page")

# 5. placeholders listed
ph = sorted({m for f in files for m in re.findall(r'data-placeholder="([^"]+)"', f.read_text(encoding="utf-8"))})
gate("placeholders", True, f"open placeholders: {ph or 'none'}")

# 6. browser: console errors, overflow, screenshots, search
with sync_playwright() as pw:
    br = pw.firefox.launch()
    errs = {}
    overflow = {}
    for vp_name, vp in (("desk", {"width": 1366, "height": 900}), ("mob", {"width": 390, "height": 844})):
        ctx = br.new_context(viewport=vp, device_scale_factor=1)
        page = ctx.new_page()
        for path in PAGES:
            msgs = []
            page.on("console", lambda m, msgs=msgs: msgs.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda ex, msgs=msgs: msgs.append(str(ex)))
            page.goto(BASE + path, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(300)
            w = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            if w > 1:
                overflow[f"{vp_name}{path}"] = w
            own = [m for m in msgs if "btcmap" not in m.lower() and "youtube" not in m.lower()]
            if own:
                errs[f"{vp_name}{path}"] = own[:3]
            name = (path.strip("/").replace("/", "_") or "home")[:40]
            page.screenshot(path=str(SHOTS / f"{vp_name}-{name}.png"), full_page=True)
        ctx.close()
    gate("console-errors", not errs, f"{len(PAGES) * 2} page loads; pages with errors: {len(errs)}; first: {str(next(iter(errs.items())))[:300] if errs else 'none'}")
    gate("no-overflow", not overflow, f"horizontal overflow: {overflow or 'none'}")

    ctx = br.new_context(viewport={"width": 1366, "height": 900})
    page = ctx.new_page()
    page.goto(BASE + "/", wait_until="networkidle")
    page.click("[data-search-open]")
    queries = {"proof of keys": "Proof of Keys", "poznan": "Poznań", "standard": "Standard", "fiat": "Fiat"}
    sr = {}
    for q, expect in queries.items():
        page.fill("#search-q", q)
        page.wait_for_timeout(400)
        txt = page.inner_text("#search-res")
        sr[q] = expect.lower() in txt.lower()
    page.screenshot(path=str(SHOTS / "desk-search.png"))
    gate("search", all(sr.values()), json.dumps(sr, ensure_ascii=False))

    page.goto(BASE + "/kronika/", wait_until="networkidle")
    total = page.locator(".tl-wrap .tl__item").count()
    page.click('.filters button[data-filter="t-standard-bitcoina"]')
    vis = page.locator(".tl-wrap .tl__item:not(.is-hidden)").count()
    gate("chronicle-filter", 0 < vis < total, f"{vis} of {total} entries visible after 'Standard Bitcoina' filter")
    br.close()

ok = all(r[1] for r in results)
(HERE / "report.md").write_text("# QA report\n\n" + "\n".join(f"- {'PASS' if r[1] else 'FAIL'} **{r[0]}**: {r[2]}" for r in results) + "\n", encoding="utf-8")
print("ALL PASS" if ok else "SOME FAIL")
sys.exit(0 if ok else 1)
