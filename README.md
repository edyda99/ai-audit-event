**NOTICE — READ BEFORE USE:** Attestation metadata stored in this system is stored as-submitted. Correctness is the submitting party's responsibility. This service does not verify reviewer identity or review completeness. No retroactive verification will occur. This schema is v0.1-DRAFT, is not committed for production use, and may change before general availability. Implementers assume all responsibility for compliance outcomes.

---

# Audit-Log Schema — v0.1-DRAFT

An open, model-agnostic schema for recording LLM call attestation metadata. Designed for any organization that needs a tamper-evident, append-only audit log of AI model invocations — regardless of the regulatory framework (NYDFS Part 500, SOC 2, ISO 27001, EU AI Act, or internal governance).

## What this is

A proposed wire format for six core fields that capture the minimum traceable record of an LLM API call: who made it, which model handled it, what policy governed it, and whether a human reviewed it. Nothing more. The schema intentionally does not encode regulatory jurisdiction — it is a substrate on which compliance plugins can be layered.

## What this is not

This schema does not verify the identity of the caller, the completeness of any human review, or the authenticity of any attestation submitted. It records what was submitted. Correctness is the submitting party's responsibility. See NOTICE.md for the full conspicuous notice, which must be included verbatim in any API response envelope, UI artifact-viewer, and customer contract that references this schema.

## Who it is for

- Fintech and regulated-industry engineering teams building internal LLM audit infrastructure.
- Compliance and CISO teams that need a citable, schema-versioned artifact to reference in audit responses.
- Vendors building on top of a neutral audit substrate without committing to a single jurisdiction.

## Why I'm building this

<!-- FOUNDER_INTRO_PLACEHOLDER — Ed fills personally before publish -->
<!-- Suggested prompts to address: -->
<!-- 1. What you do day-to-day (without naming employer if sensitive) -->
<!-- 2. The specific moment / observation that made you build this -->
<!-- 3. Why you, specifically, are the right person to maintain it -->
<!-- 2-3 short paragraphs total. First-person. No marketing language. -->

## Files in this repo

```
README.md                              this file
NOTICE.md                              conspicuous notice — verbatim, for contract / UI inclusion
INDEXING.md                            queryability guidance (Cloudflare Workers KV index pattern)
schema/v0.1/audit-event.json           JSON Schema for the core six-field log entry
schema/v0.1/human-review-flag.json     three-state enum co-field rules
schema/v0.1/key-transition.json        key-rotation event record (append-only, signed with new key)
```

## Schema versioning

This is v0.1-DRAFT. Wire-stable within the draft period. Breaking changes will increment the minor version (v0.2) with 30 days notice before any production cut-over. The `$id` URI in each schema file is the canonical version reference.

## How to submit feedback

Open a GitHub issue. Tag it `schema-feedback`. Response time is best-effort during the draft window. No pull requests accepted to the schema files during the draft window — the spec is intentionally frozen for comment collection, not active iteration.
