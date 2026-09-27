# Independent agency candidate digest recheck

All forty retained item digests recompute exactly, including the nine event digests and fourteen event-result row digests. Every recorded owner decision points to its independently recomputed item digest: twenty-six links match, with no missing or unknown decidable items. Events include their result rows in retained order, and that order matches each event's explicit `rows` list. No producer helper was imported or executed.

The aggregate candidates digest matches both the retained declaration and REF-072's approved digest:

`sha256:7fe88a9167a9363f5c2bfdcd3911953b7323abe1564d40586991c9612f95f4bc`

The optional whole-report check also matches:

`sha256:449b89032917badfa1be4462f7d7b6f9d442210797092009c4e4b40a7b9b4431`

## Explicit rule sources

`plans/agency-registry-design.md:175–195` describes per-item binding, event-member coverage, excluded replay/effects, and the stale-decision rule. `tools/assemble_agency_registry_batch_1.py:85` declares the two excluded entry fields, `content_digest` and `effect_note`; lines 1355–1374 define the entry/member preimage and canonical JSON encoding. Lines 1581–1599 bind event rows to the event. `src/refspec/atlas/v3_registry_alignments_entity.py:1256` and the JSON's own `candidates_digest_covers` explicitly name the four aggregate fields: `candidates`, `events`, `non_emissions`, and `no_fr_bridge`. REF-072 at `docs/decisions.md:5977–5986` names the approved aggregate and the bound owner decisions. [Definition context](definition-context.json) retains exact line excerpts and file hashes.

The independent replay implements those declared rules with Python's standard library: UTF-8 JSON, sorted object keys, unchanged array order and Unicode, compact separators, no terminal newline, and SHA-256. The individual item preimage has `entry` and `members`; a non-event has an empty member list. The aggregate hashes the four full retained arrays, including their declared item hashes. Recomputed individual hashes are checked first, so the aggregate cannot conceal an inconsistent item hash.

## Mutation evidence

[The receipt](receipt.json) records six in-memory controls. Changing a bridge's reasoning stales only that bridge decision. Changing an event's date basis stales that event. Changing one result's functions changes that row and its containing event digest, and stales the event's decision. Rewording an owner option stales that item's decision. Each changed covered field also breaks the declared aggregate match.

The exclusions are checked separately: changing `effect_note` leaves the individual item and decision current, while changing a top-level replay count leaves every item and the aggregate unchanged. The whole-report digest still changes for the replay count. One precise distinction matters: the aggregate covers the full four arrays, so an `effect_note` inside them changes the aggregate even though it is excluded from an individual decision's digest. No coverage ambiguity was found in the explicit definitions.

## Replay

```sh
python3 /path/to/digest-recheck/scripts/recheck_digests.py \
  --repo /path/to/RefSpec \
  --output-dir /tmp/agency-digest-recheck
```

`--repo` defaults to `REFSPEC_REPO`, then the current directory. Output must be outside the repository. The script reads files only and performs mutations in memory. A second execution from `/tmp` produced byte-identical receipts. The completed prior `retain/` package and original evidence remain untouched. This addon closes its stated candidate-content digest limitation; it does not change any owner decision or expand source acquisition.
