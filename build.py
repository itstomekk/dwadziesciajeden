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
import struct
from datetime import date
from pathlib import Path

import whitepaper_page as wpp
import mission_page

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
C = ROOT / "content"

BASE = os.environ.get("DJ_BASE", "").rstrip("/")  # live on dwadziesciajeden.pl since 2026-10-23
SITE_URL = os.environ.get("DJ_SITE_URL", "https://dwadziesciajeden.pl").rstrip("/")
NOINDEX = os.environ.get("DJ_NOINDEX", "0") == "1"
BUILT = date.today().isoformat()

INVITE_ENDPOINT = "https://dj-invitations.kolotom.workers.dev/subscribe"
INVITE_PAGE = "/dolacz-do-nas/#invite"
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

# brand icons: Telegram, X and the social icons below from Simple Icons (CC0), Nostr from mbarulli/nostr-logo (CC0)
def icon(name):
    paths = {
        "telegram": ("0 0 24 24", "M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"),
        "x": ("0 0 24 24", "M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"),
        "nostr": ("44 44 172 172", "M210.8 199.4c0 3.1-2.5 5.7-5.7 5.7h-68c-3.1 0-5.7-2.5-5.7-5.7v-15.5c.3-19 2.3-37.2 6.5-45.5 2.5-5 6.7-7.7 11.5-9.1 9.1-2.7 24.9-.9 31.7-1.2 0 0 20.4.8 20.4-10.7s-9.1-8.6-9.1-8.6c-10 .3-17.7-.4-22.6-2.4-8.3-3.3-8.6-9.2-8.6-11.2-.4-23.1-34.5-25.9-64.5-20.1-32.8 6.2.4 53.3.4 116.1v8.4c0 3.1-2.6 5.6-5.7 5.6H57.7c-3.1 0-5.7-2.5-5.7-5.7v-144c0-3.1 2.5-5.7 5.7-5.7h31.7c3.1 0 5.7 2.5 5.7 5.7 0 4.7 5.2 7.2 9 4.5 11.4-8.2 26-12.5 42.4-12.5 36.6 0 64.4 21.4 64.4 68.7v83.2ZM150 99.3c0-6.7-5.4-12.1-12.1-12.1s-12.1 5.4-12.1 12.1 5.4 12.1 12.1 12.1S150 106 150 99.3Z"),
        "rss": ("0 0 24 24", "M19.199 24C19.199 13.467 10.533 4.8 0 4.8V0c13.165 0 24 10.835 24 24h-4.801zM3.291 17.415c1.814 0 3.293 1.479 3.293 3.295 0 1.813-1.485 3.29-3.301 3.29C1.47 24 0 22.526 0 20.71s1.475-3.294 3.291-3.295zM15.909 24h-4.665c0-6.169-5.075-11.245-11.244-11.245V8.09c8.727 0 15.909 7.184 15.909 15.91z"),
        "instagram": ("0 0 24 24", "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"),
        "youtube": ("0 0 24 24", "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"),
        "facebook": ("0 0 24 24", "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"),
        "github": ("0 0 24 24", "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"),
        "tiktok": ("0 0 24 24", "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"),
        "linkedin": ("0 0 24 24", "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"),
        "applepodcasts": ("0 0 24 24", "M5.34 0A5.328 5.328 0 000 5.34v13.32A5.328 5.328 0 005.34 24h13.32A5.328 5.328 0 0024 18.66V5.34A5.328 5.328 0 0018.66 0zm6.525 2.568c2.336 0 4.448.902 6.056 2.587 1.224 1.272 1.912 2.619 2.264 4.392.12.59.12 2.2.007 2.864a8.506 8.506 0 01-3.24 5.296c-.608.46-2.096 1.261-2.336 1.261-.088 0-.096-.091-.056-.46.072-.592.144-.715.48-.856.536-.224 1.448-.874 2.008-1.435a7.644 7.644 0 002.008-3.536c.208-.824.184-2.656-.048-3.504-.728-2.696-2.928-4.792-5.624-5.352-.784-.16-2.208-.16-3 0-2.728.56-4.984 2.76-5.672 5.528-.184.752-.184 2.584 0 3.336.456 1.832 1.64 3.512 3.192 4.512.304.2.672.408.824.472.336.144.408.264.472.856.04.36.03.464-.056.464-.056 0-.464-.176-.896-.384l-.04-.03c-2.472-1.216-4.056-3.274-4.632-6.012-.144-.706-.168-2.392-.03-3.04.36-1.74 1.048-3.1 2.192-4.304 1.648-1.737 3.768-2.656 6.128-2.656zm.134 2.81c.409.004.803.04 1.106.106 2.784.62 4.76 3.408 4.376 6.174-.152 1.114-.536 2.03-1.216 2.88-.336.43-1.152 1.15-1.296 1.15-.023 0-.048-.272-.048-.603v-.605l.416-.496c1.568-1.878 1.456-4.502-.256-6.224-.664-.67-1.432-1.064-2.424-1.246-.64-.118-.776-.118-1.448-.008-1.02.167-1.81.562-2.512 1.256-1.72 1.704-1.832 4.342-.264 6.222l.413.496v.608c0 .336-.027.608-.06.608-.03 0-.264-.16-.512-.36l-.034-.011c-.832-.664-1.568-1.842-1.872-2.997-.184-.698-.184-2.024.008-2.72.504-1.878 1.888-3.335 3.808-4.019.41-.145 1.133-.22 1.814-.211zm-.13 2.99c.31 0 .62.06.844.178.488.253.888.745 1.04 1.259.464 1.578-1.208 2.96-2.72 2.254h-.015c-.712-.331-1.096-.956-1.104-1.77 0-.733.408-1.371 1.112-1.745.224-.117.534-.176.844-.176zm-.011 4.728c.988-.004 1.706.349 1.97.97.198.464.124 1.932-.218 4.302-.232 1.656-.36 2.074-.68 2.356-.44.39-1.064.498-1.656.288h-.003c-.716-.257-.87-.605-1.164-2.644-.341-2.37-.416-3.838-.218-4.302.262-.616.974-.966 1.97-.97z"),
        "spotify": ("0 0 24 24", "M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"),
    }
    vb, d = paths[name]
    return f'<svg class="ico" viewBox="{vb}" aria-hidden="true" focusable="false"><path fill="currentColor" d="{d}"/></svg>'


