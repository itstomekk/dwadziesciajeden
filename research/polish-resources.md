# Polish Bitcoin resources — verification summary

Checked: 2026-10-23. Data: `polish-resources.json` (38 verified items + `unverified` + `excluded` lists).
Method: every URL fetched (Python urllib with browser UA; web_extract for YouTube / Geyser / Meetup). All 38 items returned HTTP 200 on the final pass. `description_pl` is written fresh in Polish, not copied from publishers.

## Counts per category
| category | items |
|---|---|
| books | 13 (7 FP books, 2 FP bundles, 4 Helion) |
| communities | 7 (2 Telegram, X, 4 BTC Map city pages) |
| organizations | 5 (PSB, twentyone.world, Satsback, Parliament campaign, Bitcoin in Polish/Geyser) |
| events | 5 (BFF, Bitcoin Poland, Bitcoin Warsaw, BitcoinWalk Warszawa, Poznań BitcoinWalk) |
| websites | 4 (Archiwum Bitcoina, whitepaper PL PDF, bitcoin.org/pl, bitcoinpl.org) |
| tools | 2 (BTC Map Poland, BTCPay /pl) |
| podcasts-video | 2 (Bitcoin Polska YT, Laissez Faire) |

## Books
All 9 products from wydawnictwofp.pl/temat/ekonomia/bitcoin/ are in (7 books + 2 bundles, type `bundle`). Each has an og:image URL that returns 200, plus ISBN, translator and original title in `extra`. Helion adds 4 Polish editions: Rosenbaum, Antonopoulos/Harding, Antonopoulos/Osuntokun/Pickhardt (Lightning), Jimmy Song.
No separate Polish "Mały Bitcoiner" / "Little Bitcoin Book" edition found, so none listed. I did not look for other bitcoin books from other publishers beyond Helion.

## Dubious / needs a human decision
- **Gilder, "Standard złota w epoce pieniądza cyfrowego"**: book is about gold (2015), not Bitcoin. FP files it under Bitcoin. Fine as "sound money", not as a Bitcoin title.
- **Bitcoin Poland conference (Poznań, 5–6 Oct 2026)**: already happened; calls itself bitcoin-only, but the speaker list includes Michael Terpin (Transform Ventures) and the founder of DeFi Talks. Part of Invest Cuffs. Don't label it bitcoin-only without checking.
- **Bitcoin FilmFest BFF'26** was co-located with MoneroKon (per its own press page). Included, flagged.
- **Satsback.com**: "Polish-founded" is NOT confirmed. Own AMA says "based in Europe"; dwadziesciajeden.pl lists it as a project and says it co-runs the Kraków meetup.
- **bitcoinpl.org**: says "bitcoin only, since 2019", but the owner is unknown and the guides point to MiCA-compliant exchanges (likely affiliates). Review manually.
- **Polskie Stowarzyszenie Bitcoin**: site says founded 2013, Szczecin, KRS 0000480255. Not strictly bitcoin-only (also covers "emisja kryptowalut").
- **Laissez Faire PL** is a general libertarian podcast; only the "₿ujać – O Bitcoinie po polsku" series is about Bitcoin. Activity not verified.
- **YouTube @bitcoinpolska**: loads, but ~32 subscribers, 6 videos, last ~3 years ago. The Oskar Pilch attribution comes from dwadziesciajeden.pl/projekty/, not from the channel.
- **BTCPay /pl**: only the translation of the site was checked; the page calls it a "cryptocurrency" processor.

## Could NOT verify (in `unverified`)
- jesterhodl.com — connection refused (https, http, www).
- Kraków Bitcoin Meetup — meetup.com says "Group not found" (dwadziesciajeden.pl/krakow/ still links it).
- t.me/BitcoinWarsaw — only a "Contact @BitcoinWarsaw" stub, no group preview.
- btcmap.org/community/dwadzieścia-jeden — 404 (entry marked `trash` in the BTC Map API). City pages (Warszawa, Poznań, Wrocław, Katowice) work. dwadziesciajeden.pl/projekty/ links the dead URL.
- Bitcoin Poland Silesia — BTC Map page and its website both 404.
- Dwadzieścia Jeden Nostr npub / `wss://relay.dwadziesciajeden.pl` — listed on the site, not tested over Nostr.

## Excluded (not bitcoin-only)
Bitcoin Radio podcast (altcoin episodes), bitcoin.pl / bithub.pl, pl.wikibooks "Bitcoin i kryptowaluty", Filmweb and the DJP law firm.

## Other notes
- Telegram t.me pages return 200 even for non-groups; I counted only pages that showed a title and member count (290 and 59 on 2026-10-23).
- Next BitcoinWalk Warszawa: Sat 24 Oct 2026, 11:30, Ogród Saski (per the page). The Poznań BitcoinWalk Meetup page loads, but bitcoinwalk.org/poznan/ is 404.
- The Satsback link on dwadziesciajeden.pl is an affiliate link; the JSON uses the plain URL.
