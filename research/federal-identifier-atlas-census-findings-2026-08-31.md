<!-- markdownlint-disable MD013 -->

# Federal identifier atlas findings from the full catalog and available prose

Compiled 2026-08-31 from the `federal_identifier_atlas/` research bundle,
RefSpec's current identifier and citation readers, the preserved 1,993,040-row
source catalog, available Federal Register and presidential bodies, the
250,000-opinion court corpus, and the 192,141-row congressional bill corpus.

## Status and decision

The atlas is useful as a **research inventory and hypothesis generator**. It
surfaces identifier families, identity dimensions, lifecycle rules, privacy
concerns, and examples that RefSpec does not yet express consistently. It is
not a production recognizer and this comparison does not ask it to replace
RefSpec's existing readers.

The main finding is that RefSpec should import selected **concepts and tested
identifier families**, not the atlas's regex helper as a unit. Large-corpus
testing confirmed several valuable additions, especially reporter citations,
lettered Supreme Court namespaces, explicit RIN label handling, composite
congressional identity, and source-scoped legacy Federal Register numbers. The
same testing also produced a useful negative-fixture set: many plausible
identifier shapes collide with ordinary prose unless the reader uses field,
source, label, and neighboring-text context.

This note records research evidence only. It changes no normative RefSpec
requirement, production reader, release, or publication decision.

## What was tested

The comparison used four different evidence layers. Their scopes matter:

| Evidence layer | Population | What it establishes |
| --- | ---: | --- |
| Preserved source catalog | 1,993,040 rows | Selected structured identifier fields and selected long-form source prose, measured across every row |
| Federal Register and presidential body files | 48,309 files; 1,133,647,533 visible characters | Behavior in long regulatory prose and legacy document-number recovery |
| Court opinions | 250,000 rows; 249,915 with selected prose; 3,316,497,245 characters | Reporter-family value, court-pattern collisions, and source-specific behavior |
| Congressional bills | 192,141 rows | Composite bill identity, historical exceptions, and public-law citations in action prose |

The comparison did not stop at titles and identifier columns. An earlier broad
title scan mainly exposed short-token collisions; the quantified prose scan
reported here covered 111,746 distinct abstracts plus 104 distinct withdrawal
reasons. It did not claim every text-bearing field: document, docket, and
Federal Register titles and arrays such as `additional_rins`,
`regulation_id_numbers_json`, `docket_ids_json`, and `cfr_references_json` are
outside the prose counts below. In this note, "full catalog" means every row
for each named field, not every column in the catalog.

The catalog does **not** contain full document bodies. Full-body tests therefore
used the separate body corpora listed above.

### Source-catalog prose inventory

| Field | Populated occurrences | Distinct texts | Occurrence characters | Distinct characters | Treatment |
| --- | ---: | ---: | ---: | ---: | --- |
| Regulations.gov docket abstracts | 1,268,081 | 108,899 | 386,131,666 | 18,136,177 | Scanned |
| Federal Register abstracts | 3,740 | 2,900 | 2,219,925 | 1,716,079 | Scanned |
| Combined abstracts | 1,271,821 | 111,746 | 388,351,591 | 19,824,954 | Scanned once per distinct text |
| Withdrawal reasons | 125 | 104 | 5,921 | 5,112 | Scanned once; duplicate observation copies excluded |
| `selection.reason` | 1,909,111 | 15,073 | 164,901,957 | Not measured for this test | Excluded because the build generated it |

Fifty-three abstract texts occur in both source families. The docket abstracts
range from 1 to 3,960 characters and the Federal Register abstracts from 75 to
4,125 characters. `sourceObservedTopics` contains no values in this snapshot.

Two checks confirm the absence of embedded full bodies:

- `text_extraction_status` is null in every catalog row.
- The exact preserved upstream `documents.parquet` has 1,993,040 rows and
  `count(text_content) = 0`.

The catalog carries 140,923 candidate renditions for 130,589 items, but those
are external URLs rather than captured bytes. They include 93,015 HTML and
46,510 PDF renditions, plus smaller spreadsheet, Word, text, and RTF groups.

## What the atlas contributes

The bundle contains 263 identifier-family records, 244 regular expressions,
and 588 examples. Its highest-value contribution is its descriptive model:

