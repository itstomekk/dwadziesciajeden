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
- [x] TXT added by domain owner; [ ] click Verify at github.com/settings/pages   @tomek
- [x] launch build is the default, `docs/CNAME`, custom domain set in repo Pages settings
- [x] domain owner switched A/AAAA at Njalla, added `www` CNAME, kept MX/TXT
- [ ] enforce HTTPS, re-run QA against https://dwadziesciajeden.pl, submit sitemap   @agent
- [ ] keep Ghost backup until the new site is confirmed   @tomek

## Phase 3 — Content rounds   (NEXT)
- [ ] mine Telegram exports: places accepting BTC, translation history, chronicle events (no member names)   @agent
- [ ] Bitcoin w Parlamencie: press coverage, MP replies   @agent
- [ ] design polish: post headlines, project thumbnails, BTC Map embed centering   @agent
- [x] newsletter replaced by RSS (`/rss.xml`, kronika + artykuły) — owner 2026-10-26
- [ ] ask Gigi before using the Polish TwentyOne logo fork on merch   @tomek

## Backlog

## Done
1. Preview rebuild, rounds 1 to 3 — 2026-10-23
