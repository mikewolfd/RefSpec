"""Reproduce the recorded Atlas diagnostic without modifying the checkout."""

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
import dataclasses, hashlib, io, json, zipfile
from pathlib import Path
from unittest.mock import patch
from tools import verify_atlas_source_fidelity as v
import tempfile

fixture = tempfile.TemporaryDirectory(prefix="lc-fixture-", dir=args.output_dir)
root = Path(fixture.name)
source = next(s for s in v.SOURCES if s.name == "lc-external-target-endpoints-2026-08-15")
rows = (
    "\n".join(
        [
            "<http://id.loc.gov/authorities/subjects/sh1> <http://www.loc.gov/mads/rdf/v1#hasExactExternalAuthority> <http://aims.fao.org/aos/agrovoc/1> .",
            "<http://id.loc.gov/authorities/subjects/sh2> <http://www.loc.gov/mads/rdf/v1#hasExactExternalAuthority> <http://vocab.getty.edu/aat/2> .",
            '<http://aims.fao.org/aos/agrovoc/1> <http://www.loc.gov/mads/rdf/v1#authoritativeLabel> "AGROVOC fixture label" .',
            '<http://vocab.getty.edu/aat/2> <http://www.loc.gov/mads/rdf/v1#authoritativeLabel> "GETTY fixture label" .',
        ]
    )
    + "\n"
)
out = io.BytesIO()
with zipfile.ZipFile(out, "w") as z:
    z.writestr("external_links.nt", rows)
b = out.getvalue()
(root / "input.zip").write_bytes(b)
pin = dataclasses.replace(
    source.inputs[0], path="input.zip", sha256="sha256:" + hashlib.sha256(b).hexdigest(), byte_length=len(b)
)
specs = tuple(
    dataclasses.replace(
        source, name=f"fixture-{key}", release_keys=(f"lc-external-{key}-endpoints-2026-08-15",), inputs=(pin,)
    )
    for key in ["agrovoc", "getty-aat"]
)
with patch.dict(v._LC_TARGET_ENDPOINT_COUNTS, {"agrovoc": 1, "getty-aat": 1}):
    individual = {s.name: sorted(v._read_lc_external_target_endpoints(s, {pin: b}).concepts) for s in specs}
    ctx = v.build_context(root / "missing-distribution", root, specs=specs)
    cached = {p.spec.name: sorted(p.publisher.concepts) for p in ctx.pairs}
    result = {
        "individualReader": individual,
        "combinedBuildContext": cached,
        "cacheLeakReproduced": individual != cached,
        "pinFailures": ctx.pin_failures,
        "expectedSyntheticMissingDistribution": ctx.load_failures,
    }
write_json(args.output_dir, "lc-cache.json", result)
fixture.cleanup()
assert not result["pinFailures"]
assert result["cacheLeakReproduced"]
