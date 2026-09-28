# Atlas audit simplification

RDF remains supported and independently validated, as requested. This change
removes redundant processing and retained state; it preserves the audit checks.
The production diff removes a net 546 lines. Copied old implementations remain
in tests as independent comparison oracles.

| Change | Result |
| --- | --- |
| Parquet preflight | DuckDB reads the existing files directly. Deleted full Arrow-table loading, combined identity arrays and bespoke join helpers. The Arrow-table API uses the same query implementation. |
| RDF fact access | Reads the existing graph indexes. Deleted the duplicate fact/type tables, membership cache, reorder machinery and private predicate allowlists. |
| Sampled RDF/Parquet comparison | Scans RDF once for all samples, spools selected lines to temporary files and parses one sample at a time. Deleted repeated full-file scans and avoided simultaneous raw-line retention. |
| Publisher type index | A cached property belongs to its publisher view. Deleted the process-global cache that retained completed views. |

## Measurements and scope

The [full-candidate columnar preflight](full-columnar-preflight.json) passed in
14.23 seconds, with 2.35 GiB peak physical footprint and 2.42 GiB peak RSS.
The [result](full-columnar-result.json) identifies the exact distribution/view
pins, checks performed and RDF checks still required. This is not a full RDF
qualification or publisher-fidelity verdict. DuckDB's 512 MB buffer-manager
setting does not cap process memory; upstream view verification still reads
some complete projected columns.

The [bounded real RDF audit](bounded-rdf-audit.json) passed in audit mode on the
retained UMTHES distribution, including its semantic checks. The
[standalone binding corpus](binding-corpus.json) also passed. The fixture
regeneration check reproduced the same fixture-tree digest; its receipt changed
only to record the new validator source hash.

The cold fact-index comparison used the same 262,530 quads and seven semantic
gates. [Old](facts-old.json) versus [new](facts-new.json) peak RSS was
200.58 versus 190.36 MiB; total measured work was 4.407 versus 4.348 seconds.
The gates themselves slowed from 0.456 to 0.713 seconds, while parsing became
faster. These are single bounded runs, not full-scale capacity proof.

The final disk-spooled [sample scan comparison](sample-scan-benchmark.json)
returned identical rows in 0.082 versus 0.381 seconds (4.67 times faster).
It used 50,000 retained lines and 45 resource subjects. The earlier in-memory
prototype's timing is labeled historical in that receipt; it is not the final
implementation. High-fan-out releases have separate oracle/cleanup tests.

Phase resource measurements cover the supervised macOS process group; descendants
that create a different session/group can escape that scope. RSS and physical
footprint are distinct metrics. The publisher-cache change permits completed
views to be released; it does not reduce the live context's source population.

## Cost and verification

Relational scans read selected column bytes. Expected hash-join work is
`O(N + M + K)` for input row counts `N`, `M` and result size `K`; grouping and
spilling can require additional sorting and I/O. Removing the duplicate RDF
index removes its corpus-sized allocation; the canonical graph remains resident.

Sample selection changes `O(S * B)` repeated reads to `O(B + M)` work, where
`S` is sampled IDs, `B` is RDF bytes and `M` is matched bytes written. Scratch
disk is `O(M)`; memory retains one sample graph, sampled row payloads and a
bounded number of buffered files. A single large release sample can still
require a large graph. Cleanup completes before comparison results return.

The frozen-oracle tests cover real data and mutations. Explicit differences
are limited to private predicate access, preflight failure-example wording,
iteration/first-diagnostic order for multiple defects, and typed refusals replacing accidental Arrow exceptions for
malformed null enumerations. They do not change acceptance of valid data or
rejection of those corruptions. See the new focused tests and
[check results](checks.json). [Source hashes](source-pins.json) identify the
executed implementations; [checksums](SHA256SUMS) cover retained evidence.

The full RDF audit still needs a completed full-corpus run. Its earlier
30 GiB capacity stop is retained in the [prior repair evidence](../repair-validation/README.md).
These changes do not establish that the entire graph now fits that budget.
No full rebuild, upload, deployment or promotion was performed in this cleanup.

Benchmark scripts are retained unchanged from `output/atlas-audit-simplification/`.
Replay them from that original location in the repository with the named
retained inputs available; their relative root calculation assumes that path.
