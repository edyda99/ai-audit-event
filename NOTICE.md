# Conspicuous Notice — Audit-Log Schema v0.1-DRAFT

**This notice must be reproduced verbatim in any of the following contexts:**
- API response envelopes (as the `audit_notice` field)
- UI artifact-viewers that display audit log entries
- Customer contracts or service agreements that reference this schema or any service implementing it

---

Attestation metadata is stored as-submitted. Correctness is the submitting party's responsibility. This service does not verify reviewer identity or review completeness. No retroactive verification will occur.

---

**Implementation note for API responses.** Every response envelope from a conforming service must include exactly this JSON field:

```json
"audit_notice": "Attestation metadata is stored as-submitted. Correctness is the submitting party's responsibility. This service does not verify reviewer identity or review completeness. No retroactive verification will occur."
```

This field is not optional decoration. It is the wire-level liability boundary. Omitting it from a response envelope means that response does not conform to this schema version.

**Schema version this notice applies to:** v0.1-DRAFT and all v0.1.x patch releases.
