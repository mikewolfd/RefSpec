# Atlas refresh, 2026-09-27

The refresh starts from RefSpec dev21 (`41e2bf9d`, SpicyDocs 0.46.0) on
`lane/atlas-refresh-20260927`. Commit `cc507773` corrects the independent validator's
preferred-label rule before rebuilding the full Atlas. Bounded artifacts pass
independent validation, but the full build stopped at its memory guard before
producing a completed distribution. Full qualification remains blocked by
capacity and the source-fidelity verifier defects documented below. Nothing
in this lane has been published.
This revisits the [August acceptance findings](../acceptance-gate-blind-spots-2026-08-21.md)
against current code and retained publisher inputs.
No wheel was rebuilt from the changed source. The existing dev21 wheel belongs
to its unchanged release worktree; shipping this correction requires a new
package version and verified consumer pins, rather than different bytes under
the same dev21 version.

## Label policy and source evidence

REF-037 and the binding README allow one preferred label per language. The
resource shape instead imposed one preferred label in total. The retained
UMTHES archive
`output/registry-real-data-sources/umthes-gemet-endpoints-2026-08-15.zip`
(SHA-256 `978b10cd1e3f2f8729372a86f2afa1b62d2790e4810c6d57af5343835259d25f`)
contains the counterexample in `records/_00000013.nt`.

Its subject `https://sns.uba.de/umthes/_00000013` is a SKOS concept in the
UMTHES scheme, with `"Abbau"@de` and `"degradation"@en` explicitly marked
as preferred labels. The surrounding triples mark `"Abbaumechanismus"@de`
and `"decomposition"@en` as alternatives, and link broader concepts
`_00047435` and `_00049270`. Thus the two preferred labels belong to the
same concept and are neither alternative labels nor labels of a parent.

The shape now uses `sh:uniqueLang` over preferred literal forms. The linear
label-integrity check counts label identities before deduplicating literal
values: distinct label nodes carrying identical preferred text in one language
must still fail. This adds no global graph traversal; it remains linear in the
labels already visited for each resource.

`tests/test_atlas_v3_preferred_languages.py` retains the old cardinality
clause as an independent test-only oracle. Its mutation table freezes the
intended difference: distinct languages change from refusal to acceptance;
duplicate languages, including identical literals on distinct label nodes,
remain refused. The real publisher specimen and the duplicate-literal mutation
both reproduced their failures before the correction. The conformance corpus
now exercises both cases. Publisher inputs and the adopted language policy
remain unchanged; the binding digest and dependent release digests change.

## Completed checks

- Pinned input verification: `uv run --frozen python tools/fetch_pinned_inputs.py
  --check --workers 2` exited 0. Inputs were cloned into this isolated worktree;
  no mutable generated output is shared with the dev21 worktree.
- Focused oracle and publisher regression tests exited 0.
- `make contract-dev` exited 0: regenerated corpus accepted, bounded release
  rebuilt, smoke checked, and independently compared with the publisher input.
- The bounded audit-mode shape benchmark exited 0: 2.0 seconds against the
  existing 2.5-second baseline, within its tolerance. This is a bounded-shape
  regression check under shared host load, not a full-Atlas capacity measurement.
- Agency registry view build and `--check` exited 0 and reproduced
  `sha256:77b357cc06fe3e67bcacb0591833884087572727064f89643e10aa2a28ad6b87`.
- Lint, strict RDF parsing, generated-file checks, registry inventory and JSON
  binding checks passed. `make test-package` exited 0 with 6,271 passed and the
  existing strict expected failure. With four workers under shared load it took
  170 seconds, within the 240-second runaway limit but above the target.
- The binding's slow tests exited 0: six tests, including the default and
  fallback RDF stores, exact fixture rebuilding and receipt invalidation.
- A complete UMTHES-only distribution passed the standalone validator (exit 0).
  Its manifest SHA-256 is
  `474328e2a2d2bcbbcb2c00861afc18831c215c06ec82b826700b79c845838e02`.
- A bounded distribution containing both FERC tables and the Unified Agenda
  citation types passed standalone validation (exit 0).
- The agency-registry distribution, including all endpoint dependencies,
  passed standalone validation (exit 0) over 2,249,291 quads. Its manifest
  SHA-256 is `560266ed48d2db7a8c86cddd861f17f31f9b3d6ead7f10edbdc45be61de14dc1`.
  The [bounded artifact receipts](bounded-artifacts.json) retain all manifest
  and view pins, counts, exit codes and log locations.

