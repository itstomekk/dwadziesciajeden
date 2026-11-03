# Organization log

## 2026-11-03 — Invitation request backend

- Added `signup-worker/` as a dedicated Cloudflare Worker and D1 implementation for email/npub invitation requests. It remains a subproject of `dwadziesciajeden-site`; it is separate from the Bitcoin FilmFest signup Worker to keep storage, notification identity, and deployment lifecycle independent.
- Later the same day: D1 `dj-invitations` and Worker `dj-invitations` created on Cloudflare (storage only, no e-mail). Site not pushed.