NAV = [
    ("Kim jesteśmy", "/kim-jestesmy/"),
    ("Edukacja", "/edukacja/"),
    ("Bitcoin w Polsce", "/bitcoinowa-mapa-polski/"),
    ("Projekty", "/projekty/"),
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


def strip_telegram_urls(text: str) -> str:
    return re.sub(r"""https?://(?:t\.me|telegram\.me|telegram\.dog)/[^\s"'<>)]*""", "", text, flags=re.I)


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


SOCIAL_NAMES = {"x": "X", "nostr": "Nostr", "instagram": "Instagram", "youtube": "YouTube", "facebook": "Facebook",
                "linkedin": "LinkedIn", "github": "GitHub", "tiktok": "TikTok", "spotify": "Spotify",
                "applepodcasts": "Apple Podcasts", "rss": "RSS"}


def social_handle(s):
    """Short label for a social profile: explicit `label`, else the last path part of the URL."""
    if s.get("label"):
        return s["label"]
    tail = s["url"].rstrip("/").rsplit("/", 1)[-1]
    return tail if tail.startswith("@") or s["kind"] in ("github", "linkedin", "youtube") else "@" + tail


def social_row(pr, cls="proj__social"):
    """Row of icon links to a partner's social profiles (cards on /projekty/)."""
    items = pr.get("social", [])
    if not items:
        return ""
    return (f'<p class="{cls}">' + "".join(
        f'<a href="{e(s["url"])}" rel="noopener" title="{e(SOCIAL_NAMES[s["kind"]])}: {e(social_handle(s))}" '
        f'aria-label="{e(SOCIAL_NAMES[s["kind"]])}: {e(social_handle(s))}">{icon(s["kind"])}</a>' for s in items) + "</p>")


def text_of(h: str) -> str:
    h = strip_telegram_urls(h)
    h = re.sub(r"<script\b.*?</script>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


# Header/footer wordmark: orange circle emoji + name on two lines (owner pick 2026-11-06, variant 2).
LOGO = '<i class="mark mark--dot" aria-hidden="true">🟠</i>'
# Subtitle under the wordmark (owner pick 2026-11-06, variant 1 with a drawn flag: the flag emoji shows as "PL" on Windows).
BRAND_NAME = ('<span class="brand__txt"><span class="brand__name">Dwadzieścia<br>Jeden</span>'
              '<small class="brand__sub">BITCOIN POLSKA<svg class="brand__flag" viewBox="0 0 16 10" aria-hidden="true">'
              '<rect width="16" height="5" fill="#fff"/><rect y="5" width="16" height="5" fill="#DC143C"/>'
              '<rect x=".25" y=".25" width="15.5" height="9.5" fill="none" stroke="#cfcfcf" stroke-width=".5"/></svg></small></span>')


def layout(path, title, body, desc="", kind="page", og_image=None, crumbs=None, ld=None):
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
{jsonld(path)}{ld or ""}<meta property="og:type" content="{'article' if kind == 'post' else 'website'}">
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
    <a class="brand" href="{b('/')}">{LOGO}{BRAND_NAME}</a>
    <nav class="nav" id="nav" aria-label="Główne menu">{nav}</nav>
    <div class="top__act">
      <button class="icon-btn" type="button" data-search-open aria-label="Szukaj"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg></button>
      <a class="btn btn--primary btn--sm" href="{b(INVITE_PAGE)}" data-goatcounter-click="dolacz-zaproszenie-naglowek" data-goatcounter-title="Dołącz (nagłówek)">Dołącz</a>
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
      <a class="brand" href="{b('/')}">{LOGO}{BRAND_NAME}</a>
      <p>Polska społeczność Bitcoin Only. Część sieci <a href="https://twentyone.world/" rel="noopener">TwentyOne</a>.</p>
    </div>
    <div class="foot__col">
      <h2>Społeczność</h2>
      <a class="ico-link" href="{X_URL}" rel="noopener">{icon("x")}@21BitcoinPolska na X</a>
      <a class="ico-link" href="{NOSTR_ARMADA}" rel="noopener">{icon("nostr")}Społeczność na Nostrze (Armada)</a>
      <a class="ico-link" href="{NOSTR_URL}" rel="noopener">{icon("nostr")}Profil na Nostrze</a>
      <a href="{b(INVITE_PAGE)}">Dołącz do Telegrama</a>
    </div>
    <div class="foot__col">
      <h2>Strona</h2>
      <a href="{b('/edukacja/')}">Edukacja: jak zacząć</a>
      <a href="{b('/artykuly/')}">Artykuły</a>
      <a href="{b('/slowniczek/')}">Słowniczek</a>
      <a href="{b('/bitcoin-whitepaper/')}">Whitepaper po polsku</a>
      <a href="https://github.com/itstomekk/dwadziesciajeden" rel="noopener">Kod strony na GitHubie</a>
    </div>
    <div class="foot__col">
      <h2>RSS</h2>
      <a class="ico-link" href="{b('/rss.xml')}">{icon("rss")}Kanał RSS</a>
      <p class="muted">Kronika i artykuły w Twoim czytniku. Bez zapisów i bez maili.</p>

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
         "sameAs": [X_URL, "https://github.com/itstomekk/dwadziesciajeden", "https://twentyone.world/"]},
        {"@type": "WebSite", "@id": f"{SITE_URL}/#site", "url": f"{SITE_URL}/", "name": "Dwadzieścia Jeden",
         "inLanguage": "pl-PL", "publisher": {"@id": f"{SITE_URL}/#org"}}]}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'


