# PLAN — Dwadzieścia Jeden site

**Program:** dwadziesciajeden
**Status:** active
**Phase:** 2 of 3 — Launch on dwadziesciajeden.pl
**Last reviewed:** 2026-10-23

## Goal
dwadziesciajeden.pl serves this static site from GitHub Pages over HTTPS, indexed, with old Ghost URLs still working and Proton mail untouched.

## Phase 1 — Rebuild and preview   (DONE)
- [x] Ghost import, new sections, QA gates, preview at itstomekk.github.io/dwadziesciajeden/

## Phase 2 — Domain cutover   (ACTIVE)
- [ ] verify dwadziesciajeden.pl in GitHub account (Settings > Pages > Verified domains), give TXT to domain owner   @tomek
- [ ] build with `DJ_BASE=""`, `NOINDEX=False`, add `docs/CNAME`, set custom domain in repo Pages settings   @agent   BLOCKED: wait for Tomek's go
- [ ] domain owner switches A/AAAA at Njalla to GitHub Pages, adds `www` CNAME, keeps MX/TXT   @tomek
- [ ] enforce HTTPS, re-run QA against https://dwadziesciajeden.pl, submit sitemap   @agent
- [ ] keep Ghost backup until the new site is confirmed   @tomek

## Phase 3 — Content rounds   (NEXT)
- [ ] mine Telegram exports: places accepting BTC, translation history, chronicle events (no member names)   @agent
- [ ] Bitcoin w Parlamencie: press coverage, MP replies   @agent
- [ ] design polish: post headlines, project thumbnails, BTC Map embed centering   @agent
- [ ] ?? newsletter tool (Nostr long-form, Substack, Buttondown)   DECIDE
- [ ] ask Gigi before using the Polish TwentyOne logo fork on merch   @tomek

## Backlog

## Done
1. Preview rebuild, rounds 1 to 3 — 2026-10-23