- issuer, object type, namespace, and uniqueness scope;
- raw, displayed, and normalized forms;
- required context and semantic validation beyond lexical shape;
- lifecycle and effective-date changes;
- privacy class and handling constraints;
- explicit decisions that no safe universal regex exists;
- decomposed court, congressional, award, and procurement namespaces; and
- examples that can become positive, negative, and collision fixtures.

These ideas fit RefSpec's evidence model better than a flat list of regexes.
They let RefSpec say what a token might be, what context supports that reading,
which authority can verify it, and when the format applies.

## Census results

### Selected structured source-catalog identifiers

The atlas document pattern matched 1,920,314 of 1,993,040 catalog IDs
(96.351%). It missed 72,628 `_FRDOC_` records and 98 GIPSA `NONRULEMAKING`
records. More importantly, every one of those 1,920,314 matches also matched
the atlas's comment and docket patterns. The three regexes therefore do not
identify the object type without field or record context.

RefSpec's generic normalizer preserved all 1,993,040 source IDs. Its stricter
prose reader recognized 1,877,510 specifically as document IDs. That split is
useful: lossless field normalization and conservative prose recognition are
different jobs.

For the native docket field, the census contained 1,847,476 occurrences and
277,249 distinct values. The atlas accepted 1,774,753 occurrences (96.064%).
RefSpec normalized 1,847,343 (99.993%) and missed 133 GIPSA suffix cases.

The raw RIN field contained 64,537 occurrences and 184 distinct values. Both
approaches accepted the 8,173 real values, representing 183 distinct RINs, and
rejected 56,364 copies of `Not Assigned`.

### Regulation Identifier Numbers

The official Unified Agenda roster contains 46,547 distinct RINs, all in the
strict form `dddd-LLdd`: four digits, a hyphen, two letters, and two digits.
That result supports a narrow, roster-backed Unified Agenda shape, not a
universal RIN grammar. Five source-confirmed Federal Register RIN-field values
fall outside it: `0648-XD990`, `0648-XC705`, `3090-00XX`, `1115-09AE`, and
`2070-78AB`. RefSpec already preserves them as source facts while refusing to
mint them through the roster-backed space.

Long-prose testing exposed two complementary issues:

- Atlas-only matches included 90 genuine compact labels such as
  `RIN-2060-AE83`. RefSpec's hyphen-aware boundary rejects the identifier when
  it begins immediately after `RIN-`.
- RefSpec-only matches included false positives such as `1992-JUNE`,
  `1000-YARD`, `1099-MISC`, and OMB control-number fragments. RefSpec also
  recovered some real values with Unicode dashes that the atlas did not
  normalize.

The tested direction is:

1. use `\d{4}-[A-Z]{2}\d{2}` as the roster-backed, mintable Unified Agenda
   shape;
2. retain case and Unicode-dash normalization;
3. add a labeled reader for forms such as `RIN-2060-AE83` and
   `RIN: 2060-AE83`; and
4. use an official roster for existence checks and damaged-column correction,
   while retaining a source-field/refusal path for confirmed outliers.

### Federal Register document numbers

Across 1,004,233 distinct Federal Register `document_number` values, the atlas
accepted 980,606 and RefSpec's current combined logic accepted 1,003,873.
RefSpec-only coverage comprised 23,357 values. Atlas-only coverage comprised
90 short correction forms. Neither accepted 270 values.

The 48,309 body-file test explains the apparent gap:

| Measure | Atlas | RefSpec |
| --- | ---: | ---: |
| Federal Register number matches | 155,691 | 49,583 |
| Exact shared matches | 48,338 | 48,338 |
| Matches unique to the approach | 107,353 | 1,245 |
| Own filename recovered | 46,783 | 5,270 |

An own filename literal appears in 48,296 of 48,309 bodies. Atlas recovered
96.8% of those IDs. RefSpec recovered 10.9% because it deliberately refuses
bare legacy forms such as `97-1017`; it recovered none of the 39,786 legacy
rule filenames, while the atlas recovered 38,441.

That recall does not justify a global broad regex. Atlas also produced 9,160
embedded matches in bodies. In docket abstracts, 305,080 of 320,637
occurrence-weighted matches were embedded; collapsing repeated abstract text
leaves 3,660 embedded matches among 5,918 occurrences. These often take
fragments from docket IDs. The useful import is a **source-scoped or explicitly
labeled legacy Federal Register reader**, with the broad grammar disabled in
unrelated prose.

