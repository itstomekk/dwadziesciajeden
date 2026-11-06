# Handoff

## 2026-11-06: partner social media, Telegram chat cards, Laissez Faire + Bujać cards, footer (DEPLOYED da94a81)

- Social media on partners: new `social` list in `content/projekty.json` (`kind` = x, nostr, instagram, youtube, facebook, linkedin, github, tiktok, spotify, applepodcasts, rss; optional `label`). Cards on /projekty/ show an icon row (`social_row()`), partner subpages a "Social media" list, and the URLs go into the page's JSON-LD `sameAs`. Sources: each partner's own site footer (2026-11-06), plus web search for BitcoinWalk (@BitcoinWalkOrg) and Free Market Simpson (Instagram @freemarketsimpson). Telegram profiles of partners are left out because the build strips every t.me link. New CC0 icons from Simple Icons in `icon()`. BFF's X link moved from `links` to `social`.
- New friends cards: "Laissez Faire · Yellow Pill" (`/projekty/laissez-faire/`, story from the podcast's RSS feed: since 2019-07-19, 228 episodes, 14 Yellow Pill episodes 2021-2025) and "Bujać!" (`page: "/bujac/"`, so the card links to the existing /bujac/ page and no subpage is generated; `partner_path()` honours `page`). Images letterboxed from the official covers (`assets/projekty/laissez-faire.jpg`, `bujac.jpg`; raw Laissez Faire cover in `source-archive/project-images/`).
- Laissez Faire's podhome page links Tomek's X; both cards are under Zaprzyjaźnieni until the owner says they are "ours".
- /projekty/ inicjatywy: "Pomóż tłumaczyć" moved to the end; "Czaty i społeczności" gets two Telegram cards (main chat and Poznań, both "na zaproszenie", link = invitation form; `ini_card()` now accepts `{B}` internal URLs). Card images `assets/projekty/telegram-21.jpg`, `telegram-poznan.jpg` rendered from HTML. Initiative blocks are wider (`.cat .ini-grid` minmax 250px, 4 per row at 1280).
- Footer: "Zasady i sieć TwentyOne" link removed (the /zasady/ page stays; the brand line "Część sieci TwentyOne" stays).
- Satsback link `satsback.com/register/dlorDWND5JPeV7pw` is the referral link from the old Ghost page "Nasze projekty", which said it was a partner link; the "ponad 600 polskich sklepów" claim comes from the same old page.
- Built 60 pages, 254 search records; QA ALL PASS (10 gates, port 8771). Not committed, not pushed.

## 2026-11-06: partner subpages + 🟠 two-line header (DEPLOYED da94a81)

- Header/footer brand: logo image replaced by an 🟠 emoji (`LOGO` in build.py, `.mark--dot` in site.css) and the wordmark set on two lines "Dwadzieścia / Jeden" (owner picked option 2 of the mockups in `Hermes/image-gen/2026-11-06-dj-header-logo-variants/`).
- Every non-"ours" project (20) now has its own page `/projekty/<id>/` (`build_partner_pages`): card text, image, 2-3 paragraph Polish story (`story` in projekty.json), links (`links` + `more_links`), "U nas na stronie" list of kronika entries and pages that mention it (`match` terms), chips to other friends, WebPage+about JSON-LD. Card heading on /projekty/ links to the page. Pages are in search.json, sitemap.xml and llms.txt under ## Projekty.
- Stories come from 4 research subagents (private notes + sources in `private/partner-research/out-*.json`, gitignored); all 44 extra links returned 200 on 2026-11-06, key claims spot-checked. Card claims NOT confirmed by research: Satsback "600 polskich sklepów", DJP "pod przewodnictwem Gracjana Pietrasa" (he is one of the Bitcoin Desk partners), Alby's Polish team members, Freedom Publishing "od 2021", Nostrwall/zencharts author and date.
- Free Market Simpson card image re-made: the source photo had a ~30 px strip of another picture under the painting (rows 741+), now cropped off before compositing.
- Built 59 pages; QA ALL PASS (10 gates, port 8763). Not committed, not pushed.

## 2026-11-06: Free Market Simpson art project (DEPLOYED da94a81)

- Added Free Market Simpson (Polish free-market painter and muralist, free-market-simpson.is; his site links back to 21) at the end of Zaprzyjaźnieni in `content/projekty.json` (status "sztuka", kind "friends"), links: home + murals page. Card image `assets/projekty/free-market-simpson.jpg` = his painting "The old world recipe" letterboxed on a blurred copy; raw images in `source-archive/project-images/fms-*.jpg`.
- Built 39 pages, 251 search records; QA ALL PASS (10 PASS gates, port 8761). Anchor, llms.txt, llms-full.txt and search.json entries checked. Not committed, not pushed (deploy only on Tomek's word).

## 2026-11-03: partners reorder, Freedom Publishing, "Dołącz do Telegrama" label (deployed)

- /projekty/ Zaprzyjaźnieni: Filmweb removed; BitcoinWalk moved under bitblik; Alby moved under Cyfrowa Ekonomia; Freedom Publishing added at the end (publisher of the Polish "Standard Bitcoina", gave the campaign a good price; logo = their SVG rendered black on white, `assets/projekty/freedom-publishing.jpg`).
- Every "Poproś o zaproszenie" CTA (hero, join card, footer, edukacja, Kraków note) now reads "Dołącz do Telegrama" but still links to `/dolacz-do-nas/#invite` (owner chose label-only change). The form page keeps its own heading and button. Note: the label now promises Telegram while the link goes to the invitation form.

## 2026-11-03: BitcoinWalk partner + project anchor links (deployed)

- Added BitcoinWalk as a "partner" in `content/projekty.json` (status "partner", kind "friends"), linking bitcoinwalk.org and the Walkie Talkie companion app (bitcoinwalk.org/app). Card image `assets/projekty/bitcoinwalk.jpg` (official horizontal lockup centred on white); raw logos in `source-archive/project-images/` (gitignored).
- Each project heading on /projekty/ is now a self-link (`#id`, `#` marker) and llms.txt gained a "## Projekty" section listing every project with an anchor URL; those build.py/site.css edits went out inside the invitation-form commit 3d26804. search.json indexes projects by their `#id`.
- Built 39 pages; QA ALL PASS (11 gates). Deployed on Tomek's word.

## 2026-11-03: invitation-request flow (DEPLOYED, commit 3d26804)

- `/dolacz-do-nas/#invite` now has an email-or-npub invitation request form; public Telegram destination URLs are stripped from generated site pages. The form posts to `https://dj-invitations.kolotom.workers.dev/subscribe`.
- Added `signup-worker/`: D1 schema, origin allowlist, validation, consent, honeypot, blocklist, per-IP rate limit, idempotency, protected export, optional NIP-04 DM ping, and automated tests. No e-mail is sent (Resend dropped). Worker is separate from the BFF signup Worker.
- Verified: build 39 pages; site QA ALL PASS (11 gates); invitation-flow tests 2/2; Worker tests 5/5; local Wrangler end-to-end tests passed. Local QA/Wrangler processes have been stopped.
- Worker AND site DEPLOYED 2026-11-03 (commit `3d26804`, live-checked: form + action on /dolacz-do-nas/, no t.me links on home or join page, live POST from the site origin returned 201; test row deleted). Nostr DM pings ON (to Tomek and 21 npubs, live-verified). Read requests with `GET /admin/export`.
- Collected requests are read with `GET /admin/export` (Bearer ADMIN_KEY, `?format=csv`).
- Personal Nostr recipient confirmed by Tomek 2026-11-03; `signup-worker/wrangler.toml` matches `nostr-personal` in `social-media-tools/CONNECTIONS.json`. Open: dedicated bot key to sign the DMs.
- Next: confirm Nostr recipient/signing identity; complete D1, secrets, and sender setup; deploy and live-test the Worker; rerun site build/QA; publish only on Tomek's explicit instruction.

## 2026-10-31: white paper as full text (local, NOT deployed)

- `/bitcoin-whitepaper/` (Polish, meeDamian's translation) and new `/bitcoin-whitepaper/en/` (original) are now readable text pages with section anchors, 7 figures (PNG crops of the PDF pages), 4 equations (MathML), the C listing, result tables and linked references. Both PDFs stay as downloads, unchanged (SHA-256 on the page; PL equals bitcoin.org).
- Source of the text: `content/whitepaper.json`, made by `tools/extract_whitepaper.py` from the hosted PDFs (also exports `assets/whitepaper/*.png`). Rendering: `whitepaper_page.py`, called from `build.py` (`build_whitepaper`); CSS block `.wp-*` at the end of `assets/site.css`. The old imported page is skipped in the import loop.
- Fidelity gate: prose tokens vs PDF text, 99.7% (PL) / 99.8% (EN) of page tokens match in order; the rest are figure labels, equations, code and tables, which are not prose. Build 39 pages, QA ALL PASS (port 8721).
- DEPLOYED 2026-10-31 (commit cccd162, live-checked: PL and EN pages, figures, PDFs return 200 with new strings).
- Posts 2026-10-31 (Tomek approved exact text, drafts in `private/social/2026-10-31-whitepaper/v3/`): X https://x.com/21BitcoinPolska/status/2116575008679944319 (card ok, @meeDamian links to /meeDamian); Nostr https://njump.me/e4ffc06983e6145b3adda85066a49260928e27d3f415a2b094f7bd82d9f01e38 (primal.net and nos.lol read back, damus.io connection closed; p-tag meeDamian).
- 2026-10-31 OG: /bitcoin-whitepaper/ and /en/ use `assets/whitepaper/og-18.jpg` (gpt-image-2 art from PDF screenshots + site style, text composed in code; sources in `Hermes/image-gen/2026-10-31-21-whitepaper-18/`, chosen variant F2). Homepage OG (`assets/og.jpg`) unchanged; redesign options still open.
- Accounts wired: X session `x-21`, Nostr identity `21` (see social-media-tools).
- Markdown twins: `<math>` becomes an inline alt text and `<pre>` a fenced block (`_MD` in `build.py`).

## 2026-10-30: library shelf "Pieniądz, wolność i szkoła austriacka"

- New category `wolnosc` in `content/biblioteka.json` (after `ksiazki`): Hayek "Denacjonalizacja pieniądza" (Animi2 / Fundacja Lethe, 2019, ISBN 9788366303010), Mises "Ludzkie działanie" (Instytut Misesa, sklep.mises.pl), Rand "Atlas zbuntowany" (Zysk i S-ka). Covers in `assets/books/` (Mises cover cropped from the shop's flat image and upscaled 2x; the others from lubimyczytac.pl). Links point to lubimyczytac.pl for Hayek and Rand because publisher shops do not sell them (Zysk shows it unavailable; Animi2 site unreachable). The `checked` date was not bumped. Built, QA ALL PASS on port 8811 (8741 is in a Windows reserved port range). Not committed, not deployed.
## 2026-10-30: buying guide and Bitomat.com

- Private, unpublished buying-guide draft: `private/poradnik-jak-kupic-bitcoin-draft.md`. Provider pages checked 2026-10-30; live P2P PLN liquidity and end-to-end purchase remain unverified. Recheck changing conditions and tax advice before publishing.
- Bitomat.com added to friendly projects locally, with official logo. The site describes itself as a directory, not the machines' operator. No deploy in this session.
- Build succeeded. QA on port 8796: ALL PASS on rerun. Earlier mobile overflow happened in a transient build containing concurrent support-widget markup with missing CSS; that work subsequently disappeared from the working tree, and the current source rebuild has no such markup. One rerun also hit a Firefox context-close error before a successful retry. Do not infer the support-widget work was fixed or deployed.

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

## Round 7 (2026-10-30): /bujac/ podcast page

- New `/bujac/` (`build_bujac()` in build.py, data `content/bujac.json`, images `assets/bujac/`, styles `.bujac-hero`/`.ep*` at the end of site.css): 18 episodes in Sezon 1/2/Docinki/Sezon 3 with illustration thumbnails (captioned as illustrations, not official covers), tags, Spotify/YouTube-trailer/archive links. Listed in llms.txt (Edukacja) and the library entry in `/edukacja/` now links to it (`{B}/bujac/`, internal links in `res_row` supported). QA ALL PASS. NOT yet committed or pushed (deploy only on Tomek's word).
- Gotcha: port 8733 is blocked by Windows here (WinError 10013); run QA on another port via `DJ_QA_PORT`.

## Round (2026-11-06): Ryszard Zalski as partner

- New friends card + subpage `/projekty/ryszard-zalski/` (status `partner`, schema Person), appended last in `content/projekty.json`. Owner: "friend of the site, make him the partner". Sources: youtube.com/@RyszardZalski about page + RSS (channel "Gospodarka & Geopolityka", joined 6 Apr 2025), wnet.fm 2025-03-07 (Pomarańczowe Studio Radia Wnet, "Prowadzi Ryszard Zalski"), wnet.fm Poranek Wnet 2022 (Studio Tajpej), `content/bujac.json` s2-e07. Image `assets/projekty/ryszard-zalski.jpg` = channel avatar (Radio Wnet studio photo) letterboxed over blur; raw in `source-archive/project-images/`.
- `build.py`: optional `name_with` field (instrumental case) for the partner-page note ("historię z Ryszardem Zalskim"); falls back to `name`.
- Build: 61 pages, 255 search records. QA 10 PASS, ALL PASS.
- DEPLOYED 2026-11-06 on Tomek's "publish all": commit `da94a81` pushed everything that was local (all 2026-11-06 rounds above: partner subpages, header, social icons, Telegram cards, Laissez Faire/Bujać/Free Market Simpson cards, Zalski). Live-checked: /projekty/ card anchors + image, /projekty/ryszard-zalski/, llms.txt, search.json, sitemap.xml.