The bounded release pins now recorded in the Makefile are:

| Manifest | SHA-256 |
| --- | --- |
| Federal Register distribution | `27ba0277a2ee407ee6527ac9d327e08a85d89f7e75974fa13bd8e3bbcdabfc9c` |
| Federal Register Parquet view | `ad545cd4e53f299c44e1228d88cc8c7c7530eb81eff0fe7525f031fe18a58000` |

Local execution logs, exit codes and memory samples are under
`output/atlas-refresh-2026-09-27-evidence/`. `checks.log` records a run that
started with the first correction's superseded pins and stopped at the digest
comparison; `checks-final.log` reruns the gates with the final pins.
That run passed the preliminary gates but the fast tier exceeded its initial
8 GiB process-tree limit near the end (exit 143). `test-package-final.log`
records the complete retry under a 12 GiB cap, exit 0.
The initial bounded agency attempts refused missing referenced releases;
the successful `agency-build-complete-closure.log` includes the agency unit,
its rosters, Treasury accounts and CFR titles. Those earlier scope errors are
retained in `checks.json`; they are not failures of the completed distribution.

## Source-fidelity blockers found independently

The [retained UMTHES fidelity receipt](umthes-source-fidelity.json) records a
failed run (exit 1); its SHA-256 is
`cf10dbcb4b6023cda256c964d4334a79ea780c6a4914d11e21f421e790b3c1ab`.
Labels, identities and admitted relations agree with publisher bytes, but this
is not a passing source-fidelity result. These repairs remain:

- The global declaration check rejects the grouped
  `lc-external-target-endpoints-2026-08-15` comparison for owning multiple
  construction units, and rejects the eCFR and Regulations.gov agency rosters'
  `publisher-key` identity policy. The check intentionally examines scoped-out
  declarations too. These errors also reproduce with the real declarations
  and a tiny synthetic context, without a large data build. Repairing the LC
  declarations must preserve correct per-unit comparison and shared-input
  caching; simply splitting the declaration would reuse the wrong cached
  publisher subset because its reader is not in `SPEC_SCOPED_RECORD_READERS`.
- UMTHES provenance still expects raw response digests in `atlas:sourceDigest`.
  `_add_source_record` now writes the digest of canonical `nativePayload`, and
  the independent binding validator verifies it. On source record
  `urn:ref:atlas-source-record:000e6359baff727a9e55e40b8c8f9a4415e901c9dd60e211ae529b73df9b0f08`,
  for publisher concept `_00028834`, both the stored record digest and the
  independently hashed payload are `b2f45f92...be4eaba8`. The raw archive
  member hashes to `3c81b1fe...1bf8974`, exactly the retained
  `responseDigest`. The verifier compares those two different meanings and
  refuses the record. Its provenance check reports 3,415 differences across
  resource and relation evidence records. A repair must continue comparing
  the retained response digest and all native fields against publisher bytes;
  accepting a self-consistent payload alone would weaken the check.
- The [declaration comparison](fidelity-declaration-coverage.json) finds no
  independent comparison for `agency-registry-2026-09-26`,
  `ferc-docket-prefixes`, `ferc-document-class-types`, or
  `unified-agenda-legal-authority-citation-types`. This compares the producer's
  declared construction keys with the verifier's actual `SOURCES`; it does
  not treat a catalog entry or a passing producer test as publisher-fidelity
  coverage. Production comparisons remain missing. The independent checks
  below provide bounded source and mutation evidence for implementing them;
  they do not complete the full artifact's qualification.

Replay the bounded audit with:

```sh
uv run --frozen python tools/verify_atlas_source_fidelity.py \
  --distribution output/atlas-3.1-umthes-2026-09-27/distribution \
  --only umthes-gemet-endpoints-2026-08-15 \
  --output output/atlas-refresh-2026-09-27-evidence/umthes-source-fidelity.json
```

The shape correction does not change these declarations, digest rules or
publisher claims. These failures block source qualification and downstream
adoption of the refreshed full artifact.

### Independent rechecks

Separate reviewers reproduced the declaration failures, missing comparisons,
and UMTHES provenance failure from current code and retained inputs. They also
reran the label regressions and complete UMTHES standalone validation. Their
retained [configuration and coverage report](independent/configuration/REPORT.md)
and [provenance report](independent/provenance/REPORT.md), together with the
[validation review](independent/validation/README.md), include portable replay
scripts, source specimens and checksummed results. A successful diagnostic
process means it reproduced the finding; it is not a passing Atlas audit.
Their checks distinguish the following additional findings:

