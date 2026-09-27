# Independent check of the adopted agency change events

The cited primary records support the adopted organization changes and stated function splits. All nineteen cited URLs were retrieved successfully. One linked official Federal Register PDF was also retained to check the printed postal heading. There are no unresolved access failures and no contradiction of a selected event date or function split was established in this bounded pass.

Several dates remain **owner-selected interpretations of the documented dates**, rather than explicit effective-date statements. Those distinctions were already present in the candidates and decisions and must survive any future automated verifier. This check preserves the owner decisions and input pins. A subsequent independent comparison now verifies the bounded agency RDF distribution and the separately built agency Parquet tables, as described below.

The [claim receipt](claim-receipt.json) covers every adopted event, every result row, dates, organization names and functions. Its statuses distinguish matches, roster display-name variants, explicit date-policy qualifications and the separate owner decision about identity versus succession. [Source receipts](source-receipts.json) bind every retained source to its URL, actual retrieval timestamp, SHA-256, byte length, HTTP status and local path. Original bytes are under `sources/`; extracted text is only a navigation aid. `context/` preserves the reviewed text with line numbers. Scanned PDF content was read visually, not inferred from an empty text layer.

| Event | Date and change verified | Qualification |
| --- | --- | --- |
| `fr96`, Customs Service | H. Doc. 108-32 plan subsection (a) puts Customs interior enforcement into ICE; subsection (b) puts border/port functions into CBP. Its implementation-date block says March 1, 2003. HSA section 412 retains Treasury customs-revenue authority. | Present-day roster display names differ from the historical bureau names. The retained authority is not an additional successor-identity claim. |
| `fr150`, Export Administration | 67 FR 20630-20631 expressly says the internal order renamed BXA to BIS on April 18, 2002 and makes the rule effective that day. | April 19 signature and April 26 publication are separate dates. Roster names invert the historical Bureau-of wording. |
| `fr232`, INS | HSA section 451(b) assigns services/adjudications to BCIS; the plan places Border Patrol/inspection in CBP and investigation/detention/removal/intelligence in ICE. The plan and 68 FR 10922 support March 1, 2003 transfer/abolition. | The HSA general effective date and the March 6 delegation-rule effective date are separate. |
| `fr259`, International Investment | The publisher roster expressly says the name changed November 21, 2008; 73 FR 70716 changes the chapter heading to Office of Investment Security. | The final rule expressly takes effect December 22, 2008. The selected November 21 date is the owner-approved roster rename date. |
| `fr404`, Pension and Welfare Benefits | Order 1-2003 section 4 renames PWBA as EBSA; section 7 is effective upon February 3, 2003 publication. Programs and delegations continue. | January 23 signature and April 3 conforming-rule dates are distinct. |
| `fr510`, USIA | FARRA sections 1311/1312 abolish USIA and transfer functions to State except BBG/IBB and their functions; section 1322 continues the existing BBG. Its roster confirms independent status on October 1, 1999. | Section 1301 also permits an earlier date under the section 1601 plan. That uncited plan was not newly acquired. Broadcasting functions were retained, not moved to a newly created board. |
| `fr543`, ICC | ICCTA section 2 gives January 1, 1996. Sections 101/201 abolish ICC and establish STB. Sections 102/103, 203 and 314-316 support the division between Board economic-regulation functions and Secretary of Transportation functions. | Preserve the Board/Secretary distinction; the Act did not transfer everything to STB. |
| `fr559`, HCFA | The June 29, 2001 order retitles HCFA as CMS and continues delegations. | The order has **no effective-date clause**. June 29 is its date/signature/filing basis chosen by the owner; June 14 announcement and July 31 conforming-rule effective date are separate. The primary text says **Health Care Financing Administration**, while the retained roster label says **Health Care Finance Administration**. |
| `fr564`, Postal Rate Commission | PAEA section 604 redesignates it as Postal Regulatory Commission; the Act was approved December 20, 2006. The FR409 roster calls it the successor agency. | Section 604 has no separate effective-date clause. Section 603(d)'s later date applies to section 603 amendments. The owner used enactment date and explicitly chose succession over duplicate-record identity; the statutory rename alone does not prove that FR564/FR409 are period-disjoint identities. |

## Important source distinctions

