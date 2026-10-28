# Handoff

Updated 2026-10-23.

## State

- Live at https://dwadziesciajeden.pl (GitHub Pages custom domain). Old github.io preview URL redirects there.
- 36 pages. QA: ALL PASS (old URLs 26/26, internal links, console errors, overflow, search, chronicle filter).
- Done in round 2:
  - Friendly projects added: bitblik, Cryptosteel, Bitcoin District (`content/projekty.json`).
  - Polish projects: `/inicjatywy/` (sections: Polskie projekty, Pomóż tłumaczyć, Organizacje, Wydarzenia, Czaty). `/polskie-projekty/` redirects there.
  - Full article `/bitcoin-w-parlamencie/` (sources: @21BitcoinPolska posts Oct 2025 to Jan 2026, campaign page, Geyser).
  - Warsaw regulars on `/warszawa/` and `/inicjatywy/`: BitcoinWalk Saturdays 11:30 (Ogród Saski, Fontanna Wielka), Bitcoin Café Mondays 18:00 (meetup.com/bitcoin-warsaw).
  - `/biblioteka/` with 13 book covers (local copies in `assets/books/`), sites, recordings. `/zasady/` from twentyone.world.
  - Telegram group t.me/dwadziesciajeden exported read-only (`tools/tg_export_topics.py`): topics "Bitcoin w Polsce i po polsku" (2324 msgs), "Bitcoin po Polsku" (2060), plus "Linki i polecajki" and "Projekty, appki". Files in `source-archive/telegram/` (private, gitignored). Only public resource links were used on the site; no member messages or names are published.

