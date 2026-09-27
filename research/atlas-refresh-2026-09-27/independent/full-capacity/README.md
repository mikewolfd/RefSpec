# Full-build capacity result, 2026-09-27

The full build did not complete. Its existing 18 GiB process-tree RSS guard terminated it at 20:36:28 UTC; the watcher recorded exit 143 at 20:36:38 UTC and sampled peak tree RSS of 20,499,008 KiB (19.55 GiB). The guard can overshoot its threshold between five-second samples. No assistant signal was sent: a follow-up measurement found the process had already exited. No other job was interrupted.

All 119 source releases and all 12 mapping releases completed their construction loops, including 801,992 LC mapping records. The last visible phase was `derive-registered-relations`, entered at elapsed 5,307.9 seconds. That label also covers later source-accounting construction and validation; it does not identify the precise Python function active at termination. The completed distribution and full-view manifests are absent. Actual final pack sizes, full standalone validation, and compact search-view generation remain incomplete. This is a capacity outcome, not a semantic rejection or pass.

## Memory observations

At 2026-09-27T20:35:50.269789+00:00, our builder's physical footprint was 33,772,217,664 bytes (31.45 GiB), while its reported RSS was only about 2.25 GiB. The external dev21 worker's physical footprint was 33,290,909,648 bytes (31.00 GiB). The host has 48 GiB RAM. Raw pressure level was 2 and the `memory_pressure -Q` free percentage was 39%; raw swap output was `vm.swapusage: total = 25600.00M  used = 24146.81M  free = 1453.19M  (encrypted)`. These different metrics must not be substituted for one another. In particular, RSS alone did not reveal compressed/swapped memory charged to the process.

At 2026-09-27T20:36:51.132328+00:00, our PID was absent, raw pressure level was 1, and the free percentage was 79%. Raw swap output was `vm.swapusage: total = 18432.00M  used = 16543.81M  free = 1888.19M  (encrypted)`. The external worker remained alive at that follow-up observation. It subsequently finished at 20:37:30 UTC, exit 0, with four producer-side tests passed on `41e2bf9d`; `external-dev21-completion.json` records that later result. The jobs were concurrent during our failed attempt. The retained before/after JSON contains command results and untouched stdout/stderr; footprint JSON contains detailed measurements. A previous native sample at 20:25:45 UTC reported 12.1 GB footprint and active sorting/string rendering, including 39 of 91 main-thread samples below `builtin_sorted`, rather than the earlier all-GC pattern. The native sample does not expose exact Python function names.

## Code-based explanation, distinguished from runtime attribution

`accounting-code-excerpts.txt` records exact source lines and the complete source file SHA-256 at commit `cc507773af7d01a9330b0bdd0dca293b25380147`. `_stream_construct_graphs` calls `_validate_compiled_source_accounting` after the derivation phase marker. That calls `_mapping_accounting_expectations`, which reconstructs `_expected_mapping_asserted_graph` over every mapping release. The graph includes assertions, evidence bindings, source records, policies and events, although the caller ultimately reduces it to source-record-to-assertion sets. `_new_build_graph` uses `_MutationTrackedGraph(store="SimpleMemory")`.

This is a concrete memory-scaling risk proportional to the complete mapping RDF population, contrary to the bounded release spooling used earlier. It is a credible explanation for the observed growth, not proven exact runtime attribution: the native stack lacks Python frame names and the phase marker spans multiple functions. No source or limits were changed during this run. The shared-host outcome also does not establish the minimum RAM needed by an isolated run.

## Retained partial data

`partial-output-inventory.json` records 229 files totaling 36,630,819,719 bytes under `/Users/mikewolfd/Work/spicy-stack-worktrees/refspec-atlas-refresh-20260927/output/atlas-3.1-full-2026-09-27`. All partial files remain in place. The package contains only their metadata, not duplicate artifact bytes. Existence is not a supported-resume guarantee; resumability has not been verified. No restart, cleanup, source change, standalone full validation, or compact view build followed the failed build.

The initial bounded validation proofs remain in the separate `retain` package. Every file in this capacity package is listed in `SHA256SUMS`.
