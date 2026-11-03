import { finalizeEvent, nip04, nip19 } from 'nostr-tools';

const ORIGINS = ['https://dwadziesciajeden.pl', 'https://www.dwadziesciajeden.pl'];
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const NPUB_RE = /^npub1[023456789acdefghjklmnpqrstuvwxyz]{58}$/;
const HOURLY_LIMIT = 10;
const DEFAULT_RELAYS = ['wss://relay.primal.net', 'wss://nos.lol', 'wss://nostr.mom'];

function allowedOrigin(origin) {
  if (!origin) return null;
  if (ORIGINS.includes(origin)) return origin;
  if (/^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/.test(origin)) return origin;
  return null;
}

function json(body, status, origin) {
  const headers = { 'content-type': 'application/json; charset=utf-8' };
  const permitted = allowedOrigin(origin);
  if (permitted) {
    headers['access-control-allow-origin'] = permitted;
    headers.vary = 'Origin';
  }
  return new Response(JSON.stringify(body), { status, headers });
}

async function sha256(value) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function safeEqual(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Storing requests needs only the database and the two local secrets.
function configured(env) {
  return Boolean(env.DB && env.IP_SALT && env.ADMIN_KEY);
}

// Optional Nostr DM ping; requests are stored whether or not it is set up.
function nostrConfigured(env) {
  return Boolean(env.NOSTR_NOTIFY_SK_HEX && env.NOSTR_NOTIFY_TO_NPUBS);
}

async function publish(relay, event, timeoutMs = 6000) {
  const response = await fetch(relay.replace(/^wss:/, 'https:'), { headers: { Upgrade: 'websocket' } });
  const socket = response.webSocket;
  if (!socket) throw new Error(`${relay}: no websocket (${response.status})`);
  socket.accept();
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      try { socket.close(); } catch { /* already closed */ }
      reject(new Error(`${relay}: timeout`));
    }, timeoutMs);
    socket.addEventListener('message', (message) => {
      try {
        const payload = JSON.parse(String(message.data));
        if (payload[0] !== 'OK') return;
        clearTimeout(timer);
        try { socket.close(); } catch { /* already closed */ }
        if (payload[2]) resolve(relay);
        else reject(new Error(`${relay}: ${payload[3] || 'rejected'}`));
      } catch (error) {
        if (error instanceof SyntaxError) return;
        clearTimeout(timer);
        reject(error);
      }
    });
    socket.addEventListener('error', () => {
      clearTimeout(timer);
      reject(new Error(`${relay}: websocket error`));
    });
    socket.send(JSON.stringify(['EVENT', event]));
  });
}

async function notifyNostr(env, contact, kind) {
  const secret = Uint8Array.from(env.NOSTR_NOTIFY_SK_HEX.match(/../g).map((part) => parseInt(part, 16)));
  const recipients = env.NOSTR_NOTIFY_TO_NPUBS.split(',').map((value) => value.trim()).filter(Boolean);
  const relays = (env.NOSTR_RELAYS || DEFAULT_RELAYS.join(',')).split(',').map((value) => value.trim()).filter(Boolean);
  const results = await Promise.all(recipients.map(async (npub) => {
    const decoded = nip19.decode(npub);
    if (decoded.type !== 'npub') throw new Error('notification recipient is not an npub');
    const recipient = decoded.data;
    const content = await nip04.encrypt(secret, recipient, `Nowa prośba o zaproszenie (${kind}): ${contact}`);
    const event = finalizeEvent({ kind: 4, created_at: Math.floor(Date.now() / 1000), tags: [['p', recipient]], content }, secret);
    const sent = await Promise.allSettled(relays.map((relay) => publish(relay, event)));
    if (!sent.some((result) => result.status === 'fulfilled')) throw new Error(`Nostr DM failed for ${npub}`);
    return npub;
  }));
  const failures = results.filter((result) => result.status === 'rejected');
  if (failures.length) throw new Error(`${failures.length} Nostr recipient(s) were not notified`);
}

