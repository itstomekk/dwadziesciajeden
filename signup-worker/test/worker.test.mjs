import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';

const ORIGIN = 'https://dwadziesciajeden.pl';

function memoryDb() {
  const rows = new Map();
  const db = {
    rows,
    prepare(sql) {
      let args = [];
      return {
        bind(...values) { args = values; return this; },
        async first() {
          if (sql.includes('COUNT(*)')) return { n: 0 };
          return null;
        },
        async run() {
          if (sql.includes('INSERT INTO requests')) {
            const [id, contact, kind, ipHash] = args;
            if (rows.has(contact)) return { meta: { changes: 0 } };
            rows.set(contact, { id, contact, kind, ip_hash: ipHash, created_at: '2026-11-03 12:00:00' });
            return { meta: { changes: 1 } };
          }
          return { meta: { changes: 0 } };
        },
        async all() { return { results: [...rows.values()] }; },
      };
    },
  };
  return db;
}

function post(contact, extra = {}, origin = ORIGIN) {
  return new Request('https://worker.test/subscribe', {
    method: 'POST',
    headers: { Origin: origin, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ contact, consent: 'yes', ...extra }),
  });
}

async function call(request, env, tasks = []) {
  const response = await worker.fetch(request, env, { waitUntil: (task) => tasks.push(task) });
  await Promise.all(tasks);
  return response;
}

test('valid email request is stored once and duplicates are idempotent', async () => {
  const DB = memoryDb();
  const env = { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' };
  const first = await call(post('Test@Example.org'), env);
  assert.equal(first.status, 201);
  assert.deepEqual(await first.json(), { ok: true, already: false });
  const duplicate = await call(post(' test@example.org '), env);
  assert.equal(duplicate.status, 200);
  assert.deepEqual(await duplicate.json(), { ok: true, already: true });
  assert.equal(DB.rows.size, 1);
});

test('npub is accepted and malformed contacts are rejected', async () => {
  const DB = memoryDb();
  const env = { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' };
  const accepted = await call(post('npub1' + 'q'.repeat(58)), env);
  assert.equal(accepted.status, 201);
  assert.equal([...DB.rows.values()][0].kind, 'npub');
  const rejected = await call(post('not-a-contact'), env);
  assert.equal(rejected.status, 422);
});

test('honeypot and disallowed origin never write a request', async () => {
  const DB = memoryDb();
  const env = { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' };
  const bot = await call(post('bot@example.org', { _honey: 'filled' }), env);
  assert.equal(bot.status, 200);
  const foreign = await call(post('other@example.org', {}, 'https://evil.example'), env);
  assert.equal(foreign.status, 403);
  assert.equal(DB.rows.size, 0);
});

test('missing consent is rejected', async () => {
  const DB = memoryDb();
  const request = new Request('https://worker.test/subscribe', {
    method: 'POST',
    headers: { Origin: ORIGIN, 'Content-Type': 'application/json' },
    body: JSON.stringify({ contact: 'a@example.org' }),
  });
  const response = await call(request, { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' });
  assert.equal(response.status, 422);
  assert.equal(DB.rows.size, 0);
});

test('requests are stored without any notification setup', async () => {
  const DB = memoryDb();
  const response = await call(post('a@example.org'), { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' });
  assert.equal(response.status, 201);
  assert.equal(DB.rows.size, 1);
  const health = await call(new Request('https://worker.test/health'), { DB, IP_SALT: 'test-salt', ADMIN_KEY: 'test-admin' });
  assert.deepEqual(await health.json(), { ok: true, ready: true, nostr_notify: false });
});

test('missing local secrets refuse new requests without storing them', async () => {
  const DB = memoryDb();
  const response = await call(post('a@example.org'), { DB });
  assert.equal(response.status, 503);
  assert.equal(DB.rows.size, 0);
});