class _MD(html.parser.HTMLParser):
    """Small HTML -> Markdown converter for the <main> of a page (stdlib only)."""
    SKIP = {"script", "style", "svg", "button", "iframe", "noscript", "form", "input", "math"}
    BLOCK = {"p", "div", "section", "article", "header", "ul", "ol", "dl", "table", "figure", "blockquote", "nav", "li", "dt", "dd", "tr", "br"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.href, self.li = [], 0, [], 0
        self.drop_tag, self.drop_depth = None, 0
        self.pre, self.pres = 0, []

    def handle_starttag(self, tag, a):
        a = dict(a)
        if self.drop_tag:
            self.drop_depth += tag == self.drop_tag
            return
        if tag == "math" and not self.skip:
            self.out.append(f" `{a.get('alttext', '')}` ")
        if tag == "pre" and not self.skip:
            self.pre += 1
            self.pres.append([])
            self.out.append(f"\n\n\x00PRE{len(self.pres) - 1}\x00\n\n")
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
        if tag == "pre" and self.pre:
            self.pre -= 1
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
        if self.pre and not self.drop_tag:
            self.pres[-1].append(d)
        elif not self.skip and not self.drop_tag:
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
        for i, chunks in enumerate(self.pres):
            t = t.replace(f"\x00PRE{i}\x00", "```\n" + "".join(chunks).strip("\n") + "\n```")
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
    body = (f"---\ntitle: {title}\nurl: {SITE_URL}{path}\nlanguage: {'en' if path.startswith('/bitcoin-whitepaper/en/') else 'pl'}\n---\n\n"
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
    doc = re.sub(r"""<a\b(?=[^>]*\bhref\s*=\s*["']https?://(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/[^"']*["'])[^>]*>(.*?)</a>""", r"\1", doc, flags=re.I | re.S)
    doc = strip_telegram_urls(doc)
    target.write_text(doc, encoding="utf-8")
    write_twin(path, doc)


def add_index(path, title, kind, text, tags=()):
    pages_index.append({"u": path, "t": title, "k": kind, "x": strip_telegram_urls(text)[:1200], "g": list(tags)})


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
        ("Bitcoin w Polsce", "/bitcoinowa-mapa-polski/", "Mapa, miasta, projekty i kronika społeczności."),
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
    <p class="cta-row"><a class="btn btn--primary" href="{b(INVITE_PAGE)}">Dołącz do Telegrama</a><a class="btn btn--ghost" href="{b('/kim-jestesmy/')}">Kim jesteśmy</a></p>
  </div>
  <div class="shell">
    <div class="shell__bar"><span>~/dwadziesciajeden</span><span>bash</span></div>
    <pre class="shell__body"><span class="l"><i>$</i> whoami</span><span class="l o">dwadziescia_jeden: polska społeczność bitcoin only</span><span class="l"><i>$</i> cat zasady.txt</span><span class="l o">bitcoin only · zero altcoinów · nic nie sprzedajemy</span><span class="l"><i>$</i> bitcoin-cli getblockcount</span><span class="l o"><b class="tip" data-tip>…</b></span><span class="l"><i>$</i> ./dolacz.sh</span><span class="l o">→ poproś o zaproszenie na stronie</span><span class="l"><i>$</i> <span class="cur" aria-hidden="true"></span></span></pre>
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
    <p>Rozmawiamy o bieżących sprawach, sprawdzamy memy przed publikacją, otwieramy kanały Lightning, organizujemy meetupy i ostrzegamy przed scamem.</p>
    <div class="join__grid">
      <a class="join__card join__card--main" href="{b(INVITE_PAGE)}"><span>Dołącz do społeczności</span><strong>Dołącz do Telegrama</strong></a>
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
        if slug in ("projekty", "bitcoinowa-mapa-polski", "miasta", "warszawa", "krakow", "poznan", "bitcoin-whitepaper"):
            continue  # custom pages below
        body_html = fill(p["html"])
        if slug == "kim-jestesmy":
            body_html = body_html.replace(f'<p><a href="{BASE}/autor/jesterhodl/">@JesterHodl</a></p>',
                                          f'<p class="byline">Tekst: <a href="{BASE}/autor/jesterhodl/">@JesterHodl</a></p>')
            body = mission_page.render(BASE, body_html)
            desc = "Dlaczego Bitcoin? Poznaj nasze argumenty, trudne pytania i misję społeczności Dwadzieścia Jeden."
            write("/kim-jestesmy/", layout("/kim-jestesmy/", "Dlaczego Bitcoin?", body, desc=desc))
            add_index("/kim-jestesmy/", "Dlaczego Bitcoin? Kim jesteśmy", "strona", text_of(body))
            continue
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
            body_html = re.sub(r'<p class="cta-row"><a class="btn btn--primary" href="https://t[.]me/[^"]*">Dołącz do naszej grupy na Telegramie</a></p>', "", body_html)
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

    build_whitepaper()

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
            h = re.sub(r'<h3 id="bitcoinwalk">BitcoinWalk</h3><a class="link-card" href="https://bitcoinwalk\\.org/poznan/".*?</a>',
                       '<h3 id="bitcoinwalk">BitcoinWalk</h3><p>Formuła spacerów pochodzi z <a href="https://bitcoinwalk.org/" rel="noopener">bitcoinwalk.org</a>. Terminy publikujemy na Meetup i na X.</p>', h, flags=re.S)
            if c["slug"] == "krakow":
                # meetup.com/krakow-bitcoin-meetup returns "Group not found" (checked 2026-10-23)
                h = re.sub(r'<a class="link-card" href="https://www\.meetup\.com/pl-PL/krakow-bitcoin-meetup/".*?</a>',
                           f'<p class="note">Grupa Kraków Bitcoin Meetup na meetup.com nie jest już dostępna. Krakowskie spotkania ogłaszamy na X. <a href="{b(INVITE_PAGE)}">Dołącz do Telegrama</a>.</p>', h, flags=re.S)
                h += ('<h3>Z archiwum</h3><ul><li><a href="https://x.com/21BitcoinPolska/status/1794694392374342098" rel="noopener">„Dla kogo jest Bitcoin, kiedy i jak go kupić?”, Techies, maj 2024</a></li>'
                      '<li><a href="https://x.com/21BitcoinPolska/status/1919430740485304721" rel="noopener">Meetup w Krakowie, 9 maja 2025</a></li></ul>')
            if c["slug"] == "poznan":
                h = re.sub(r'<h3 id="telegram">Telegram</h3><a class="link-card" href="https://t[.]me/[^"]*">.*?</a>', "", h, flags=re.S)
                h = h.replace('<h3 id="meetup">', '<h3 id="stale">Stałe spotkania</h3><div class="regulars">'
                              '<a class="regular" href="https://www.meetup.com/poz21m/" rel="noopener"><span class="regular__when">Spacery, terminy na Meetup</span><strong>Poznań BitcoinWalk · Spacery ku wolności</strong><span>Spacer i rozmowa o Bitcoinie. Zbiórka zwykle przy Skwerze Jana Suwarta, ul. Ewangelicka. Latem także grill i spacery nad Rusałką.</span></a>'
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
          f'<li><a href="{b(INVITE_PAGE)}">Napisz do nas</a>, żebyśmy mogli pochwalić się nowym miejscem.</li></ol>')
    polska_body = (f'<article class="article"><p class="kicker">Mapa i społeczność</p><h1>Bitcoin w Polsce</h1>'
            f'<p class="lede">Gdzie zapłacisz bitcoinem, gdzie się spotykamy i co wspólnie tworzymy.</p>'
            f'<nav class="toc" aria-label="Na tej stronie"><a href="#mapa">Mapa</a><a href="#miasta">Miasta</a><a href="#polskie-projekty">Projekty</a><a href="#kronika">Kronika</a></nav>'
            f'<div class="prose" id="mapa">{m}</div></article>' + miasta_section
            + f'<section class="cat" id="polskie-projekty"><h2 class="sec-title">Projekty</h2>'
              f'<p>W naszym katalogu znajdziesz <strong>{len(projekty["projects"])} projektów</strong> naszych i zaprzyjaźnionych.</p>'
              f'<a class="link-arrow" href="{b("/projekty/")}">Zobacz wszystkie projekty</a></section>')
    add_index("/bitcoinowa-mapa-polski/", "Bitcoin w Polsce", "strona", text_of(m))

    # ---- projekty + inicjatywy (one page)
    def proj_card(pr):
        img = (f'<img src="{b("/assets/" + pr["image"])}" alt="{e(pr.get("image_alt", ""))}" loading="lazy">' if pr.get("image") else
               f'<span class="proj__mono" aria-hidden="true">{e(pr["name"][:1])}</span>')
        vids = [(yt_id(l.get("url", "")), l) for l in pr["links"]]
        vids = "".join(f'<figure class="video">{yt_frame(v, l["url"], l.get("label", pr["name"]))}</figure>' for v, l in vids if v)
        page = pr["kind"] != "ours"  # every friend/partner has its own subpage /projekty/<id>/
        head = (f'<a class="proj__anchor proj__anchor--page" href="{b(partner_path(pr))}">{e(pr["name"])}</a>' if page
                else f'<a class="proj__anchor" href="#{pr["id"]}">{e(pr["name"])}</a>')
        more = [f'<a class="proj__more" href="{b(partner_path(pr))}">Więcej o projekcie</a>'] if page else []
        return (f'<article class="proj proj--{pr["kind"]}" id="{pr["id"]}"><div class="proj__img">{img}</div>'
                f'<div class="proj__body"><p class="proj__status">{e(pr["status"])}{" · nasz projekt" if pr["kind"] == "ours" else " · zaprzyjaźnieni"}</p>'
                f'<h2>{head}</h2><p>{e(pr["text"])}</p>{vids}<p class="proj__links">{" · ".join(more + [link(l) for l in pr["links"]])}</p>{social_row(pr)}</div></article>')
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
        body += f'<p class="note proj-note">Linki sprawdzone {pl_date(inicjatywy["checked"])}. Grafiki pochodzą ze stron projektów. Brakuje czegoś? <a href="{b(INVITE_PAGE)}">Napisz do nas</a>.</p>'
    write("/projekty/", layout("/projekty/", "Projekty i inicjatywy", body, desc="Projekty społeczności Dwadzieścia Jeden, zaprzyjaźnieni i polskie inicjatywy bitcoinowe."))
    add_index("/projekty/", "Projekty i inicjatywy", "strona", "projekty inicjatywy stowarzyszenia wydarzenia czaty")
    for pr in projekty["projects"]:
        if pr["kind"] == "ours":
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
    polska_body += (f'<details id="kronika" class="cat polska-kronika"><summary><span class="sec-title">Kronika społeczności</span> '
                    f'<span>Rozwiń · {len(ks)} wpisów</span></summary>'
                    f'<p>Historia społeczności od 2021 roku.</p><div class="filters" role="group" aria-label="Filtruj kronikę">{fbar}</div>'
                    f'<div class="tl-wrap">{blocks}</div><p><a class="link-arrow" href="{b("/kronika/")}">Kronika i zdjęcia na osobnej stronie</a></p></details>')
    write("/bitcoinowa-mapa-polski/", layout("/bitcoinowa-mapa-polski/", "Bitcoin w Polsce", polska_body,
          desc="Mapa miejsc, miasta, projekty i kronika bitcoinowej społeczności w Polsce."))
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

    # ---- one subpage per friend/partner (last, so its "on our site" list sees every built page)
    build_partner_pages(projekty["projects"], kronika)

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



def partner_path(pr):
    """Own subpage of a friend/partner; `page` points at an existing page instead (e.g. /bujac/)."""
    return pr.get("page") or f"/projekty/{pr['id']}/"


def partner_terms(pr):
    """Words that count as a mention of a partner: explicit `match` list, else the name plus link domains."""
    if pr.get("match"):
        return pr["match"]
    terms = [pr["name"]]
    for l in pr["links"]:
        m = re.match(r"https?://(?:www\.)?([^/]+)", l.get("url", ""))
        if m and m.group(1) not in ("x.com", "github.com", "youtube.com", "youtu.be", "gitworkshop.dev"):
            terms.append(m.group(1))
    return terms


def partner_mentions(pr, kronika):
    """Chronicle entries and built pages (outside /projekty/ and /kronika/) that mention the partner."""
    rx = re.compile(r"(?<![\w.])(?:" + "|".join(re.escape(t) for t in partner_terms(pr)) + r")(?![\w])", re.I)
    ks = sorted((k for k in kronika if rx.search(" ".join([k["title"], k["text"]] + [l.get("url", "") for l in k.get("links", [])]))),
                key=lambda k: k["date"], reverse=True)
    pages = []
    for f in sorted(OUT.rglob("index.html")):
        rel = "/" + f.parent.relative_to(OUT).as_posix().strip(".") + "/"
        rel = rel.replace("//", "/")
        if rel.startswith(("/projekty/", "/kronika/", "/tag/", "/autor/", "/artykuly/")) or rel == "/":
            continue
        doc = f.read_text(encoding="utf-8")
        m = re.search(r'<main id="tresc">(.*)</main>', doc, re.S)
        if not m or 'http-equiv="refresh"' in doc:
            continue
        main = m.group(1)
        if rx.search(text_of(main)) or rx.search(" ".join(re.findall(r'href="([^"]+)"', main))):
            title = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1)).replace(" · Dwadzieścia Jeden", "")
            pages.append((rel, title))
    return ks, pages