async function notify(env, contact, kind) {
  try {
    await notifyNostr(env, contact, kind);
  } catch (error) {
    console.log('invitation notification failed', String(error));
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin');

    if (request.method === 'OPTIONS') {
      const permitted = allowedOrigin(origin);
      return new Response(null, { status: permitted ? 204 : 403, headers: permitted ? {
        'access-control-allow-origin': permitted,
        'access-control-allow-methods': 'POST, OPTIONS',
        'access-control-allow-headers': 'content-type',
        'access-control-max-age': '86400',
        vary: 'Origin',
      } : {} });
    }
    if (url.pathname === '/health' && request.method === 'GET') {
      return json({ ok: true, ready: configured(env), nostr_notify: nostrConfigured(env) }, 200, origin);
    }

    if (url.pathname === '/admin/export' && request.method === 'GET') {
      const auth = (request.headers.get('Authorization') || '').replace(/^Bearer /, '');
      if (!env.ADMIN_KEY || !safeEqual(auth, env.ADMIN_KEY)) return json({ ok: false, error: 'unauthorized' }, 401, null);
      const { results } = await env.DB.prepare('SELECT contact, kind, created_at FROM requests ORDER BY created_at DESC').all();
      if (url.searchParams.get('format') === 'csv') {
        const csv = 'contact,kind,created_at\n' + results.map((row) =>
          `"${row.contact.replace(/"/g, '""')}",${row.kind},${row.created_at}`).join('\n');
        return new Response(csv, { headers: { 'content-type': 'text/csv; charset=utf-8' } });
      }
      return json({ ok: true, count: results.length, requests: results }, 200, null);
    }

    if (url.pathname === '/subscribe' && request.method === 'POST') {
      if (!allowedOrigin(origin)) return json({ ok: false, error: 'forbidden origin' }, 403, null);
      if (!configured(env)) {
        return json({ ok: false, error: 'Formularz jest chwilowo niedostępny.' }, 503, origin);
      }
      let data;
      try {
        const contentType = request.headers.get('content-type') || '';
        data = contentType.includes('json') ? await request.json() : Object.fromEntries(await request.formData());
      } catch {
        return json({ ok: false, error: 'Nieprawidłowe żądanie.' }, 400, origin);
      }
      if (data._honey) return json({ ok: true, already: false }, 200, origin);
      if (data.consent !== 'yes') return json({ ok: false, error: 'Zaznacz zgodę na kontakt w sprawie zaproszenia.' }, 422, origin);

      const contact = String(data.contact || '').trim().toLowerCase();
      if (!contact || contact.length > 254) return json({ ok: false, error: 'Podaj adres e-mail albo npub.' }, 422, origin);
      const kind = NPUB_RE.test(contact) ? 'npub' : EMAIL_RE.test(contact) ? 'email' : null;
      if (!kind) return json({ ok: false, error: 'To nie wygląda na poprawny e-mail ani npub.' }, 422, origin);
      const blocked = String(env.BLOCKLIST || '').split(',').map((value) => value.trim().toLowerCase()).filter(Boolean);
      if (blocked.some((part) => contact.includes(part))) return json({ ok: true, already: false }, 200, origin);

      const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
      const ipHash = await sha256(`${env.IP_SALT || ''}${ip}`);
      const recent = await env.DB.prepare(
        "SELECT COUNT(*) AS n FROM requests WHERE ip_hash = ? AND created_at > datetime('now','-1 hour')",
      ).bind(ipHash).first();
      if (recent && recent.n >= HOURLY_LIMIT) return json({ ok: false, error: 'Za dużo prób. Spróbuj ponownie później.' }, 429, origin);

      const result = await env.DB.prepare(
        'INSERT INTO requests (id, contact, kind, ip_hash) VALUES (?, ?, ?, ?) ON CONFLICT(contact) DO NOTHING',
      ).bind(crypto.randomUUID(), contact, kind, ipHash).run();
      const created = result.meta.changes > 0;
      if (created && nostrConfigured(env) && !env.TEST_DISABLE_NOTIFICATIONS) ctx.waitUntil(notify(env, contact, kind));
      return json({ ok: true, already: !created }, created ? 201 : 200, origin);
    }
    return json({ ok: false, error: 'not found' }, 404, origin);
  },
};
