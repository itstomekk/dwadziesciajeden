"""Build the static Dwadzieścia Jeden site into docs/.

Stdlib only. Reads content/*.json, writes docs/ (wiped each run, CNAME kept).
BASE: URL prefix. GitHub Pages project site = "/dwadziesciajeden"; custom domain = "".
    python build.py                 # BASE from config below
    DJ_BASE= python build.py        # build for the root of a custom domain
NOINDEX stays True until the owner says go live.
"""
import html
import html.parser
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
C = ROOT / "content"

BASE = os.environ.get("DJ_BASE", "").rstrip("/")  # live on dwadziesciajeden.pl since 2026-10-23
SITE_URL = os.environ.get("DJ_SITE_URL", "https://dwadziesciajeden.pl").rstrip("/")
NOINDEX = os.environ.get("DJ_NOINDEX", "0") == "1"
BUILT = date.today().isoformat()

TG = "https://t.me/dwadziesciajeden"
TG_POZNAN = "https://t.me/DwadziesciaJedenPoznan"
X_URL = "https://x.com/21BitcoinPolska"
NOSTR_NPUB = "npub1cpmvpsqtzxl4px44dp4544xwgu0ryv2lscl3qexq42dfakuza02s4fsapc"
NOSTR_ARMADA = "https://armada.buzz/c/50bb9c75a72e30c95c2a0cd7e3b4bf39e6e3b81faa9d5bf65aa25a10dc5b21c6/4e95853f368df5a47d306a7ab7233e3c5451b7ef55279417498fa9be7c7c5c4d/m/6f327e5556b324781f4c9e48f575c8a2f7b1dc6c2a5b1e9463c93e1d3ef1e15b"
NOSTR_URL = "https://primal.net/p/nprofile1qqsvqakqcq93r06sn26ks6626n8yw83jx90cv0csvnq24x57mwpwh4gx83su2"
EMAIL = "kontakt@dwadziesciajeden.pl"
GOATCOUNTER = "https://dwadziesciajeden21.goatcounter.com/count"  # cookieless, no consent banner needed
INDEXNOW_KEY = "5f1d2a9c8e7b4630a1c2d3e4f5a6b7c8"  # public by design (served as /<key>.txt)
# training-only crawlers (search/answer bots like OAI-SearchBot, ChatGPT-User, Claude-User, PerplexityBot stay allowed)
AI_TRAIN_BOTS = ["GPTBot", "ClaudeBot", "anthropic-ai", "Google-Extended", "Applebot-Extended", "CCBot",
                 "meta-externalagent", "Bytespider", "Amazonbot", "cohere-training-data-crawler", "Diffbot", "omgili"]
# Founding: first message of the Telegram group "yellowpilled", 2021-04-05 16:56:13 UTC (source-archive/telegram/yellowpilled.json).
# Chain tip at that moment: block 677896 (mined 16:50:47 UTC; 677897 came at 16:57:35). Checked via mempool.space + blockstream.info.
FOUNDING_BLOCK = 677896
FOUNDING_BLOCK_TXT = "677&nbsp;896"
# Home hero headline: one phrase per day ("|" = line break), same for every visitor that
# day (visitor's local date), cycling through the list (mixed so similar phrases are not neighbours). The first one is the static HTML
# (no JS, crawlers); a tiny inline script right after the h1 swaps it before first paint.
HERO_PHRASES = ["Dwadzieścia|Jeden", "Uczciwy|pieniądz", "Technologia|Wolności",
                "Nie ufaj,|weryfikuj", "Cicha|rewolucja", "Wolność|od inflacji",
                "Bądź swoim|bankiem", "Wolna|przyszłość", "Odporny|na cenzurę",
                "Pieniądz|przyszłości", "Prywatność|to wolność", "Pokojowa|rewolucja",
                "Sygnał,|nie szum", "Wolność|w kodzie", "Bez|pozwolenia",
                "Wolnościowa|rewolucja", "Otwarty|dla każdego", "Wolność,|która działa"]

# brand icons: Telegram + X from Simple Icons (CC0), Nostr from mbarulli/nostr-logo (CC0)
def icon(name):
    paths = {
        "telegram": ("0 0 24 24", "M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"),
        "x": ("0 0 24 24", "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"),
        "nostr": ("44 44 172 172", "M210.8 199.4c0 3.1-2.5 5.7-5.7 5.7h-68c-3.1 0-5.7-2.5-5.7-5.7v-15.5c.3-19 2.3-37.2 6.5-45.5 2.5-5 6.7-7.7 11.5-9.1 9.1-2.7 24.9-.9 31.7-1.2 0 0 20.4.8 20.4-10.7s-9.1-8.6-9.1-8.6c-10 .3-17.7-.4-22.6-2.4-8.3-3.3-8.6-9.2-8.6-11.2-.4-23.1-34.5-25.9-64.5-20.1-32.8 6.2.4 53.3.4 116.1v8.4c0 3.1-2.6 5.6-5.7 5.6H57.7c-3.1 0-5.7-2.5-5.7-5.7v-144c0-3.1 2.5-5.7 5.7-5.7h31.7c3.1 0 5.7 2.5 5.7 5.7 0 4.7 5.2 7.2 9 4.5 11.4-8.2 26-12.5 42.4-12.5 36.6 0 64.4 21.4 64.4 68.7v83.2ZM150 99.3c0-6.7-5.4-12.1-12.1-12.1s-12.1 5.4-12.1 12.1 5.4 12.1 12.1 12.1S150 106 150 99.3Z"),
        "rss": ("0 0 24 24", "M19.199 24C19.199 13.467 10.533 4.8 0 4.8V0c13.165 0 24 10.835 24 24h-4.801zM3.291 17.415c1.814 0 3.293 1.479 3.293 3.295 0 1.813-1.485 3.29-3.301 3.29C1.47 24 0 22.526 0 20.71s1.475-3.294 3.291-3.295zM15.909 24h-4.665c0-6.169-5.075-11.245-11.244-11.245V8.09c8.727 0 15.909 7.184 15.909 15.91z"),
    }
    vb, d = paths[name]
    return f'<svg class="ico" viewBox="{vb}" aria-hidden="true" focusable="false"><path fill="currentColor" d="{d}"/></svg>'


NAV = [
    ("Kim jesteśmy", "/kim-jestesmy/"),
    ("Edukacja", "/edukacja/"),
    ("Mapa i miasta", "/bitcoinowa-mapa-polski/"),
    ("Projekty", "/projekty/"),
    ("Kronika", "/kronika/"),
]

MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia",
          "września", "października", "listopada", "grudnia"]
MONTHS_NOM = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień",
              "Wrzesień", "Październik", "Listopad", "Grudzień"]

e = html.escape
pages_index = []  # for search


def load(name, default=None):
    p = C / name
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def b(path: str) -> str:
    return BASE + path


def fill(h: str) -> str:
    return h.replace("{B}", BASE)


def pl_date(d: str) -> str:
    parts = d.split("-")
    if len(parts) == 3:
        return f"{int(parts[2])} {MONTHS[int(parts[1]) - 1]} {parts[0]}"
    if len(parts) == 2:
        return f"{MONTHS_NOM[int(parts[1]) - 1]} {parts[0]}"
    return d


def link(l):
    if l.get("internal"):
        return f'<a href="{b(l["internal"])}">{e(l["label"])}</a>'
    return f'<a href="{e(l["url"])}" rel="noopener">{e(l["label"])}</a>'


