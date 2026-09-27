# Independent validation-gap verification

Checked commit `cc507773af7d01a9330b0bdd0dca293b25380147` in `/Users/mikewolfd/Work/spicy-stack-worktrees/refspec-atlas-refresh-20260927`. Read-only repository investigation; temporary probes and evidence are in this directory. No active jobs were interrupted. Timestamp and artifact metadata are in `snapshot.json`.

## Verdict

The preferred-label correction is verified against policy, retained publisher context, independent regression execution, extra negative mutations, and a fresh standalone run on the complete UMTHES distribution. Mapping partition code is exercised through both whole-graph and streaming writers. Full-distribution structural acceptance, actual pack limits, and source qualification remain unverified until the running full build finishes and its own independent checks run. The external dev21 full-Atlas tier cannot substitute for these checks.

## Checks I executed

- `uv run --frozen pytest -q -n 0 tests/test_atlas_v3_preferred_languages.py`: 7 passed in 2.55s; `preferred-label-tests.log`.
- Fresh standalone validator on `output/atlas-3.1-umthes-2026-09-27/distribution`, using `uv run --no-project --with-requirements bindings/atlas/3.1/requirements.txt`: exit 0, 262,530 quads, 3,365 resources, 17,241 labels, 4,900 relations/evidence bindings, 3,415 source records. `umthes-standalone-validation.log` records every phase through complete. This is structural validation, not source-fidelity qualification.
- Extra label boundary probes: multilingual preferred labels accept; duplicate language, identical literals on distinct label identities, missing language, and preferred/alternate role overlap refuse. Uppercase tags are accepted by the isolated semantic calls but refused by canonical wire grammar, the intended earlier boundary. An initial probe incorrectly expected the semantic calls alone to enforce casing; the corrected probe tests the actual wire boundary. `additional-label-boundaries.json`.
- Three focused packing tests passed: large mapping partition decision, cross-partition dependency pinning, and streamed/whole-graph output oracle. `packing-tests.log`.
- Forced partitioning in a bounded synthetic mapping case by temporarily setting the in-process threshold to 1; both writers produced byte-identical full outputs with four mapping packs (`.../8.nq.zst`, `.../2.nq.zst`, `.../e.nq.zst`, `.../b.nq.zst`). Repository constants were unchanged. `partitioned-mapping-writer-probe.json` and `forced-partition-writers/`.

## Policy and actual raw evidence

`bindings/atlas/3.1/README.md:410-425` requires explicit lowercase language tags, permits at most one preferred label per language, and requires disjoint label roles. `docs/decisions.md:2417-2438` records the original policy and explicit correction. `bindings/atlas/3.1/shapes/atlas.shacl.ttl:341-360` preserves role and node constraints while checking `sh:uniqueLang` on preferred literal forms. `bindings/atlas/3.1/tools/validate.py:6850-6898` counts each preferred label identity before literal deduplication and retains role checks.

I opened the complete retained `records/_00000013.nt` member, saved here as `umthes-00000013.nt`. The same subject `_00000013` has preferred `degradation`@en and `Abbau`@de. Nearby triples separately identify alternatives `decomposition`@en, `Abbaumechanismus`@de, and others; broader concepts `_00047435` and `_00049270` have their own subjects. Thus the preferred labels are not accidental neighboring or parent labels. The regression independently verifies the archive against `tools/pinned_inputs.json` and freezes the exact two literals.

The regression file's test-only old SHACL clause and mutation table are at `tests/test_atlas_v3_preferred_languages.py:32-114`. It covers the intended accept/reject change, including the equal-literal case that property-path set semantics alone cannot catch. The fresh UMTHES standalone run additionally verifies the producer's complete retained-source slice, beyond transplanting specimen labels into the test fixture.

## Pack-size evidence and limit

The retained August manifest independently confirms 192 packs, 100,915,760 quads, 24,995,517,100 total uncompressed bytes, and a largest LC mapping pack of 6,580,663,676 bytes. That pack exceeds the unchanged 4 GiB limit. The total fits the unchanged 32 GiB limit. These are manifest declarations, not a new full byte scan.

