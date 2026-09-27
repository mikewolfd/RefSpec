"""Retain exact small source specimens and input digests, without fetching."""

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
import hashlib
import itertools
import json
import zipfile


def pin(path):
    source = args.repo / path
    h = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return {"path": path, "bytes": source.stat().st_size, "sha256": h.hexdigest()}


def read(path):
    return json.loads((args.repo / path).read_text())


paths = {
    "ecfr": "tests/fixtures/cfr_list_of_subjects/ecfr-agencies-2026-08-15.json",
    "regs": "tests/fixtures/regulations_gov_agencies/regulations-gov-agencies-2026-08-16.json",
    "candidates": "plans/agency-registry-batch-1-candidates.json",
    "decisions": "plans/agency-registry-batch-1-decisions.json",
    "fercClass": "output/registry-real-data-sources/ferc-class-types-january-2025.pdf",
    "fercDocket": "output/registry-real-data-sources/ferc-docket-prefix-june-2025.pdf",
    "ua": "tests/fixtures/unified_agenda_codes/risc-preamble-202210.pdf",
    "lc": "output/registry-real-data-sources/lcsh-externallinks-2026-08-15.nt.zip",
}
pins = {name: pin(path) for name, path in paths.items()}
expected = {
    "ecfr": "766685f466d62fa558a504cdeac23eef1d41f3ea24a2f5a3f78b38f2bcd5365e",
    "regs": "28ab9f5422dd27fc7906ddc696e8e7811b11056822f370bcee7ea18a28418fa2",
    "candidates": "6bb7c2d4dc818b24cb92b1e220704b9d9acb9afc6be6fc400c0daccde14b71d2",
    "decisions": "a454ea277d533ce25a331a996a676d58f0bd2573700a43893a1f52b6c8938098",
    "fercClass": "af632c9c6adbf0e7919d17e018b3a65078d0746bd1ab69a8d9fa65043720d688",
    "fercDocket": "c32efae9f51a70b6f955821d2fb3d3025995ef0e17e57bf2d32dfa16c2508dcb",
    "ua": "b7372fec456cf0c346bd23528ae227913e37f546bb1c03689da19ee6a44cb2a5",
    "lc": "7d279d69c6920b41a579634a84a1b31ff73af764345fe51df3f7c480efeba9d1",
}
assert {name: value["sha256"] for name, value in pins.items()} == expected
specimens = []


def walk(rows, pointer="/agencies", parent=None):
    for ordinal, row in enumerate(rows):
        row_pointer = f"{pointer}/{ordinal}"
        if row["slug"] == "economic-analysis-bureau":
            specimens.append({"input": "ecfr", "jsonPointer": row_pointer, "parentSlug": parent, "row": row})
        walk(row.get("children", []), f"{row_pointer}/children", row["slug"])


walk(read(paths["ecfr"])["agencies"])
for i, row in enumerate(read(paths["regs"])["data"]):
    if row["id"] == "ABMC":
        specimens.append({"input": "regs", "jsonPointer": f"/data/{i}", "row": row})
candidates = read(paths["candidates"])
ids = {"same:fr118:ecfr:economic-analysis-bureau", "event:fr564"}
for field, identity in [("candidates", "candidate_id"), ("events", "event_id")]:
    for i, row in enumerate(candidates[field]):
        if row[identity] in ids:
            specimens.append({"input": "candidates", "jsonPointer": f"/{field}/{i}", "row": row})
decisions = read(paths["decisions"])
for identity in sorted(ids):
    specimens.append(
        {"input": "decisions", "jsonPointer": "/decisions/" + identity, "row": decisions["decisions"][identity]}
    )
write_json(args.output_dir, "raw-context.json", {"inputs": pins, "specimens": specimens})
with zipfile.ZipFile(args.repo / paths["lc"]) as archive:
    with archive.open("external_links.nt") as stream:
        lines = [
            f"{i}: " + line.decode("ascii").rstrip("\r\n") for i, line in enumerate(itertools.islice(stream, 30), 1)
        ]
(args.output_dir / "lc-first30-lines.txt").write_text("\n".join(lines) + "\n")