**CMS date:** [the original order](https://www.federalregister.gov/documents/2001/07/05/01-16800/centers-for-medicare-and-medicaid-services-statement-of-organization-functions-and-delegations-of) carries the selected June 29 date and the rename. An automated check may confirm this source fact and the owner's policy. It must not report that the order expressly states June 29 is the effective date. The candidate already says that the order states no effective date.

**Treasury date:** [the roster](https://www.federalregister.gov/agencies/international-investment-office) and [the final rule](https://www.federalregister.gov/documents/2008/11/21/E8-27525/regulations-pertaining-to-mergers-acquisitions-and-takeovers-by-foreign-persons) support different date meanings. This is not a failed match when the owner's chosen meaning remains explicit.

**Postal identity:** The [primary statute](https://www.congress.gov/109/plaws/publ435/PLAW-109publ435.htm) proves the redesignation. The retained [FR564 roster](https://www.federalregister.gov/agencies/postal-rate-commission) still describes the post-PAEA commission. I also inspected the [official 2003 PDF](https://www.govinfo.gov/content/pkg/FR-2003-03-25/pdf/03-7022.pdf), printed page 14435: the middle-column heading actually joins `POSTAL RATE COMMISSION` with `39 U.S.C. 3623`, while the AGENCY line separately names Postal Rate Commission. Thus the odd heading is present on the printed primary page; it is not evidence that a third organization exists. The owner-selected succession classification remains a separate modeled judgment.

**DHS source:** The useful body of [H. Doc. 108-32](https://www.govinfo.gov/content/pkg/CDOC-108hdoc32/pdf/CDOC-108hdoc32.pdf) is scanned. PDF page 5 contains subsection (a); page 6 contains subsection (b) and the implementation date. Full pages 5-9 were rendered and inspected, including the following contextual resource tables. Their text layer alone would not establish the claims.

## Actual generated-artifact comparison

The bounded eight-unit agency distribution completed on 2026-09-27 at repository commit `cc507773af7d01a9330b0bdd0dca293b25380147`. The independent read-only [comparison receipt](receipts/artifact-comparison.json) reports zero differences for all nine events and fourteen result rows, thirteen identity bridges, four recorded non-emissions, and twenty-six owner decisions. Expected values come directly from the retained candidate JSON and owner answers; the replay script imports no RefSpec producer or view-builder code.

The replay also independently reads all selected Federal Register, eCFR and Federal Hierarchy endpoints from their pinned raw JSON. Publisher names and parent organizations match the candidate fields; the retained raw-field receipt records each exact source file and digest.

The comparison checks the RDF event original and result sets, typed effective dates, complete event-native payloads (publisher names, date basis, result-specific functions, reasoning and row identifiers), every public-record citation and URL, owner decision outcomes, notes and bound digests. It also checks the bridge endpoints, names, parents, reasons and selected basis. Every event has its complete set of public-record evidence bindings; every bridge has both endpoint records. The approved reviewer, date and human-review evidence axes match on all forty-eight bindings. Source-record native JSON hashes and outgoing-RDF record hashes match their respective digest fields. Fourteen isolated corruptions of the actual data are detected, including altered dates, function assignments, endpoint names, owner decisions, bridge parents, non-emission reasons, missing results and RDF payloads.

The separate agency Parquet view matches every declared column for all event, bridge and non-emission rows. Its four non-emissions retain the owner's exact selected-option or withdrawal reasoning: Export-Import Bank's reverse-lookup cost rejection, the held statutory-rename basis for the foundation, the binational commission versus United States section withdrawal, and CISA's absent counterpart. The three rejected identity pairs and the CISA bridge emit no assertion in the agency mapping pack. These checks preserve the recorded owner choices; they do not independently re-adjudicate organizational identity.

The existing [manual primary-source claim receipt](claim-receipt.json) is joined back to the same selected dates, date bases, original organizations, result organizations, transferred functions and owner decisions. All twenty retained original source files still match their acquired SHA-256 and byte length. The artifact's source-record digest hashes its native JSON; it does not claim to hash the public document retrieved at that URL. The acquired public-document hashes remain separate evidence in [source receipts](source-receipts.json).

| Artifact | Actual SHA-256 |
| --- | --- |
| Bounded RDF `distribution/atlas-manifest.json` | `560266ed48d2db7a8c86cddd861f17f31f9b3d6ead7f10edbdc45be61de14dc1` |
| Agency RDF mapping pack, compressed bytes | `077bb0f5ff122badfefc2eb7bd66563ff7288e864a66d1dc697c059d8b50d24c` |
| Dedicated agency `output/agency-registry-view/view-manifest.json` | `77b357cc06fe3e67bcacb0591833884087572727064f89643e10aa2a28ad6b87` |

The generic Atlas Parquet view intentionally omits organization-change events and their evidence bindings. This is a separate artifact boundary, not a defect found by this check. Its manifest digest is recorded for traceability, while event table assertions concern the dedicated agency registry view. The parent's separate whole-distribution validation passed; this script does not substitute for that validator or rerun it.

## Replay and retained evidence

Run the repository's existing Python environment from any directory. For example:

```sh
"$REFSPEC_REPO/.venv/bin/python" /path/to/retain/scripts/compare_artifacts.py \
  --repo "$REFSPEC_REPO" \
  --output-dir /tmp/agency-artifact-replay
```

The default artifact locations are relative to `--repo` (or `REFSPEC_REPO`, or the current directory). Override `--distribution` and `--agency-view` to check another retained build. `--output-dir` must be outside the repository. The script reads the adjacent claim receipt by default. Add `--evidence-dir /path/to/full-evidence` to authenticate the original primary-source bytes against `source-receipts.json`. The script performs no fetching or repository writes; all fourteen mutation checks operate on in-memory copies.

The compact `retain/` package includes the report, claim and acquisition receipts, reviewed context excerpts, inspected PDF page PNGs, selected event inputs, actual-field snapshots, replay script and checksums. It deliberately excludes the original HTML/PDF files and extracted whole-document text. Those originals remain under the full evidence directory's `sources/`; preserve that directory in ignored output beside a copy of `source-receipts.json`. Relative `sources/` paths in the claim and source receipts identify those external originals. Rendered pages and excerpts support review but do not replace the originals.

## Remaining limits

This closes the bounded agency event and owner-decision artifact comparison. It does not make the generic source-fidelity verifier cover this construction unit, qualify every Atlas unit, or replace the missing FERC/Unified Agenda checks. It also does not change the owner-selected date meanings or the postal identity-versus-succession judgment. Decision digests match the selected candidate digests, but this script does not independently re-derive the candidate-content digest algorithm. The uncited FARRA section 1601 plan remains outside the requested source acquisition scope.