Current `_release_pack_plans` at `tools/generate_atlas_v3_full.py:9908-9923` sets mapping `resource_count` from the mapping count. `_release_pack_partition` at `7601-7622` applies the same 50,000 threshold to both mapping and source releases and uses one SHA-256 hex digit for 16 partitions. Streaming routing uses that function at `6090-6111`; streaming output has the partitioned mapping path at `6298-6304`, and the whole-graph writer at `8355-8361` does likewise. The synthetic forced-partition probe verifies both paths execute and agree.

This count-based threshold is not a proof that every pack is under the byte limit. Prebuild partition checks at `10254-10265` test only whether a partition exists. The independent validator's actual bounds are at `bindings/atlas/3.1/tools/validate.py:336-338`, `3069-3079`, and `3161-3167`: 4 GiB content and 1 GiB transport per pack, 32 GiB total content. After the full build, inspect all manifest lengths, then run standalone validation to verify actual bytes/digests/placement rather than assuming 16 buckets guarantee acceptance.

## Test-tier and commit boundaries

`Makefile:208-209` runs exactly the `full-atlas` tier. `conftest.py:48-57` selects that marker. The four tests are `tests/test_producer_prebuild_validation.py:126`, `205`, `256`, and `1067`. Three share `complete_prebuild` at 108-123; the fourth calls producer prebuild with `deep=True` at 1068-1076. `tools/generate_atlas_v3_full.py:10269-10337` shows that deep mode constructs and validates release-scoped output without materializing a distribution. It neither calls standalone `validate_distribution` on written files nor invokes source-fidelity verification. The generator explicitly reports `independentFileConsumerValidation.performedByGenerator = False`, pinned by `tests/test_generate_atlas_v3_full.py:349-353`.

The external long-tier runner in `/Users/mikewolfd/Work/corpora/opencode-lanes-20260927/refspec/long-tiers/run.sh` explicitly runs dev21 worktree commit `41e2bf9d8474dca501a11a18e799855f74e70cec`. Its slow exit is 0; its full-tier log still shows three dots and no completion at this snapshot. The refresh commit is `cc507773`, with additional validator changes. The local fast-tier and binding-slow logs end with exit 0 and confirm their stated counts; they are not a full slow-tier rerun on cc507773. The separate standalone UMTHES result is on the current correction.

## Capacity evidence

The 22 GB heap comment at `bindings/atlas/3.1/tools/validate.py:10440-10458` cites an August 12 run, before later optimizations. The stronger historical measurement in `plans/validation-cost-reset-plan.md:137-142` and `204-213` is standalone acceptance at 29,286,753 quads using 13.83 GiB, with a comparable run at 14.31 GiB. I did not find retained raw full-size acceptance receipts in the current main output tree; these historical performance numbers are documented measurements, not newly reproduced measurements.

The current full topology is about 3.45 times as many quads as that optimized historical run. A simple proportional extrapolation would suggest about 47.7 GiB, but data mix, fixed costs, term reuse and later code changes make that an estimate, not a capacity result. A 30 GiB process-tree guard on the 48 GiB host is prudent; completion under that cap is unproven. Do not use the old 22 GB comment as evidence that current full validation fits. Do not increase semantic pack limits. Retain phase/RSS progress from the real run; if it reaches the guard, report a capacity blocker rather than a semantic pass or failure.

## Minimum remaining checks

1. Let the existing build finish; retain its exit code and sealed distribution/view digests.
2. Compare every pack's declared content and transport bytes and total content against the existing limits.
3. Run the standalone file validator on the exact final distribution with bounded memory and retain verdict, phase progress and peak RSS. No cache-derived or smoke result substitutes for acceptance.
4. Independently repair and prove the known source-fidelity comparison/declaration gaps, then run qualification on the final candidate.
5. Generate and verify the compact search view against the exact full-view digest. Keep source qualification, package version/release, consumer adoption and deployment as separate outcomes.
