# Independent checks of the omitted vocabulary units

The bounded emitted artifact agrees with the retained source for all 95 FERC
docket prefixes and the three selected Unified Agenda citation types. For the
FERC class/type table, 234 rows match; one row has a text-layer/rendering
disagreement in the publisher PDF. Its emitted wording agrees with the visible
page. This is a recorded exception requiring interpretation, not an
unconditional class/type pass or a confirmed producer defect.

This checks actual Parquet rows in
`output/atlas-3.1-omitted-vocabularies-2026-09-27/parquet-view` at source commit
`cc507773`. It goes beyond confirming missing verifier declarations. No generic
source-fidelity adapter was added, no source input changed, and no full-Atlas
qualification is claimed.

## Independent extraction and comparison

The expected data is constructed before either producer loader is imported.
`extract_pdf_tables.py` uses Poppler word coordinates and stock XML parsing;
it does not import RefSpec's PDF readers, FERC parser, field dictionaries,
regular expressions or transcribed glossary definitions. Column positions come
from each page's own header words. Category/prefix anchors establish row order,
and docket continuation words remain in their table column and row band.
No data-row word in the class table's body is left unassigned.

A small explicit representation rule folds PDF ligatures and typographic
hyphens to their ordinary characters. It preserves en/em dashes and other
letters. Raw words/cells remain in `independent-extraction.json` and the
Poppler outputs, so this normalization is visible and reversible as an
observation. The Unified Agenda definitions come from independently delimited
paragraphs on glossary pages 18-19, not the producer's Python constants.

`replay.py` then loads producer records as observations, compares them to the
independent expectations, and follows their resource identities into the actual
bounded Parquet tables. This separates the PDF-to-record comparison from the
loader-to-emitted-row comparison. Source-local concept identities are also
recomputed using the declared acquisition time, source URL, row position,
notation and independently read display label; the algorithm is implemented
locally with hashlib/datetime/uuid rather than imported from the producer.

The receipt records:

- Exact PDF hashes/lengths, distribution and view manifest hashes, and every
  view member's authenticated file hash/length.
- Exact counts of the three units, with no unexpected emitted resource.
- Zero loader-to-artifact differences across the 333 resources, native payloads,
  definitions, labels, notations, status and locators.
- Zero canonical payload hash differences; all SourceRecord identities and
  source-release links reproduce from their observed payload and original
  authenticated source pin. This is identity consistency, not a substitute
  for the independent field comparison.
- Complete source-comparison differences and bounded mutation results.

The diagnostic exits 0 when it finishes recording findings. Its exit is not a
source-qualification verdict. It is expected to retain the class-row finding.

## FERC docket prefixes: matches the retained source

All 95 rows agree on prefix, library, full definition and table-derived status.
There are 77 active records (standard and non-standard formats) and 18
explicitly discontinued records. The emitted display label and definition
retain complete wrapped sentences; the notation retains the prefix.

I inspected the rendered pages identifying all three tables: page 1 is
`Table 1 - Active: Standard Docket Format`, page 5 is the non-standard active
table, and page 6 is the discontinued table. On page 6, `AR | G` means Area Rate
Proceedings, while the next row `CI | G` continues onto `Marketers`; that word
is part of CI's definition. The `DA` row's parenthetical replacement prefixes
stay with DA. Page 5's `P | H | Hydropower Projects` is an active single-letter
prefix, not an extraction anomaly. These cases agree with the emitted rows.

## Unified Agenda citation types: matches the declared subset

The actual artifact contains exactly `U.S.C.`, `Pub. L.`, and `E.O.`, with the
publisher's glossary definitions and the expected notations/source metadata.
Both full glossary pages were visually inspected. The U.S.C. definition's
historical wording says 50 titles; the artifact preserves it. The glossary also
contains CFR, FR, RIN and other entries. This check verifies the deliberately
selected citation-type subset, not the completeness or contemporary accuracy
of a general legal-identifier universe.

The native identifier's authority URL, source URL, capture time, unknown
effective date and source digest agree with the declared retained capture.
Capture metadata and the choice of these three entries are representation
rules, not facts newly inferred from the PDF.

## FERC class/types: 234 matches, one rendered-source exception

All 235 category/library/classification/description rows are recovered from
page geometry. Duplicate descriptions remain separate records: `Annual Charges
Report` appears on page 4 for library E, page 5 for G, and page 7 for `H, E and
RM`. Those pages were visually inspected. The full four-column rows and their
source-local identities remain distinct in the artifact.

The only difference is zero-based row 233 on page 7:

- Visible page and emitted value end in `Hinshaw Pipe`.
- Poppler's text layer places a separate word `lines` immediately after `Pipe`.
- pypdf also extracts `lines`, but earlier as an orphan before the table header;
  its emitted row line ends at `Pipe`.
- The full page and 600 dpi crop visibly end at `Pipe`; the next row is Form 552,
  and no continuation appears below.

`specimens/class-row233-discrepancy.json` preserves the exact Poppler coordinates,
pypdf contexts and source pin. `specimens/class-page7-pypdf.txt` retains the raw
page extraction. The full-page render and high-resolution crop are retained
with commands in `specimens/rendered-pages.json`. The parent agent independently
viewed both renders and confirmed this reading.

The emitted resource is
`urn:ref:source-concept:v2:ferc-document-class-types:019fc910-3b40-737b-aaac-b2ee73a8a6c9`.
A text-layer-only expectation appends `lines`, which changes the label, native
text/type-description and the derived resource identity. The receipt leaves all
three field-level differences visible. It does not silently discard the extra
word, declare the existing producer defective, or prescribe appending it.
An eventual audit policy must retain the publisher observation and explicitly
state why it uses the rendered reading or the text-layer reading.

## Mutation evidence

Ten field/row mutations add failures beyond the existing class-row finding:
active/discontinued swap, lost continuation, changed prefix notation, changed
classification, duplicate-label library swap, changed citation definition,
changed identity, missing discontinued record, missing citation type, and an
extra unrelated glossary entry. Separate mutations of each input's last byte
fail its exact source pin. These are tests of this bounded comparison, not
installed acceptance gates or tests against rewritten/resealed distributions.

## Replay and limits

From any working directory, use the project environment and explicit paths:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --frozen --project /path/to/RefSpec \
  python /path/to/retained/replay.py \
  --repo /path/to/RefSpec \
  --output-dir /path/outside/checkout/omitted-vocabulary-replay
```

`--view` accepts an explicit Parquet view path; the default is the bounded
three-unit candidate above. The packaged replay was run from `/tmp` with an
explicit repository path and completed successfully. Scripts refuse to write
diagnostics under the checkout. Full PDFs are not duplicated in this package.

Source-path ordinals and original upstream digest comparisons use loader
observations because these fields do not appear directly as Parquet columns.
The corresponding resource identity, source-release identity, source URL and
native payload are verified in the actual artifact. This bounded diagnostic
does not prove the full RDF-to-Parquet transformation independently; the
standalone binding validation is a separate check. It also does not resolve
the generic verifier's declaration/provenance defects or the class PDF's
text-layer/rendering difference.
