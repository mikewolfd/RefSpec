# Columnar Atlas audit: architecture review

## Findings and decision

**RESHAPE the full audit around DuckDB queries and bounded Arrow batches.**
The current whole-graph Python store has exceeded the local memory guard.
Retain independent verification of canonical RDF and publisher evidence; change
how facts are processed. This is a design recommendation, not an implemented
replacement or a measured performance result.

- **CONCERN — corpus-sized resident state.** The standalone parser accumulates
  all packs in one dataset (`bindings/atlas/3.1/tools/validate.py:3145`), with
  two Python lookup indexes (`parse_substrate.py:101`). The retained
  [capacity receipt](repair-validation/full-qualification-capacity.json) records
  the full audit stopping during parsing. Replace those resident structures
  with streamed local checks and spillable global operations.
- **CONCERN — the existing columnar path still loads whole tables.**
  `src/refspec/atlas/parquet_preflight.py:597` calls `pq.read_table` for every
  member, retaining all columns. Its checks use Arrow, not DuckDB. Reuse their
  semantics, select only needed columns, and use DuckDB for global joins and
  duplicate detection rather than another bespoke indexing layer.
- **BLOCKER to using today's Parquet alone — incomplete audit coverage.**
  The binding explicitly omits organization-change events and their bindings
  from the ordinary typed view (`bindings/atlas/3.1/README.md:575`). The preflight
  also explicitly excludes release-only checks
  (`src/refspec/atlas/parquet_preflight.py:66`). A passed preflight cannot replace
  full qualification. Account for RDF-only facts and prove complete correspondence
  for every field used by a migrated check.

## Artifact and lineage

This review concerns proof infrastructure at RefSpec revision `d6e15122`.
The beneficiary is release qualification, currently unable to finish within
the measured local memory budget.

| Prior decision or component | Relationship |
| --- | --- |
| REF-026, `docs/decisions.md:1217` | Prove conformance at release/audit boundaries; consumers verify authenticated artifacts. |
| REF-028, `docs/decisions.md:1346` | RDF remains authoritative; producer receipts do not establish semantic conformance. |
| REF-021, `docs/decisions.md:704` | DuckDB is already a disposable query implementation over authenticated Parquet. |
| `src/refspec/atlas/parquet_tables.py:682` | Existing owner of the mapping between logical fields and typed columns. |
| `src/refspec/atlas/parquet_preflight.py:538` | Existing referential, uniqueness, count and evidence checks to reuse. |

RefSpec owns validation and view schemas. DuckDB/Arrow provide execution and
storage access. SpicySearch consumes authenticated views; a validator execution
change need not alter those view identities or consumer APIs. The existing
compact search view is unsuitable for full auditing because it omits native
payload bodies (`docs/atlas-parquet-view.md`, Compact search profile).

## Invariants

Preserve the canonical RDF meaning, exact identities, raw publisher evidence,
complete check coverage, and independent verdict. The binding requires the
independent reader to recompute facts from serialized data
(`bindings/atlas/3.1/README.md:948`). Choosing a columnar execution engine does
not require inheriting the builder's trusted state.

Authentication proves which bytes were read. Full RDF-to-table comparison must
also prove their correspondence. Current identity equality and bounded whole-row
sampling (`bindings/atlas/3.1/README.md:810`) do not establish every field needed
for a replacement full audit. Silently normalizing invalid RDF into acceptable
rows would also break the verdict.

## Concrete execution design

1. Authenticate the pinned input files with existing byte readers. Stream RDF
   lexical, graph-role and per-subject digest checks without retaining a graph.
2. Compare independently reconstructed logical rows to the full Parquet rows,
   including fields and multiplicities. Route RDF-only records through bounded
   audit batches or temporary tables, without adding a new published format.
3. Run counts, cardinality, duplicate IDs, reference closure, ownership and
   evidence joins through DuckDB over the authenticated files. Use Arrow batches
   for payload hashing and custom per-row validation.
4. Cover every remaining shape, policy, lifecycle, derived/projection and
   hierarchy rule explicitly. Graph reachability needs its own measured plan;
   an unrestricted recursive SQL query is not automatically efficient.
5. Replace the full audit only after the copied old validator agrees on real
   inputs and mutations, under the repository's oracle rule (`AGENTS.md`).
   Leaving the old full resident graph in the production sequence would retain
   the capacity problem.

## Performance, DRY and KISS

Scans cost `O(B)` in bytes read. Keyed joins cost expected `O(N + M + K)` for
input row counts `N`, `M` and output `K`; duplicate detection may use expected
linear hashing or `O(N log N)` sorting. Spilling adds I/O. Reachability can be
superlinear across many starts and must not be described as an ordinary join.

[DuckDB](https://duckdb.org/docs/current/data/parquet/overview) reads selected
Parquet columns and pushes applicable filters into scans. Its
[larger-than-memory operators](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads)
can spill joins, groups and sorts to disk, but some query combinations and
aggregate states can still exhaust memory. Retain the external resource guard,
set explicit memory/scratch limits, and measure actual query plans and peak use.
[Arrow batches](https://arrow.apache.org/docs/python/dataset.html#iterative-out-of-core-or-streaming-reads)
support bounded iteration; whole-table materialization does not.

Reuse the existing schemas, authentication helpers and check definitions.
Keep temporary query state disposable. Do not add a database service, custom
graph engine or permanent second copy of the Atlas. Producer and auditor must
still derive semantic evidence independently.

## User value and counterfactual

The intended outcome is complete independent qualification within an explicit
resource budget. Failure to preserve negative verdicts, materialize all required
facts, or improve full-corpus capacity would invalidate this design. Merely
running the current preflight before the same full graph audit would not deliver
that outcome. Removing RDF verification today would leave admitted data outside
the checked tables and could miss wire-level defects.

## Verdict

**RECONSIDER the resident-graph execution model; KEEP the assurance requirements.**
The existing Arrow preflight and DuckDB dependency partially supply the required
implementation. Confidence is high in the identified coverage and retention
problems; the replacement's full-corpus speed and memory use remain unmeasured.
No production validator code changed during this review.
