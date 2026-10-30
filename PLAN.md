# PLAN — Dwadzieścia Jeden site

**Program:** dwadziesciajeden
**Status:** active
**Phase:** 2 of 3 — Launch on dwadziesciajeden.pl
**Last reviewed:** 2026-10-23 (site live on the domain)

## Goal
dwadziesciajeden.pl serves this static site from GitHub Pages over HTTPS, indexed, with old Ghost URLs still working and Proton mail untouched.

## Phase 1 — Rebuild and preview   (DONE)
- [x] Ghost import, new sections, QA gates, preview at itstomekk.github.io/dwadziesciajeden/

## Phase 2 — Domain cutover   (ACTIVE)
- [x] TXT added by domain owner; [x] click Verify at github.com/settings/pages   @tomek (2026-10-26)
- [x] launch build is the default, `docs/CNAME`, custom domain set in repo Pages settings
- [x] domain owner switched A/AAAA at Njalla, added `www` CNAME, kept MX/TXT
- [x] enforce HTTPS, re-run QA against https://dwadziesciajeden.pl, submit sitemap   @agent
- [x] Ghost backup: kept permanently as an archive (owner, 2026-10-27)

## Phase 3 — Content rounds   (NEXT)
- [ ] Finish buying-Bitcoin guide: verify Polish service availability and conditions, assess KYC/privacy and P2P risks; private draft in `private/poradnik-jak-kupic-bitcoin-draft.md`.
- [ ] mine Telegram exports: places accepting BTC, translation history, chronicle events (no member names)   @agent
- [ ] Bitcoin w Parlamencie: press coverage, MP replies   @agent
- [x] own BTC Map view with filters and grouping (replaces the iframes) 2026-10-26
- [ ] design polish: post headlines   @agent
- [x] newsletter replaced by RSS (`/rss.xml`, kronika + artykuły) — owner 2026-10-26
- [x] TwentyOne logo on merch: brand is open source and Gigi granted a licence privately (owner, 2026-10-27)

## Backlog

## Done
1. Preview rebuild, rounds 1 to 3 — 2026-10-23