- The LC cache problem is demonstrated with the actual reader and context
  builder: separately, AGROVOC and Getty select their own records; together,
  the proposed split reuses AGROVOC records for Getty. Fixing the declarations
  therefore also requires correct selection-aware caching.
- An independent archive-to-artifact comparison found no discrepancies in
  UMTHES resource payloads, transformed-relation payloads, payload hashes, or
  SourceRecord identities. The current verifier still rejects different
  digest meanings. Its failure is not evidence that those publisher records
  were corrupted.
- The relation verifier misses altered provenance. Mutating a retained
  relation's `responseDigest` or transformation reason and recomputing its
  internal hashes adds no failure to the already-failing audit. Mutating the
  relation object is detected. This demonstrates a missing independent field
  comparison; it does not mean a compromised distribution passed the audit.
- Bounded authenticated probes reproduced the digest mismatch beyond UMTHES
  in Federal Register API topics, GCMD, GovInfo collections, retained GAO
  topics, and EuroVoc-to-MeSH mapping evidence. BILLSTATUS bill types provide
  a counterexample: a missing policy flag does not itself prove a mismatch.
  The green `contract-dev` check uses a separate verifier and the Federal
  Register PDF thesaurus, not the API-topics comparison implicated here.
- Agency-registry verification must cover change events and non-emissions as
  well as identity bridges. The retained owner decisions and roster inputs
  support checking their own faithful representation. Public-record URLs and
  summaries in those decisions do not constitute retained legal-record bytes.
  Adding a generic mapping comparison would leave event dates, organizations,
  function transfers and non-emissions unverified.

The full-Atlas pytest tier performs producer-side construction checks. It does
not call the standalone file validator or the publisher-fidelity verifier.
Likewise, the historical optimized standalone capacity measurement covers a
smaller distribution; it does not establish capacity for the refreshed full
artifact. Actual full validation remains a separate required run.

### Data checks for the omitted vocabulary units

The [independent vocabulary comparison](independent/omitted-vocabularies/REPORT.md)
checks the actual bounded Parquet output against a separate PDF extraction.
All docket-prefix records and selected Unified Agenda citation types match.
The FERC class/type table has one explicit exception: the visible page and
emitted row end in `Hinshaw Pipe`, while the PDF text layer also contains
`lines`. Full-page and high-resolution renders confirm the emitted reading;
the text-layer observation remains in the receipt. This is neither an
unconditional class/type pass nor a confirmed producer defect. Appending the
extra word would also change the derived resource identity.

The remaining class/type rows match. The comparison authenticates view-member
pins and source-record payloads and detects mutations of fields, row coverage,
identities and input pins. These bounded checks add substantive data evidence;
they do not install the missing production verifier comparisons or qualify the
full Atlas.

### Agency source and emitted-record comparison

The [independent agency comparison](independent/agency/REPORT.md) checks the
bounded RDF distribution and the separately sealed agency-registry Parquet
view. Events, result rows, identity bridges, recorded non-emissions, selected
roster names/parents and owner decisions match, with no differences. The
comparison also checks their evidence bindings, native-payload hashes and RDF
record hashes; deliberate corruptions are detected.

The reviewer retrieved every cited primary record, inspected the relevant
rendered PDF pages, and joined those source claims back to the emitted fields.
The receipt preserves the selected date meanings: an order date is not silently
relabeled as an express legal effective date, and a statutory rename does not
independently resolve the owner's identity-versus-succession judgment. No
selected-date or function-split contradiction was established within the cited
source scope. The uncited FARRA section 1601 plan remains outside that scope.

Original public-record bytes and their acquisition receipts are retained in
`output/atlas-refresh-2026-09-27-evidence/agency-primary-sources/`; the compact
report, claim receipts, source hashes, reviewed context and replay are under
`independent/agency/`. Those acquired document hashes are separate from the
artifact's native-record digests. They do not change the frozen producer inputs.
The generic Atlas Parquet view intentionally omits change-event tables; the
event-row comparison concerns the dedicated agency view. The production
source-fidelity verifier still lacks this comparison.