- Round 3 (owner feedback): old site look restored (white, amber #F2A900, original "21 Bitcoin Polska" logo from Ghost, Montserrat headings to match the logo; old theme CSS in `source-archive/oldtheme/`). Armada Nostr community link added (header join grid, footer, inicjatywy). Poznań walks = meetup.com/poz21m ("Spacery ku wolności"). Added Laissez Faire, bitcoin.pl, PSB; removed YouTube Bitcoin Polska. DJP stays as friend and Bitcoin lawyer.

## Domain cutover (dwadziesciajeden.pl): LIVE since 2026-10-23

- Live at http://dwadziesciajeden.pl (Pages cname set; DNS resolves to GitHub at Njalla, 1.1.1.1, 8.8.8.8). `www` works, 26/26 old URLs 200. HTTPS cert was pending at launch; enforce HTTPS once it is issued.
- Default `python build.py` now builds the LIVE site (root base, indexable, CNAME). Never push a project-path preview build.
- Open: Tomek clicks Verify for dwadziesciajeden.pl at github.com/settings/pages (API showed `protected_domain_state: unverified`; TXT record is in place).
- HTTPS enforced (cert approved, expires 2027-01-24, GitHub renews).
- Analytics + crawler doors (2026-10-26): GoatCounter site `dwadziesciajeden21` since 2026-10-27 (https://dwadziesciajeden21.goatcounter.com, cookieless; the old code `dwadziesciajeden` was created nested under roatanlive and is unreadable, so it was replaced; header "Dołącz" counts as event `dolacz-telegram-naglowek`). Every layout page gets a Markdown twin `<page>/index.md` + `<link rel="alternate" type="text/markdown">`; `/llms.txt` (index, sections in `LLMS_SECTIONS`) and `/llms-full.txt` (all twins). robots.txt: `Content-Signal: search=yes, ai-input=yes` (ai-train left unset until the owner decides). Home has JSON-LD Organization + WebSite. IndexNow key file `/<INDEXNOW_KEY>.txt`; sitemap submitted 2026-10-26 (202). GitHub Pages cannot send `X-Robots-Tag` for the .md twins.
- GoatCounter check (2026-10-26): all 31 content pages carry the snippet; the 7 `Przeniesiono` meta-refresh stubs (`/author/jesterhodl/`, `/biblioteka/`, `/inicjatywy/`, `/mapa/`, `/meetupy/`, `/miasta/`, `/polskie-projekty/`) deliberately do not, because they redirect at once and would double-count the hit.
- Someone edits `docs/CNAME` through the GitHub UI: always `git fetch` + rebase before pushing.
- Local QA `console-errors` fails only because mempool.space is unreachable from Tomek's network (block-height widget), not a site bug.

History of the cutover:

- Domain owner is Tomek's colleague. DNS at Njalla (njal.la), mail at Proton (MX + TXT must stay). Old web host (Ghost): A `151.115.73.132`, AAAA `2001:bc8:1d90:123:dc00:ff:fe09:69c7` (rollback values).
- Tomek added `dwadziesciajeden.pl` under github.com/settings/pages (account itstomekk). Pending TXT, for the colleague to add: `_github-pages-challenge-itstomekk` = `dfe0834c3de16736ecf92e4cb1c948`. Then click Verify.
- Colleague's DNS change: delete old A/AAAA on `@`; add A 185.199.108-111.153, AAAA 2606:50c0:8000-8003::153, CNAME `www` -> `itstomekk.github.io`.
- Launch (only after A records resolve to GitHub, check `nslookup dwadziesciajeden.pl 1-you.njalla.no`):
  `DJ_BASE= DJ_SITE_URL=https://dwadziesciajeden.pl DJ_NOINDEX=0 python build.py` (writes `docs/CNAME`, robots Allow + sitemap), QA with
  `DJ_BASE= python qa/serve.py 8733` + `DJ_BASE= DJ_QA_PORT=8733 C:/Python314/python.exe qa/qa_run.py` (gate `launch-indexable`), commit, push,
  then `gh api -X PUT repos/itstomekk/dwadziesciajeden/pages -f cname=dwadziesciajeden.pl`, wait for the cert, `-F https_enforced=true`.
- A preview build (default env) never writes CNAME. Do not push a launch build before DNS points to GitHub: the github.io preview would redirect to a dead domain.
- Port 8721 may be held by a stale preview server from another session; use another port via `DJ_QA_PORT`.

## Round 4 (owner feedback 2026-10-26, QA ALL PASS, live: went out inside commit a59d7e3, which another session pushed with `git add -A`)

- README.md is now a welcoming, human-facing Polish page (hero screenshot `.github/readme/home.jpg`); the technical notes moved to DEVELOPMENT.md.
- Friend added: Cyfrowa Ekonomia (cyfrowaekonomia.pl, status "partner"; logo = their SVG rendered white on dark, `assets/projekty/cyfrowa-ekonomia.jpg`). Note: the portal also covers altcoins; listed at the owner's request.
- QA gate `launch-indexable` now checks only the `User-agent: *` group (named AI-training bots are disallowed on purpose).

- Founding = first message of Telegram group yellowpilled, 2021-04-05 16:56:13 UTC; chain tip then = block 677896 (`FOUNDING_BLOCK` in build.py). Home dateline says "Bitcoin Only od bloku #677 896" (the live current-block item there was removed; the shell `getblockcount` line still shows the live tip).
- Facts bar starts at 2021; new `stages_html()` strip (2021 to 2026, each links to `/kronika/#rok-YYYY`, every claim backed by a kronika entry).
- YouTube links in lists (Edukacja/biblioteka `res_row`, initiative cards, project links) render as click-to-play thumbnails (`yt_frame()`, youtube-nocookie iframe only after click).
- Removed kronika entry "Pomarańczowe tulipany w Poznaniu".
- Newsletter column replaced by RSS: `/rss.xml` (60 newest articles + kronika entries; each kronika entry now has a stable id from `chron_id()`), `<link rel=alternate>` in every head.
- Background: big Bitcoin mark (`BTC_MARK`, amber) fixed behind everything at 5% opacity; site.js sets `--sp` (scroll progress) and CSS turns/drifts/scales it slightly. Off for reduced motion and print.

## Round 5 (2026-10-26)

- Biblioteka: new section "Katalogi i listy" (`/edukacja/#katalogi`) with Awesome Bitcoin Culture and Awesome Bitcoin Events (owner request). Live, QA ALL PASS, commit 14a5b74.
- Friendly-project candidates mined from both Telegram groups, checked live: `private/friendly-projects-candidates-2026-10-26.md` (local only, not in git). Owner picked 1, 2, 4, 6, 7, 10: live (commit abf6107). Round 2 (#11-17): owner skipped WallAxe, cryptoproducts.cz, Clinch, Fedimint on Start9 (2026-10-27); lnalias stays on hold (TLS cert for the wrong host). Old git history keeps one public GitHub nick from an earlier candidate list: owner said leave it. the conversation continues in Telegram HERMES CONTROL CENTER, topic GENERAL 2 (4359). Ask authors before listing member-built tools (old group rule: added with the author's consent).

## Round 6 (2026-10-26): own BTC Map view

- GitHub Pages custom domain verified by the owner (API: protected_domain_state verified, https_enforced true).
- Map page and all 5 city pages: btcmap.org iframes replaced by our Leaflet map + filters + grouped list (see DEVELOPMENT.md "Map"). Snapshot 2026-10-27 UTC: 302 places in PL (160 ATMs, 51 exchanges, 91 merchants); 5 places across the border dropped. QA ALL PASS.
- Data is a snapshot: manual refresh = `python tools/fetch_btcmap.py && python build.py`.
- Monthly refresh (owner asked 2026-10-27): Hermes cron `bf6d33ac848f` `dwadziesciajeden-btcmap-monthly`, 1st of the month 04:00, no-agent, wrapper `%LOCALAPPDATA%\hermes\scripts\dj_btcmap_monthly.py` -> `tools/refresh_btcmap_monthly.py`. Works in a fresh clone (local edits never published), aborts if the place count drops >20%, commits only `content/btcmap-pl.json` + `docs/`, pushes, posts one line to HCC GENERAL 2 (silent when nothing changed).
- 2026-10-27: map made compact (full content width, search + selects in one row, chips + payments in a second row) and ATMs + exchanges merged into one toggle chip "Bankomaty i kantory".

## Owner rules

- Owner 2026-10-23: the community started as Telegram group "yellowpilled" (created 2021-04-05); the current group was created 2022-06-06 as a redesign joining the 21 network. BFF grew out of 21. Topic restrictions: see private/NOTES.md (local only). Sometimes call altcoins "sh**coiny". Friends added: Alby, Deltabadger, Quark (Quark is NOT in YouBuyBitcoin Orange Pages as of 2026-10-23; its network notice says shops reopen 2026-11-02 after MiCA licensing).
- Kronika now has 93 entries: 63 from a read-only review of the whole Telegram group (17 topics, ~50k messages, exported 2026-10-23 with `tools/tg_export_topics.py --all`; digests + per-topic candidate JSON in `source-archive/telegram/digest/`, private). Telegram-sourced entries carry `"source": "telegram"` and a link to the main chat only. Left out on purpose: moderation disputes, credit disputes, politics, the Bitcoin Poland conference, individual trades.

- Miasta live inside Mapa (`/bitcoinowa-mapa-polski/#miasta`); `/miasta/` and `/meetupy/` redirect there. Nav: Kim jesteśmy, Edukacja, Mapa i miasta, Projekty, Biblioteka, Kronika.
- `/edukacja/` = mission + Bitcoin basics + six steps + scam warning + the whole Biblioteka (`#biblioteka`, `catalog_html()`); `/biblioteka/` redirects there. Education only, never investment advice.
- Telegram Poznań is not promoted on the home page (stays on the Poznań city page). Telegram/X/Nostr links carry CC0 icons (`icon()` in build.py).

- Look = old amber/white identity + "hacker layer" (end of `assets/site.css`): JetBrains Mono for UI voice (`//` kickers, `##` section titles, `./` index rows), square corners, terminal hero (`.shell`, live block height from mempool.space via `[data-tip]`, silent fallback), dark stats bar and console join band, project images grayscale until hover. Owner does not use many photos: prefer type and terminal motifs over imagery. Note `.term` is the glossary class; terminal styles use `.shell`.

- Every project and initiative card gets an image. Sources: og:image / logo from the project's own site, Geyser API (`api.geyser.fund/graphql`, `projectGet.thumbnailImage`), or our own X media. Normalised to 800x600 JPG in `assets/projekty/` (wide text banners letterboxed on a blurred copy, logos centred on a plain background). Raw downloads in `source-archive/project-images/`.
- Projekty and Inicjatywy are one page (`/projekty/`); `/inicjatywy/` and `/polskie-projekty/` redirect there. Do not list the same thing twice (projects win over initiative cards).
- Never quote Telegram members by name.
- Anatomia Bitcoina is PSB's, not ours; we only helped translate some materials.
- No Bitcoin Poland conference. Satsback is Polish, no need to say so.

## Facts to keep straight

- BitcoinWalk Warszawa: Tomek said Saturdays 11:00; bitcoinwalk.org and Meetup both list 11:30. Site shows 11:30.
- Bitcoin Café venue in late Sept 2026: Vita Cafe, Dobra 42. Site says "check the Meetup event" instead of a fixed venue.
- meetup.com/krakow-bitcoin-meetup is gone ("Group not found"); Kraków page now points to the chat.
- bitcoinwalk.org/wroclaw/ and /poznan/ return 404.
- bujac.pl is behind a Cloudflare challenge (403 to scripts, fine in a browser).

## Plan (next rounds)

1. Mine the Telegram exports further: Polish places accepting BTC, translation history, events timeline for the chronicle. Ask before quoting any member by name.
2. Newsletter: decide tool (Nostr long-form, Substack, Buttondown) and fill the placeholder.
3. Design polish: post headlines instead of repeated "Post na X", project thumbnails for letter placeholders (bitblik, Cryptosteel, Bitcoin District logos with permission), city pages BTC Map embed centering.
4. Bitcoin w Parlamencie: add press coverage (bitcoin.pl, comparic.pl link is 404 now) and any replies from MPs.
5. Launch: point dwadziesciajeden.pl (Ghost today) at Pages, set `DJ_BASE=""`, `NOINDEX=False`, add CNAME, submit sitemap.
6. TwentyOne logo: brand is open source; Gigi granted a licence privately (owner, 2026-10-27). Merch use is cleared.

## Round 7 (2026-10-28): headline of the day

- Home h1 shows one phrase per day (18 phrases: 5 first + 13 owner picks from a list of 30, 2026-10-28), no animation (owner: "napisy nie mają się zmieniać, po prostu mogą być inne każdego dnia"). List in `HERO_PHRASES` (build.py, "|" = line break), cycled by the visitor's local date, so everyone sees the same phrase that day. Static HTML and crawlers get "Dwadzieścia Jeden"; an inline script right after the h1 swaps it before first paint (no flash). `text_of()` strips scripts so it stays out of search.json. h1 `white-space:nowrap` keeps the planned line break (checked 320 to 1920 px).
- Narrow phones (<375px): header tightened (smaller brand/buttons; <340px brand wraps to two lines), book grid uses minmax(0,1fr) + hyphens. All 37 pages have no horizontal scroll at 320px.
