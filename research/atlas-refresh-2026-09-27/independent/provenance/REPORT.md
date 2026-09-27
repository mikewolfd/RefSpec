# Independent UMTHES provenance verification, 2026-09-27

The retained UMTHES candidate preserves the evidence examined here. Its failing
provenance gate primarily compares different digest meanings. The verifier also
misses changes to two fields in transformed-relation evidence. This is a bounded
investigation of current commit `cc507773af7d01a9330b0bdd0dca293b25380147`, not
full-Atlas source qualification. No repository code or artifact was changed.

## Current artifact and independent checks

The fresh audit against `output/atlas-3.1-umthes-2026-09-27/distribution`
reproduced the original result: 23 of 26 checks pass; `configuration`,
`claim-scope`, and `rdf-provenance-fidelity` fail. Provenance reports 3,415
failures. `fresh-receipt.json` is byte-identical to the earlier receipt:
SHA-256 `cf10dbcb4b6023cda256c964d4334a79ea780c6a4914d11e21f421e790b3c1ab`.
The replay script exits successfully after collecting the failed audit; its
process exit is not an audit pass.

A separate PyArrow/rdflib/hashlib probe checked the retained publisher archive
against the candidate rather than treating that receipt as evidence:

- All 3,365 represented resource records reproduce their declared native fields
  from raw N-Triples plus authenticated capture metadata. Response lengths,
  response digests, locators, labels, relationships, legacy identities, and
  retrieval metadata agree. Every archive member matches its manifest pin.
- All 50 targetless transformed-relation records have exact publisher triples,
  correct response digests and the declared transformation. An independent
  traversal of the raw broader/narrower relationships reconstructs exactly the
  same 50 association records that conflict with a hierarchy path, including
  their complete native payloads.
- All 3,415 payload hashes match the published `source_digest`. Their retained
  native payloads, locators, digests and represented resources also match the
  independently loaded RDF packs. Recomputing each SourceRecord identity from
  the payload hash, original upstream digest, locator and source release
  reproduces all identities.
- All 4,900 evidence bindings pin their SourceRecord's `content_digest`; none
  incorrectly uses its native-payload `source_digest` as that evidence pin.
  This checks the Parquet linkage. The separately completed binding validator
  is the proof that these record content digests match the RDF facts.

The raw specimen `specimen.nt` is the full captured `_00028834` response, not
an isolated grep hit. Its first block labels neighboring transport concepts;
its later block explicitly identifies `_00028834` as the concept with preferred
`Verkehr` (German) and `transport` (English), alternatives, a broader concept,
narrower concepts, related concepts, and a GEMET close match. The neighboring
labels are not mistaken for this concept's own labels.

For SourceRecord `urn:ref:atlas-source-record:000e6359baff727a9e55e40b8c8f9a4415e901c9dd60e211ae529b73df9b0f08`:

- Canonical native payload / stored `source_digest`:
  `b2f45f92cc6f098ac49aefab2151b54365d256c50b8f2e7d3b4cb8bcbe4eaba8`.
- Raw response / retained `responseDigest`:
  `3c81b1fe83ece0c213ae1c54c1c1a645d8457f35180dfb61ff27e669f1bf8974`.
- Locator: `https://sns.uba.de/umthes/de/concepts/_00028834.nt`.

## Why the current check fails

`tools/generate_atlas_v3_full.py:3464` emits each SourceRecord with the hash
of its complete canonical native payload. The original source digest remains
in the identity basis at line 3533. This was an intentional change in commit
`37d2d11020eac4227e4f7967751e48f1612f5a60` (August 9), and the independent
binding enforces it at `bindings/atlas/3.1/tools/validate.py:6936`.
Evidence-binding digests have a separate meaning: the full SourceRecord RDF
content, as constructed at generator line 3945 and checked at validator line 5482.

The UMTHES stock reader reconstructs raw response digests at verifier line
11173, and its declaration at line 18127 leaves
`record_digest_is_native_payload_digest=False`. Resource provenance therefore
compares the response digest with the complete payload digest at lines
21425-21473. Enabling only that policy in memory reduces 3,415 failures to 50;
it does not repair the targetless relation branch.

That branch at `tools/verify_atlas_source_fidelity.py:21314` hashes the inner
`publisherRelation`, compares it directly to the outer `sourceDigest`, then
continues at line 21338. Current output instead hashes the whole payload,
including transformation metadata. This is stale verifier behavior, not
missing raw response evidence in the examined candidate.

## Additional missed mutation checks

The primary mutation replay uses the actual, unmodified `SOURCES` declaration;
`relation-mutation-results.json` records `uses_unmodified_source_spec: true`.
The clean baseline is already red: configuration has 3 failures, claim-scope 1,
and provenance 3,415. These are in-memory mutations of the fidelity checker
input, not rewritten or resealed distributions.

