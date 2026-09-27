# Independent verification of Atlas fidelity configuration and coverage

Verified against `cc507773` in `/Users/mikewolfd/Work/spicy-stack-worktrees/refspec-atlas-refresh-20260927`. This investigation made no repository edits and did not run or interrupt a full build. It independently reproduced the reported declaration problems, exercised the LC cache defect, and inspected retained source specimens. It does not constitute a passing full-distribution source audit.

## Confirmed findings

1. **All three configuration errors are real verifier inconsistencies.** `scripts/check_config.py` calls the current `check_configuration` with the complete actual `SOURCES` registry and a tiny declaration-only context. It reproduces exactly the LC one-unit error and the eCFR/Regulations.gov `publisher-key` errors. The check explicitly examines scoped-out declarations (`tools/verify_atlas_source_fidelity.py:20832`), so `--only` cannot bypass them. Configuration validation supports `source-key-derived`, not `publisher-key` (`:20851`); the roster declarations are `:19044` and `:19086`. These are invalid audit declarations, not demonstrated producer data defects.

2. **The roster policy fix is a naming repair supported by actual source records.** The independent stock readers authenticate the retained inputs and reconstruct 316 eCFR records and 331 Regulations.gov records (`scripts/check_agency_identity.py`, `receipts/agency-identity.json`). eCFR identity is `urn:ref:ecfr-agency:` plus the publisher slug (`:4885`); Regulations.gov uses the publisher agency ID (`:5440`). Raw eCFR record `economic-analysis-bureau` appears beneath parent `commerce-department`, with name `Bureau of Economic Analysis`, display name including the department, short name `EAB`, and CFR title 15/chapter VIII. Raw Regulations.gov `ABMC` has type `agencies`, name `American Battle Monuments Commission`, null parent, and self-link ending `/agencies/ABMC`. These are source-key-derived identities. Replacing only each spec's identity policy with `source-key-derived` makes its configuration check pass; this does not establish fidelity of a generated distribution.

3. **The LC split has a reproduced cache defect.** The declaration at `:17932` groups 14 non-FAST construction units, violating the one-unit rule at `:20868`. The actual reader selects vocabulary from `spec.release_keys` (`:10737`), but the cache key at `:20566` excludes release keys and excludes `spec.name` for this reader. `scripts/check_lc_cache.py` uses the actual reader and actual `build_context` with a two-vocabulary synthetic ZIP. Individually AGROVOC returns only AGROVOC and Getty AAT returns only Getty. In the combined context, both specs receive AGROVOC. Input authentication passes; deliberately absent distribution files are recorded separately and do not cause the publisher-cache result. Evidence: `receipts/lc-cache.json`.

   A split declaration must also make the publisher view depend on vocabulary selection. The smallest correctness repair keys the cache by the declared selection for this reader. It would repeat two scans of the shared ZIP per vocabulary, so a better bounded implementation parses the shared ZIP once into partitionable records and selects each unit afterward. Preserve the current grouped reader as a test-only oracle and compare the union of partitions against it on the real pinned file. Do not relax the one-unit check merely to silence this error: grouping loses the ability to prove the contents of each individual unit. Note that `SPEC_SCOPED_RECORD_READERS` also changes which Atlas subjects are treated as publisher concepts (`:23721`); adding LC there changes more than caching and needs a test proving those subject sets stay correct.

   The retained raw ZIP mixes names, subjects, and label statements. Its first 30 lines are retained in `receipts/lc-first30-lines.txt`: line 11 maps an LC **name** to FAST; line 13 maps LC **subject** `sh97007572` to RAMEAU `cb124656189`; other lines are labels with no connecting subject claim. This context confirms that selecting every endpoint label or every LC link would be wrong. The reader's subject-prefix filter is meaningful.

