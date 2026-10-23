# Handoff

Updated 2026-10-23.

## State

- Preview live at https://itstomekk.github.io/dwadziesciajeden/ (noindex, robots Disallow all).
- 36 pages. QA: ALL PASS (old URLs 26/26, internal links, console errors, overflow, search, chronicle filter).
- Done in round 2:
  - Friendly projects added: bitblik, Cryptosteel, Bitcoin District (`content/projekty.json`).
  - Polish projects: `/inicjatywy/` (sections: Polskie projekty, Pomóż tłumaczyć, Organizacje, Wydarzenia, Czaty). `/polskie-projekty/` redirects there.
  - Full article `/bitcoin-w-parlamencie/` (sources: @21BitcoinPolska posts Oct 2025 to Jan 2026, campaign page, Geyser).
  - Warsaw regulars on `/warszawa/` and `/inicjatywy/`: BitcoinWalk Saturdays 11:30 (Ogród Saski, Fontanna Wielka), Bitcoin Café Mondays 18:00 (meetup.com/bitcoin-warsaw).
  - `/biblioteka/` with 13 book covers (local copies in `assets/books/`), sites, recordings. `/zasady/` from twentyone.world.
  - Telegram group t.me/dwadziesciajeden exported read-only (`tools/tg_export_topics.py`): topics "Bitcoin w Polsce i po polsku" (2324 msgs), "Bitcoin po Polsku" (2060), plus "Linki i polecajki" and "Projekty, appki". Files in `source-archive/telegram/` (private, gitignored). Only public resource links were used on the site; no member messages or names are published.

- Round 3 (owner feedback): old site look restored (white, amber #F2A900, original "21 Bitcoin Polska" logo from Ghost, Montserrat headings to match the logo; old theme CSS in `source-archive/oldtheme/`). Armada Nostr community link added (header join grid, footer, inicjatywy). Poznań walks = meetup.com/poz21m ("Spacery ku wolności"). Added Laissez Faire, bitcoin.pl, PSB; removed YouTube Bitcoin Polska. DJP stays as friend and Bitcoin lawyer.

## Domain cutover (dwadziesciajeden.pl), in progress 2026-10-23

- Domain owner is Tomek's colleague. DNS at Njalla (njal.la), mail at Proton (MX + TXT must stay). Old web host (Ghost): A `151.115.73.132`, AAAA `2001:bc8:1d90:123:dc00:ff:fe09:69c7` (rollback values).
- Tomek added `dwadziesciajeden.pl` under github.com/settings/pages (account itstomekk). Pending TXT, for the colleague to add: `_github-pages-challenge-itstomekk` = `dfe0834c3de16736ecf92e4cb1c948`. Then click Verify.
- Colleague's DNS change: delete old A/AAAA on `@`; add A 185.199.108-111.153, AAAA 2606:50c0:8000-8003::153, CNAME `www` -> `itstomekk.github.io`.
- Launch (only after A records resolve to GitHub, check `nslookup dwadziesciajeden.pl 1-you.njalla.no`):
  `DJ_BASE= DJ_SITE_URL=https://dwadziesciajeden.pl DJ_NOINDEX=0 python build.py` (writes `docs/CNAME`, robots Allow + sitemap), QA with
  `DJ_BASE= python qa/serve.py 8733` + `DJ_BASE= DJ_QA_PORT=8733 C:/Python314/python.exe qa/qa_run.py` (gate `launch-indexable`), commit, push,
  then `gh api -X PUT repos/itstomekk/dwadziesciajeden/pages -f cname=dwadziesciajeden.pl`, wait for the cert, `-F https_enforced=true`.
- A preview build (default env) never writes CNAME. Do not push a launch build before DNS points to GitHub: the github.io preview would redirect to a dead domain.
- Port 8721 may be held by a stale preview server from another session; use another port via `DJ_QA_PORT`.

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
6. TwentyOne logo: no formal license; ask Gigi (dergigi.com/contact) before using the Polish fork on merch.
