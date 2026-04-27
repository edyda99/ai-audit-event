**NOTICE — READ BEFORE USE:** Attestation metadata stored in this system is stored as-submitted. Correctness is the submitting party's responsibility. This service does not verify reviewer identity or review completeness. No retroactive verification will occur. This schema is v0.1-DRAFT, is not committed for production use, and may change before general availability. Implementers assume all responsibility for compliance outcomes.

---

# Audit-Log Schema — v0.1-DRAFT

An open, model-agnostic schema for recording LLM call attestation metadata. Designed for any organization that needs a tamper-evident, append-only audit log of AI model invocations — regardless of the regulatory framework (NYDFS Part 500, SOC 2, ISO 27001, EU AI Act, or internal governance).

## What this is

A proposed wire format for six core fields that capture the minimum traceable record of an LLM API call: who made it, which model handled it, what policy governed it, and whether a human reviewed it. Nothing more. The schema intentionally does not encode regulatory jurisdiction — it is a substrate on which compliance plugins can be layered.

## What this is not

This schema does not verify the identity of the caller, the completeness of any human review, or the authenticity of any attestation submitted. It records what was submitted. Correctness is the submitting party's responsibility. See CONSPICUOUS-NOTICE.md for the full conspicuous notice, which must be included verbatim in any API response envelope, UI artifact-viewer, and customer contract that references this schema.

## Who it is for

- Fintech and regulated-industry engineering teams building internal LLM audit infrastructure.
- Compliance and CISO teams that need a citable, schema-versioned artifact to reference in audit responses.
- Vendors building on top of a neutral audit substrate without committing to a single jurisdiction.

## Why I'm building this

I'm a senior backend developer and DevOps lead at a fintech. My day
splits between Java Quarkus and Spring Boot services in production and the Kubernetes, Helm, and GitLab CI infrastructure those services run on — I write the code and I run the pipelines that ship it. Five years in, three AWS certifications, CKAD: the credentials matter less than the fact that I've spent those years building systems where audit isn't an afterthought. I've shipped one audit framework before this accountability and traceability were load-bearing, not checkboxes. 
I try to automate everything I can. One time I built a flow to handle env-var changes — when a Jira ticket landed in the functional user's queue, the system would read the requirement and open the merge request itself. It ran fine for a while, until I came back from a vacation, looked at a recently-merged MR, and couldn't remember whether I'd clicked merge on it. The AI agent had the ability to merge but had been explicitly told not to — and I had no way of proving the final decision had actually been mine. The model was local; that didn't matter. There was no record, and there should have been.
This repo isn't a product, and it doesn't try to define a regulatory
framework. What I offer is a schema kept honest by someone who runs 
both sides of these systems — code and infrastructure — and has 
shipped audit before, not just talked about it. Wire format stays 
steady; the rest is for people closer to the regulators to argue.

## Optional: the sampling agent

The schema alone tells you what happened. It does not tell you whether what happened was representative of what your AI systems were doing in the days and hours before an incident.

There is an optional sampling agent that runs alongside the schema ingestor. It draws stratified samples from your append-only log at configurable intervals — not to verify individual records, but to surface statistical drift in call patterns: model versions, policy-tag distribution, human-review-flag ratios. When a regulator or an internal auditor asks "was this incident behavior typical or anomalous?", the sampling agent gives you a defensible answer beyond "here is the log."

If you run only the schema, you have a receipt. If you run the schema plus the sampling agent, you have a receipt and a baseline.

**What you give up by not running it:**

- No pre-incident baseline to compare against during an investigation
- No drift alerts if human-review-flag ratios shift over a rolling window
- Anomaly claims in any incident report remain qualitative, not data-backed

The sampling agent is documented separately and is not required to implement this schema. It is available for organizations that anticipate needing to answer the anomaly question, not just the retrieval question. A reference implementation will be linked from this README when one is available.

## Files in this repo

```
README.md                              this file
CONSPICUOUS-NOTICE.md                  conspicuous notice — verbatim, for contract / UI inclusion
INDEXING.md                            queryability guidance (Cloudflare Workers KV index pattern)
schema/v0.1/audit-event.json           JSON Schema for the core six-field log entry
schema/v0.1/human-review-flag.json     three-state enum co-field rules
schema/v0.1/key-transition.json        key-rotation event record (append-only, signed with new key)
```

## Schema versioning

This is v0.1-DRAFT. Wire-stable within the draft period. Breaking changes will increment the minor version (v0.2) with 30 days notice before any production cut-over. The `$id` URI in each schema file is the canonical version reference.

## How to submit feedback

Open a GitHub issue. Tag it `schema-feedback`. Response time is best-effort during the draft window. No pull requests accepted to the schema files during the draft window — the spec is intentionally frozen for comment collection, not active iteration.
