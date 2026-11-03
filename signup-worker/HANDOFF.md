# Handoff

- Worker DEPLOYED 2026-11-03 at `https://dj-invitations.kolotom.workers.dev` (version 963fb8d1) and the site form is live (commit `3d26804`). Stores e-mail/npub requests in D1; sends NO e-mail (Resend dropped on Tomek's decision).
- Local verification passed 2026-11-03: `npm test` (5/5), `node --check src/index.js`, Wrangler local D1 end-to-end checks (health, insert, duplicate, invalid contact, honeypot, foreign origin), and site QA ALL PASS. Local test rows were deleted; local servers are stopped.
- Remote D1 `dj-invitations` created 2026-11-03 (id in `wrangler.toml`); `schema.sql` applied remotely (table `requests` + 2 indexes, empty).
- Secrets set on the Worker: `ADMIN_KEY`, `IP_SALT`, `NOSTR_NOTIFY_SK_HEX` (Nostr DM pings ON since 2026-11-03; bot npub `npub1ql790228j6…`). Live-verified: a test request produced DMs to Tomek and to the 21 npub, read back from primal, nos.lol and nostr.mom. DM failures are only logged; the request is stored regardless. Never store secret values in the repository.
- Local copy of all values (outside the repo): `C:\Users\Lenovo\.secrets\dj-invitations\secrets.json`, incl. dedicated bot key (bot npub `npub1ql790228j6jc9lkydvn49wgrev7456avw95nrqjfk5ur0de09h0s3lpkg4`).
- Live-tested 2026-11-03: `/health` ready:true; POST 201 then 200 on repeat; 422 invalid contact and missing consent; honeypot 200 without write; foreign origin 403; export 401 without key and 200 with it. Test row deleted (D1 empty).
- Personal Nostr recipient confirmed 2026-11-03: `npub14wxtsrj7…` in `wrangler.toml` matches `nostr-personal` in `social-media-tools/CONNECTIONS.json`.
- Next: check `/admin/export` periodically. Optionally replace the bot npub's metadata/follow it so DMs are recognisable in clients.
