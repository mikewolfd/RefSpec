# Atlas repair implementation and validation

The [F1–F14 repair proposal](../../../plans/atlas-refresh-repair-plan-2026-09-27.md)
is implemented locally. Full-corpus qualification is pending a fresh measured
build and independent audit. Package adoption, artifact qualification and public
promotion remain separate results. The previous incomplete output and the
August artifact remain intact.

## Implemented behavior

| Findings | Change and executable evidence |
| --- | --- |
| F1 | Preserve the per-language preferred-label correction and its frozen old-shape oracle in `tests/test_atlas_v3_preferred_languages.py`. |
| F2–F4 | Correct declarations; parse LC captures once per family and select each vocabulary independently; compare expected canonical payloads and exact UMTHES transformations; reuse provenance results within one invocation. See `tests/test_atlas_provenance_repair.py` and `tests/test_verify_atlas_source_fidelity.py`. |
| F5–F7 | Independent positioned-PDF and agency adapters, exact docket-status checks, declaration/implementation coverage, separately pinned review evidence. Real retained UMTHES, PDF and agency audits passed their scoped gates; retained receipts explicitly identify excluded comparisons. |
| F8–F10 | Reuse bounded expected graphs for accounting, drain owning queues, reread derivation spools, remove repeated forced full GC, bound sort chunks by bytes, and enforce actual binding byte limits. Frozen accounting oracle and mutation tests are in `tests/test_atlas_builder_capacity_repairs.py`. |
| F11 | One exclusive phase harness records RSS and physical footprint separately, disk/host observations, elapsed/CPU time and failure status. macOS permits swap within the footprint budget; Linux requires a real delegated cgroup v2 with an explicit swap limit. Tests cover timeouts, descendant cleanup, resource stops and unavailable controls. |
| F12–F13 | A shared qualification command pins a completed distribution, copies and runs the standalone binding in audit mode, requires complete publisher comparison and agency evidence, verifies the full view, then builds/verifies the compact view. Compact decoding selects only required columns while authentication still reads all bytes. The workflow stages authenticated agency evidence before its costly build. |
| F14 | Candidate RefSpec version is `0.1.0.dev22`. Isolated DocSpec and SpicySearch adoption checks use normally resolved installed wheels. Publication requires a trusted search-view pin, frozen output inventory, exact served-byte checks and Worker version; candidate upload and active selection verification have distinct receipts. |

The altered-transformation artifact test reseals all dependent identities,
accounting and transport bytes: both baseline and mutation pass the standalone
binding, while publisher fidelity rejects only the altered transformation.
The LC test uses a dependency-complete sample extracted from the authenticated
real ZIP and a copied grouped-reader oracle. It proves selection/cache behavior;
it is not a full-family capacity measurement.

Fast adapter tests use committed bounded fixtures. Retained-artifact tests fail
explicitly when their required bytes are absent. See
`tests/fixtures/atlas_independent_adapters/README.md` for replay prerequisites.

## Performance, Big O, DRY and KISS

Let `B` be processed bytes, `I` retained identities, `b` the construction batch,
`Bg` its RDF/payload footprint, `R` releases, and `r` sort runs. Hash-table bounds
are expected-case; string hashing/comparison also costs bytes.

| Path | Implemented cost and remaining limit |
| --- | --- |
| Mapping accounting | `O(B)` fact processing plus canonical sorting; `O(Bg + I)` temporary graph/identity state. The full build still preloads source models and retains corpus-sized accounting and ownership IDs. |
| Release queue | Reverse once and pop: `O(R)` queue work, replacing `O(R²)` front deletion. Repeated whole-heap collection is removed. |
| Sorting | Bounded serialized chunks and existing bounded merge; `O(B log_f r)` merge I/O at fan-in `f`, plus comparisons and Python/string overhead. Record count alone is not a byte bound. |
| LC and provenance | Shared capture parsing costs `O(B)` plus selection/sorting. Expected payloads are hashed once; each immutable source pair is compared once per audit invocation. |
| Requested hierarchy paths | Worst-case `O(s(V+E) + Q)` traversal/query work for `s` queried starts and `Q` requested pairs; `O(V+E+Q)` state. Exact reachability remains required. |
| PDF and coverage | Per-page word sorting/sweep: `O(W log W)`; keyed declaration coverage: `O(declarations + units)`. |
| Compact/public views | Compact writing avoids unused column decoding; authentication remains `O(all stored bytes)`. Public verification streams `O(served bytes)` with bounded buffers. |
| Standalone/full fidelity | Full dataset and family views remain resident. Bounded tests do not prove the full-corpus memory ceiling. The measured full run decides whether further execution changes are necessary. |

[Accounting measurements](accounting-scaling.json) compare separate cold
processes at 1×, 2× and 4× record and release counts. All old/new accounting
digests match. At 4×, the old expected graph reached 15,362 triples; the new
graph stayed at 962 with a 32-claim test batch. Measured physical footprints
were about 114–116 MB old and 92–93 MB new. These are accounting-only probes;
they do not measure full derivation, input loading or release qualification.
The reproducible driver and raw native timing observations are retained here.

DRY: the builder reuses its exact batch graph, the verifier shares parsing but
keeps publisher semantics independent, qualification uses existing validators,
and upload/verification share one publication checker. KISS: no new graph engine,
persistent cache, scheduler, recovery subsystem or agency policy framework.
Adaptive pack splitting and family-at-a-time fidelity remain conditional on an
observed failure; the present writer fails explicitly at the existing limits.

## Run and receipt locations

Local command logs and resource samples are under
`output/atlas-refresh-repair-validation/`. This directory retains bounded audit
receipts and scaling evidence with [checksums](SHA256SUMS). Audit receipts record
the tool hashes used at execution; later code edits require a new qualification
receipt, not a rewritten old receipt.

For a Linux release runner, configure `ATLAS_CGROUP_PARENT` and a retained
`ATLAS_AGENCY_EVIDENCE_ROOT` outside the checkout. The latter contains the frozen
manifest's `retainedPath` members. `tools/stage_atlas_audit_evidence.py` authenticates
all members before copying missing originals without overwriting existing files.
It performs no network acquisition. The workflow still requires an operational
runner/store and signing-key decisions before public release.

After a successful fresh build, use `make qualify-atlas-release` with the exact
distribution/full-view pins, agency view/evidence/review pins, separate compact
output and report directory, and explicit memory/time limits. See
`tools/qualify_atlas_release.py --help` and `.github/workflows/release.yml` for
the same runnable argument list. A failed or incomplete phase stops the sequence.

Public delivery follows
[the candidate publication procedure](../../../deploy/cloudflare-explorer/build/PUBLICATION.md).
No upload, deployment, promotion or public UI verification has run in this repair.
