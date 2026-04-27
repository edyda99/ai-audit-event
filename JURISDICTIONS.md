# Jurisdictions — Regulatory Framework Alignment Notes

This schema is a substrate, not a jurisdiction-locked product. The customer-write field set in `schema/v0.1/audit-event.json` is wire-stable and deliberately jurisdiction-agnostic. Mapping those fields against specific regulatory evidence requirements is a layer above the wire format — and that mapping work belongs to people closer to the regulators than this repo's author.

This file records frameworks where the mapping has been examined honestly, and invites engineers operating under other frameworks to do the same.

---

## Currently acknowledged frameworks

The following frameworks have been examined against this schema's field set. Honest framing only — no claims beyond what the field actually provides.

### NYDFS Part 500 §500.17(a) — Cybersecurity Incident Notification (New York)

**Source (primary):** New York Department of Financial Services, *23 NYCRR Part 500 — Cybersecurity Requirements for Financial Services Companies, Second Amendment, effective November 1, 2023* — published at [dfs.ny.gov](https://www.dfs.ny.gov/system/files/documents/2023/12/rf23_nycrr_part_500_amend02_20231101.pdf). DFS hub page with all current cybersecurity guidance: [dfs.ny.gov/industry_guidance/cybersecurity](https://www.dfs.ny.gov/industry_guidance/cybersecurity).

**What the regulation requires:** Covered entities must notify the DFS superintendent "as promptly as possible but in no event later than 72 hours after determining that a Cybersecurity Incident has occurred" (§500.17(a), per the November 1, 2023 second amendment). The amendment expanded and formally defined the term "Cybersecurity Incident" to cover, among other things, events requiring notice to any government body, events with reasonable likelihood of materially harming normal operations, and ransomware deployment within a material part of the entity's information systems. Implicit in that 72-hour notification window is the ability to produce evidence of what AI systems were doing at the time of the incident.

**What this schema provides:** `timestamp_utc`, `caller_identity`, and `model_id` together answer "which model was called, by whom, and when" within a sub-second KV index query (see `INDEXING.md`). The `policy_version_hash` field provides a citable reference to the policy in force at call time.

**Honest gap:** The schema stores hashes and metadata as-submitted. It does not retrieve or validate the referenced policy document. If a covered entity's policy document is not separately retained and retrievable, the hash is not independently useful to a DFS examiner.

---

### FFIEC IT Handbook — Architecture, Infrastructure & Operations Booklet, Section VII.D (AI/ML risk awareness)

**What the booklet addresses:** The FFIEC IT Handbook AIO booklet, Section VII.D, surfaces AI/ML risk awareness for examiners (including explainability limits and bias considerations). It is supervisory expectation language, not a prescriptive technical standard.

**What this schema provides:** `model_id` (which model was invoked), `human_review_flag` (whether a human reviewed the output), and `policy_version_hash` (policy in force) map reasonably to evidence of governance controls a supervisor might ask about. The `human_review_flag` is a three-state enum — `none`, `attested`, `sampled` — defined in `schema/v0.1/human-review-flag.json`; institutions documenting human-in-the-loop controls can use it without redefining states.

**Honest gap:** The AIO booklet does not prescribe AI traceability or audit-record formats. Whether this schema's fields satisfy a specific examiner's evidence request depends on the institution's existing model risk management framework and how they characterize LLM use within it. No claim is made here that conforming to this schema satisfies FFIEC examination.

---

### MAS Technology Risk Management Guidelines — Audit Log Retention (Singapore)

**What the guidelines require:** The Monetary Authority of Singapore TRM Guidelines specify a 1-year minimum retention requirement for audit and event logs generally — not specifically for AI-assisted decisions. The retention requirement supports incident investigation and forensic analysis.

**What this schema provides:** The append-only, tamper-evident structure (SHA-256 `self_hash` chain, `prev_entry_hash` linkage) supports the forensic integrity expectation. The `timestamp_utc` / `client_timestamp_utc` dual-clock design is specifically intended to survive client clock drift while preserving the submitted timestamp as evidence.

**Honest gap:** Retention duration is an operational decision, not a schema property. An implementer running this schema on Cloudflare R2 with a 1-year retention policy satisfies the duration requirement independently of this schema. This schema does not enforce retention duration.

---

### FCA SYSC 8.1.8(9) — Outsourced-Activity Data Access (United Kingdom)

**What the rule requires:** FCA SYSC 8.1.8(9) requires that firms ensure their outsourcing arrangements do not impair the FCA's and PRA's ability to supervise the firm, including the ability to access data and premises relating to outsourced activities. This is an outsourcing-access rule, not an algorithmic-record-keeping rule.

**What this schema provides:** Where LLM API calls are routed through a third-party provider (i.e., the LLM call is itself an outsourced activity or is part of one), `caller_identity`, `model_id`, and `timestamp_utc` together constitute a minimal access log for that outsourced call surface. The `policy_version_hash` provides a citable governance artifact.

**Honest gap:** SYSC 8.1.8(9) is about supervisory access to data, not the format of that data. Whether the FCA would regard an R2-backed audit log conforming to this schema as satisfying the "data access" expectation in a specific outsourcing arrangement is a legal and supervisory question this schema cannot answer. Firms subject to FCA supervision should obtain their own legal advice.

---

## Co-signatories by jurisdiction

This section is currently empty.

If you operate under a regulatory framework not yet listed above — EU AI Act Article 12 record-keeping, APRA CPS 234, OCC AI model risk guidance, DORA ICT risk management, internal governance only — open an issue tagged `jurisdiction:<your-framework>` and tell us how this schema's fields map (or fail to map) against your evidence requirements.

Honest "doesn't fit" responses are as valuable as confirmations. A gap analysis is more useful than a gap that goes undocumented. Template:

- Which fields directly map to your evidence requirement?
- Which requirements have no corresponding field?
- What would a minimal addition look like (without breaking wire stability)?

The goal is a maintained mapping layer above a stable wire format — not a schema that tries to encode every jurisdiction's requirements into the core fields.

---

## Wire stability note

The eight customer-write fields — `entry_id`, `timestamp_utc`, `client_timestamp_utc`, `model_id`, `caller_identity`, `policy_version_hash`, `human_review_flag`, `signing_key_version` — are wire-stable for v0.1-DRAFT. Jurisdiction-specific mapping is a documentation and plugin layer, not a wire-format layer. Adding a new jurisdiction mapping to this file or to `jurisdictions/<framework>.md` does not require a schema version bump.

The three server-appended fields (`prev_entry_hash`, `self_hash`, `violation_detail`) are not part of the customer-write payload; they are appended at ingest by the conforming service implementation.
