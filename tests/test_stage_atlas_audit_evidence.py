"""Local evidence staging preserves pins and refuses destructive replacements."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import stage_atlas_audit_evidence as staging


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


@pytest.fixture
def inputs(tmp_path):
    root, retained = tmp_path / "checkout", tmp_path / "retained"
    root.mkdir()
    retained.mkdir()
    (root / "tracked.json").write_bytes(b"tracked")
    (retained / "original.pdf").write_bytes(b"original")
    members = [
        {"path": "tracked.json", "sha256": digest(b"tracked"), "byteLength": 7},
        {
            "path": "output/evidence/original.pdf",
            "retainedPath": "original.pdf",
            "sha256": digest(b"original"),
            "byteLength": 8,
        },
    ]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"members": members}))
    return {
        "root": root,
        "retained_root": retained,
        "manifest": manifest,
        "manifest_sha256": digest(manifest.read_bytes()),
    }


def test_stages_verified_originals_and_reuses_exact_targets(inputs):
    first = staging.stage_evidence(**inputs)
    assert [r["action"] for r in first["members"]] == ["already-present", "staged"]
    assert (inputs["root"] / "output/evidence/original.pdf").read_bytes() == b"original"
    assert (inputs["retained_root"] / "original.pdf").read_bytes() == b"original"
    assert all(r["action"] == "already-present" for r in staging.stage_evidence(**inputs)["members"])


@pytest.mark.parametrize(
    "mutation",
    (
        "source-bytes",
        "source-size",
        "target-bytes",
        "source-link",
        "target-link",
        "parent-link",
        "manifest-pin",
        "missing-source",
    ),
)
def test_preflight_refuses_before_any_copy(inputs, mutation):
    root, retained = inputs["root"], inputs["retained_root"]
    source = retained / "original.pdf"
    if mutation == "source-bytes":
        source.write_bytes(b"XXXXXXXX")
    elif mutation == "source-size":
        source.write_bytes(b"X")
    elif mutation == "target-bytes":
        (root / "tracked.json").write_bytes(b"XXXXXXX")
    elif mutation == "source-link":
        source.rename(retained / "real.pdf")
        source.symlink_to(retained / "real.pdf")
    elif mutation == "target-link":
        (root / "tracked.json").unlink()
        (retained / "tracked.json").write_bytes(b"tracked")
        (root / "tracked.json").symlink_to(retained / "tracked.json")
    elif mutation == "parent-link":
        (root / "output").symlink_to(retained, target_is_directory=True)
    elif mutation == "manifest-pin":
        inputs["manifest_sha256"] = digest(b"wrong")
    elif mutation == "missing-source":
        source.unlink()
    with pytest.raises(ValueError):
        staging.stage_evidence(**inputs)
    assert not (root / "output/evidence/original.pdf").exists()


def test_missing_later_member_preflights_before_first_copy(inputs):
    document = json.loads(inputs["manifest"].read_bytes())
    document["members"].append(
        {"path": "output/evidence/missing.pdf", "retainedPath": "missing.pdf", "byteLength": 1, "sha256": digest(b"x")}
    )
    inputs["manifest"].write_text(json.dumps(document))
    inputs["manifest_sha256"] = digest(inputs["manifest"].read_bytes())
    with pytest.raises(ValueError, match="missing or differs"):
        staging.stage_evidence(**inputs)
    assert not (inputs["root"] / "output").exists()


def test_concurrent_target_is_not_overwritten(inputs, monkeypatch):
    original = staging.shutil.copyfile
    target = inputs["root"] / "output/evidence/original.pdf"

    def race(source, staged):
        result = original(source, staged)
        target.write_bytes(b"concurrent")
        return result

    monkeypatch.setattr(staging.shutil, "copyfile", race)
    with pytest.raises(FileExistsError):
        staging.stage_evidence(**inputs)
    assert target.read_bytes() == b"concurrent"
    assert not list(target.parent.glob(".atlas-audit-*"))
