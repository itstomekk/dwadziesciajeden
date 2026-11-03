# Handoff

- Worker DEPLOYED 2026-11-03 at `https://dj-invitations.kolotom.workers.dev` (version 963fb8d1). Stores e-mail/npub requests in D1; sends NO e-mail (Resend dropped on Tomek's decision). The site is NOT published: the form still has to be pushed on Tomek's word.
- Local verification passed 2026-11-03: `npm test` (5/5), `node --check src/index.js`, Wrangler local D1 end-to-end checks (health, insert, duplicate, invalid contact, honeypot, foreign origin), and site QA ALL PASS. Local test rows were deleted; local servers are stopped.
- Remote D1 `dj-invitations` created 2026-11-03 (id in `wrangler.toml`); `schema.sql` applied remotely (table `requests` + 2 indexes, empty).
- Secrets set on the Worker: `ADMIN_KEY`, `IP_SALT`. Optional, NOT set: `NOSTR_NOTIFY_SK_HEX` (enables Nostr DM pings to the 21 and Tomek npubs; failures are only logged). Never store secret values in the repository.
- Local copy of all values (outside the repo): `C:\Users\Lenovo\.secrets\dj-invitations\secrets.json`, incl. dedicated bot key (bot npub `npub1ql790228j6jc9lkydvn49wgrev7456avw95nrqjfk5ur0de09h0s3lpkg4`).
- Live-tested 2026-11-03: `/health` ready:true; POST 201 then 200 on repeat; 422 invalid contact and missing consent; honeypot 200 without write; foreign origin 403; export 401 without key and 200 with it. Test row deleted (D1 empty).
- Personal Nostr recipient confirmed 2026-11-03: `npub14wxtsrj7…` in `wrangler.toml` matches `nostr-personal` in `social-media-tools/CONNECTIONS.json`.
- Next: push the site (commit scope + CRLF check) on Tomek's word, then re-test the form from https://dwadziesciajeden.pl. Decide whether to enable Nostr DM pings (set `NOSTR_NOTIFY_SK_HEX`); the live DM path is untested.