RefSpec's Unicode-dash folding also remains valuable. The atlas misses those
presentation variants.

### Citations in abstracts

The default atlas helper admitted 110 families. Applied to the 111,746
distinct abstracts and 104 withdrawal reasons, it produced 8,318 hits across
5,610 texts, with 45 families represented and 390 same-span collisions.

Several results are strong citation signals:

| Family | Atlas hits | Texts |
| --- | ---: | ---: |
| Code of Federal Regulations | 2,241 | 1,878 |
| United States Code | 1,072 | 920 |
| Federal Register citation | 712 | 597 |
| Public law | 496 | 460 |
| Executive order | 293 | 231 |
| Statutes at Large | 57 | 56 |
| RIN | 38 | Not separately counted |

Against RefSpec's contextual readers, measured by distinct abstract text:

| Family | Both | RefSpec only | Atlas only | Interpretation |
| --- | ---: | ---: | ---: | --- |
| CFR | 1,877 | 118 | 1 | Keep RefSpec's broader contextual reader |
| U.S.C. | 920 | 55 | 0 | Keep RefSpec's broader contextual reader |
| Public law | 460 | 3 | 0 | Near agreement |
| Statutes at Large | 56 | 0 | 0 | Exact agreement |
| Executive order | 229 | 5 | 2 | Atlas-only cases were ordinary `EO` prose, not orders |
| Federal Register | 593 | 47 | 3 | RefSpec also recognizes compact forms such as `76FR` |
| Existing reporter families | 25 | 0 | 0 | Exact agreement in this source |

The comparison supports RefSpec's current parser style: labels, boundaries,
normalization, source gates, and longest-match arbitration add real value.

### Congressional identifiers

All 192,141 congressional rows have unique stored IDs. The atlas's composite
`congress/type/number` model works for 192,126. The 15 exceptions are six
historical `cen_doc_h` House documents and nine bills with Roman-numeral or
half-number forms such as `LXXXV` and `260½`.

Composite identity is the important atlas idea: a bill number needs its
Congress and bill type. RefSpec should preserve historical source spellings
and provide an explicit fallback instead of forcing every record through the
modern shape.

In public-law action prose, RefSpec recognized 10,913 rows and the atlas 7,525.
The 3,388-row difference comes chiefly from `Public Law No:` forms, which the
atlas grammar misses because it expects whitespace after `No.`. The atlas's
Senate-bill and Congressional Record patterns also collide on 6,377 action
occurrences. This is another reason to retain the contextual parser.

### Courts and reporter citations

The atlas lists 44 court families and 42 regexes. Its default helper enables
22. On 249,915 court opinions, those default patterns produced 1,067,527
family candidates: 1,040,968 reporter citations and 26,559 other court
patterns. Force-enabling the excluded patterns added more than 22 million
candidates, which confirms the importance of the atlas's own context flags.

The strongest additions are reporter families corroborated by the corpus's
existing citation markup:

| Atlas family | Regex matches | Markup-corroborated | Corroboration |
| --- | ---: | ---: | ---: |
| `B.R.` | 5,105 | 5,051 | 98.94% |
| `F. App'x` and typographic variants | 9,504 | 9,111 | 95.86% |
| `Fed. Cl.` / `Ct. Cl.` | 8,982 | 8,907 | 99.16% |
| Federal Reporter | 450,801 | 447,648 | 99.30% |
| Federal Supplement | 52,108 | 51,665 | 99.15% |
| `NLRB` | 441 | 439 | 99.55% |
| `S. Ct.` | 189,210 | 188,851 | 99.81% |
| `T.C.` | 111,206 | 110,951 | 99.77% |
| `U.S.` | 332,065 | 330,708 | 99.59% |
| `Vet. App.` | 1,527 | 1,521 | 99.61% |

The five clearest RefSpec additions—`B.R.`, `F. App'x`, `Fed. Cl.`/`Ct.
Cl.`, `NLRB`, and `Vet. App.`—contribute 25,029 annotated citations outside
RefSpec's current reporter set. `T.C.` adds 110,951, but the atlas labels the
family broad and its `T.C.M.` example does not satisfy its own regex. Split and
verify that family before import. `FLRA` had 11 regex matches and no markup
corroboration in this corpus.

Supreme Court emergency-application identifiers appeared 1,394 times and
original-jurisdiction identifiers five times. Their lettered namespaces are
strong source-context candidates.

