"""Import the old dwadziesciajeden.pl content into content/*.json.

Sources (all kept in the gitignored source-archive/ folder):
- source-archive/ghost/{posts,pages,settings}.json  Ghost Content API dump (live site, 2026-10-23)
- source-archive/wayback/extracted.json             posts deleted from Ghost but captured by Wayback
- source-archive/x-own-tweets.json                  @21BitcoinPolska tweets found via Wayback + syndication
- source-archive/x-media/manifest.json              media files of those tweets

Ghost card markup is rewritten to the new site's simple components. Re-run after any change to
the archive; never hand-edit content/imported.json.
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCH = ROOT / "source-archive"
OUT = ROOT / "content"
MEDIA_OUT = ROOT / "assets" / "media"

SITE = "https://dwadziesciajeden.pl"


def clean_ref(url: str) -> str:
    url = html.unescape(url)
    url = re.sub(r"([?&])ref=dwadziesciajeden\.pl(&|$)", lambda m: m.group(1) if m.group(2) else "", url)
    url = re.sub(r"[?&]ref_src=twsrc%5Etfw", "", url)
    url = url.rstrip("?&")
    return url


def local_media(url: str) -> str:
    """Map an old Ghost media URL to {B}/assets/media/... and copy the file if we have it."""
    path = url.split("dwadziesciajeden.pl/", 1)[1].split("?")[0]
    src = ARCH / "media" / path
    rel = path.replace("content/", "", 1)
    dst = MEDIA_OUT / rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return "{B}/assets/media/" + rel
    return url


INTERNAL = {
    "/slowniczek/": "/slowniczek/",
    "/author/jesterhodl": "/autor/jesterhodl/",
    "/tag/meetupy/": "/kronika/#meetupy",
}


def rewrite_links(h: str) -> str:
    def repl(m):
        attr, url = m.group(1), m.group(2)
        url = clean_ref(url)
        if re.match(r"https?://(www\.)?dwadziesciajeden\.pl/content/", url):
            return f'{attr}="{local_media(url)}"'
        mm = re.match(r"https?://(www\.)?dwadziesciajeden\.pl(/[^\"]*)?$", url)
        if mm:
            p = mm.group(2) or "/"
            p = INTERNAL.get(p, p)
            return f'{attr}="{{B}}{p}"'
        if url.startswith("/") and not url.startswith("//"):
            return f'{attr}="{{B}}{INTERNAL.get(url, url)}"'
        return f'{attr}="{html.escape(url, quote=True)}"'

    return re.sub(r'(href|src)="([^"]+)"', repl, h)


def bookmark(m):
    blk = m.group(0)
    href = re.search(r'class="kg-bookmark-container" href="([^"]+)"', blk).group(1)
    title = re.search(r'kg-bookmark-title">(.*?)</div>', blk, re.S)
    desc = re.search(r'kg-bookmark-description">(.*?)</div>', blk, re.S)
    author = re.search(r'kg-bookmark-author">(.*?)</span>', blk, re.S)
    t = title.group(1).strip() if title else href
    t = t.replace("DwadzieÅia", "Dwadzieścia")
    d = desc.group(1).strip() if desc else ""
    # strip signal/telegram invite noise copied from meetup descriptions
    d = re.sub(r"Signal group:\S+", "", d)
    d = (d[:220].rsplit(" ", 1)[0] + "…") if len(d) > 220 else d
    a = author.group(1).strip() if author else ""
    return (
        f'<a class="link-card" href="{href}" rel="noopener">'
        f'<span class="link-card__source">{a}</span>'
        f'<span class="link-card__title">{t}</span>'
        + (f'<span class="link-card__desc">{d}</span>' if d else "")
        + "</a>"
    )


def file_card(m):
    blk = m.group(0)
    href = re.search(r'href="([^"]+)"', blk).group(1)
    title = re.search(r'kg-file-card-title">(.*?)</div>', blk, re.S).group(1).strip()
    cap = re.search(r'kg-file-card-caption">(.*?)</div>', blk, re.S)
    size = re.search(r'kg-file-card-filesize">(.*?)</div>', blk, re.S)
    return (
        f'<a class="file-card" href="{href}" download>'
        f'<span class="file-card__icon" aria-hidden="true">PDF</span>'
        f'<span class="file-card__body"><span class="file-card__title">{title}</span>'
        f'<span class="file-card__meta">{(cap.group(1).strip() + " · ") if cap else ""}{size.group(1).strip() if size else ""}</span></span></a>'
    )


def yt(m):
    blk = m.group(0)
    vid = re.search(r"youtube\.com/embed/([\w-]+)", blk).group(1)
    title = re.search(r'title="([^"]*)"', blk)
    cap = re.search(r"<figcaption>(.*?)</figcaption>", blk, re.S)
    t = html.unescape(title.group(1)) if title else "YouTube"
    return (
        f'<figure class="video"><div class="video__frame" data-yt="{vid}">'
        f'<a class="video__poster" href="https://www.youtube.com/watch?v={vid}" rel="noopener">'
        f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
        f'<span class="video__play" aria-hidden="true"></span><span class="video__title">{html.escape(t)}</span></a></div>'
        + (f"<figcaption>{cap.group(1)}</figcaption>" if cap else "")
        + "</figure>"
    )


def tweet(m):
    blk = m.group(0)
    body = re.search(r"<p[^>]*>(.*?)</p>", blk, re.S).group(1)
    link = re.search(r'href="(https://twitter\.com/(\w+)/status/\d+)[^"]*">([^<]+)</a></blockquote>', blk)
    url = link.group(1).replace("twitter.com", "x.com") if link else "https://x.com/21BitcoinPolska"
    handle = link.group(2) if link else "21BitcoinPolska"
    date = link.group(3) if link else ""
    if handle.lower() != "21bitcoinpolska":
        # Third-party post: link only, do not republish someone else's text.
        return (
            f'<a class="link-card" href="{url}" rel="noopener"><span class="link-card__source">X · @{handle}</span>'
            f'<span class="link-card__title">Wątek o zbiórce na X</span><span class="link-card__desc">{date}</span></a>'
        )
    return (
        f'<blockquote class="post-quote"><p>{body}</p>'
        f'<footer>@21BitcoinPolska · <a href="{url}" rel="noopener">{date} na X</a></footer></blockquote>'
    )


def btcmap(m):
    src = re.search(r'src="([^"]+)"', m.group(0)).group(1)
    return (
        f'<div class="map-embed"><iframe title="BTC Map" loading="lazy" allow="geolocation" '
        f'allowfullscreen src="{src}"></iframe></div>'
    )


def toggle(m):
    head, content = m.group(1), m.group(2)
    return f"<details class=\"toggle\"><summary>{re.sub('<[^>]+>', '', head)}</summary>{content}</details>"


PLACES = {
    "BarBazaar": ("BarBazaar, ul. Ząbkowska 12, Warszawa", "BarBazaar Ząbkowska 12 Warszawa"),
    "Bracka%2020": ("ul. Bracka 20, Warszawa", "Bracka 20 Warszawa"),
    "Literatka": ("Kawiarnia Literatka, Rynek 56/57, Wrocław", "Rynek 56 Wrocław"),
}


def gmaps(m):
    label, q = PLACES.get(m.group(1), (m.group(1), m.group(1)))
    return f'<p><a href="https://www.openstreetmap.org/search?query={q.replace(" ", "%20")}" rel="noopener">{label}: pokaż na mapie</a></p>'


def transform(h: str) -> str:
    h = re.sub(r'<figure class="kg-card kg-bookmark-card[^"]*">.*?</figure>', bookmark, h, flags=re.S)
    h = re.sub(r'<div class="kg-card kg-file-card[^"]*">.*?</a>\s*</div>', file_card, h, flags=re.S)
    h = re.sub(r'<figure class="kg-card kg-embed-card[^"]*"><iframe[^>]*youtube.*?</figure>', yt, h, flags=re.S)
    h = re.sub(r'<figure class="kg-card kg-embed-card"><(?:div><)?blockquote class="twitter-tweet">.*?</figure>', tweet, h, flags=re.S)
    h = re.sub(r"<!--kg-card-begin: html-->\s*<div><iframe.*?</iframe>\s*</div>\s*<!--kg-card-end: html-->", btcmap, h, flags=re.S)
    h = re.sub(r'<div class="kg-card kg-toggle-card".*?kg-toggle-heading-text">(.*?)</h4>.*?kg-toggle-content">(.*?)</div>\s*</div>', toggle, h, flags=re.S)
    h = re.sub(
        r'<div class="kg-card kg-callout-card[^"]*"><div class="kg-callout-emoji">(.*?)</div><div class="kg-callout-text">(.*?)</div></div>',
        r'<aside class="callout"><span aria-hidden="true">\1</span><p>\2</p></aside>', h, flags=re.S)
    h = re.sub(r'<div class="kg-card kg-button-card[^"]*"><a href="([^"]+)" class="kg-btn[^"]*">(.*?)</a></div>',
               r'<p class="cta-row"><a class="btn btn--primary" href="\1">\2</a></p>', h, flags=re.S)
    h = re.sub(r'<figure class="kg-card kg-image-card[^"]*"><img src="([^"]+)"[^>]*></figure>',
               r'<figure class="inline-img"><img src="\1" alt="" loading="lazy"></figure>', h)
    h = re.sub(r"<!--kg-card-(begin|end): html-->", "", h)
    # Google Maps embeds (old meetup posts) -> plain link, no third-party iframe
    h = re.sub(r'<iframe src="https://www\.google\.com/maps/embed\?pb=[^"]*?!2s([^!"]+)![^"]*"[^>]*></iframe>', gmaps, h)
    h = re.sub(r'<script[^>]*>.*?</script>', "", h, flags=re.S)
    h = re.sub(r'<span style="white-space: pre-wrap;">(.*?)</span>', r"\1", h, flags=re.S)
    h = re.sub(r'<b><strong style="white-space: pre-wrap;">(.*?)</strong></b>', r"<strong>\1</strong>", h, flags=re.S)
    h = re.sub(r"<p></p>", "", h)
    h = re.sub(r'\s(id="[^"]*")', lambda m: " " + m.group(1), h)
    h = rewrite_links(h)
    h = re.sub(r'href="mailto:[^"]+"', 'href="{B}/dolacz-do-nas/#kontakt"', h)
    # Images that were never archived (old Ghost host only): drop rather than hotlink a dying URL.
    h = re.sub(r'<figure class="inline-img"><img src="https://dwadziesciajeden\.pl/[^"]*"[^>]*></figure>',
               '<p class="note">(Obraz z oryginalnego wpisu nie zachował się w archiwum.)</p>', h)
    return h.strip()


def main():
    OUT.mkdir(exist_ok=True)
    posts = json.loads((ARCH / "ghost/posts.json").read_text(encoding="utf-8"))["posts"]
    pages = json.loads((ARCH / "ghost/pages.json").read_text(encoding="utf-8"))["pages"]
    records = []
    for kind, items in (("post", posts), ("page", pages)):
        for p in items:
            feat = p.get("feature_image")
            # iStock feature image on /kim-jestesmy/ has no licence for redistribution: dropped.
            if feat and "iStock" in feat:
                feat = None
            records.append({
                "slug": p["slug"],
                "kind": kind,
                "title": p["title"],
                "published": p["published_at"][:10],
                "updated": (p.get("updated_at") or "")[:10],
                "tags": [t["name"] for t in p.get("tags", []) if not t["name"].startswith("#")],
                "excerpt": (p.get("custom_excerpt") or p.get("excerpt") or "").strip(),
                "feature_image": local_media(feat) if feat else None,
                "html": transform(p["html"] or ""),
                "source": f"{SITE}/{p['slug']}/",
                "origin": "ghost-content-api-2026-10-23",
            })
    for a in json.loads((ARCH / "wayback/extracted.json").read_text(encoding="utf-8")):
        slug = a["path"].strip("/")
        if slug in ("mapa", "meetupy"):
            kind = "redirect"
        else:
            kind = "post"
        body = a["html"]
        body = re.sub(r'<section class="article-comments.*', "", body, flags=re.S)
        body = re.sub(r'\s*</div>\s*<div class="pagination-container.*', "", body, flags=re.S)
        records.append({
            "slug": slug,
            "kind": kind,
            "title": html.unescape(a["title"].split(" - ")[0].split(" | ")[0]).strip(),
            "published": (a["published"] or "")[:10],
            "updated": "",
            "tags": ["Meetupy"] if slug.startswith("meetup") else (["Zbiórki"] if "wosp" in slug else []),
            "excerpt": "",
            "feature_image": None,
            "html": transform(body),
            "source": f"https://web.archive.org/web/{a['wayback_ts']}/{SITE}{a['path']}",
            "origin": f"wayback-{a['wayback_ts']}",
        })
    settings = json.loads((ARCH / "ghost/settings.json").read_text(encoding="utf-8"))["settings"]
    for key in ("cover_image", "logo"):
        if settings.get(key):
            local_media(settings[key])
    (OUT / "imported.json").write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"imported {len(records)} records:", ", ".join(r["slug"] for r in records))


if __name__ == "__main__":
    main()
