"""Reproduce the recorded Atlas diagnostic without modifying the checkout."""

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
from dataclasses import replace, asdict
from types import SimpleNamespace
from pathlib import Path
import json
from tools import verify_atlas_source_fidelity as v
from tools import generate_atlas_v3_full as g

fixed = []
for s in v.SOURCES:
    if s.name == "lc-external-target-endpoints-2026-08-15":
        fixed.extend(replace(s, name=k, release_keys=(k,)) for k in s.release_keys)
    elif s.name in {"ecfr-agencies-roster-2026-08-15", "regulations-gov-agencies-roster-2026-08-16"}:
        fixed.append(replace(s, identity_policy="source-key-derived"))
    else:
        fixed.append(s)
ctx = SimpleNamespace(
    expectations=v.Expectations(), declared_specs=lambda: tuple(fixed), specs=(), native_control_pairs=()
)
config = v.check_configuration(ctx)
sourcekeys, mappingkeys = g.split_construction_unit_keys(g._declared_construction_unit_keys())
ctx = SimpleNamespace(
    expectations=v.Expectations(),
    units=tuple(
        v.DistributionUnit(k, "mapping" if k in mappingkeys else "sourceRelease", (), (), {})
        for k in sourcekeys | mappingkeys
    ),
    loaded_specs=lambda: frozenset(v.SOURCES),
    scoped_out_release_keys=lambda: frozenset(),
    specs=v.SOURCES,
    pack_pins={},
)
coverage = v.check_distribution_coverage(ctx)
out = {
    "declarationRepair": asdict(config),
    "declaredFullyLoadedCoverageOnly": asdict(coverage),
    "note": "No actual distribution data or publisher fidelity verdict is represented.",
}
write_json(args.output_dir, "repair-probe.json", out)
assert config.passed
assert not coverage.passed and len(coverage.failures) == 5