One default court family needs demotion: `court.cfc_case` produced 23,790
candidates, but only 3,153 had an explicit `No.` label. The rest included
statutes, Social Security Rulings, and code-like text. Require a label or Court
of Federal Claims context.

Running RefSpec's regulatory readers indiscriminately over court prose also
created false positives, including reporter page ranges read as Federal
Register numbers and `2015—five` read as a RIN. Source gates apply to both
approaches.

### Collision fixtures found in real prose

The atlas found several compact strings that look valid in isolation but mean
something else in context. These should become named regression fixtures:

- `E5` and `E2` airspace classes matching Congressional Record pages;
- CFR sections such as `75.500` matching Assistance Listing numbers;
- `S10`, `S6`, and `S4` matching both Senate bills and Congressional Record
  pages;
- `PM2`, `PM10`, and `EC135` matching House or Senate communications;
- `SOLUTIONS`, `PRECISION`, and `PETITIONS` matching an FEC candidate shape;
- `APPLICATIONS`, `INSTRUCTIONS`, and `REGISTRATION` matching a UEI shape;
- ZIP+4 spans matching both DUNS and National Item Identification Numbers;
- a Bioguide-shaped token colliding with a PMA identifier;
- a National Stock Number found inside a docket substring; and
- an aircraft part number matching a Supreme Court application.

These are not reasons to discard the atlas families. They define the field,
label, source, or authority evidence each family needs.

## Concept import ledger

| Atlas concept or finding | RefSpec disposition | Census evidence | Next artifact |
| --- | --- | --- | --- |
| Namespace plus field/source context | Strengthen the core identifier model | Overlapping atlas document, comment, and docket patterns triple-type 1,920,314 catalog IDs | Identifier context vocabulary and conformance examples |
| Lexical, semantic, and registry validation as separate states | Import | RIN-shaped and court-shaped prose can be lexically valid but semantically wrong | Validation-state vocabulary and authority-check interface |
| Raw plus normalized representation | Strengthen current practice | Unicode dashes and historical spellings affect recall; source forms remain evidence | Normalization provenance fields and fixtures |
| Lifecycle and effective dates | Import | SSN, UEI/DUNS, FJC, procurement, and legacy document formats change over time | Versioned authority record design |
| Explicit refusal of a universal regex | Import | FAIN, TIN, court dockets, and award keys require subtype or authority context | `no-universal-shape` decision type |
| Roster-backed RIN shape plus label reader | Refine current parser | Unified Agenda roster supports one mintable shape; Federal Register fields contain confirmed outliers; body prose contains `RIN-...` | RIN positive, negative, outlier, Unicode, and labeled fixtures |
| Legacy Federal Register forms | Add only as a source-scoped reader | Atlas recovers 38,441 legacy own IDs but creates many embedded fragments | Federal Register source-reader proposal |
| Five reporter families | Add after focused tests | 25,029 existing markup-backed citations beyond RefSpec's current set | Reporter grammar patch and fixture set |
| `T.C.` reporter family | Research before import | High corpus support, but broad label and failed `T.C.M.` example | Split-family investigation |
| Supreme Court application and original namespaces | Add with court context | 1,394 application and five original-jurisdiction occurrences | Typed Supreme Court identifier proposal |
| Congressional composite identity | Import | Modern composite covers 192,126 of 192,141 rows; 15 historical exceptions | Composite key plus source-spelling fallback |
| Court-number decomposition | Promote selectively | Broad standalone case shapes generate heavy noise | Court-by-court source and label rules |
| Award and procurement distinctions | Add to gap ledger | Atlas separates PIID, FAIN, Assistance Listing, and USAspending keys | Authority proposals after consumer demand |
| Privacy class | Import as handling policy, not identity syntax | SSN/TIN and masked values require different storage and display rules | Sensitive-identifier detection and redaction policy |
| Real-corpus collisions | Import immediately as research fixtures | 390 same-span abstract collisions plus court/body false positives | Cross-family negative and arbitration fixture package |

## What not to import directly

- **The default helper as runtime behavior.** It filters some broad or sensitive
  families, but does not enforce every `required_context` rule or call all
  semantic validators.
- **Regex confidence labels as final evidence.** Several rows marked
  `candidate` behave broadly in real prose.
