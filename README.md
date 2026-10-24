# Dwadzieścia Jeden: site

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
| `content/kronika.json` | Chronicle, curated from @21BitcoinPolska posts |
| `content/projekty.json` | Our projects and friendly projects |
| `content/inicjatywy.json` | Polish projects, organizations, events, translation work, chats |
| `content/biblioteka.json` | Books, sites, recordings in Polish |
| `content/zasady.json` | Community rules and the TwentyOne concept |
| `content/miasta.json` | City index |

`source-archive/` (gitignored) holds raw captures: Ghost dump, Wayback, X media, and Telegram topic exports.
See `HANDOFF.md` for state and the plan.
