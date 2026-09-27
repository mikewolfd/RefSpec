# Bounded independent agency fixture

`agency-registry.nq.zst` copies the mapping-only pack from the independently
compared September 27 agency distribution. It is a frozen observed artifact,
not expected truth: tests reconstruct expectations from the committed candidate,
decision and raw-roster inputs, and mutate the artifact's semantic fields.
The frozen comparison implementation remains under `tests/oracles/atlas_refresh/`.

Fast source-reading tests use the committed Poppler coordinate captures and
compare the old and new page algorithms. They need Python, not Poppler.

Run the additional retained-evidence replay explicitly:

```sh
uv run pytest -q tests/test_atlas_independent_adapters.py -m slow
```

That replay requires `pdftotext` from Poppler, the pinned PDFs, the retained
primary originals named in the audit-evidence manifest, and the separately
built agency distribution/view. Missing inputs fail rather than skip. It reads
the existing evidence and does not acquire, fabricate or rebuild prerequisites.
