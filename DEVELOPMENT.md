# Development

Static rebuild of dwadziesciajeden.pl, the Polish Bitcoin-only community in the TwentyOne network.

- Live: https://dwadziesciajeden.pl (GitHub Pages custom domain, DNS at Njalla, owned by a colleague)
- Repo: https://github.com/itstomekk/dwadziesciajeden (GitHub Pages from `docs/` on `main`)

## Build

```bash
python build.py            # content/*.json + assets/ -> docs/ (stdlib only)
python qa/serve.py &       # http://127.0.0.1:8721/
cd qa && C:/Python314/python.exe qa_run.py   # Playwright Firefox gates
```

Defaults build the live site (root base, indexable, `docs/CNAME`). The old project-path preview needs `DJ_BASE=/dwadziesciajeden DJ_SITE_URL=https://itstomekk.github.io/dwadziesciajeden DJ_NOINDEX=1` and must never be pushed.

## Content

| File | What |
|---|---|
| `content/imported.json` | Pages and posts imported from the old Ghost site (via `import_content.py`) |
| `content/artykuly.json` | New articles written for this site (e.g. Bitcoin w Parlamencie) |
| `content/kronika.json` | Chronicle, curated from @21BitcoinPolska posts and the community chat (no member names) |
| `content/projekty.json` | Our projects and friendly projects |
| `content/inicjatywy.json` | Polish projects, organizations, events, translation work, chats |
| `content/biblioteka.json` | Books, sites, recordings in Polish |
| `content/zasady.json` | Community rules and the TwentyOne concept |
| `content/miasta.json` | City index |
| `content/btcmap-pl.json` | BTC Map snapshot for Poland (from `tools/fetch_btcmap.py`), drawn by `assets/mapa.js` |

Generated extras: `/rss.xml` (articles + chronicle), `/llms.txt`, `/llms-full.txt`, Markdown twins (`<page>/index.md`), `sitemap.xml`, `search.json`.

`source-archive/` (gitignored) holds raw captures: Ghost dump, Wayback, X media, and Telegram topic exports.
See `HANDOFF.md` for state and the plan.

## Map (Bitcoinowa Mapa Polski + city pages)

`/bitcoinowa-mapa-polski/` and every city page render our own map (`btcmap_app()` in build.py, `assets/mapa.js`,
styles `.bmap*` at the end of `assets/site.css`), not the btcmap.org iframe. Leaflet 1.9.4 and Leaflet.markercluster 1.5.3
are vendored in `assets/vendor/` (licenses alongside). Tiles: OpenStreetMap standard, shown in grayscale by CSS
(CARTO did not resolve from the owner's network).

Refresh the data, then rebuild:

```bash
python tools/fetch_btcmap.py   # BTC Map v4 places inside the PL polygon; city/voivodeship from Nominatim, cached in source-archive/btcmap/
python build.py
```

Filters: category (ATMs and exchanges off by default on the country map, on for city pages), payment (Lightning,
on-chain, contactless; all selected must match), city, freshness (confirmed in 1 or 2 years), search; list grouped by
city, voivodeship or category. Filter state lives in the query string (`?kat=…&platnosc=ln&miasto=…&grupuj=woj&q=…`).
City pages lock the city by the name in `content/miasta.json`, which must match the Nominatim/OSM city name.
