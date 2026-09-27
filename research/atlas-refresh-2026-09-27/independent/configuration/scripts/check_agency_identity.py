"""Reproduce the recorded Atlas diagnostic without modifying the checkout."""

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
import dataclasses, json
from pathlib import Path
from types import SimpleNamespace
from tools import verify_atlas_source_fidelity as v
from refspec.input_pin import read_verified_file_pin

root = args.repo
out = []
for name in ("ecfr-agencies-roster-2026-08-15", "regulations-gov-agencies-roster-2026-08-16"):
    s = next(s for s in v.SOURCES if s.name == name)
    payloads = {
        p: read_verified_file_pin(
            v._resolve_source_pin(root, p),
            expected_sha256=p.sha256,
            expected_byte_length=p.byte_length,
            logical_path=p.path,
        )
        for p in s.inputs
    }
    pub = v._PUBLISHER_READERS[s.reader](s, payloads)
    resource = next(iter(sorted(pub.concepts)))
    fields = pub.expected_native_payloads[resource]
    fixed = dataclasses.replace(s, identity_policy="source-key-derived")
    config = v.check_configuration(
        SimpleNamespace(
            expectations=v.Expectations(), declared_specs=lambda: (fixed,), specs=(), native_control_pairs=()
        )
    )
    out.append(
        {
            "name": name,
            "pinCount": len(payloads),
            "publisherConcepts": len(pub.concepts),
            "sourceKeyDerivedConfigPass": config.passed,
            "resource": resource,
            "nativePayload": fields,
        }
    )
write_json(args.output_dir, "agency-identity.json", out)
assert [r["publisherConcepts"] for r in out] == [316, 331]
assert all(r["sourceKeyDerivedConfigPass"] for r in out)
s = next(s for s in v.SOURCES if s.name == "lc-external-target-endpoints-2026-08-15")
print("LC language exclusion applies", v._language_exclusion_for_spec(s) is not None)
