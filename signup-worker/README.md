# Dwadzieścia Jeden invitation requests

Cloudflare Worker + D1 backend for the invitation form on `/dolacz-do-nas/#invite`.

- Endpoint: `https://dj-invitations.kolotom.workers.dev` (`POST /subscribe`, `GET /health`, `GET /admin/export`)
- Table: D1 `dj-invitations`, unique normalized email/npub, hourly per-IP rate limit
- Protections: strict origin allowlist, consent validation, honeypot, optional blocklist, salted IP hash
- Storage only by default: every request goes to D1 and is read with `GET /admin/export`. Optional NIP-04 DM ping to the 21 and Tomek npubs when the secret `NOSTR_NOTIFY_SK_HEX` is set (off by default). No e-mail is sent.
- Notifications are a deployment precondition: POST returns 503 until all mail, Nostr and admin secrets are configured. No submissions are accepted in the incomplete configuration.

## Local development

```bash
npm install
npm test
npx --yes wrangler@4 dev --local --port 8788 --ip 127.0.0.1
```

Apply `schema.sql` to the local D1 store before testing against Wrangler. The unit tests use a local in-memory D1 stand-in and never call external services.

## Production setup (not yet deployed)

1. Create a dedicated D1 database and make `wrangler.production.toml` with its real id. Keep `wrangler.toml` as the placeholder/local config.
2. Apply `schema.sql` with the production config.
3. Set the secrets `ADMIN_KEY` and `IP_SALT` (required) and optionally `NOSTR_NOTIFY_SK_HEX` with `wrangler secret put`; never store them in this repository.
4. Optional: set `NOSTR_NOTIFY_SK_HEX` to enable Nostr DM pings (`/health` then reports `nostr_notify: true`).
5. Deploy, check `/health` reports `ready: true`, then run CORS and validation probes.
6. Only then switch the site form to this endpoint and deploy the site.

Admin export: `GET /admin/export` or `GET /admin/export?format=csv` with `Authorization: Bearer <ADMIN_KEY>`.