def text_of(h: str) -> str:
    h = re.sub(r"<script\b.*?</script>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


LOGO_SRC = BASE + "/assets/logo.jpg"
LOGO = f'<img class="mark" src="{LOGO_SRC}" width="44" height="44" alt="">'


def layout(path, title, body, desc="", kind="page", og_image=None, crumbs=None):
    full_title = f"{title} · Dwadzieścia Jeden" if title != "Dwadzieścia Jeden" else "Dwadzieścia Jeden: polska społeczność Bitcoin Only"
    desc = desc or "Dwadzieścia Jeden: polska społeczność bitcoinowych maksymalistów, część sieci TwentyOne."
    og = og_image or b("/assets/og.jpg")
    nav = "".join(
        f'<a href="{b(u)}"{" aria-current=page" if path.startswith(u) else ""}>{e(t)}</a>' for t, u in NAV
    )
    robots = '<meta name="robots" content="noindex,nofollow">' if NOINDEX else ""
    crumb = ""
    if crumbs:
        crumb = '<nav class="crumbs" aria-label="Okruszki">' + " / ".join(
            f'<a href="{b(u)}">{e(t)}</a>' for t, u in crumbs) + "</nav>"
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="canonical" href="{SITE_URL}{path}">
{md_alt(path)}<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Dwadzieścia Jeden">
{jsonld(path)}<meta property="og:type" content="{'article' if kind == 'post' else 'website'}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}{og.replace(BASE, '', 1) if og.startswith(BASE) else og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@21BitcoinPolska">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{b('/assets/favicon.png')}" type="image/png">
<link rel="apple-touch-icon" href="{b('/assets/apple-touch-icon.png')}">
<link rel="preload" href="{b('/assets/fonts/montserrat-latin.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{b('/assets/fonts/fonts.css')}">
<link rel="stylesheet" href="{b('/assets/site.css')}?v={BUILT}">
<link rel="alternate" type="application/rss+xml" title="Dwadzieścia Jeden: kronika i artykuły" href="{SITE_URL}/rss.xml">
</head>
<body class="k-{kind}" data-base="{BASE}">
<div class="btc-bg" aria-hidden="true">{BTC_MARK}</div>
<a class="skip" href="#tresc">Przejdź do treści</a>
<header class="top">
  <div class="top__in">
    <a class="brand" href="{b('/')}">{LOGO}<span>Dwadzieścia Jeden</span></a>
    <nav class="nav" id="nav" aria-label="Główne menu">{nav}</nav>
    <div class="top__act">
      <button class="icon-btn" type="button" data-search-open aria-label="Szukaj"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg></button>
      <a class="btn btn--primary btn--sm" href="{TG}" rel="noopener" data-goatcounter-click="dolacz-telegram-naglowek" data-goatcounter-title="Dołącz (nagłówek)">Dołącz</a>
      <button class="icon-btn menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
</header>
<main id="tresc">
{crumb}
{body}
</main>
<footer class="foot">
  <div class="foot__in">
    <div class="foot__brand">
      <a class="brand" href="{b('/')}">{LOGO}<span>Dwadzieścia Jeden</span></a>
      <p>Polska społeczność Bitcoin Only. Część sieci <a href="https://twentyone.world/" rel="noopener">TwentyOne</a>.</p>
    </div>
    <div class="foot__col">
      <h2>Społeczność</h2>
      <a class="ico-link" href="{TG}" rel="noopener">{icon("telegram")}Czat na Telegramie</a>
      <a class="ico-link" href="{X_URL}" rel="noopener">{icon("x")}@21BitcoinPolska na X</a>
      <a class="ico-link" href="{NOSTR_ARMADA}" rel="noopener">{icon("nostr")}Społeczność na Nostrze (Armada)</a>
      <a class="ico-link" href="{NOSTR_URL}" rel="noopener">{icon("nostr")}Profil na Nostrze</a>
      <a href="{b('/dolacz-do-nas/#kontakt')}">Kontakt</a>
    </div>
    <div class="foot__col">
      <h2>Strona</h2>
      <a href="{b('/edukacja/')}">Edukacja: jak zacząć</a>
      <a href="{b('/artykuly/')}">Artykuły</a>
      <a href="{b('/zasady/')}">Zasady i sieć TwentyOne</a>
      <a href="{b('/slowniczek/')}">Słowniczek</a>
      <a href="{b('/bitcoin-whitepaper/')}">Whitepaper po polsku</a>
      <a href="https://github.com/itstomekk/dwadziesciajeden" rel="noopener">Kod strony na GitHubie</a>
    </div>
    <div class="foot__col">
      <h2>RSS</h2>
      <a class="ico-link" href="{b('/rss.xml')}">{icon("rss")}Kanał RSS</a>
      <p class="muted">Kronika i artykuły w Twoim czytniku. Bez zapisów i bez maili.</p>
      <p class="muted">Na bieżąco: <a href="{TG}" rel="noopener">Telegram</a>.</p>
    </div>
  </div>
  <p class="foot__fine">Nie udzielamy porad inwestycyjnych. Not your keys, not your coins.</p>
</footer>
<div class="search" id="search" hidden>
  <div class="search__box" role="dialog" aria-modal="true" aria-label="Szukaj">
    <input type="search" id="search-q" placeholder="Szukaj: artykuły, miasta, książki, projekty…" autocomplete="off">
    <ol class="search__res" id="search-res"></ol>
    <button class="search__close" type="button" data-search-close>Zamknij <kbd>Esc</kbd></button>
  </div>
</div>
<script src="{b('/assets/site.js')}?v={BUILT}" defer></script>
<script data-goatcounter="{GOATCOUNTER}" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""


def md_url(path):
    """Markdown twin URL for a page path, or None (only directory pages get twins)."""
    return path + "index.md" if path.endswith("/") else None


def md_alt(path):
    u = md_url(path)
    return f'<link rel="alternate" type="text/markdown" href="{b(u)}">\n' if u else ""


def jsonld(path):
    if path != "/":
        return ""
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{SITE_URL}/#org", "name": "Dwadzieścia Jeden",
         "alternateName": "21 Bitcoin Polska", "url": f"{SITE_URL}/", "logo": f"{SITE_URL}/assets/logo.jpg",
         "email": EMAIL, "description": "Polska społeczność Bitcoin Only, część sieci TwentyOne.",
         "sameAs": [X_URL, TG, "https://github.com/itstomekk/dwadziesciajeden", "https://twentyone.world/"]},
        {"@type": "WebSite", "@id": f"{SITE_URL}/#site", "url": f"{SITE_URL}/", "name": "Dwadzieścia Jeden",
         "inLanguage": "pl-PL", "publisher": {"@id": f"{SITE_URL}/#org"}}]}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'


class _MD(html.parser.HTMLParser):
    """Small HTML -> Markdown converter for the <main> of a page (stdlib only)."""
    SKIP = {"script", "style", "svg", "button", "iframe", "noscript", "form", "input"}
    BLOCK = {"p", "div", "section", "article", "header", "ul", "ol", "dl", "table", "figure", "blockquote", "nav", "li", "dt", "dd", "tr", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.href, self.li = [], 0, [], 0
        self.drop_tag, self.drop_depth = None, 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        if self.drop_tag:
            self.drop_depth += tag == self.drop_tag
            return
        cls = (a.get("class") or "").split()
        if a.get("aria-hidden") == "true" or {"shell", "dateline", "skip", "crumbs"} & set(cls):
            if tag not in ("img", "br", "input"):
                self.drop_tag, self.drop_depth = tag, 1
            return
        if tag in self.SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.out.append(" **" if self.li else "\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.li += 1
            self.out.append("\n- ")
        elif self.li and tag in self.BLOCK:
            self.out.append(" ")
        elif tag == "dt":
            self.out.append("\n\n**")
        elif tag == "dd":
            self.out.append("\n")
        elif tag in self.BLOCK:
            self.out.append("\n\n")
        elif tag in ("strong", "b"):
            self.out.append(" **")
        elif tag == "a":
            h = a.get("href") or ""
            if h.startswith("/"):
                h = SITE_URL + (h[len(BASE):] if BASE and h.startswith(BASE) else h)
            self.href.append(h)
            self.out.append("[")
        elif tag == "img" and a.get("alt"):
            self.out.append(f"Obraz: {a['alt']}")

    def handle_endtag(self, tag):
        if self.drop_tag:
            if tag == self.drop_tag:
                self.drop_depth -= 1
                if not self.drop_depth:
                    self.drop_tag = None
            return
        if tag in ("span", "small", "time", "em", "kbd", "code"):
            self.out.append(" ")
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "a" and self.href:
            h = self.href.pop()
            self.out.append(f"]({h})" if h and not h.startswith("#") else "]")
        elif tag in ("strong", "b"):
            self.out.append("** ")
        elif tag == "dt":
            self.out.append("**")
        elif tag == "li":
            self.li = max(0, self.li - 1)
            self.out.append("\n")
        elif self.li and re.fullmatch(r"h[1-6]", tag):
            self.out.append("** ")
        elif self.li and tag in self.BLOCK:
            self.out.append(" ")
        elif re.fullmatch(r"h[1-6]", tag) or tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip and not self.drop_tag:
            self.out.append(re.sub(r"\s+", " ", d))

    def md(self):
        t = "".join(self.out)
        t = re.sub(r"\[\s*\]\([^)]*\)", "", t)          # empty links (image-only)
        t = re.sub(r"\)\s*\[", ") · [", t)
        t = re.sub(r"\*\* +([\]),.:;!?])", r"**\1", t)
        t = re.sub(r"\[\s+", "[", t)
        t = re.sub(r"\s+\]", "]", t)
        t = re.sub(r"[ \t]{2,}", " ", t)
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"\n[ \t]+", "\n", t)
        t = re.sub(r"\n- \n", "\n- ", t)
        t = re.sub(r"\*\*\s*\*\*", "", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip() + "\n"


md_pages = []  # (path, title, description) for llms.txt


def write_twin(path, doc):
    u = md_url(path)
    m = re.search(r'<main id="tresc">(.*)</main>', doc, re.S)
    if not u or not m or 'name="robots" content="noindex' in doc:
        return
    title = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1))
    desc = (html.unescape(re.search(r'<meta name="description" content="(.*?)"', doc, re.S).group(1)).strip()).replace("\n", " ")
    p = _MD()
    p.feed(m.group(1))
    body = (f"---\ntitle: {title}\nurl: {SITE_URL}{path}\nlanguage: pl\n---\n\n"
            f"> {desc}\n\n" + p.md())
    (OUT / u.lstrip("/")).write_text(body, encoding="utf-8")
    desc = re.sub(r"\s*\*\s+", ", ", re.sub(r"\s+", " ", desc)).replace(":,", ":").replace(",,", ",")
    short = title.replace(" · Dwadzieścia Jeden", "")
    if desc.startswith("Dwadzieścia Jeden: polska społeczność bitcoinowych") and path != "/":
        desc = ""
    if len(desc) > 150:
        desc = desc[:150].rsplit(" ", 1)[0].rstrip(",.:;") + "…"
    md_pages.append((path, short, desc))


def write(path, doc):
    target = OUT / path.strip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    write_twin(path, doc)


def add_index(path, title, kind, text, tags=()):
    pages_index.append({"u": path, "t": title, "k": kind, "x": text[:1200], "g": list(tags)})


def page_head(kicker, title, lede=""):
    return (f'<header class="ph-head"><p class="kicker">{kicker}</p><h1>{e(title)}</h1>'
            + (f'<p class="lede">{lede}</p>' if lede else "") + "</header>")


def redirect(path, to):
    write(path, f'<!doctype html><meta charset="utf-8"><title>Przeniesiono</title>'
                f'<meta name="robots" content="noindex"><link rel="canonical" href="{SITE_URL}{to}">'
                f'<meta http-equiv="refresh" content="0; url={b(to)}"><p><a href="{b(to)}">Strona przeniesiona.</a></p>')


# ---------------------------------------------------------------- components

def post_card(p, compact=False):
    tag = p["tags"][0] if p["tags"] else ""
    return (f'<a class="post-card" href="{b("/" + p["slug"] + "/")}">'
            f'<span class="post-card__meta">{e(tag)}{" · " if tag else ""}{pl_date(p["published"])}</span>'
            f'<span class="post-card__title">{e(p["title"])}</span></a>')


def chronicle_item(en, show_images=True):
    imgs = ""
    if show_images and en.get("images"):
        imgs = '<div class="tl__imgs">' + "".join(
            f'<a href="{b("/assets/kronika/" + i["file"])}" class="tl__img"><img src="{b("/assets/kronika/" + i["file"])}" alt="{e(i["alt"])}" loading="lazy"></a>'
            for i in en["images"]) + "</div>"
    cls = " ".join("t-" + re.sub(r"[^a-z0-9]+", "-", t.lower()) for t in en.get("tags", []))
    return (f'<li class="tl__item {cls}" id="{chron_id(en)}"><time datetime="{en["date"]}">{pl_date(en["date"])}</time>'
            f'<div class="tl__body"><h3>{e(en["title"])}</h3><p>{e(en["text"])}</p>{imgs}'
            f'<p class="tl__links">{" · ".join(link(l) for l in en.get("links", []))}</p></div></li>')


