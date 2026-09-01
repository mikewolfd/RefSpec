# Repositories, APIs, schemas, and wikis for U.S. federal identifiers

Reviewed/cataloged: 2026-08-31.

## Tier 1 — issuer or official publication infrastructure

### LibraryOfCongress/api.congress.gov
- URL: https://github.com/LibraryOfCongress/api.congress.gov
- Use for Congress-scoped object keys and controlled type values: bills/resolutions, amendments, nominations, treaties, committee codes, communications, votes, and CRS products.
- Important boundary: an API route key is not necessarily the human citation or the GovInfo publication package ID.

### usgpo/bill-status
- URL: https://github.com/usgpo/bill-status
- Use for bill-status XML schemas, action/type enumerations, text-version codes, committees, members, laws, and related identifiers.
- Better than copying examples from prose because controlled values and schema changes can be diffed.

### usgpo/bulk-data
- URL: https://github.com/usgpo/bulk-data
- Use for collection-specific bulk schemas and real package/granule examples.
- Pair with GovInfo API collection help. GovInfo package IDs and granule IDs are platform identifiers, not always legal citations.

### usgpo/uslm
- URL: https://github.com/usgpo/uslm
- Use for legal-document hierarchy, structural identifiers, USLM attributes, and machine-readable legislative/statutory text.
- It is a markup/schema authority, not a catalog of every person, award, agency, or court identifier.

### usnationalarchives/federalregister-api-core
- URL: https://github.com/usnationalarchives/federalregister-api-core
- Use for Federal Register document metadata, document-number behavior, agencies, citation fields, and API semantics.

### fedspendingtransparency/usaspending-api
- URL: https://github.com/fedspendingtransparency/usaspending-api
- Use for award data models, generated platform award IDs, PIID/FAIN fields, agency/account dimensions, and source-system crosswalk behavior.
- Preserve issuer-native PIID/FAIN separately from USAspending-generated IDs.

### niemopen/niem-model
- URL: https://github.com/niemopen/niem-model
- Use as a broad schema/code-list atlas spanning justice, immigration, emergency management, education, screening, cyber, addresses, organizations, and many identifier-bearing properties.
- NIEM usually tells you that a property/code list exists; it is not a curated regex corpus and may model restricted/nonpublic values.

## Tier 2 — legal citation and court operational data

### freelawproject/eyecite
- URL: https://github.com/freelawproject/eyecite
- Best available open parser for full, short, supra, id., statutory, journal, and reporter citations.
- Use it instead of a single giant reporter regex; legal citation resolution is stateful.

### freelawproject/reporters-db
- URL: https://github.com/freelawproject/reporters-db
- Reporter abbreviations, editions, historical variants, ambiguity metadata, laws/journals, and regex templates.
- A reporter abbreviation can map to more than one reporter; date/court context remains necessary.

### CourtListener, Juriscraper, and RECAP
- CourtListener: https://github.com/freelawproject/courtlistener
- Juriscraper: https://github.com/freelawproject/juriscraper
- RECAP: https://github.com/freelawproject/recap
- Use for court slugs, docket/opinion models, court-specific scraper behavior, PACER/ECF ingestion, and real-world formatting variations.
- CourtListener IDs/slugs and RECAP object IDs are platform keys, not official court docket identities.

## Tier 3 — crosswalks and generic recognizers

### unitedstates/congress-legislators
- URL: https://github.com/unitedstates/congress-legislators
- High-value crosswalks among Bioguide, LIS, ICPSR, GovTrack, FEC, Wikidata, social, and historical member metadata.

### Presidio
- URL: https://github.com/data-privacy-stack/presidio
- Useful generic PII candidate recognizers and context scoring.
- Do not treat its regexes as issuer validation. In the reviewed SSN recognizer, semantic rejection covers area 000 and 666 but not SSA-invalid area 900–999, illustrating why an official semantic layer is still required.

### LexNLP
- URL: https://github.com/LexPredict/lexpredict-lexnlp
- Useful extraction components for legal/financial text; less authoritative than issuer schemas and the Free Law Project reporter data for U.S. citation identity.

### Wikidata identifier properties
- URL: https://www.wikidata.org/wiki/Wikidata:Database_reports/List_of_properties/all
- Excellent discovery layer for formatter URLs, format constraints, examples, and cross-database properties such as Bioguide and FEC IDs.
- Community-maintained; copy neither regex nor lifecycle claims into production without checking the issuer.

## What does not exist

There is no authoritative repository containing every federal identifier grammar. The closest practical stack is:

1. issuer API/schema or program manual;
2. GovInfo/Congress.gov for legal and publication objects;
3. NIEM for broad data-model/code-list discovery;
4. Free Law Project for legal citations and court data;
5. an internal versioned registry that stores open/delegated families and effective dates.