- **Regex-only object typing for document, docket, and comment identity.**
  Their patterns overlap; field and record type carry the distinction.
- **Open court-number patterns.** Court, label, and case-type context are
  essential.
- **Unsigned provenance as source proof.** The manifest checks bundle
  consistency, not source authorship, retrieval time, or source version.
- **Atlas examples without canonical/presentation separation.** Of 546
  regex-backed examples, 523 full-match and 23 fail; ten of the failures do
  not even search-match. Another 42 examples belong to families with no regex.

All 244 regexes compile, so the issue is not basic syntax. It is the intended
meaning and operating context of each pattern.

## Atlas gaps worth retaining in the research ledger

The folder does not yet carry several families or distinctions described in
the supplied research prose:

- Federal Judicial Center legacy `JID` and current `nid`;
- DoD Routing Identifier Code (`RIC`) and Unit Identification Code (`UIC`);
- IRS Document Locator Number (`DLN`);
- health-care provider taxonomy codes; and
- USAspending's separate Unique Award Key.

These are gaps in the experiment, not proof that RefSpec needs each family.
Add them to the candidate ledger and require a consumer, authority source, and
test corpus before promotion.

## Recommended next work

1. Convert the real collision examples into a small, reviewed negative-fixture
   package shared by identifier and citation readers.
2. Add focused proposals for roster-backed RIN handling, the five
   high-confidence reporter families, and lettered Supreme Court namespaces.
3. Design the source-scoped legacy Federal Register reader separately from the
   global prose grammar.
4. Add identifier metadata for namespace, uniqueness scope, required context,
   lifecycle, privacy, and validation level where RefSpec lacks an equivalent.
5. Treat the remaining atlas families as a gap ledger. Promote one only when a
   concrete RefSpec consumer and authoritative verification path exist.
6. Re-run each promoted family against its relevant prose source, not a single
   undifferentiated corpus.

## Reproducibility and evidence locations

- Atlas experiment: `federal_identifier_atlas/`
- Preserved catalog:
  `~/Work/corpora/_preserved-2026-08-31-v11-lineage/source-catalog-release/data/source-items.json`
  (3,948,345,547 bytes; SHA-256
  `6780532c689f9d655a0e3028a5937fb02feb20df83d48fd3094cfc19ab59029a`)
- Catalog build history:
  `~/Work/spicysearch/docs/history/2026-08-15-full-catalog-metadata-build.md`
- Exact upstream Regulations.gov table:
  `~/Work/corpora/_preserved-2026-08-27/landing-output/source-catalog-release-regulations-gov-2021-2025-metadata-complete-inputs/documents.parquet`
- Pinned Federal Register table used for the 1,004,233-value census:
  `~/Work/corpora/_preserved-2026-08-27/rulespec-stabilization-baseline-final/federal_register.parquet`
  (SHA-256
  `ac18315faa8be4a8d3656e758597d672c5d85c23cc6f8fde0ac53c9295b22bf2`)
- Legacy rule bodies: `~/Work/spicysearch/output/rule-bodies-pre2000-2026-08-22/`
- Presidential XML: `~/Work/spicysearch/output/presidential-bodies-2026-08-22/`
- Recovered presidential HTML:
  `~/Work/spicysearch/output/presidential-bodies-recovered-2026-08-22/`
- Court opinions:
  `~/Work/corpora/_preserved-2026-08-27/spicy-regs-output-complete/court-data-2026-08-22/court_opinion_bodies.parquet`
- Congressional bills:
  `~/Work/corpora/_preserved-2026-08-27/spicy-regs-output-complete/congress_bills.parquet`
- Temporary body comparison output: `/tmp/fr_body_scan_results.json` (the
  durable results needed for this decision are summarized in this note; the
  raw temporary file has not been promoted to research evidence)
- Relevant historical Claude session:
  `~/.claude/projects/-Users-mikewolfd-Work-spicysearch/3b6c6860-ea96-4a5d-a417-360c0bf8a5b1.jsonl`

The historical Claude session indexed `proceeding-description` and
`document-abstract` text units for lexical search, but its identifier census
targeted structured fields rather than validating extraction over all prose.
The session also inferred that upstream `text_content` held bodies; the exact
preserved parquet contradicts that inference because every value is null.

## Delivery boundary

This is a local research note. No RefSpec term, grammar, code path, test suite,
commit, release, publication, or downstream system changed as part of this
work.
