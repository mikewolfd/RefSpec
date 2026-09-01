# Validation and extraction notes

## Why regex is only layer one

A production recognizer should distinguish:

- **Lexical candidate:** the text could have the shape.
- **Syntactic validity:** positions, separators, ranges and check digits pass.
- **Semantic validity:** component codes and effective dates agree.
- **Issuer resolution:** the issuer/API confirms an actual record.
- **Identity resolution:** the record is linked to the correct entity/object in context.

The registry's `regex_exactness` field describes the lexical pattern, not issuance confidence.

## Collision-first routing

Route by label, document collection and issuer before testing broad numeric patterns. Examples:

- 9 digits can be SSN, EIN without punctuation, DUNS, A-number, passport locator, I-94 fragment, PMID, or an agency-local number.
- 10 digits can be NPI, CIK display, FRN, FEI, application/case values, or ordinary numbers.
- 12 digits can be UEI-like alphanumeric, EPA FRS/RMP IDs, NCES school IDs, a future NDC, or a generic database key.
- `23-1234` can be a circuit docket, Supreme Court docket, CAVC case, local agency matter, or a year-sequence label.
- A five-character token can be CAGE/NCAGE, a PSC fragment, an office code, or ordinary text.

## Court rules

Never use a docket string alone as a global key. Use `court + canonical local docket`. Preserve office/division, case type, zero padding, judge/reassignment suffixes and related/consolidated dockets. ECF document numbers are scoped to the case. GovInfo USCOURTS package and granule IDs are publication keys and must not overwrite the official court docket.

## Congressional/publication rules

Keep at least three layers when available:

1. the human legal citation (`Pub. L. 117-58`, `H.R. 1`, `89 FR 12345`);
2. the issuer/API compound key (`118/hr/1`);
3. the GovInfo package/granule ID (`BILLS-118hr1ih`, `CREC-...-PgH...`).

These layers can refer to the same intellectual work but have different granularity and lifecycle.

## Lifecycle and effective-date traps

- DUNS is legacy for federal entity identification; UEI is current.
- HICN is legacy beneficiary identity; MBI is current.
- Assistance Listing suffixes are no longer safely numeric-only.
- FDA native 10-digit NDC, HIPAA 11-digit padding, and the future 12-digit 6-4-2 format must be versioned separately.
- FMCSA USDOT suffix modernization is proposed/transitional; do not delete MC/FF/MX support prematurely.
- Reporter editions, Census geography codes, NAICS/SOC/PSC codes, Treasury codes and organizational identifiers need edition/effective dates.

## Privacy and secrets

Privacy-class counts in this registry: {'highly_sensitive': 12, 'mixed': 6, 'public': 223, 'public_or_restricted': 2, 'secret': 2, 'sensitive': 18}.

SSNs, ITINs, A-numbers, passport numbers, I-94s, MBIs, HICNs, SEVIS IDs and similar values should be detected for protection before they are indexed for retrieval. Secrets such as IRS IP PINs and SEC CCC credentials should be redacted immediately and never treated as knowledge-graph identifiers.

## Code-audit lesson: generic PII recognizers

The reviewed Presidio SSN recognizer contains useful candidate patterns and rejects several bad groups/examples, but it does not reject the SSA-invalid 900–999 area range. Treat generic PII libraries as recall-oriented detectors and layer official semantic validators on top.

## Legal citations

Use eyecite plus reporters-db for case citations. One regex cannot reliably handle full and short citations, parallel reporters, nominative reports, pin cites, id./supra antecedents, OCR variants, reporter ambiguity and date/court disambiguation.

## Families intentionally recorded without a universal regex

19 families are explicit open/opaque/nonexistent classes:

