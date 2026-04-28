#!/usr/bin/env python3
"""
verify.py — Validate an audit-event entry against the v0.1-DRAFT schema.

Usage:
    python3 verify.py <path-to-entry.json>

Returns exit code 0 if valid, 1 if invalid (with the validation error printed).

Requires: jsonschema >= 4.18 and referencing.
    pip install jsonschema

This script is illustrative — it loads the local schema files and runs a
single-entry validation. Production implementations should use the same
referencing setup against an HTTP-served schema or a local registry built
once at startup.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError:
    sys.stderr.write("ERROR: jsonschema (>=4.18) missing. Run: pip install jsonschema\n")
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 verify.py <path-to-entry.json>\n")
        return 2

    entry_path = Path(sys.argv[1])
    if not entry_path.exists():
        sys.stderr.write(f"ERROR: file not found: {entry_path}\n")
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    schema_dir = repo_root / "schema" / "v0.1"
    audit_event_path = schema_dir / "audit-event.json"
    human_review_path = schema_dir / "human-review-flag.json"

    if not audit_event_path.exists() or not human_review_path.exists():
        sys.stderr.write(
            f"ERROR: schema files not found under {schema_dir}\n"
            "Expected: audit-event.json and human-review-flag.json\n"
        )
        return 2

    with audit_event_path.open() as f:
        audit_event_schema = json.load(f)
    with human_review_path.open() as f:
        human_review_schema = json.load(f)

    # Build a referencing Registry mapping each schema's $id to its content.
    # The audit-event schema's $ref to the human-review-flag schema resolves
    # against this registry rather than over HTTP.
    registry = Registry().with_resources([
        (
            audit_event_schema["$id"],
            Resource.from_contents(audit_event_schema, default_specification=DRAFT202012),
        ),
        (
            human_review_schema["$id"],
            Resource.from_contents(human_review_schema, default_specification=DRAFT202012),
        ),
    ])
    validator = Draft202012Validator(audit_event_schema, registry=registry)

    with entry_path.open() as f:
        entry = json.load(f)

    # Strip the convenience _comment field if present — examples use it to
    # annotate intent; it is not part of the schema.
    entry.pop("_comment", None)

    errors = sorted(validator.iter_errors(entry), key=lambda e: list(e.absolute_path))
    if not errors:
        print(f"VALID: {entry_path}")
        return 0

    print(f"INVALID: {entry_path}")
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        print(f"  - at {path}: {err.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
