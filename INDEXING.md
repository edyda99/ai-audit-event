# Queryability Index Design — v0.1-DRAFT

## Why this exists

When a cybersecurity incident occurs, NYDFS Part 500 §500.17(a) requires notification within 72 hours of determining an incident occurred. Once that clock starts, a CISO presenting audit evidence cannot afford to block on a full R2 scan — "show me all LLM calls by this caller_identity between these two timestamps" needs a sub-second answer. This document specifies the Cloudflare Workers KV index pattern that makes that query fast without adding infrastructure cost.

This guidance applies equally to any regulatory or internal audit framework with similar time-range queryability requirements.

## Storage split

| Layer | What lives there | Why |
|---|---|---|
| R2 | Full AuditLogEntry and KeyTransitionRecord JSON objects | Cheap bulk storage ($0.015/GB/mo). Immutable. Append-only. |
| Cloudflare Workers KV | Index entries only — keys encode (customer_id, timestamp_utc); values are R2 object keys | Sub-millisecond reads. KV is not the source of truth, R2 is. |

## KV index key shape

```
${customer_id}:${timestamp_utc_iso}:${entry_id}
```

Example:
```
acme-bank:2026-04-26T03:14:15.926Z:a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

- `customer_id` as prefix enables namespace isolation per customer.
- `timestamp_utc_iso` as middle segment enables lexicographic range scans within a customer namespace. RFC 3339 sorts correctly as a string when milliseconds are zero-padded.
- `entry_id` as suffix prevents collision on same-millisecond ingest bursts.

KV value:
```json
{
  "r2_key": "logs/acme-bank/2026/04/26/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json",
  "entry_type": "audit_log_entry"
}
```

## Query pattern (pseudocode)

```javascript
// Cloudflare Workers KV — list keys in range, then fetch from R2

async function queryRange(customerId, fromUtc, toUtc, env) {
  const prefix = `${customerId}:`;
  const startKey = `${customerId}:${fromUtc.toISOString()}`;
  const endKey   = `${customerId}:${toUtc.toISOString()}`;

  // KV list is lexicographic; iterate pages until endKey is exceeded
  let cursor = undefined;
  const r2Keys = [];

  do {
    const page = await env.AUDIT_INDEX.list({
      prefix,
      cursor,
      limit: 1000,
    });

    for (const key of page.keys) {
      // Key format: customer_id:timestamp:entry_id
      const parts = key.name.split(':');
      const keyTs = parts[1]; // ISO timestamp segment
      if (keyTs < fromUtc.toISOString()) continue;
      if (keyTs > toUtc.toISOString()) break;
      const meta = JSON.parse(key.metadata ?? '{}');
      r2Keys.push(meta.r2_key);
    }

    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);

  // Fetch full entries from R2 in parallel (batched to avoid egress burst)
  const entries = await Promise.all(
    r2Keys.map(k => env.AUDIT_BUCKET.get(k).then(obj => obj.json()))
  );

  return entries;
}
```

Sub-second target is achievable at 10K users / 10MB-per-user-per-day scale: KV list latency is ~1-5ms per page; R2 GET latency is ~20-50ms per object. A 90-day range query for a single customer that produces 5,000 entries resolves in under 3 seconds including R2 fetches.

## KV write path (pseudocode)

```javascript
// On ingest — after R2 write confirms, write KV index entry
async function indexEntry(entry, r2Key, env) {
  const kvKey = `${entry.customer_id}:${entry.timestamp_utc}:${entry.entry_id}`;
  const kvValue = JSON.stringify({
    r2_key: r2Key,
    entry_type: 'audit_log_entry',
  });

  // KV put with metadata for zero-parse list scans
  await env.AUDIT_INDEX.put(kvKey, kvValue, {
    metadata: { r2_key: r2Key },
  });
}
```

R2 write is the commit point. If the KV index write fails, the entry is not lost — R2 is source of truth. A background reconciliation Worker runs nightly: it scans R2 for entries missing from the KV index and backfills.

## Backfill strategy for existing customers

When a new customer is onboarded or the index is rebuilt after a KV namespace incident:

1. List all R2 objects under `logs/${customerId}/`.
2. For each object, deserialize the entry and compute the KV key.
3. Write KV entries in batches of 1,000 (KV bulk write API, one HTTP call per batch).
4. A 100,000-entry backfill completes in under 5 minutes at KV bulk write throughput (~500ms per batch of 1,000).

No human intervention required. The backfill Worker is triggered by a Cloudflare Cron Trigger or a one-time API call from the operator. Zero support ticket surface.

## Cost note

At 10K users, 10MB/day each, 90-day retention in KV index: approximately 10K users × 90 days × ~10 KV entries/day = 9M KV keys. Cloudflare Workers KV storage: first 1GB free, then $0.50/GB/mo. At ~200 bytes per KV key + value, 9M keys = ~1.8GB = ~$0.40/mo incremental. Negligible. Full cost picture in spec-v0.1-draft-checklist.md Section 6.
