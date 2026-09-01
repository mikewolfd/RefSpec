from federal_identifier_patterns import (
    load_registry, matches_value, validate_ssn, validate_itin, validate_atin,
    validate_npi, validate_dea_registration, validate_mbi,
    validate_faa_n_number, parse_native_ndc10, validate_assistance_listing,
)
import re

def test_all_regexes_compile():
    for row in load_registry()["identifiers"]:
        if row["candidate_regex_python"]:
            re.compile(row["candidate_regex_python"])

def test_semantic_validators():
    assert validate_ssn("219-09-9999")
    assert not validate_ssn("900-12-3456")
    assert not validate_ssn("666-12-3456")
    assert validate_itin("912-70-1234")
    assert not validate_itin("912-93-1234")
    assert validate_atin("912-93-1234")
    assert validate_npi("1234567893")
    assert validate_dea_registration("AB1234563")
    assert not validate_dea_registration("AB1234564")
    assert validate_mbi("1EG4-TE5-MK73")
    assert validate_faa_n_number("N123AB")
    assert not validate_faa_n_number("N12O")
    assert not validate_faa_n_number("N12")  # FAA-reserved N1-N99 by default
    assert parse_native_ndc10("1234-5678-90") == ("1234", "5678", "90")
    assert parse_native_ndc10("1234567890") is None
    assert validate_assistance_listing("31.A1A")
    assert validate_assistance_listing("93.778")

def test_selected_value_regexes():
    assert matches_value("congress.member.bioguide", "A000360")
    assert matches_value("clinicaltrials.nct", "NCT01234567")
    assert matches_value("court.scotus_application", "23A123")
    assert matches_value("sec.accession_number", "0001193125-15-118890")
