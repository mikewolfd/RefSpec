"""Reproduce the recorded Atlas diagnostic without modifying the checkout."""

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
import dataclasses, json
from pathlib import Path
from types import SimpleNamespace
from tools import verify_atlas_source_fidelity as v
from tools import generate_atlas_v3_full as g

ctx = SimpleNamespace(
    expectations=v.Expectations(), declared_specs=lambda: v.SOURCES, specs=(), native_control_pairs=()
)
r = v.check_configuration(ctx)
p = g._declared_construction_unit_keys()
f = {k for s in v.SOURCES for k in s.release_keys}
out = {
    "configuration": dataclasses.asdict(r),
    "producerUnits": len(p),
    "verifierUnits": len(f),
    "missing": sorted(p - f),
    "extra": sorted(f - p),
    "lc_reader_in_spec_cache": v.LC_EXTERNAL_TARGET_ENDPOINT_READER in v.SPEC_SCOPED_RECORD_READERS,
}
write_json(args.output_dir, "config.json", out)
assert out["producerUnits"] == 131 and out["verifierUnits"] == 127
assert len(r.failures) == 3
assert out["missing"] == [
    "agency-registry-2026-09-26",
    "ferc-docket-prefixes",
    "ferc-document-class-types",
    "unified-agenda-legal-authority-citation-types",
]
assert not out["extra"]