def build_partner_pages(projects, kronika):
    """/projekty/<id>/ for every friend/partner: story, links to their work, mentions on our site, JSON-LD."""
    friends = [p for p in projects if p["kind"] != "ours"]
    for pr in friends:
        if pr.get("page"):  # has its own page elsewhere on the site
            continue
        path = partner_path(pr)
        links = pr["links"] + pr.get("more_links", [])
        ext = [l["url"] for l in links if l.get("url")] + [s["url"] for s in pr.get("social", [])]

        def host(u):
            return re.sub(r"^https?://(?:www\.)?", "", u).split("/")[0]
        img = (f'<figure class="partner__img"><img src="{b("/assets/" + pr["image"])}" alt="{e(pr.get("image_alt", ""))}"></figure>'
               if pr.get("image") else "")
        story = "".join(f"<p>{e(s)}</p>" for s in pr.get("story", []))
        vids = "".join(f'<figure class="video">{yt_frame(v, l["url"], l.get("label", pr["name"]))}</figure>'
                       for v, l in ((yt_id(l.get("url", "")), l) for l in links) if v)
        link_items = "".join(
            f'<li>{link(l)}<small>{e(host(l["url"]) if l.get("url") else "dwadziesciajeden.pl")}</small></li>' for l in links)
        soc = ""
        if pr.get("social"):
            soc = ('<h2>Social media</h2><ul class="partner__links partner__social">' + "".join(
                f'<li><a class="ico-link" href="{e(s["url"])}" rel="noopener">{icon(s["kind"])}{e(SOCIAL_NAMES[s["kind"]])}</a>'
                f'<small>{e(social_handle(s))}</small></li>' for s in pr["social"]) + "</ul>")
        ks, pages = partner_mentions(pr, kronika)
        ment = ""
        if ks or pages:
            ment = ('<h2>U nas na stronie</h2><ul class="partner__mentions">'
                    + "".join(f'<li><a href="{b("/kronika/#" + chron_id(k))}">{e(k["title"])}</a><small>kronika · {pl_date(k["date"])}</small></li>' for k in ks)
                    + "".join(f'<li><a href="{b(u)}">{e(t)}</a><small>strona</small></li>' for u, t in pages)
                    + "</ul>")
        others = "".join(f'<a href="{b(partner_path(o))}">{e(o["name"])}</a>' for o in friends if o is not pr)
        body = (f'<article class="article partner"><p class="kicker">{e(pr["status"])} · zaprzyjaźnieni</p>'
                f'<h1>{e(pr["name"])}</h1><p class="lede">{e(pr["text"])}</p>{img}'
                f'<div class="prose">{story}{vids}<h2>Linki</h2><ul class="partner__links">{link_items}</ul>{soc}{ment}</div>'
                f'<p class="note">Coś nieaktualne albo chcesz dopisać swoją historię z {e(pr.get("name_with", pr["name"]))}? '
                f'<a href="{b(INVITE_PAGE)}">Napisz do nas</a>.</p>'
                f'<nav class="partner__others" aria-label="Inni zaprzyjaźnieni"><h2 class="kicker">Inni zaprzyjaźnieni</h2>{others}</nav></article>')
        about = {"@type": pr.get("schema", "Organization"), "name": pr["name"]}
        if ext:
            about["url"] = ext[0]
            if len(ext) > 1:
                about["sameAs"] = ext[1:]
        ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{SITE_URL}{path}", "name": pr["name"],
              "inLanguage": "pl-PL", "isPartOf": {"@type": "WebSite", "@id": f"{SITE_URL}/#site", "url": f"{SITE_URL}/"},
              "about": about,
              "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Projekty", "item": f"{SITE_URL}/projekty/"},
                  {"@type": "ListItem", "position": 2, "name": pr["name"], "item": f"{SITE_URL}{path}"}]}}
        if pr.get("image"):
            ld["primaryImageOfPage"] = f"{SITE_URL}/assets/{pr['image']}"
        desc = pr["text"] if len(pr["text"]) <= 160 else pr["text"][:157].rsplit(" ", 1)[0].rstrip(",.:;") + "…"
        write(path, layout(path, pr["name"], body, desc=desc,
                           og_image=b("/assets/" + pr["image"]) if pr.get("image") else None,
                           crumbs=[("Projekty", "/projekty/"), ("Zaprzyjaźnieni", "/projekty/#zaprzyjaznieni")],
                           ld=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'))
        add_index(path, pr["name"], "projekt", " ".join([pr["text"]] + pr.get("story", [])), [pr["status"]])


def build_whitepaper():
    """/bitcoin-whitepaper/ (Polish translation) and /bitcoin-whitepaper/en/ (original) as full-text pages."""
    data = load("whitepaper.json")
    px = {}
    for png in (ROOT / "assets" / "whitepaper").glob("*.png"):
        px[png.stem] = struct.unpack(">II", png.read_bytes()[16:24])

    def card(lang, title, meta):
        return (f'<a class="file-card" href="{b(wpp.PDF[lang])}" download><span class="file-card__icon" aria-hidden="true">PDF</span>'
                f'<span class="file-card__body"><span class="file-card__title">{title}</span>'
                f'<span class="file-card__meta">{meta} · {wpp.SIZE[lang]}</span></span></a>')

    tr = "https://github.com/meeDamian/bitcoinwhitepaper"
    pl = data["pl"]
    body = ('<article class="article wp"><p class="kicker">Zasoby</p><h1>Bitcoin Whitepaper</h1>'
            '<p class="lede">Decydując się na hosting białej księgi Bitcoina, wyrażamy dla niego nasze poparcie. '
            'Poniżej cały tekst, z rysunkami, wzorami i źródłami. Można go czytać na telefonie i przeszukiwać.</p>'
            + card("pl", "Bitcoin: Elektroniczny System Pieniężny Typu Peer-to-Peer", "Whitepaper po polsku")
            + card("en", "Bitcoin: A Peer-to-Peer Electronic Cash System", "Whitepaper, oryginał")
            + f'<p class="note">Tłumaczenie na polski: <a href="https://github.com/meeDamian" rel="noopener">meeDamian (Damian Mee)</a>, '
              f'<a href="{tr}" rel="noopener">repozytorium tłumaczeń</a>. Plik PDF jest identyczny z wersją na bitcoin.org. '
              f'Tekst oryginału po angielsku: <a href="{b("/bitcoin-whitepaper/en/")}">czytaj tutaj</a>.</p>'
            + wpp.toc_html("pl", pl) + wpp.paper_html("pl", pl, b, px)
            + wpp.footer_html("pl", b, b("/")) + "</article>")
    write("/bitcoin-whitepaper/", layout("/bitcoin-whitepaper/", "Bitcoin Whitepaper", body,
          desc="Biała księga Bitcoina po polsku: pełny tekst z rysunkami, wzorami i źródłami oraz PDF do pobrania. Tłumaczenie: meeDamian.",
          crumbs=[("Edukacja", "/edukacja/")], og_image=b("/assets/whitepaper/og-18.jpg")))
    add_index("/bitcoin-whitepaper/", "Bitcoin Whitepaper", "strona", text_of(body), ["Zasoby"])

    en = data["en"]
    body = ('<article class="article wp" lang="en"><p class="kicker">Original text</p><h1>Bitcoin Whitepaper</h1>'
            '<p class="lede">The original paper by Satoshi Nakamoto, as plain text with its figures, equations and references.</p>'
            + card("en", "Bitcoin: A Peer-to-Peer Electronic Cash System", "Whitepaper, original")
            + f'<p class="note">Polish translation by meeDamian: <a href="{b("/bitcoin-whitepaper/")}" hreflang="pl">czytaj po polsku</a>.</p>'
            + wpp.toc_html("en", en) + wpp.paper_html("en", en, b, px)
            + wpp.footer_html("en", b, b("/")) + "</article>")
    write("/bitcoin-whitepaper/en/", layout("/bitcoin-whitepaper/en/", "Bitcoin Whitepaper (English)", body,
          desc="The Bitcoin white paper in English: full text with figures, equations and references, plus the original PDF.",
          crumbs=[("Bitcoin Whitepaper", "/bitcoin-whitepaper/")], og_image=b("/assets/whitepaper/og-18.jpg")))
    add_index("/bitcoin-whitepaper/en/", "Bitcoin Whitepaper (English)", "strona", text_of(body), ["Zasoby"])


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
    listed_rest = [p for p in rest if not (p.startswith("/projekty/") and p != "/projekty/")]  # partner pages: under ## Projekty
    if listed_rest:
        lines.append("## Optional\n")
        for p in sorted(listed_rest):
            t, d = known[p]
            lines.append(f"- [{t}]({SITE_URL}{md_url(p)})" + (f": {d}" if d else ""))
        lines.append("")
    projs = [p for p in pages_index if p["k"] == "projekt"]
    if projs:
        lines.append("## Projekty\n")
        for p in projs:
            d = re.sub(r"\s+", " ", p["x"]).strip()
            if len(d) > 150:
                d = d[:150].rsplit(" ", 1)[0].rstrip(".,:;") + "…"
            u = p["u"] if "#" in p["u"] else md_url(p["u"])
            lines.append(f"- [{p['t']}]({SITE_URL}{u}): {d}")
        lines.append("")
    lines.append("## Kontakt\n")
    lines.append(f"- Zaproszenie: {SITE_URL}{INVITE_PAGE}\n- X: {X_URL}\n- E-mail: {EMAIL}\n")
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
    return f"""<section class="prose-wide invite" id="invite">
<h2>Poproś o zaproszenie</h2>
<p>Podaj adres e-mail albo npub. Wyślemy Ci prywatne zaproszenie do społeczności.</p>
<form method="POST" action="{INVITE_ENDPOINT}" data-invite-form>
  <label for="invite-contact">Adres e-mail albo npub</label>
  <input id="invite-contact" type="text" name="contact" autocomplete="off" maxlength="254" required>
  <label class="invite__consent"><input type="checkbox" name="consent" value="yes" required><span>Zgadzam się, aby podany kontakt został użyty wyłącznie w sprawie zaproszenia.</span></label>
  <label class="invite__honeypot" aria-hidden="true">Nie wypełniaj tego pola<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label>
  <button class="btn btn--primary" type="submit">Poproś o zaproszenie</button>
  <p class="invite__status" data-invite-status aria-live="polite"></p>
</form>
<p class="note">Dane wykorzystamy wyłącznie do kontaktu w sprawie zaproszenia. Kontakt: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</section>
<section class="prose-wide">
<h2>Zanim napiszesz pierwszą wiadomość</h2>
<p>Jesteśmy społecznością Bitcoin Only. Nie promujemy altcoinów, tokenów ani „okazji inwestycyjnych”, nie wysyłamy linków polecających bez kontekstu i nie prosimy nikogo o seed. Pełne zasady: <a href="{b('/zasady/')}">Zasady społeczności</a>.</p>
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
        body += f'<p class="note proj-note">Linki sprawdzone {pl_date(data["checked"])}. Brakuje czegoś? <a href="{b(INVITE_PAGE)}">Napisz do nas</a>.</p>'
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
    internal = i["url"].startswith("{B}")  # e.g. the invitation form for the Telegram chats
    i = dict(i, url=fill(i["url"]))
    host = "dwadziesciajeden.pl" if internal else re.sub(r"^https?://(www\.)?", "", i["url"]).split("/")[0]
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
        f'Masz wątpliwość? <a href="{b(INVITE_PAGE)}">Napisz do nas</a>, zanim klikniesz albo coś wyślesz.',
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
             f'<li><a href="{b(INVITE_PAGE)}">Dołącz do Telegrama</a>: żadne pytanie nie jest głupie.</li></ul>'
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
