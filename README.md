# Dwadzieścia Jeden: site

Static rebuild of dwadziesciajeden.pl, the Polish Bitcoin-only community in the TwentyOne network.

- Preview: https://itstomekk.github.io/dwadziesciajeden/ (noindex until launch)
- Repo: https://github.com/itstomekk/dwadziesciajeden (GitHub Pages from `docs/` on `main`)

## Build

```bash
python build.py            # content/*.json + assets/ -> docs/ (stdlib only)
python qa/serve.py &       # http://127.0.0.1:8721/dwadziesciajeden/
cd qa && C:/Python314/python.exe qa_run.py   # Playwright Firefox gates
```

`DJ_BASE=""` builds for a custom domain at the root. `NOINDEX` in `build.py` must be set to `False` at launch.

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
