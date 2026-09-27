"""Replay bounded independent Atlas checks; run with the RefSpec uv environment.

Usage: uv run --frozen python /path/to/replay.py --repo . --output /tmp/replayed
Needs the pinned UMTHES archive and the existing UMTHES-only distribution.
Writes only --output and a temporary directory; no full build or large validator.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    checks = []

    def run(name: str, command: list[str]) -> None:
        with (output / f"{name}.log").open("w") as log:
            result = subprocess.run(command, cwd=repo, stdout=log, stderr=subprocess.STDOUT)
        checks.append({"name": name, "command": command, "exitCode": result.returncode})
        if result.returncode:
            raise RuntimeError(f"{name} failed: see {output / (name + '.log')}")

    run("preferred-label-tests", [
        "uv", "run", "--frozen", "pytest", "-q", "-n", "0",
        "tests/test_atlas_v3_preferred_languages.py",
    ])
    run("packing-tests", [
        "uv", "run", "--frozen", "pytest", "-q", "-n", "0",
        "tests/test_generate_atlas_v3_full.py::test_a_large_mapping_release_buckets_its_pack",
        "tests/test_generate_atlas_v3_full.py::test_same_release_cross_partition_reference_pins_target_pack",
        "tests/test_generate_atlas_v3_full.py::test_streamed_construction_matches_the_whole_graph_oracle",
    ])
    run("umthes-standalone-validation", [
        "uv", "run", "--no-project", "--with-requirements",
        "bindings/atlas/3.1/requirements.txt", "python",
        "bindings/atlas/3.1/tools/validate.py", "--distribution",
        "output/atlas-3.1-umthes-2026-09-27/distribution",
    ])

    # Load the existing test-only oracle and complete synthetic fixture.
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "tests"))
    import pytest
    from rdflib import Literal
    import test_atlas_v3_preferred_languages as labels
    import test_generate_atlas_v3_full as packing
    import rdf_canonical

    validator = labels.validator
    ontology, shapes = validator._parse_binding_graphs()
    mutations = {
        "multilingual": (Literal("A", lang="de"), Literal("B", lang="en")),
        "duplicate-language-different-text": (Literal("A", lang="en"), Literal("B", lang="en")),
        "duplicate-literal-distinct-ids": (Literal("A", lang="en"), Literal("A", lang="en")),
        "missing-language": (Literal("A"),),
        "uppercase-language": (Literal("A", lang="EN"),),
    }
    results = []
    for name, literals in mutations.items():
        fixture = labels._with_preferred_labels(literals)
        results.append({"case": name, **semantic_verdict(validator, fixture, ontology, shapes)})
    fixture = labels._with_preferred_labels((Literal("A", lang="en"), Literal("B", lang="de")))
    first = next(fixture.asserted.objects(labels.RESOURCE, labels.SKOSXL.prefLabel))
    fixture.asserted.add((labels.RESOURCE, labels.SKOSXL.altLabel, first))
    fixture.projection = validator._expected_projection(fixture.asserted)
    results.append({"case": "role-overlap", **semantic_verdict(validator, fixture, ontology, shapes)})
    assert [row["acceptedBySemanticChecks"] for row in results] == [True, False, False, False, True, False]
    issue = rdf_canonical.canonical_line_issue(b'<urn:test:s> <urn:test:p> "A"@EN <urn:test:g> .')
    assert issue is not None
    results.append({"case": "uppercase-language-wire", "acceptedByCanonicalGrammar": False, "issue": str(issue)})
    write_json(output / "additional-label-boundaries.json", results)

    with zipfile.ZipFile(repo / "output/registry-real-data-sources/umthes-gemet-endpoints-2026-08-15.zip") as archive:
        (output / "umthes-00000013.nt").write_bytes(archive.read("records/_00000013.nt"))

    with tempfile.TemporaryDirectory(prefix="atlas-partition-probe-") as temporary:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(packing.generator, "_registry_asserted_graph", packing._compiled_descriptor_graph)
            patch.setattr(packing.generator, "_PACK_LARGE_RELEASE_RESOURCE_THRESHOLD", 1)
            releases, mapping = packing._compiled_mapping_case(Path(temporary))
            _, manifest = packing.write_both_and_compare(
                Path(temporary), releases, (mapping,),
                packing._compiled_stream_prebuild(releases, (mapping,)),
                created_at=packing._TEST_CREATED_AT,
            )
            packs = [row for row in manifest["packs"] if row["kind"] == "mapping"]
            assert len(packs) > 1
            assert all("/mappings/" in row["path"] and row.get("partition", {}).get("prefix") for row in packs)
            write_json(output / "partitioned-mapping-writer-probe.json", {
                "mode": "synthetic-force-partition-via-test-only-threshold",
                "wholeAndStreamedBytesEqual": True,
                "mappingPackCount": len(packs),
                "mappingPackPaths": [row["path"] for row in packs],
                "productionThreshold": 50000,
                "limitation": "Writer-path equivalence, not full-artifact size or acceptance.",
            })
    checks.extend([
        {"name": "additional-label-boundaries", "exitCode": 0},
        {"name": "partitioned-mapping-writer-probe", "exitCode": 0},
    ])
    write_json(output / "checks.json", {
        "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "checks": checks,
        "qualification": "bounded structural and writer-path checks only",
    })
    checksums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in sorted(output.iterdir()) if path.is_file() and path.name != "SHA256SUMS"]
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    print(f"Passed bounded replay; evidence: {output}")


def semantic_verdict(validator, fixture, ontology, shapes) -> dict:
    try:
        validator._run_shacl({"asserted": fixture.asserted, "projection": fixture.projection, "derived": fixture.derived}, ontology, shapes)
        validator._check_label_integrity(fixture.asserted)
    except validator.AtlasValidationError as error:
        return {"acceptedBySemanticChecks": False, "code": error.code, "message": str(error)[:600]}
    return {"acceptedBySemanticChecks": True}


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


if __name__ == "__main__":
    main()
