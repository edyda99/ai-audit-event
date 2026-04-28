# Examples

Sample audit-event entries plus a tiny verifier so you can see the schema reject malformed input.

## Files

| File | What it is |
|---|---|
| `valid-none.json` | Minimal valid entry. `human_review_flag.state = "none"`. No co-fields required. |
| `valid-attested.json` | Valid entry with `state = "attested"` and all required co-fields (`attested_by`, `attestation_timestamp_utc`, `attestation_justification`, `attestation_scope`). |
| `valid-sampled.json` | Valid entry with `state = "sampled"` and all required co-fields (`sample_rate`, `sample_method`, `sampled_by_system`). |
| `invalid-attested-missing-cofields.json` | Deliberately invalid. `state = "attested"` but the required co-fields are missing. The verifier should reject it. |
| `verify.py` | ~80-line Python script that loads the local schema and validates a single entry. |

## Run

```
$ pip install jsonschema
$ cd examples
$ python3 verify.py valid-none.json
VALID: valid-none.json

$ python3 verify.py valid-attested.json
VALID: valid-attested.json

$ python3 verify.py valid-sampled.json
VALID: valid-sampled.json

$ python3 verify.py invalid-attested-missing-cofields.json
INVALID: invalid-attested-missing-cofields.json
  - at human_review_flag: 'attested_by' is a required property
  - at human_review_flag: 'attestation_timestamp_utc' is a required property
  - at human_review_flag: 'attestation_justification' is a required property
  - at human_review_flag: 'attestation_scope' is a required property
```

## What this is not

The verifier shown here is illustrative — it covers per-entry schema validation only. It does NOT verify the chain (`prev_entry_hash` / `self_hash` continuity), the seal anchors, or the key-transition records. A production-grade verifier walks the chain forward, recomputes hashes against the canonical blob, checks that R2 seal anchors match, and resolves `signing_key_version` against the key-transition log. See `ARCHITECTURE.md` for the full chain mechanism. A reference implementation of the full verifier is out of scope for the v0.1-DRAFT window — link will be added here when one exists.

## Sample data — what's real, what's representative

The `model_id` value (`claude-sonnet-4-6`) is a real model identifier. The `policy_version_hash` is a real SHA-256 hex string of representative length but does not correspond to any real policy document. The `caller_identity` values are plausibly-shaped service identifiers but are not real service accounts. The `signing_key_version` follows the AWS KMS key-alias-with-version convention but is not a real KMS resource. Treat these examples as schema-shape references, not as wire-protocol fixtures.