- `agency.rulemaking_docket.generic` — Agency rulemaking docket number (generic open class): Docket prefixes, year placement, separators and sequence lengths vary by agency and system. Regulations.gov IDs are only one major family.
- `assistance.fain` — Federal Award Identification Number (FAIN): There is no government-wide lexical grammar; award numbers can encode program, fiscal year, continuation/supplement and amendment information.
- `court.service_cca_docket` — Military service Court of Criminal Appeals docket identifier: No single inter-service grammar: summary/regular/miscellaneous cases use different prefixes, bare serials and year-number forms; rehearing annotations are not base IDs.
- `credential.piv_fascn` — PIV FASC‑N: FIPS 201-3 discourages relying on FASC-N as the sole identifier; uniqueness is not universal outside the Executive Branch/PIV-I, and replacement/reissuance matters.
- `grants.opportunity_number` — Grants.gov funding opportunity number: No universal grammar; can include fiscal year, office, program and competition sequence; may be reused only under agency rules.
- `health.hicn` — Health Insurance Claim Number (HICN): Often SSN-derived with Beneficiary Identification Code, but RRB and other forms differ. Replaced by MBI and remains highly sensitive in historical data.
- `health.national_patient_id` — National patient identifier: Do not mislabel MRNs, MBIs, HICNs, SSNs or insurer member IDs as a national patient identifier.
- `legal.case_citation_generic` — American case citation (generic parsed object): Reporter ambiguity, nominative reports, parallel citations, pin cites, short forms, id./supra, OCR and HTML boundaries require stateful parsing.
- `nara.local_identifier` — NARA local identifier: No universal grammar; local IDs are only unique within the creating/cataloging unit and can contain punctuation/spaces.
- `platform.data_gov_dataset` — Data.gov/agency dataset identifier: Data.gov aggregates catalogs; a CKAN UUID/slug is not necessarily the source agency's durable identifier and migrations can change it.
- `procurement.award_number_generic` — Agency grant/contract award number (generic open class): No single federal award-number regex covers procurement and assistance; many apparent formats are program-local.
- `procurement.piid_supplementary` — Supplementary PIID / order identifier: Length/placement varies; a delivery/task order may itself have a standalone PIID and a parent IDV PIID.
- `procurement.solicitation_number` — Solicitation number: No universal grammar; may resemble PIID but can contain more separators/text and can be amended without changing base solicitation.
- `records.foia_tracking` — FOIA request/tracking number (generic open class): No government-wide grammar; agencies migrate portals and can expose separate request, appeal, referral and case numbers.
- `sec.ccc` — SEC EDGAR CIK Confirmation Code (CCC): Secret credential, not a public identifier. Do not extract into search indexes or knowledge graphs.
- `security.dhs_redress_number` — DHS TRIP redress control number: Public sources do not define a reliable universal regex; do not conflate with a Known Traveler Number.
- `security.known_traveler_number` — Known Traveler Number / PASS ID: KTN/PASS ID/DoD ID inputs are operationally accepted in different contexts; no single safe public regex should be used for all.
- `supply.iuid_uii` — Item Unique Identification / Unique Item Identifier (IUID/UII): No single regex: CAGE/DUNS/DoDAAC enterprise IDs, serials and part/lot values create multiple constructs; data-matrix encoding includes identifiers/qualifiers.
- `tax.tin_generic` — Taxpayer Identification Number (generic class): TIN is not synonymous with SSN; forms may accept several namespaces and masked values.

Recording these negative results is important: otherwise downstream teams repeatedly invent overbroad regexes for identifiers whose grammar is delegated to each issuer.

## Suggested match object

```json
{
  "raw_value": "H.R. 1",
  "normalized_value": "HR:1",
  "family_id": "congress.bill.hr",
  "issuer_namespace": "US_CONGRESS",
  "context": {
    "congress": 118
  },
  "validation_status": "issuer_resolved",
  "validation_provenance": {
    "validator": "congress_api_resolver",
    "validator_version": "2026-08-31",
    "source": "Congress.gov API",
    "checked_at": "2026-08-31T00:00:00Z"
  }
}
```