4. **The four missing construction-unit comparisons are real coverage gaps.** Independent imports of the producer's `_declared_construction_unit_keys()` (`tools/generate_atlas_v3_full.py:2304`) and verifier `SOURCES` produce 131 producer keys, 127 verifier keys, no verifier-only keys, and exactly these missing keys:
   - `agency-registry-2026-09-26`
   - `ferc-docket-prefixes`
   - `ferc-document-class-types`
   - `unified-agenda-legal-authority-citation-types`

   The actual `check_distribution_coverage` is also exercised with the declared units and all existing comparison specs represented as loaded. It fails exactly these four units (`receipts/repair-probe.json`). That is a declaration-coverage test, not an assertion that any actual source data loaded or passed fidelity. In-memory splitting of LC and changing the two policy names makes global configuration pass with zero configuration failures while the four coverage failures remain.

## What the omitted comparisons must verify

### FERC document class/type table

Producer loader: `src/refspec/atlas/v3_registry_codes.py:694`, class mapping `:716` and release `:731`. Input `output/registry-real-data-sources/ferc-class-types-january-2025.pdf`, 193934 bytes, SHA-256 `af632c9c6adbf0e7919d17e018b3a65078d0746bd1ab69a8d9fa65043720d688`.

I rendered and inspected page 4, including column headings and surrounding rows. It has four distinct columns: Category, Library, Classification, Type Description. One row is `Submittal | E | Report/Form | Annual Charges Report`. Independent Poppler extraction finds the same description under `G` on page 5 and `H, E and RM` on page 7; only page 4 was visually inspected. Identity cannot be keyed by display label. A comparison needs all four values, page/row position, native `text`, and source evidence. The producer intentionally uses row-position identity, with Type Description as display label. Independent extraction should use the existing verifier's stock PDF infrastructure without importing `refspec.registry.ferc_elibrary_codes`. Tests need a duplicate-label/different-library pair, swapped classification, dropped row, and stale source pin.

### FERC docket prefixes

Producer mapping: `src/refspec/atlas/v3_registry_codes.py:744-782`; parser `src/refspec/registry/ferc_elibrary_codes.py:326`. Input `output/registry-real-data-sources/ferc-docket-prefix-june-2025.pdf`, 282729 bytes, SHA-256 `c32efae9f51a70b6f955821d2fb3d3025995ef0e17e57bf2d32dfa16c2508dcb`.

I rendered and inspected page 6. It is explicitly headed `Table 3 - Discontinued Prefixes`, with Prefix, Library, Definition columns. `AR | G | Area Rate Proceedings - Independent Natural Gas Producers` is a discontinued record, not an active prefix. `CI` has a wrapped definition ending in `Marketers`; `DA` carries replacement prefixes in its definition. A correct independent comparison must retain table-derived active/discontinued status, complete wrapped definitions, prefix notation, library, and source-local row identity. Tests need a table-status swap, dropped continuation line, changed notation/library, and omitted discontinued row.

### Unified Agenda citation types

Producer mapping: `src/refspec/atlas/v3_registry_codes.py:1757-1820`; transcribed definitions `src/refspec/registry/unified_agenda_codes.py:134`. Input `tests/fixtures/unified_agenda_codes/risc-preamble-202210.pdf`, 148467 bytes, SHA-256 `b7372fec456cf0c346bd23528ae227913e37f546bb1c03689da19ee6a44cb2a5`.

I rendered and inspected full pages 18 and 19. Section V is an abbreviations glossary, with E.O. on page 18 and Pub. L./U.S.C. on page 19. It also contains unrelated abbreviations such as CFR, FR, FY, RFA, RIN and Seq. No.; matching every abbreviation would overstate this source slice. The producer deliberately selects three citation types and publishes each glossary definition. The U.S.C. definition itself says the Code is divided into 50 titles; fidelity must preserve this historical publisher statement rather than silently modernizing it. This is `captureSubset`, not proof of a complete contemporary legal-identifier universe. Verify exact selected values, definitions, notation/identifier, source locator and native fields. Mutations should alter a definition, admit an unrelated glossary abbreviation, omit one type, and mutate its identity.