def chron_id(en):
    """Stable anchor for a chronicle entry (used by the page, the home stages and the RSS feed)."""
    if "Standard Bitcoina" in en.get("tags", []) and en["date"] == "2025-10-31":
        return "standard-bitcoina"
    if "meetupy" in en.get("tags", []) and en["date"] == "2022-11-04":
        return "meetupy"
    return "k-" + en["date"] + "-" + slugify(en["title"])[:48].strip("-")


# Bitcoin mark (public-domain logo), drawn in the site amber; shown at ~5% behind every page.
BTC_MARK = ('<svg viewBox="0 0 64 64" focusable="false"><path fill="#F2A900" d="M63.04 39.741c-4.274 17.143-21.638 27.575-38.783 23.301C7.12 58.768-3.313 41.404.962 24.262 5.234 7.117 22.597-3.317 39.737.957c17.144 4.274 27.576 21.64 23.302 38.784z"/>'
            '<path fill="#fff" d="M46.11 27.441c.636-4.258-2.606-6.547-7.039-8.074l1.438-5.768-3.511-.875-1.4 5.616c-.923-.23-1.871-.447-2.813-.662l1.41-5.653-3.509-.875-1.439 5.766c-.764-.174-1.514-.346-2.242-.527l.004-.018-4.842-1.209-.934 3.75s2.605.597 2.55.634c1.422.355 1.679 1.296 1.636 2.042l-1.638 6.571c.098.025.225.061.365.117l-.371-.092-2.296 9.205c-.174.432-.615 1.08-1.609.834.035.051-2.552-.637-2.552-.637l-1.743 4.019 4.569 1.139c.85.213 1.683.436 2.503.646l-1.453 5.834 3.507.875 1.439-5.772c.958.26 1.888.5 2.798.726l-1.434 5.745 3.511.875 1.453-5.823c5.987 1.133 10.489.676 12.384-4.739 1.527-4.36-.076-6.875-3.226-8.515 2.294-.529 4.022-2.038 4.483-5.155zM38.087 38.69c-1.085 4.36-8.426 2.003-10.806 1.412l1.928-7.729c2.38.594 10.012 1.77 8.878 6.317zm1.086-11.312c-.99 3.966-7.1 1.951-9.082 1.457l1.748-7.01c1.982.494 8.365 1.416 7.334 5.553z"/></svg>')


# Stages of the community since the founding block; every claim is a kronika entry.
STAGES = [
    ("2021", "yellowpilled", "Grupa na Telegramie, pierwsze tłumaczenia (mempool.space, bitcoin-intro) i pierwsze piwo w Warszawie."),
    ("2022", "Dwadzieścia Jeden", "Dołączamy do sieci TwentyOne, startuje strona i pierwszy meetup w Warszawie, potem Wrocław i Śląsk."),
    ("2023", "Rośniemy", "Z naszej społeczności wyrasta Bitcoin FilmFest. Poznań, Trójmiasto, relay Nostr i Bitcoinowa Mapa Polski."),
    ("2024", "Edukacja", "Przedmiot o Bitcoinie na PJATK, Bitcoin w Polskim Radiu, BitcoinWalki w Poznaniu."),
    ("2025", "Standard Bitcoina", "Cotygodniowe BitcoinWalki w Warszawie i start zbiórki na książki dla Parlamentu."),
    ("2026", "Książki w Sejmie", "560 egzemplarzy „Standardu Bitcoina” trafia do posłów, senatorów i Prezydenta."),
]


def stages_html():
    items = "".join(f'<li><a href="{b("/kronika/#rok-" + y)}"><strong>{y}</strong><span class="stages__name">{e(n)}</span>'
                    f'<span class="stages__text">{e(t)}</span></a></li>' for y, n, t in STAGES)
    return (f'<section class="stages" aria-label="Etapy"><p class="kicker">Od bloku #{FOUNDING_BLOCK_TXT}, bez przerwy</p>'
            f'<ol class="stages__list">{items}</ol></section>')


YT_RE = re.compile(r"(?:youtube\.com/watch\?(?:.*&)?v=|youtu\.be/|youtube\.com/(?:embed|shorts|live)/)([A-Za-z0-9_-]{11})")


def yt_id(url):
    m = YT_RE.search(url or "")
    return m.group(1) if m else None


def yt_frame(vid, url, title):
    """Click-to-play YouTube: thumbnail first, the iframe (youtube-nocookie) only after a click (assets/site.js)."""
    return (f'<div class="video__frame" data-yt="{vid}"><a class="video__poster" href="{e(url)}" rel="noopener" aria-label="Odtwórz: {e(title)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy"><span class="video__play" aria-hidden="true"></span></a></div>')


def btcmap_embed(community=None, title="BTC Map"):
    src = (f"https://btcmap.org/communities/map?community={community}" if community
           else "https://btcmap.org/map#6/52.07/19.48")
    return (f'<div class="map-embed"><iframe title="{e(title)}" loading="lazy" allow="geolocation" allowfullscreen '
            f'src="{e(src)}"></iframe></div>')


def btcmap_app(city=None):
    """Own map of BTC Map places (snapshot content/btcmap-pl.json from tools/fetch_btcmap.py), drawn by assets/mapa.js."""
    scope = f"--miasto {e(city.lower())}" if city else "--kraj pl"
    legend = ('<div class="bmap__legend"><span><i style="background:var(--orange)"></i>potwierdzone w ostatnim roku</span>'
              '<span><i style="background:#E9D9A6"></i>1 do 2 lat temu</span><span><i style="background:#fff"></i>dawniej</span>'
              '<span><i style="background:var(--ink)"></i>kantor lub bankomat</span></div>')
    return (f'<link rel="stylesheet" href="{b("/assets/vendor/leaflet/leaflet.css")}">'
            f'<link rel="stylesheet" href="{b("/assets/vendor/markercluster/MarkerCluster.css")}">'
            f'<section class="bmap" data-bmap data-src="{b("/assets/btcmap-pl.json")}?v={BUILT}"'
            + (f' data-city="{e(city)}"' if city else "") + ' aria-label="Mapa miejsc, w których zapłacisz bitcoinem">'
            f'<div class="bmap__bar"><b>btcmap {scope}</b><span><strong data-count>…</strong> miejsc · dane BTC Map z <span data-fetched>…</span></span></div>'
            '<div class="bmap__tools"></div><div class="bmap__body"><div class="bmap__map"></div><div class="bmap__list" aria-live="polite">'
            '<noscript><p class="bmap__empty">Mapa potrzebuje JavaScriptu. Zobacz ją na <a href="https://btcmap.org/country/pl">btcmap.org</a>.</p></noscript>'
            f'</div></div>{legend}</section>'
            f'<script src="{b("/assets/vendor/leaflet/leaflet.js")}" defer></script>'
            f'<script src="{b("/assets/vendor/markercluster/leaflet.markercluster.js")}" defer></script>'
            f'<script src="{b("/assets/mapa.js")}?v={BUILT}" defer></script>')


