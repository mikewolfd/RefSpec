# Federal Identifier Atlas

A researched, versioned registry of **263 U.S. federal identifier families** current through **2026-08-31**.

This is not a claim that every local transaction number created by every federal office has a discoverable grammar. It combines:

- concrete identifier/citation grammars;
- candidate regexes;
- normalization and semantic validation notes;
- namespace and uniqueness rules;
- privacy and lifecycle metadata;
- explicit open/delegated classes where no universal regex exists;
- official source links and evaluated code repositories.

## Files

- `federal_identifier_atlas.md` — readable full catalog.
- `federal_identifier_registry.json` — canonical structured registry.
- `federal_identifier_registry.tsv` — flat table for ingestion/review.
- `source_catalog.json` — source and repository catalog.
- `registry.schema.json` — JSON Schema.
- `federal_identifier_patterns.py` — no-dependency Python helpers and selected semantic validators.
- `test_patterns.py` — smoke tests.
- `validation_notes.md` — collision, privacy, lifecycle and architecture guidance.
- `repositories_and_wikis.md` — evaluated repository/API/wiki shortlist.

## Use

```python
from federal_identifier_patterns import find_candidates, validate_known

text = "See Pub. L. 117-58 and NCT01234567."
for candidate in find_candidates(text):
    print(candidate)

print(validate_known("health.npi", "1234567893"))
```

Run tests:

```bash
python -m pytest test_patterns.py
```

## Non-negotiable implementation rule

Store the raw text, normalized candidate, family, issuer namespace, effective date/version, validation status and provenance separately. A regex match is never issuance proof.