The separate [candidate-digest recheck](independent/agency-digest-recheck/REPORT.md)
closes the original agency report's digest limitation. An independent
standard-library implementation of the documented rules reproduces every
item, event and event-result digest, every owner-decision link, the approved
aggregate and the whole-report digest. Covered-field mutations stale the
expected decisions. The checks also confirm the precise exclusion rule:
`effect_note` is excluded from individual decision hashes but remains covered
by the aggregate. This verifies the recorded approval bindings without
changing the decisions or extending the primary-source scope.

### Release and deployment observation

The initial [read-only remote observation](deployment-observation.json) records
main at `afea0826`, no open GitHub pull requests or GitHub releases, and the current
Cloudflare account's response for `refspec-atlas-explorer`: the Worker does not
exist in that account. This does not establish its state in another account or
at an unknown public URL. The check used the project's pinned Wrangler and
the documented [deployment-status command](https://developers.cloudflare.com/workers/wrangler/commands/workers/#deployments-status).
No remote state was changed.

A follow-up at 20:39Z found both local `main` and live `origin/main` advanced
by the other owner to dev21, `41e2bf9d`, with a clean main worktree. Its separate
release worktree had been removed. The retained
[completed-tier evidence](dev21-completed-tiers/) records the slow tier passing
and the full-Atlas producer tier finishing at 20:37:30Z with exit 0. Those tests
run against dev21 and do not include this lane's label correction or validate
this lane's full output. Our correction remains on its local branch; this lane
made no remote writes. The Cloudflare observation above remains scoped to its
earlier timestamp and authenticated account.

## Full artifact qualification

The new build uses its own output directory, including its own Parquet view:

```sh
uv run --frozen python tools/generate_atlas_v3_full.py \
  --output output/atlas-3.1-full-2026-09-27/distribution
```

The build ran from 18:54:43Z to 20:36:38Z and exited 143 when its existing
18 GiB process-tree RSS guard stopped it. The last observed peak RSS was
20,499,008 KiB; periodic sampling can overshoot the configured limit. All source
and mapping release construction phases had finished. The last status label,
`derive-registered-relations`, also spans later accounting work and does not
identify the exact function that exhausted capacity.
The [capacity evidence](independent/full-capacity/README.md) retains the raw
logs, memory measurements, source excerpts, native sample and partial-output
inventory with checksums.

RSS understated memory demand on this macOS host. At 20:35:50Z, the builder's
measured physical footprint, including compressed or swapped pages, was
33,772,217,664 bytes (31.45 GiB). The separately owned full-Atlas test worker
also had a large footprint. Host pressure fell after our guard stopped the
builder. This is a capacity interruption under concurrent load, not a semantic
validation failure or a measurement of isolated build capacity. No agent sent
a manual stop signal, changed the guard, or interrupted the other worker.

No completed distribution was promoted. The retained partial output cannot
establish final manifest hashes, pack-size compliance, or a comparison of the
new full artifact with August's. The full standalone validator and compact
search-view build therefore did not run. The existing August artifact and the
partial build output remain intact; the build has not been restarted.

After a completed build, qualification still requires actual pack-bound
checks, the standalone distribution validator, the independent publisher-
fidelity verifier, and generation and verification of the compact search
view. The bounded passes above do not satisfy those full-artifact checks.
Downstream adoption and public deployment remain separate steps.

## Measured build overhead

Small releases showed a roughly six-second pause even when they emitted only
a few resources. A one-second native sample of the running builder, retained
as `output/atlas-refresh-2026-09-27-evidence/full-build-small-releases.sample.txt`,
put all main-thread samples in `gc.collect()`.
The [retained sample excerpt](small-release-profile.txt) includes the timestamp
and complete main-thread stack. `_stream_construct_graphs`
retains `all_source_releases` and `all_mapping_releases` for later derivation
and validation, but collects the entire tracked heap after every release.
That repeats work over the retained input population for each release, rather
than just the temporary objects for the release that finished. This is a
profiled optimization lead, not a measured end-to-end speedup. The build source
remained unchanged throughout the attempt; any change to collection lifetime needs
separate output-equivalence and peak-memory evidence.

A later native sample during the `derive-registered-relations` phase shows
sorting and string processing rather than the earlier repeated collection.
That status label also spans source-accounting reconciliation; it does not
identify which Python function was active. The code subsequently rebuilds the
expected mapping graph through `_mapping_accounting_expectations`, so a
phase-specific memory or timing claim needs more precise evidence. The raw
sample is retained as
`output/atlas-refresh-2026-09-27-evidence/full-build-derived.sample.txt`.