### Agency registry owner decisions

Producer: `src/refspec/atlas/v3_registry_alignments_entity.py:1670`, input construction `:1774`; authenticated plan pins `:1249`. Raw candidate and decision files were read directly. Their actual hashes match producer constants:
- `plans/agency-registry-batch-1-candidates.json`: 191706 bytes, SHA-256 `6bb7c2d4dc818b24cb92b1e220704b9d9acb9afc6be6fc400c0daccde14b71d2`.
- `plans/agency-registry-batch-1-decisions.json`: 6744 bytes, SHA-256 `a454ea277d533ce25a331a996a676d58f0bd2573700a43893a1f52b6c8938098`.

Example: `same:fr118:ecfr:economic-analysis-bureau` has Federal Register `Economic Analysis Bureau` and eCFR `Bureau of Economic Analysis`, both under their respective Commerce records. Candidate context explicitly rejects FR150 Export Administration Bureau despite the shared `EAB` short name. The separate decision file says `yes` and binds the same content digest. A verifier must reconstruct names/parents from pinned rosters and independently bind the adopted decision to the correct candidate content, not infer identity from the acronym.

This release is also more than identity triples. Example `event:fr564` binds the owner answer `1` to the dated succession of Postal Rate Commission to Postal Regulatory Commission, with a stated alternative of treating them as duplicate identities. The pinned candidate's public-record list contains URLs and source summaries; these are not the public-record bytes. The release's input list pins the five rosters plus candidate and decision documents. Thus an audit can independently prove fidelity to retained owner decisions and roster evidence; it must not claim it reauthenticated every statute/notice behind those judgments without acquiring those bytes. The existing source-fidelity verifier has no event-specific `OrganizationChangeEvent`, `effectiveDate`, `originalOrganization`, `resultingOrganization`, or `functionsTaken` comparison. Simply adding a generic mapping spec would not adequately prove the event portion. Tests must mutate decision digest/outcome, cross-roster parent/name, event date/original/result/function, and a recorded non-emission, and must ensure an identity triple is never substituted for succession.

No producer defect was established by these missing adapters. The source specimens explain what a valid independent comparison must cover; they do not substitute for such a comparison across every emitted row.

## Replay

The `scripts/` probes accept `--repo` (defaults to `REFSPEC_REPO` or the current directory) and require `--output-dir` outside that checkout. They authenticate and read retained inputs only. They do not fetch data, edit checkout files, or run expensive builds. The LC diagnostic creates and removes its tiny synthetic ZIP in the output directory. The combined runner also records source revision and diagnostic code digests.

Run from the RefSpec checkout, using absolute paths to the retained runner and a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --frozen python /path/to/retained/scripts/run_all.py \
  --repo "$PWD" \
  --output-dir /path/outside/checkout/atlas-gap-replay
```

The `receipts/` directory contains a replay from the retained scripts. `receipts/portability-replay.json` also records a successful replay launched from `/tmp` with an explicit `--repo`, proving it does not rely on the caller's working directory. `receipts/replay.json` records the source checkout revision, script hashes, exit codes, and comparison with the first diagnostic results. A success means that the recorded failure conditions reproduced; it is not an Atlas source-fidelity pass. Assertions intentionally fail after the underlying defects are fixed, keeping these historical diagnostics honest.

`receipts/raw-context.json` holds exact selected JSON records with input paths, hashes and JSON pointers. `receipts/lc-first30-lines.txt` preserves the initial ZIP-member context with source line numbers. Selected rendered PDF pages are retained with the exact source PDF hashes and rendering commands in `specimens/rendered-pages.json`. Full ZIP/PDF inputs are not duplicated here.

A future fix should freeze the current check as an oracle, add real-data comparisons plus mutations and named deliberate divergences, and add an always-run declaration-coverage/configuration test so these registry changes cannot silently outrun the verifier again.