For the actual relation record in `relation-specimen.json`, each mutation
changes its payload, recomputes `publisherRelationDigest`, updates the derived
relation locator, and recomputes the complete payload `sourceDigest`:

| Mutation | Comparison with the full baseline failure sets |
| --- | --- |
| Replace the raw `responseDigest` with a zero digest | Identical in every check; no new or removed failures |
| Replace transformation reason with `invented` | Identical in every check; no new or removed failures |
| Replace relation object with an absent publisher concept | Adds one provenance failure |

This demonstrates missed tamper detection. It does **not** demonstrate a
compromised distribution passing the current audit or binding validator.
Compressed `relation-*-checks.json.gz` retain complete baseline and mutation
check outputs, original and changed payloads, and the changed locator/digest.
The compact result records both additions and removals for every failure-set
comparison. The earlier policy-enabled experiment remains separately named
`partial-policy-*`; its baseline provenance count is 50, not 3,415.

The missing inverse is visible in current code: the UMTHES reader returns no
`expected_relation_payloads` at lines 11224-11231, so the exact expected-payload
branch at line 21277 never handles these records. The fallback at line 21314
checks the relation triple, inner self-hash, and locator, then exits before
independently checking the raw response digest or transformation fields.
Resource records do receive independent field comparisons at line 21592:
mutating their response digest, response length, retrieval time or legacy
identity, while keeping their payload self-consistent, adds the expected
field-specific failure.

## Wider digest scope, with evidence limits

There are 106 RDF declarations without the policy flag: 95 vocabulary and 11
mapping declarations. This is a configuration count, **not 106 proven defects**.
Bounded readers over authenticated retained inputs produced these comparisons:

| Source | Independently reconstructed rows | Expected upstream digest differs from native-payload digest |
| --- | ---: | ---: |
| UMTHES candidate, also checked against actual output | 3,365 resources | 3,365 |
| Federal Register API topics | 7,767 resources | 7,767 |
| GCMD science keywords | 3,774 resources | 3,774 |
| GovInfo collections | 42 resources | 42 |
| GAO retained topics | 31 resources | 31 |
| EuroVoc to MeSH alignment | 5 mapping evidence rows | 5 |
| BILLSTATUS bill types | 8 resources | 0 |

The latter six probes exercise publisher readers and the digest comparison,
not six independently built distributions. BILLSTATUS proves that a false flag
can still be correct when its expected digest already hashes the independently
reconstructed native payload. Remaining declarations have not been audited.
The EuroVoc mapping reader stores the pinned file hash in expected evidence at
line 11318; the generic mapping comparison compares that digest unchanged at
line 21627, despite the producer's universal payload-digest rule. Its complete
expected native payload retains the upstream alignment digest.

The passing `contract-dev` check uses
`tools/verify_federal_register_thesaurus_distribution.py` (Makefile line 396),
for a different PDF thesaurus release. It does not run this generic fidelity
verifier over Federal Register API topics, so the results do not conflict.

## Smallest principled correction

Treat canonical native-payload hashing as the common SourceRecord format rule,
while retaining independent comparisons of upstream evidence and native fields.
For the bounded UMTHES case, use its existing independent resource-field
comparisons and add exact independently reconstructed transformed-relation
payloads. The current ICPSR reader already demonstrates the appropriate pattern
at verifier lines 13458-13500: compute publisher hierarchy reachability, then
construct the exact transformation payload from raw relations. This probe
reproduces all 50 UMTHES payloads with that reasoning.

A production fix must compare retained `responseDigest` against raw response
bytes and retain exact transformation checking; merely turning on the flag or
accepting a self-consistent inner hash is insufficient. Mapping evidence must
compare the complete independently reconstructed payload and its payload hash,
while preserving its upstream source pin. Keep original SourceRecord identities
stable and retain the replaced check as a test-only oracle with frozen intended
changes and these mutation regressions. No fix is applied by this package.

## Replay

Run from the RefSpec worktree with the retained inputs and bounded candidate.
The scripts also accept `--repo /absolute/worktree`. Put their outputs in a
separate explicit directory; they do not write the repository or source inputs.
`replay_relation_mutations.py` includes the provenance replay.

```sh
uv run --frozen python path/to/replay_relation_mutations.py --repo . --output-dir /tmp/umthes-provenance-replay
uv run --frozen python path/to/replay_blast_radius.py --repo . --output-dir /tmp/umthes-reader-replay
```

Only bounded source specimens are retained here; the source ZIP is not copied.
`SHA256SUMS.json` records the exact evidence files. No full-Atlas source audit,
publication, deployment, or downstream adoption was performed.
