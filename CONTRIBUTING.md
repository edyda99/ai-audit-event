# Contributing — v0.1-DRAFT

Read CONSPICUOUS-NOTICE.md first. It is not boilerplate.

---

## Wire-format stability promise

The customer-write schema — the eight fields defined in `schema/v0.1/audit-event.json` — is wire-stable for the duration of the v0.1-DRAFT window. Those fields are:

`entry_id`, `timestamp_utc`, `client_timestamp_utc`, `model_id`, `caller_identity`, `policy_version_hash`, `human_review_flag`, `signing_key_version`

Implementers can build against this field set now. Breaking changes (field removal, rename, semantic change) will not happen without a minor version bump (v0.2) and 30 days advance notice.

## What is out of scope during the draft window

The three server-appended fields (`prev_entry_hash`, `self_hash`, `violation_detail`) are server-side concerns. They are appended at ingest by the conforming service implementation, not written by the customer. Pull requests that add, remove, or modify these fields in the schema files are out of scope during the draft window and will not be merged.

Pull requests modifying the core schema files in `schema/v0.1/` are also out of scope during the draft window. The spec is intentionally frozen for comment collection. Proposed schema changes should be filed as issues tagged `schema-feedback` and will be considered for v0.2.

## What contributions are welcome during the draft window

**Jurisdiction mapping notes.** If you operate under a regulatory framework and can document honestly how this schema's fields map (or fail to map) against your evidence requirements, that is the highest-value contribution right now. File these as `jurisdictions/<framework-shortname>.md` — for example, `jurisdictions/apra-cps234.md` or `jurisdictions/eu-ai-act-art12.md`. The format should follow the pattern in JURISDICTIONS.md: what the regulation requires, what the schema provides, and what the honest gaps are. No fabricated section numbers; cite the actual document.

**Bug reports on the spec.** If a field description is ambiguous, a format constraint is wrong, or an example is incorrect, open an issue tagged `spec-bug`. These are in scope.

**Sampling-agent reference implementation.** The schema includes a `human_review_flag` field with a `sampled` state that implies a sampling agent — something that selects a subset of entries for human review queue. If you want to write a reference implementation of that agent, that belongs in a separate repository. Link it here by opening an issue tagged `reference-impl` and we will add it to the README. It should not live in this repo, which is a schema spec, not a runtime.

**INDEXING.md feedback.** The Cloudflare Workers KV index pattern described in INDEXING.md is a reference design, not a normative requirement. If you have implemented a different queryability layer (DynamoDB GSI, Postgres partial index, etc.) against this schema and want to document it, open a PR against INDEXING.md or open a Discussion. Additive documentation to INDEXING.md is in scope.

## Where to post

The repo has three Discussions categories. Pick the one that matches what you're trying to do:

- **Compliance Use Cases** (Q&A format) — for "does this schema satisfy [my regulatory requirement]?" The Q&A format means the best answer gets marked accepted and becomes citable. Use this when you want a definite answer you can reference later.
- **Jurisdiction Mapping** (open discussion) — for iterative, multi-perspective work mapping the schema against a regulatory framework (e.g., MAS TRM, FCA SYSC, EU AI Act Article 12). Open discussion because mapping is contested and evolves; threads here can stay open and gather perspectives from people in different jurisdictions.
- **Schema Feedback** (Q&A format) — for specific technical questions about field semantics, format constraints, or implementation behavior. Q&A so the authoritative answer can be marked.

For structured submissions where you have already done the mapping work and want to file it as a record, the **Compliance Use Case** issue template (the "New Issue" button) is the right channel — it captures jurisdiction, evidence requirement, schema coverage, and any gaps in a structured form. For exploratory discussion before filing, use Discussions.

## Code of conduct

Be direct and honest, including about gaps and failures. Overstating what this schema provides in a compliance context harms the people who depend on audit evidence being accurate.

Beyond that: this project follows the [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

**TODO for operator (Ed):** Confirm whether Contributor Covenant 2.1 is the right choice, or whether you prefer a shorter custom CoC. If CC 2.1, create a `CODE_OF_CONDUCT.md` file at repo root that is the verbatim CC 2.1 text and update the link above to point to it locally (`./CODE_OF_CONDUCT.md`) rather than the upstream URL.