# ---------------------------------------------------------------- pages

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    # CNAME follows the build mode: only a custom-domain build (DJ_BASE="" + non-github.io
    # DJ_SITE_URL) writes it, so a preview rebuild can never carry the domain by accident.
    cname = None
    if not BASE and "github.io" not in SITE_URL:
        cname = SITE_URL.split("://", 1)[-1].split("/", 1)[0]  # no trailing newline: matches the file GitHub's Pages UI writes
    OUT.mkdir()
    if cname:
        (OUT / "CNAME").write_text(cname)
    (OUT / ".nojekyll").write_text("")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy(ROOT / "content" / "btcmap-pl.json", OUT / "assets" / "btcmap-pl.json")

    imported = load("imported.json", []) + load("artykuly.json", [])
    by_slug = {r["slug"]: r for r in imported}
    kronika = load("kronika.json", {"entries": []})["entries"]
    projekty = load("projekty.json", {"projects": [], "intro": ""})
    biblioteka = load("biblioteka.json", None)
    inicjatywy = load("inicjatywy.json", None)
    zasady = load("zasady.json", None)
    slownik = load("slowniczek.json", {"terms": []})["terms"]
    miasta = load("miasta.json", {"cities": []})["cities"]

    posts = sorted([r for r in imported if r["kind"] == "post" and not r["tags"] == ["Miasta"]],
                   key=lambda r: r["published"], reverse=True)

    # kronika images -> tracked assets/kronika (copied from the private archive once)
    kdir = ROOT / "assets" / "kronika"
    kdir.mkdir(exist_ok=True)
    for en in kronika:
        for i in en.get("images", []):
            src = ROOT / "source-archive" / "x-media" / i["file"]
            if not (kdir / i["file"]).exists() and src.exists():
                shutil.copyfile(src, kdir / i["file"])
    shutil.copytree(kdir, OUT / "assets" / "kronika", dirs_exist_ok=True)

    # ---- home
    sb = by_slug["standard-bitcoina-w-polskim-parlamencie"]
    latest_k = sorted(kronika, key=lambda x: x["date"], reverse=True)[:4]
    sections = [
        ("Edukacja", "/edukacja/", "Czym jest Bitcoin, jak zacząć, jak nie dać się oszukać. Plus biblioteka: książki, strony i nagrania po polsku."),
        ("Mapa i miasta", "/bitcoinowa-mapa-polski/", "Gdzie zapłacisz bitcoinem i gdzie się spotykamy: Warszawa, Kraków, Poznań, Wrocław, Katowice."),
        ("Projekty", "/projekty/", "Nasze projekty, zaprzyjaźnieni, stowarzyszenia, wydarzenia i czaty: kto buduje Bitcoina w Polsce."),
        ("Kronika", "/kronika/", "Od yellowpilled w 2021 do książek w Sejmie."),
    ]
    home = f"""
<div class="dateline"><span>Warszawa · Kraków · Poznań · Wrocław · Katowice</span><span title="5 kwietnia 2021: zakładamy na Telegramie grupę yellowpilled">Bitcoin Only od bloku <b>#{FOUNDING_BLOCK_TXT}</b></span></div>
<section class="hero">
  <div class="hero__text">
    <p class="kicker">Polska społeczność Bitcoin Only · sieć&nbsp;TwentyOne</p>
    <h1 id="hero-title" data-phrases="{html.escape(json.dumps(HERO_PHRASES, ensure_ascii=False))}">Dwadzieścia<br>Jeden</h1>
    <script>(function(){{var h=document.getElementById("hero-title");try{{var l=JSON.parse(h.dataset.phrases),d=new Date(),n=Math.floor((d-d.getTimezoneOffset()*6e4)/864e5),p=l[n%l.length].split("|");h.textContent=p[0];if(p[1]){{h.appendChild(document.createElement("br"));h.appendChild(document.createTextNode(p[1]));}}}}catch(e){{}}}})();</script>
    <p class="lede">Bitcoinowi maksymaliści w Polsce. Tłumaczymy, spotykamy się, budujemy mapę miejsc i wnosimy Bitcoina tam, gdzie zapadają decyzje. Bez altcoinów, bez sprzedawania czegokolwiek.</p>
    <p class="cta-row"><a class="btn btn--primary" href="{TG}" rel="noopener">Dołącz do czatu na Telegramie</a><a class="btn btn--ghost" href="{b('/kim-jestesmy/')}">Kim jesteśmy</a></p>
  </div>
  <div class="shell">
    <div class="shell__bar"><span>~/dwadziesciajeden</span><span>bash</span></div>
    <pre class="shell__body"><span class="l"><i>$</i> whoami</span><span class="l o">dwadziescia_jeden: polska społeczność bitcoin only</span><span class="l"><i>$</i> cat zasady.txt</span><span class="l o">bitcoin only · zero altcoinów · nic nie sprzedajemy</span><span class="l"><i>$</i> bitcoin-cli getblockcount</span><span class="l o"><b class="tip" data-tip>…</b></span><span class="l"><i>$</i> ./dolacz.sh</span><span class="l o">→ <a href="{TG}" rel="noopener">t.me/dwadziesciajeden</a></span><span class="l"><i>$</i> <span class="cur" aria-hidden="true"></span></span></pre>
  </div>
</section>

<section class="facts" aria-label="W liczbach">
  <div><strong>2021</strong><span>start: grupa yellowpilled na Telegramie</span></div>
  <div><strong>560</strong><span>książek dla posłów i senatorów</span></div>
  <div><strong>5</strong><span>miast na naszej mapie</span></div>
  <div><strong>0</strong><span>altcoinów</span></div>
</section>

{stages_html()}

<section class="feature">
  <div class="feature__img"><img src="{b('/assets/media/images/2025/10/IMG_1260.png')}" alt="Grafika kampanii Standard Bitcoina w polskim Parlamencie" loading="lazy"></div>
  <div class="feature__text">
    <p class="kicker">Zrealizowany projekt</p>
    <h2>Standard Bitcoina w polskim Parlamencie</h2>
    <p>Zebraliśmy w bitcoinie środki na 560 egzemplarzy książki Saifedeana Ammousa. 8 stycznia 2026 trafiły z listem otwartym do każdego posła i senatora, a cztery dni później do Prezydenta RP. Zbiórkę wsparło 80 osób.</p>
    <p class="cta-row"><a class="btn btn--dark" href="{b('/bitcoin-w-parlamencie/')}">Przeczytaj całą historię</a><a class="link-arrow" href="{b('/kronika/')}">Przebieg w kronice</a></p>
  </div>
</section>

<section class="index-list" aria-label="Działy">
  {''.join(f'<a class="index-list__row" href="{b(u)}"><span class="index-list__name">{e(t)}</span><span class="index-list__line">{e(d)}</span><span class="index-list__arrow" aria-hidden="true">→</span></a>' for t, u, d in sections)}
</section>

<section class="join">
  <div class="join__in">
    <h2>Gdzie nas znaleźć</h2>
    <p>Na czacie rozmawiamy o bieżących sprawach, sprawdzamy memy przed publikacją, otwieramy kanały Lightning, organizujemy meetupy i ostrzegamy przed scamem.</p>
    <div class="join__grid">
      <a class="join__card join__card--main" href="{TG}" rel="noopener"><span>{icon("telegram")}Telegram · główny czat</span><strong>t.me/dwadziesciajeden</strong></a>
      <a class="join__card" href="{NOSTR_ARMADA}" rel="noopener"><span>{icon("nostr")}Nostr · społeczność na Armadzie</span><strong>Dwadzieścia Jeden na Armadzie</strong></a>
      <a class="join__card" href="{X_URL}" rel="noopener"><span>{icon("x")}X</span><strong>@21BitcoinPolska</strong></a>
      <div class="join__card join__card--nostr"><span class="npub">{icon("nostr")}Nostr <a href="{NOSTR_URL}" rel="noopener">profil</a><button class="copy-btn" type="button" data-copy="{NOSTR_NPUB}">Kopiuj</button></span><strong>{NOSTR_NPUB}</strong></div>
    </div>
    <p class="join__rules">Zanim dołączysz, przeczytaj <a href="{b('/zasady/')}">zasady społeczności</a>.</p>
  </div>
</section>

<section class="two-col">
  <div>
    <h2 class="sec-title">Artykuły</h2>
    <div class="post-list">{''.join(post_card(p) for p in posts[:5])}</div>
    <a class="link-arrow" href="{b('/artykuly/')}">Wszystkie artykuły</a>
  </div>
  <div>
    <h2 class="sec-title">Z kroniki</h2>
    <ol class="tl tl--mini">{''.join(chronicle_item(x, False) for x in latest_k)}</ol>
    <a class="link-arrow" href="{b('/kronika/')}">Cała kronika</a>
  </div>
</section>

<section class="network">
  <p class="kicker">Sieć TwentyOne</p>
  <p class="network__text">Dwadzieścia Jeden to polska gałąź sieci <a href="https://twentyone.world/" rel="noopener">TwentyOne</a>: niezależnych, lokalnych społeczności Bitcoin Only, które nazywają się „dwadzieścia jeden” we własnym języku. Einundzwanzig, Veintiuno, Huszonegy, Jednadvacet, Yirmibir i my.</p>
  <a class="link-arrow" href="{b('/zasady/')}">Jak działa sieć i nasze zasady</a>
</section>
"""
    write("/", layout("/", "Dwadzieścia Jeden", home, kind="home"))
    add_index("/", "Dwadzieścia Jeden: strona główna", "strona", text_of(home))

    # ---- imported posts
    for p in imported:
        if p["kind"] == "redirect":
            continue
        slug = p["slug"]
        if slug in ("projekty", "bitcoinowa-mapa-polski", "miasta", "warszawa", "krakow", "poznan"):
            continue  # custom pages below
        body_html = fill(p["html"])
        if slug == "kim-jestesmy":
            body_html = body_html.replace(f'<p><a href="{BASE}/autor/jesterhodl/">@JesterHodl</a></p>',
                                          f'<p class="byline">Tekst: <a href="{BASE}/autor/jesterhodl/">@JesterHodl</a></p>')
        is_post = p["kind"] == "post"
        meta = ""
        if is_post:
            tags = " ".join(f'<a class="tag" href="{b("/tag/" + slugify(t) + "/")}">{e(t)}</a>' for t in p["tags"])
            meta = f'<p class="post-meta">{tags}<time datetime="{p["published"]}">{pl_date(p["published"])}</time></p>'
        feat = ""
        if p.get("feature_image"):
            feat = f'<figure class="post-feature"><img src="{fill(p["feature_image"])}" alt="" loading="lazy"></figure>'
        archived = ""
        if p["origin"].startswith("wayback"):
            archived = (f'<p class="note">Wpis odtworzony z archiwum strony. <a href="{e(p["source"])}" rel="noopener">Kopia w Wayback Machine</a>.</p>')
        extra = ""
        if slug == "dolacz-do-nas":
            extra = join_extra()
        if slug == "standard-bitcoina-w-polskim-parlamencie":
            ks = [x for x in kronika if "Standard Bitcoina" in x.get("tags", [])]
            extra = ('<section class="prose-wide"><h2>Przebieg kampanii</h2><ol class="tl">'
                     + "".join(chronicle_item(x) for x in ks) + "</ol></section>")
        crumbs = [("Artykuły", "/artykuly/")] if is_post else None
        body = (f'<article class="article">{"<p class=kicker>" + e(p["tags"][0]) + "</p>" if is_post and p["tags"] else ""}'
                f'<h1>{e(p["title"])}</h1>{meta}{feat}<div class="prose">{body_html}</div>{archived}</article>{extra}')
        desc = p["excerpt"][:160] if p["excerpt"] else text_of(body_html)[:160]
        write(f"/{slug}/", layout(f"/{slug}/", p["title"], body, desc=desc, kind="post" if is_post else "page",
                                  og_image=fill(p["feature_image"]) if p.get("feature_image") else None, crumbs=crumbs))
        add_index(f"/{slug}/", p["title"], "artykuł" if is_post else "strona", text_of(body_html), p["tags"])

    # ---- artykuły + tags + author
    write("/artykuly/", layout("/artykuly/", "Artykuły",
                              page_head("Archiwum", "Artykuły", "Wszystkie wpisy z dwadziesciajeden.pl, także te odtworzone z archiwum.")
                              + '<div class="post-list post-list--wide">' + "".join(post_card(p) for p in posts) + "</div>"))
    add_index("/artykuly/", "Artykuły", "strona", " ".join(p["title"] for p in posts))
    tag_desc = {
        "Artykuły": "Teksty o Bitcoinie, bezpieczeństwie i pieniądzu.",
        "Zbiórki": "Nasze zbiórki w bitcoinie.",
        "Meetupy": "Oto koordynaty czasoprzestrzenne naszych meetupów w przestrzeni fizycznej.",
        "Zasoby": "Materiały do pobrania.",
        "Miasta": "Strony miast, w których się spotykamy.",
    }
    all_tagged = [r for r in imported if r["kind"] in ("post", "page")]
    for tag in tag_desc:
        items = sorted([r for r in all_tagged if tag in r["tags"]], key=lambda r: r["published"], reverse=True)
        extra = ""
        if tag == "Miasta":
            items = []
            extra = city_grid(miasta)
        write(f"/tag/{slugify(tag)}/", layout(f"/tag/{slugify(tag)}/", tag,
                                             page_head("Tag", tag, tag_desc[tag])
                                             + ('<div class="post-list post-list--wide">' + "".join(post_card(p) for p in items) + "</div>" if items else "")
                                             + extra))
    author_posts = [r for r in posts if r["origin"].startswith("ghost")] + [by_slug["zbieramy-satki-na-wosp"]]
    write("/autor/jesterhodl/", layout("/autor/jesterhodl/", "JesterHodl",
                                       page_head("Autor", "JesterHodl", 'Współtwórca Dwadzieścia Jeden. Pisze na <a href="https://jesterhodl.com/" rel="noopener">jesterhodl.com</a>.')
                                       + '<div class="post-list post-list--wide">' + "".join(post_card(p) for p in author_posts) + "</div>"))
    redirect("/author/jesterhodl/", "/autor/jesterhodl/")
    redirect("/mapa/", "/bitcoinowa-mapa-polski/")
    redirect("/meetupy/", "/bitcoinowa-mapa-polski/#miasta")
    redirect("/miasta/", "/bitcoinowa-mapa-polski/#miasta")
    redirect("/polskie-projekty/", "/projekty/")
    redirect("/inicjatywy/", "/projekty/")

    # ---- miasta
    old_intro = fill(by_slug["miasta"]["html"])
    old_intro = re.sub(r"<p>Poniżej znajdziesz strony wg miast:</p><ul>.*?</ul>", "", old_intro, flags=re.S)
    meetupy_old = by_slug.get("meetupy")
    miasta_section = (f'<section class="cat" id="miasta"><h2 class="sec-title">Miasta</h2><div class="cat__intro prose">{old_intro}</div></section>'
                      + city_grid(miasta))
    for c in miasta:
        if c["slug"] in by_slug:
            h = fill(by_slug[c["slug"]]["html"])
            h = h.replace("dwadzieścia-jeden-poznań", "dwadzie%C5%9Bcia-jeden-pozna%C5%84")
            # dead bitcoinwalk.org city page (404 on 2026-10-23)
            h = re.sub(r'<h3 id="bitcoinwalk">BitcoinWalk</h3><a class="link-card" href="https://bitcoinwalk\.org/poznan/".*?</a>',
                       '<h3 id="bitcoinwalk">BitcoinWalk</h3><p>Formuła spacerów pochodzi z <a href="https://bitcoinwalk.org/" rel="noopener">bitcoinwalk.org</a>. Terminy publikujemy na Meetup, Telegramie i X.</p>', h, flags=re.S)
            if c["slug"] == "krakow":
                # meetup.com/krakow-bitcoin-meetup returns "Group not found" (checked 2026-10-23)
                h = re.sub(r'<a class="link-card" href="https://www\.meetup\.com/pl-PL/krakow-bitcoin-meetup/".*?</a>',
                           '<p class="note">Grupa Kraków Bitcoin Meetup na meetup.com nie jest już dostępna. Krakowskie spotkania ogłaszamy na <a href="https://t.me/dwadziesciajeden" rel="noopener">czacie</a> i na X.</p>', h, flags=re.S)
                h += ('<h3>Z archiwum</h3><ul><li><a href="https://x.com/21BitcoinPolska/status/1794694392374342098" rel="noopener">„Dla kogo jest Bitcoin, kiedy i jak go kupić?”, Techies, maj 2024</a></li>'
                      '<li><a href="https://x.com/21BitcoinPolska/status/1919430740485304721" rel="noopener">Meetup w Krakowie, 9 maja 2025</a></li></ul>')
            if c["slug"] == "poznan":
                h = h.replace('<h3 id="meetup">', '<h3 id="stale">Stałe spotkania</h3><div class="regulars">'
                              '<a class="regular" href="https://www.meetup.com/poz21m/" rel="noopener"><span class="regular__when">Spacery, terminy na Meetup</span><strong>Poznań BitcoinWalk · Spacery ku wolności</strong><span>Spacer i rozmowa o Bitcoinie. Zbiórka zwykle przy Skwerze Jana Suwarta, ul. Ewangelicka. Latem także grill i spacery nad Rusałką.</span></a>'
                              '<a class="regular" href="https://t.me/DwadziesciaJedenPoznan" rel="noopener"><span class="regular__when">Na bieżąco</span><strong>Dwadzieścia Jeden Poznań</strong><span>Poznańska grupa na Telegramie. Tu ogłaszamy spacery i spotkania.</span></a>'
                              '</div><p class="note">Terminy i miejsca mogą się zmienić. Zawsze sprawdź wydarzenie przed wyjściem.</p><h3 id="meetup">', 1)
                h = h.replace('https://www.meetup.com/pl-PL/pozna%C5%84-bitcoinwalk/', 'https://www.meetup.com/poz21m/').replace('Poznań BitcoinWalk | Meetup', 'Spacery ku wolności (Poznań BitcoinWalk) | Meetup')
            if c["slug"] == "warszawa":
                h = h.replace('<h3 id="meetup">', '<h3 id="stale">Stałe spotkania</h3><div class="regulars">'
                              '<a class="regular" href="https://bitcoinwalk.org/warszawa" rel="noopener"><span class="regular__when">Soboty, 11:30</span><strong>BitcoinWalk Warszawa</strong><span>Spacer i rozmowa o Bitcoinie. Zbiórka: Ogród Saski, Fontanna Wielka. Także po angielsku.</span></a>'
                              '<a class="regular" href="https://www.meetup.com/bitcoin-warsaw/" rel="noopener"><span class="regular__when">Poniedziałki, 18:00</span><strong>Bitcoin Café · Bitcoin Warsaw</strong><span>Spotkanie w małych grupach, bez prezentacji: przychodzisz z pytaniami. Miejsce w wydarzeniu na Meetup.</span></a>'
                              '</div><p class="note">Terminy i miejsca mogą się zmienić. Zawsze sprawdź wydarzenie przed wyjściem.</p><h3 id="meetup">', 1)
                h = h.replace('<h3 id="btcmap">', '<h3>Z archiwum</h3><ul>'
                              f'<li><a href="{BASE}/meetup-w-warszawie-4-xi-2022/">Meetup, 4 XI 2022</a></li>'
                              f'<li><a href="{BASE}/meetup-w-warszawie-2-xii-2022/">Meetup, 2 XII 2022</a></li>'
                              f'<li><a href="{BASE}/meetup-w-warszawie-17-ii-2023/">Meetup w BarBazaar, 17 II 2023</a></li>'
                              f'<li><a href="{BASE}/kronika/">Pozostałe spotkania w kronice</a></li></ul><h3 id="btcmap">', 1)
            pub = by_slug[c["slug"]]["published"]
        else:
            h = fill(c["html"])
            pub = None
        # own BTC Map view for the city, replacing the btcmap.org community iframe
        h = re.sub(r'<h3 id="btcmap">[^<]*</h3>\s*<div class="map-embed">.*?</div>', "", h, flags=re.S)
        h += f'<h3 id="btcmap">Gdzie zapłacisz bitcoinem: {e(c["name"])}</h3>' + btcmap_app(c["name"])
        if c.get("btcmap"):
            h += (f'<p class="note">Społeczność {e(c["name"])} na BTC Map: '
                  f'<a href="https://btcmap.org/community/{e(c["btcmap"])}" rel="noopener">btcmap.org/community/{e(c["btcmap"])}</a>.</p>')
        body = (f'<article class="article"><p class="kicker">Miasto</p><h1>{e(c["name"])}</h1>'
                f'<div class="prose">{h}</div></article>')
        write(f"/{c['slug']}/", layout(f"/{c['slug']}/", c["name"], body, desc=c["line"], crumbs=[("Mapa i miasta", "/bitcoinowa-mapa-polski/#miasta")]))
        add_index(f"/{c['slug']}/", c["name"], "miasto", text_of(h), ["Miasta"])

    # ---- mapa
    m = fill(by_slug["bitcoinowa-mapa-polski"]["html"])
    m = re.sub(r'<div class="map-embed">.*?</div>', lambda _: btcmap_app(None), m, flags=re.S)
    m = m.replace('href="https://btcmap.org/community/dwadzie%C5%9Bcia-jeden"', 'href="https://btcmap.org/country/pl"')
    city_maps = "".join(
        f'<li><a href="https://btcmap.org/community/{e(c["btcmap"])}" rel="noopener">{e(c["name"])}</a></li>'
        for c in miasta if c.get("btcmap"))
    m += (f'<h2>Społeczności miast na BTC Map</h2><ul class="city-maps">{city_maps}</ul>'
          f'<h2>Jak pomóc</h2><ol><li>Otwórz miejsce na <a href="https://btcmap.org/country/pl" rel="noopener">btcmap.org/country/pl</a>.</li>'
          f'<li>Byłeś tam niedawno i zapłaciłeś bitcoinem? Potwierdź je jednym kliknięciem.</li>'
          f'<li>Nowe miejsce dodasz przez formularz BTC Map albo bezpośrednio w OpenStreetMap.</li>'
          f'<li>Daj znać na <a href="{TG}" rel="noopener">czacie</a>, żebyśmy mogli pochwalić się nowym miejscem.</li></ol>')
    body = (f'<article class="article"><p class="kicker">Mapa i miasta</p><h1>Bitcoinowa Mapa Polski</h1>'
            f'<p class="lede">Gdzie w Polsce zapłacisz bitcoinem i gdzie się spotykamy. <a href="#miasta">Przejdź do miast</a>.</p>'
            f'<div class="prose">{m}</div></article>' + miasta_section)
    write("/bitcoinowa-mapa-polski/", layout("/bitcoinowa-mapa-polski/", "Bitcoinowa Mapa Polski", body,
                                             desc="Miejsca w Polsce, w których zapłacisz bitcoinem. Mapa BTC Map prowadzona przez społeczność."))
    add_index("/bitcoinowa-mapa-polski/", "Bitcoinowa Mapa Polski", "strona", text_of(m))

    # ---- projekty + inicjatywy (one page)
    def proj_card(pr):
        img = (f'<img src="{b("/assets/" + pr["image"])}" alt="{e(pr.get("image_alt", ""))}" loading="lazy">' if pr.get("image") else
               f'<span class="proj__mono" aria-hidden="true">{e(pr["name"][:1])}</span>')
        vids = [(yt_id(l.get("url", "")), l) for l in pr["links"]]
        vids = "".join(f'<figure class="video">{yt_frame(v, l["url"], l.get("label", pr["name"]))}</figure>' for v, l in vids if v)
        return (f'<article class="proj proj--{pr["kind"]}" id="{pr["id"]}"><div class="proj__img">{img}</div>'
                f'<div class="proj__body"><p class="proj__status">{e(pr["status"])}{" · nasz projekt" if pr["kind"] == "ours" else " · zaprzyjaźnieni"}</p>'
                f'<h2>{e(pr["name"])}</h2><p>{e(pr["text"])}</p>{vids}<p class="proj__links">{" · ".join(link(l) for l in pr["links"])}</p></div></article>')
    groups = [("nasze", "Nasze projekty", [p for p in projekty["projects"] if p["kind"] == "ours"]),
              ("zaprzyjaznieni", "Zaprzyjaźnieni", [p for p in projekty["projects"] if p["kind"] != "ours"])]
    cats = (inicjatywy or {}).get("categories", [])
    body = (page_head("Co robimy", "Projekty i inicjatywy", e(projekty["intro"]).replace("Napisz do nas.", f'<a href="{b("/dolacz-do-nas/")}">Napisz do nas.</a>'))
            + '<nav class="toc" aria-label="Spis">' + "".join(f'<a href="#{gid}">{e(t)}</a>' for gid, t, _ in groups)
            + "".join(f'<a href="#{c["id"]}">{e(c["title"])}</a>' for c in cats) + "</nav>")
    for gid, t, items in groups:
        body += f'<section class="cat" id="{gid}"><h2 class="sec-title">{e(t)}</h2><div class="proj-list">' + "".join(proj_card(p) for p in items) + "</div></section>"
    for c in cats:
        body += f'<section class="cat" id="{c["id"]}"><h2 class="sec-title">{e(c["title"])}</h2>'
        if c.get("intro"):
            body += f'<p class="cat__intro">{e(c["intro"])}</p>'
        body += '<div class="ini-grid">' + "".join(ini_card(i) for i in c["items"]) + "</div></section>"
        for i in c["items"]:
            add_index(f"/projekty/#{c['id']}", i["title"], "inicjatywa", i.get("description_pl", ""))
    if inicjatywy and inicjatywy.get("checked"):
        body += f'<p class="note proj-note">Linki sprawdzone {pl_date(inicjatywy["checked"])}. Grafiki pochodzą ze stron projektów. Brakuje czegoś? Napisz na <a href="{TG}" rel="noopener">czacie</a>.</p>'
    write("/projekty/", layout("/projekty/", "Projekty i inicjatywy", body, desc="Projekty społeczności Dwadzieścia Jeden, zaprzyjaźnieni i polskie inicjatywy bitcoinowe."))
    add_index("/projekty/", "Projekty i inicjatywy", "strona", "projekty inicjatywy stowarzyszenia wydarzenia czaty")
    for pr in projekty["projects"]:
        add_index(f"/projekty/#{pr['id']}", pr["name"], "projekt", pr["text"])

    # ---- biblioteka now lives inside /edukacja/
    redirect("/biblioteka/", "/edukacja/#biblioteka")

    # ---- kronika
    ks = sorted(kronika, key=lambda x: x["date"], reverse=True)
    years = sorted({k["date"][:4] for k in ks}, reverse=True)
    filters = ["wszystko", "meetupy", "społeczność", "edukacja", "technologia", "Standard Bitcoina", "zbiórki", "Bitcoin FilmFest"]
    fbar = "".join(f'<button type="button" data-filter="{"" if f == "wszystko" else "t-" + re.sub(r"[^a-z0-9]+", "-", f.lower())}"'
                   f'{" aria-pressed=true" if f == "wszystko" else " aria-pressed=false"}>{e(f)}</button>' for f in filters)
    blocks = ""
    for y in years:
        blocks += f'<h2 class="tl-year" id="rok-{y}">{y}</h2><ol class="tl">' + "".join(chronicle_item(x) for x in ks if x["date"][:4] == y) + "</ol>"
    gallery = [(x, i) for x in ks for i in x.get("images", [])]
    body = (page_head("Od 2021", "Kronika",
                      f'Najważniejsze momenty społeczności: ze starej strony, z naszego konta na X i z czatu na Telegramie (bez nazwisk i cytatów). Zdjęcia: <a href="{X_URL}" rel="noopener">@21BitcoinPolska</a>, każde podpięte pod swój post.')
            + f'<div class="filters" role="group" aria-label="Filtruj">{fbar}</div><div class="tl-wrap">{blocks}</div>'
            + '<section class="gallery"><h2 class="sec-title">Zdjęcia</h2><div class="gallery__grid">'
            + "".join(f'<figure><a href="{b("/assets/kronika/" + i["file"])}"><img src="{b("/assets/kronika/" + i["file"])}" alt="{e(i["alt"])}" loading="lazy"></a>'
                      f'<figcaption>{pl_date(x["date"])} · <a href="{e(x["links"][0].get("url", b(x["links"][0].get("internal", "/"))))}" rel="noopener">źródło</a></figcaption></figure>'
                      for x, i in gallery)
            + "</div></section>")
    write("/kronika/", layout("/kronika/", "Kronika", body, desc="Kronika społeczności Dwadzieścia Jeden: meetupy, zbiórki, kampanie."))
    for x in ks:
        add_index("/kronika/", f'{x["title"]} ({pl_date(x["date"])})', "kronika", x["text"], x.get("tags", []))

    # ---- zasady
    build_edukacja(biblioteka)
    build_zasady(zasady)
    build_bujac(load("bujac.json"))

    # ---- słowniczek
    dl = "".join(f'<div class="term" id="{slugify(t["term"])}"><dt>{e(t["term"])}</dt><dd>{e(t["def"])}</dd></div>' for t in slownik)
    write("/slowniczek/", layout("/slowniczek/", "Słowniczek",
                                 page_head("Pojęcia", "Słowniczek", "Słowa, które padają u nas najczęściej, wyjaśnione po ludzku.")
                                 + f'<dl class="glossary">{dl}</dl>'))
    for t in slownik:
        add_index(f"/slowniczek/#{slugify(t['term'])}", t["term"], "pojęcie", t["def"])

    # ---- 404, robots, sitemap, search index
    (OUT / "404.html").write_text(layout("/404.html", "Nie ma takiej strony",
                                         page_head("404", "Nie ma takiej strony", f'Spróbuj wyszukiwarki albo wróć na <a href="{b("/")}">stronę główną</a>.')),
                                  encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n" if NOINDEX else
                                    "# Content signals: search and AI answers may use this site; AI training may not (owner 2026-10-26).\n"
                                    "User-agent: *\nContent-Signal: search=yes, ai-input=yes, ai-train=no\nAllow: /\n\n"
                                    "# Crawlers that collect training data\n"
                                    + "".join(f"User-agent: {bot}\n" for bot in AI_TRAIN_BOTS) + "Disallow: /\n\n"
                                    f"Sitemap: {SITE_URL}/sitemap.xml\n# AI index: {SITE_URL}/llms.txt\n")
    if not NOINDEX:
        write_llms()
        (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    urls = sorted({p["u"].split("#")[0] for p in pages_index})
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                     + "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    write_rss(posts, kronika)
    (OUT / "search.json").write_text(json.dumps(pages_index, ensure_ascii=False), encoding="utf-8")
    print(f"twins: {len(md_pages)} markdown pages")
    print(f"built {len(list(OUT.rglob('index.html')))} pages, {len(pages_index)} search records, base='{BASE}', noindex={NOINDEX}")


def write_rss(posts, kronika):
    """/rss.xml: articles + chronicle entries, newest first (replaces the newsletter placeholder)."""
    from email.utils import format_datetime
    from datetime import datetime, timezone
    def when(d):
        y, m, dd = (int(x) for x in d[:10].split("-"))
        return format_datetime(datetime(y, m, dd, 12, 0, tzinfo=timezone.utc))
    items = [(p["published"], p["title"], f'{SITE_URL}/{p["slug"]}/', p.get("excerpt", ""), "Artykuły") for p in posts]
    items += [(k["date"], k["title"], f'{SITE_URL}/kronika/#{chron_id(k)}', k["text"], "Kronika") for k in kronika]
    items.sort(key=lambda x: x[0], reverse=True)
    x = html.escape
    body = "".join(f"<item><title>{x(t)}</title><link>{x(u)}</link><guid isPermaLink=\"true\">{x(u)}</guid>"
                   f"<pubDate>{when(d)}</pubDate><category>{c}</category><description>{x(s)}</description></item>\n"
                   for d, t, u, s, c in items[:60])
    (OUT / "rss.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
        f"<title>Dwadzieścia Jeden: kronika i artykuły</title><link>{SITE_URL}/</link>"
        f'<atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>'
        "<description>Polska społeczność Bitcoin Only: nowe wpisy w kronice i artykuły.</description><language>pl</language>"
        f"<lastBuildDate>{when(items[0][0])}</lastBuildDate>\n{body}</channel></rss>\n", encoding="utf-8")


LLMS_SECTIONS = [
    ("O społeczności", ["/", "/kim-jestesmy/", "/zasady/", "/dolacz-do-nas/", "/kronika/"]),
    ("Edukacja", ["/edukacja/", "/slowniczek/", "/bitcoin-whitepaper/", "/bujac/", "/artykuly/"]),
    ("Miasta, meetupy i projekty", ["/bitcoinowa-mapa-polski/", "/warszawa/", "/krakow/", "/poznan/", "/wroclaw/", "/katowice/", "/projekty/", "/bitcoin-w-parlamencie/"]),
]


def write_llms():
    """llms.txt (index of Markdown twins) and llms-full.txt (all twins in one file)."""
    known = {p: (t, d) for p, t, d in md_pages}
    used, lines = set(), ["# Dwadzieścia Jeden", "",
                          "> Polska społeczność Bitcoin Only (21 Bitcoin Polska), część międzynarodowej sieci TwentyOne. "
                          "Meetupy w polskich miastach, edukacja o Bitcoinie, tłumaczenia, projekty społeczności i kronika od 2021 roku. "
                          "Edukacja, nie porady inwestycyjne.", "",
                          f"Każda strona ma wersję Markdown pod adresem `<strona>/index.md`. Pełna treść w jednym pliku: {SITE_URL}/llms-full.txt", ""]
    for name, paths in LLMS_SECTIONS:
        lines.append(f"## {name}\n")
        for p in paths:
            if p in known:
                used.add(p)
                t, d = known[p]
                lines.append(f"- [{t}]({SITE_URL}{md_url(p)})" + (f": {d}" if d else ""))
        lines.append("")
    rest = [p for p, *_ in md_pages if p not in used]
    if rest:
        lines.append("## Optional\n")
        for p in sorted(rest):
            t, d = known[p]
            lines.append(f"- [{t}]({SITE_URL}{md_url(p)})" + (f": {d}" if d else ""))
        lines.append("")
    lines.append("## Kontakt\n")
    lines.append(f"- Telegram: {TG}\n- X: {X_URL}\n- E-mail: {EMAIL}\n")
    (OUT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    order = [p for _, ps in LLMS_SECTIONS for p in ps if p in known] + sorted(rest)
    full = "\n\n---\n\n".join((OUT / md_url(p).lstrip("/")).read_text(encoding="utf-8") for p in order)
    (OUT / "llms-full.txt").write_text(full, encoding="utf-8")


def slugify(s):
    tr = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
    return re.sub(r"[^a-z0-9]+", "-", s.translate(tr).lower()).strip("-")


def city_grid(miasta):
    return '<div class="cities">' + "".join(
        f'<a class="city" data-slug="{e(c["slug"])}" href="{b("/" + c["slug"] + "/")}"><span class="city__name">{e(c["name"])}</span><span class="city__line">{e(c["line"])}</span></a>'
        for c in miasta) + "</div>"


def join_extra():
    return f"""<section class="prose-wide">
<h2>Zanim napiszesz pierwszą wiadomość</h2>
<p>Jesteśmy społecznością Bitcoin Only. Na czacie nie promujemy altcoinów, tokenów ani „okazji inwestycyjnych”, nie wysyłamy linków polecających bez kontekstu i nie prosimy nikogo o seed. Pełne zasady: <a href="{b('/zasady/')}">Zasady społeczności</a>.</p>
</section>"""


def catalog_html(path, label, data, whitepaper=False):
    body = ""
    if whitepaper:
        body += (f'<section class="wp-strip"><div><p class="kicker">Zacznij tutaj</p><h2>Bitcoin: Elektroniczny System Pieniężny Typu Peer-to-Peer</h2>'
                 f'<p>Biała księga Satoshiego Nakamoto w tłumaczeniu Damiana Mee. Dziewięć stron, od których wszystko się zaczęło.</p></div>'
                 f'<p class="cta-row"><a class="btn btn--primary" href="{b("/assets/media/files/2023/02/bitcoin_pl.pdf")}" download>Pobierz PDF po polsku</a>'
                 f'<a class="btn btn--ghost" href="{b("/bitcoin-whitepaper/")}">Oryginał i więcej</a></p></section>')
    if not data:
        return body + '<p class="ph-block" data-placeholder="catalog">Katalog w przygotowaniu.</p>'
    cats = data["categories"]
    body += '<nav class="toc" aria-label="Spis biblioteki">' + "".join(f'<a href="#{c["id"]}">{e(c["title"])}</a>' for c in cats) + "</nav>"
    for c in cats:
        body += f'<section class="cat" id="{c["id"]}"><h3 class="sec-title">{e(c["title"])}</h3>'
        if c.get("intro"):
            body += f'<p class="cat__intro">{e(c["intro"])}</p>'
        if c.get("layout") == "books":
            body += '<div class="books">' + "".join(book_card(i) for i in c["items"]) + "</div>"
        else:
            body += '<div class="res-list">' + "".join(res_row(i) for i in c["items"]) + "</div>"
        body += "</section>"
        for i in c["items"]:
            add_index(f"{path}#{c['id']}", i["title"], label, (i.get("author", "") + " " + i.get("description_pl", "")).strip())
    if data.get("checked"):
        body += f'<p class="note proj-note">Linki sprawdzone {pl_date(data["checked"])}. Brakuje czegoś? Napisz na <a href="{TG}" rel="noopener">czacie</a>.</p>'
    return body


def book_card(i):
    img = (f'<img src="{e(i["image_local"])}" alt="Okładka: {e(i["title"])}" loading="lazy">' if i.get("image_local")
           else f'<span class="book__ph" aria-hidden="true">{e(i["title"])}</span>')
    img = img.replace("{B}", BASE)
    return (f'<a class="book" href="{e(i["url"])}" rel="noopener"><span class="book__cover">{img}</span>'
            f'<span class="book__author">{e(i.get("author", ""))}</span><span class="book__title">{e(i["title"])}</span>'
            f'<span class="book__desc">{e(i.get("description_pl", ""))}</span>'
            f'<span class="book__pub">{e(i.get("publisher", ""))}</span></a>')


def ini_card(i):
    meta = " · ".join(x for x in [i.get("type_label", ""), i.get("author", "")] if x)
    host = re.sub(r"^https?://(www\.)?", "", i["url"]).split("/")[0]
    img = f'<img src="{b("/assets/" + i["image"])}" alt="" loading="lazy">' if i.get("image") else ""
    vid = yt_id(i["url"])
    if vid:
        return (f'<div class="ini ini--video">{yt_frame(vid, i["url"], i["title"])}'
                f'<span class="ini__body"><span class="res__meta">{e(meta)}</span><a class="ini__title" href="{e(i["url"])}" rel="noopener">{e(i["title"])}</a>'
                f'<span class="res__desc">{e(i.get("description_pl", ""))}</span><span class="res__host">youtube.com</span></span></div>')
    return (f'<a class="ini" href="{e(i["url"])}" rel="noopener"><span class="ini__img">{img}</span>'
            f'<span class="ini__body"><span class="res__meta">{e(meta)}</span><span class="ini__title">{e(i["title"])}</span>'
            f'<span class="res__desc">{e(i.get("description_pl", ""))}</span><span class="res__host">{e(host)}</span></span></a>')


def res_row(i):
    meta = " · ".join(x for x in [i.get("type_label", ""), i.get("author", "")] if x)
    internal = i["url"].startswith("{B}")
    i = dict(i, url=fill(i["url"]))
    host = "dwadziesciajeden.pl" if internal else re.sub(r"^https?://(www\.)?", "", i["url"]).split("/")[0]
    vid = yt_id(i["url"])
    if vid:
        return (f'<div class="res res--video">{yt_frame(vid, i["url"], i["title"])}<span class="res__meta">{e(meta)}</span>'
                f'<a class="res__title" href="{e(i["url"])}" rel="noopener">{e(i["title"])}</a>'
                f'<span class="res__desc">{e(i.get("description_pl", ""))}</span><span class="res__host">youtube.com</span></div>')
    return (f'<a class="res" href="{e(i["url"])}" rel="noopener"><span class="res__meta">{e(meta)}</span>'
            f'<span class="res__title">{e(i["title"])}</span><span class="res__desc">{e(i.get("description_pl", ""))}</span>'
            f'<span class="res__host">{e(host)}</span></a>')



def build_edukacja(biblioteka):
    steps = [
        ("Zrozum, zanim kupisz", f'Zacznij od <a href="{b("/bitcoin-whitepaper/")}">whitepaperu po polsku</a> (dziewięć stron) i „Standardu Bitcoina”. Więcej w <a href="#biblioteka">bibliotece</a> niżej.'),
        ("Zacznij od małej kwoty", "Kupuj tylko tyle, ile możesz spokojnie trzymać latami i czego utrata nie zrujnuje Ci życia. To nie jest porada inwestycyjna, tylko zdrowy rozsądek."),
        ("Weź klucze do siebie", "Wypłać bitcoiny z giełdy do portfela, w którym to Ty masz frazę odzyskiwania (seed). Not your keys, not your coins."),
        ("Zabezpiecz frazę odzyskiwania", "Zapisz ją offline: na papierze albo na stali. Nigdy zdjęcie, chmura ani menedżer haseł. Nikomu jej nie podawaj."),
        ("Używaj", f'Zapłać bitcoinem przez Lightning, znajdź miejsca na <a href="{b("/bitcoinowa-mapa-polski/")}">mapie</a>, przyjmuj satsy za swoją pracę.'),
        ("Weryfikuj sam", "Uruchom własny węzeł, na przykład Bitcoin Core. Wtedy nie musisz nikomu wierzyć na słowo: don’t trust, verify."),
    ]
    scams = [
        "Nikt z nas nie napisze do Ciebie pierwszy w prywatnej wiadomości z ofertą albo „pomocą”.",
        "Nikt nie potrzebuje Twojej frazy odzyskiwania: ani support, ani admin, ani doradca.",
        "Obietnica stałego zysku, podwojenia środków albo gwarantowanego wyniku to oszustwo.",
        "Nowa moneta „lepsza od Bitcoina” to zwykle sposób, żeby ktoś zarobił na Tobie.",
        f'Masz wątpliwość? Zapytaj na <a href="{TG}" rel="noopener">czacie</a>, zanim klikniesz albo coś wyślesz.',
    ]
    body = page_head("Misja i edukacja", "Edukacja",
                     "Nasza misja jest prosta: żeby każdy w Polsce mógł zrozumieć Bitcoina po polsku i używać go samodzielnie. "
                     "Nie sprzedajemy kursów, sygnałów ani tokenów. Tłumaczymy, odpowiadamy na pytania i spotykamy się na żywo.")
    body += ('<nav class="toc" aria-label="Na tej stronie"><a href="#podstawy">Czym jest Bitcoin</a><a href="#jak-zaczac">Jak zacząć</a>'
             '<a href="#oszustwa">Uważaj na oszustów</a><a href="#biblioteka">Biblioteka</a></nav>')
    body += ('<section class="mission"><div><strong>Tłumaczymy</strong><span>Whitepaper, Bitcoin Core, SeedSigner i teksty, które warto znać, po polsku.</span></div>'
             f'<div><strong>Spotykamy się</strong><span>Meetupy i BitcoinWalki w pięciu miastach. <a href="{b("/bitcoinowa-mapa-polski/#miasta")}">Zobacz miasta</a>.</span></div>'
             f'<div><strong>Wnosimy Bitcoina tam, gdzie zapadają decyzje</strong><span>560 egzemplarzy „Standardu Bitcoina” w Sejmie i Senacie. <a href="{b("/bitcoin-w-parlamencie/")}">Historia akcji</a>.</span></div></section>')
    body += ('<section class="prose-wide" id="podstawy"><h2>Czym jest Bitcoin</h2>'
             '<p>Bitcoin to pieniądz i sieć płatności bez banku centralnego, bez prezesa i bez możliwości dodruku. Zasady są zapisane w otwartym kodzie, a pilnują ich tysiące niezależnych węzłów na całym świecie.</p>'
             '<p>Bitcoinów nigdy nie będzie więcej niż 21 milionów. Nowe bloki z transakcjami powstają średnio co dziesięć minut, a każdy z nich zabezpiecza praca górników (proof of work). Cofnięcie potwierdzonej historii jest praktycznie niemożliwe.</p>'
             '<p>Bitcoin nie ma konta, które ktoś może zamrozić. Masz klucze, masz bitcoiny. Dlatego najważniejsza lekcja to samodzielne przechowywanie.</p>'
             '<h2>Dlaczego tylko Bitcoin</h2>'
             '<p>Za większością innych „kryptowalut” stoi firma, fundacja albo założyciele z dużym zapasem monet. Bitcoin nie ma emitenta ani właściciela i właśnie dlatego jest wyjątkowy. Skupiamy się na nim w całości: na naszych spotkaniach i czatach nie promujemy altcoinów ani tokenów.</p></section>')
    body += ('<section class="rules" id="jak-zaczac"><h2>Jak zacząć: sześć kroków</h2><ol>' + "".join(
        f'<li><strong>{e(t)}</strong><span>{x}</span></li>' for t, x in steps) + "</ol></section>")
    body += ('<section class="prose-wide"><div class="warn" id="oszustwa"><h2>Uważaj na oszustów</h2><ul>' + "".join(f"<li>{x}</li>" for x in scams) + "</ul></div></section>")
    body += ('<section class="lib-head" id="biblioteka"><p class="kicker">Po polsku</p><h2>Biblioteka</h2>'
             '<p class="lede">Książki, strony, nagrania i dokumenty o Bitcoinie w języku polskim. Zaczynasz? Weź whitepaper i „Standard Bitcoina”.</p></section>'
             + catalog_html("/edukacja/", "biblioteka", biblioteka, whitepaper=True))
    body += ('<section class="prose-wide"><h2>Dalej</h2><ul>'
             f'<li><a href="{b("/slowniczek/")}">Słowniczek</a>: seed, sats, HODL i inne słowa, które usłyszysz na meetupie.</li>'
             f'<li><a href="{b("/bitcoinowa-mapa-polski/#miasta")}">Miasta</a>: przyjdź na spotkanie i zapytaj na żywo.</li>'
             f'<li><a href="{TG}" rel="noopener">Czat na Telegramie</a>: żadne pytanie nie jest głupie.</li></ul>'
             '<p class="note">Nie udzielamy porad inwestycyjnych. Wszystko na tej stronie to edukacja, nie rekomendacja.</p></section>')
    write("/edukacja/", layout("/edukacja/", "Edukacja", body,
                               desc="Czym jest Bitcoin, dlaczego tylko Bitcoin i jak zacząć bezpiecznie. Po polsku, bez sprzedawania."))
    add_index("/edukacja/", "Edukacja: jak zacząć z Bitcoinem", "strona", text_of(body))


def build_zasady(z):
    body = page_head("Społeczność", "Zasady i sieć TwentyOne",
                     "Dwadzieścia Jeden jest częścią TwentyOne: sieci lokalnych społeczności Bitcoin Only, które działają według wspólnych, prostych zasad.")
    if not z:
        body += '<p class="ph-block" data-placeholder="zasady">Treść w przygotowaniu.</p>'
    else:
        body += f'<section class="prose-wide"><h2>Czym jest sieć TwentyOne</h2>{z["concept_html"]}</section>'
        body += '<section class="rules"><h2>Zasady społeczności</h2><ol>' + "".join(
            f'<li><strong>{e(r["title"])}</strong><span>{e(r["text"])}</span></li>' for r in z["rules"]) + "</ol></section>"
        body += f'<section class="prose-wide">{z.get("more_html", "")}<p class="note">Źródło: <a href="https://twentyone.world/" rel="noopener">twentyone.world</a> (Gigi). Streszczenie i tłumaczenie nasze, stan na {pl_date(z["checked"])}.</p></section>'
    write("/zasady/", layout("/zasady/", "Zasady i sieć TwentyOne", body,
                             desc="Zasady społeczności Dwadzieścia Jeden i idea sieci TwentyOne."))
    add_index("/zasady/", "Zasady i sieć TwentyOne", "strona", text_of(body))


def bujac_link(l):
    cls = {"spotify": "btn btn--primary btn--sm", "youtube": "btn btn--ghost btn--sm"}.get(l["kind"], "btn btn--ghost btn--sm")
    return f'<a class="{cls}" href="{e(l["url"])}" rel="noopener">{e(l["label"])}</a>'


def bujac_card(x, intro):
    meta = " · ".join(t for t in [x["number"], pl_date(x["date"]) if x.get("date") else "data nieustalona", x.get("guest", "")] if t)
    links = list(x["links"]) + [{"kind": "archive", "label": "Archiwum", "url": intro["archive"]}]
    topics = "".join(f'<li>{e(t)}</li>' for t in x["topics"])
    return (f'<article class="ep" id="{x["id"]}"><div class="ep__img"><img src="{b("/assets/" + x["image"])}" alt="" loading="lazy" width="320" height="320"></div>'
            f'<div class="ep__body"><p class="ep__meta">{e(meta)}</p><h3>{e(x["title"])}</h3><p>{e(x["summary"])}</p>'
            f'<ul class="ep__topics" aria-label="Tematy">{topics}</ul>'
            f'<p class="ep__links">{"".join(bujac_link(l) for l in links)}</p></div></article>')


def build_bujac(data):
    if not data:
        return
    intro, eps = data["intro"], data["episodes"]
    order = [("sezon-1", "Sezon 1", "Czerwiec–lipiec 2025. Nagrania z BTC Prague i pierwsze rozmowy."),
             ("sezon-2", "Sezon 2", "Jesień 2025. Proof of Work, biznes na Bitcoinie, P2P, prywatność."),
             ("docinki", "Docinki", "Krótkie formy ze stycznia 2026, nagrane w blokach 931401–932391."),
             ("sezon-3", "Sezon 3", "Lipiec 2026. Rozmowy publikowane na Spotify.")]
    body = page_head("Podcast", "Bujać!", f'{e(intro["tagline"])} Polskie rozmowy o pieniądzu, wolności i budowaniu poza systemem: Bitcoin, NOSTR, prywatność i własne drogi komunikacji.')
    body += ('<section class="bujac-hero"><img src="' + b("/assets/bujac/okladka.jpg") + '" alt="Okładka podcastu Bujać!" width="240" height="240" loading="lazy">'
             f'<div><p>Autor: <strong>{e(intro["author"])}</strong>. Zaprzyjaźniony projekt i dobre miejsce, żeby posłuchać Polaków, którzy żyją na standardzie Bitcoina. '
             f'Tu zebraliśmy wszystkie {len(eps)} odcinki w jednym miejscu.</p>'
             f'<p class="cta-row"><a class="btn btn--primary" href="{e(intro["spotify"])}" rel="noopener">Spotify</a>'
             f'<a class="btn btn--ghost" href="{e(intro["site"])}" rel="noopener">bujac.pl</a>'
             f'<a class="btn btn--ghost" href="{e(intro["archive"])}" rel="noopener">Pełne archiwum</a></p></div></section>')
    body += '<nav class="toc" aria-label="Sezony">' + "".join(f'<a href="#{sid}">{e(t)}</a>' for sid, t, _ in order) + "</nav>"
    for sid, t, lede in order:
        items = [x for x in eps if x["series_id"] == sid]
        if not items:
            continue
        body += (f'<section class="cat" id="{sid}"><h2 class="sec-title">{e(t)}</h2><p class="cat__intro">{e(lede)}</p>'
                 '<div class="ep-list">' + "".join(bujac_card(x, intro) for x in items) + "</div></section>")
        for x in items:
            add_index(f"/bujac/#{x['id']}", f'Bujać! {x["number"]}: {x["title"]}', "podcast", f'{x.get("guest", "")} {x["summary"]}', x["topics"])
    body += ('<p class="note proj-note">Grafiki odcinków to ilustracje z archiwum Bujać!, nie oficjalne okładki. '
             f'Daty E03–E11 to daty pierwszej publikacji z zachowanego RSS, a data E10 nie przetrwała. Stan na {pl_date(intro["checked"])}. '
             'Zwiastuny na YouTube to fragmenty, pełne rozmowy są na Spotify.</p>')
    write("/bujac/", layout("/bujac/", "Bujać!", body, desc="Podcast Bujać!: 18 polskich rozmów o Bitcoinie, NOSTR, prywatności i wolności, z opisami, miniaturami i linkami do odcinków.",
                            crumbs=[("Edukacja", "/edukacja/")]))
    add_index("/bujac/", "Bujać! podcast", "strona", "podcast Bujać Mateusz Gadaj rozmowy o Bitcoinie NOSTR prywatności wolności")


if __name__ == "__main__":
    build()
