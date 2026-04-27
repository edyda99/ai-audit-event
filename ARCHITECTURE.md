# Architecture — How This Works

This document explains the audit-log mechanism end-to-end. The schema (`schema/v0.1/audit-event.json`) is the wire format; this document is what the wire format actually does in production.

## In one sentence

A customer keeps their AI call logs. We countersign cryptographic fingerprints of those logs so the customer can prove to an auditor that nothing was changed or deleted. We never see the prompts, the responses, or any customer data — only metadata.

## How a single AI call flows through the system

A customer is running an LLM in production — their application calls a model provider (Claude, GPT, an in-house model, anything) whenever a user request needs one.

1. **The application makes the call.** Prompt goes to the model provider; response comes back. This is the customer's existing flow; we don't touch it.

2. **A sidecar library captures metadata** — not the prompt, not the response. The metadata is the eight fields defined in `schema/v0.1/audit-event.json`:

   - `entry_id` — a UUID for this log entry
   - `timestamp_utc` — server ingest clock (RFC 3339, millisecond precision)
   - `client_timestamp_utc` — the customer's clock at call time, stored as-submitted
   - `model_id` — the model identifier returned by the provider
   - `caller_identity` — an opaque identifier for who initiated the call
   - `policy_version_hash` — SHA-256 of the customer's active AI usage policy at call time
   - `human_review_flag` — three-state enum (`none` / `attested` / `sampled`); see `schema/v0.1/human-review-flag.json` for co-field rules
   - `signing_key_version` — the AWS KMS key version used to sign this entry

3. **The sidecar POSTs the metadata** to the ingest endpoint (a Cloudflare Worker in the reference implementation). No prompt content, no response content.

4. **The service does three things on receipt:**
   - Validates the payload against the schema
   - Runs it through the chain machinery (the three server-appended fields described below)
   - Writes the entry to R2 storage

5. **Periodically — hourly batches by default — the chain is sealed** to immutable storage (R2 bucket lock with retention) so even the operator of the service cannot quietly rewrite history.

When a regulator or internal incident-response team asks the customer "what was your AI doing during this incident window?", the customer pulls the entries for the window plus the chain proof, hands it over, and the recipient can verify it independently. They re-hash the entries, walk the chain, and check the seal anchors.

The customer owns the data. The service owns the proof that it hasn't been changed.

## The three server-appended fields — what makes the log a chain

Three fields are added by the ingest service and are **not part of the customer-write payload**. The customer doesn't supply them; the service computes them at ingest. They are what turns a pile of records into a tamper-evident chain.

### `prev_entry_hash`

The cryptographic fingerprint (SHA-256) of the previous entry in the chain. Every new record carries a pointer to the one before it.

This is what makes it a chain rather than a set. If anyone deletes an entry, the next entry's `prev_entry_hash` still points at the deleted one — the gap is structurally visible without anyone needing to remember what the deleted entry contained.

Analogy: a notarized ledger where every page begins with "this page follows the page sealed with notary stamp #1234." Tear out a page and the next page's reference no longer resolves.

### `self_hash`

The cryptographic fingerprint (SHA-256) of every field in the current entry — including its `prev_entry_hash` and any `violation_detail`. Computed at ingest and stored alongside the entry.

If anyone — even the service operator — modifies any field after ingest, recomputing the hash on the modified record produces a different number than what was originally stored. The mismatch is detectable by anyone with the record.

Analogy: a tamper-evident plastic strip across the seam of a package. The strip doesn't prevent someone from cutting it open — it makes any cut visible.

### `violation_detail`

When a customer submits a record that fails schema validation — missing required field, malformed value, or a `human_review_flag` co-field rule violation — the service does **not** silently reject it. The broken submission is written as a first-class entry with `violation_detail` populated, describing what was wrong.

This is what closes the most common audit loophole: a customer under audit pressure has incentive to make their failures disappear. If the service silently rejected malformed submissions, the customer's local "we tried to log this and it didn't go through" record could be erased. By writing the violation into the chain, the attempt itself becomes part of the permanent audit trail. The chain prevents the violation from being deleted; the `self_hash` prevents `violation_detail` from being blanked.

Analogy: a security camera that records both successful entries and rejected entries. You cannot make a rejection disappear without leaving a visible gap in the footage.

## Suppression-resistance — the three attack vectors

What an auditor or CISO would ask: *"Can a bad-actor employee at my own company hide a problematic AI call?"*

**Attack 1: Delete an entry.** The next entry's `prev_entry_hash` points at the deleted entry's hash. The chain has a structural gap. Detected on any verification scan.

**Attack 2: Blank out the `violation_detail` to hide that a malformed submission occurred.** The stored `self_hash` was computed over the original `violation_detail`. Recomputing the hash on the blanked record produces a different number than what is stored — tamper-on-self detected. Independently, the next entry's `prev_entry_hash` was set to the original hash, so the chain breaks at the next link as well. Two failures, either alone sufficient.

**Attack 3: Fully rewrite the entry with clean content and recompute `self_hash`.** Now the attacker has to also rewrite the next entry (whose `prev_entry_hash` referenced the original), and the next-next, and every successor. Cascading rewrite of the entire tail. The hourly batch seal to immutable R2 storage closes the rewrite window: the attacker cannot rewrite past a seal without diverging from the sealed copy.

## The export the customer hands an examiner

When NYDFS Part 500 §500.17(a)'s 72-hour clock starts (see `JURISDICTIONS.md` for the framework citation), or when an internal incident-response team makes a similar request, the customer runs an export over the incident window. The export contains:

1. All entries in the window, in chain order, as JSON-L.
2. Chain verification result — PASS / FAIL with the first-break location if FAIL.
3. The hourly seal anchors (R2 object ETags) for the batches covering the window — independently verifiable.
4. The KMS key version history for signing keys active during the window.

The export is generated entirely by the Workers function. No human at the service operator's company touches it.

## What this service explicitly does not do

- It does not see prompts or responses. The sidecar sends metadata only.
- It does not verify the contents of `caller_identity` or `policy_version_hash`. Those are stored as submitted; the customer is responsible for their accuracy. See `CONSPICUOUS-NOTICE.md` for the full liability boundary.
- It does not certify that any human review actually occurred when `human_review_flag` is `attested` — the schema records what was claimed, not what was true. The optional sampling agent (described in `README.md`) is the architectural intervention against checkbox-without-a-checkbox attestation.

## Where the rest of the documentation lives

This document is about the mechanism. The other files in this repo cover:

- `JURISDICTIONS.md` — how the mechanism maps against specific regulatory frameworks (NYDFS Part 500, FFIEC AIO §VII.D, MAS TRM, FCA SYSC 8.1.8(9)), with source URLs.
- `CONSPICUOUS-NOTICE.md` — the conspicuous notice that defines the liability boundary; required verbatim in API response envelopes, UI artifact viewers, and customer contracts.
- `INDEXING.md` — the queryability pattern that makes 72-hour incident-window retrieval fast at customer-scale volumes.
- `CONTRIBUTING.md` — what kinds of changes are in scope during the v0.1-DRAFT window.

If you are a CISO trying to figure out whether this schema covers your jurisdiction's evidence requirement, start at `JURISDICTIONS.md`. If you are an engineer trying to figure out how the chain works, this document is the right entry point.
