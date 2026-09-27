"""Stage separately pinned agency audit evidence from a local retained snapshot.

Preflight every member before copying. Existing checkout files must already
match; missing originals are copied from retainedPath without overwriting data.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from atlas_independent_agency import child, pinned_json
from fetch_pinned_inputs import is_current


def _safe_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"evidence path must be relative and contained: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"evidence path contains a symlink: {current}")
        if current != root / path and current.exists() and not current.is_dir():
            raise ValueError(f"evidence parent is not a directory: {current}")
    return child(root, relative)


def stage_evidence(*, root: Path, retained_root: Path, manifest: Path, manifest_sha256: str) -> dict:
    if root.is_symlink() or retained_root.is_symlink():
        raise ValueError("evidence roots must not be symlinks")
    root = root.resolve(strict=True)
    retained_root = retained_root.resolve(strict=True)
    document = pinned_json(manifest, manifest_sha256)
    planned = []
    members = document["members"]
    if not isinstance(members, list) or not members:
        raise ValueError("audit evidence manifest must contain members")
    seen = set()
    for member in members:
        relative = member["path"]
        if relative in seen:
            raise ValueError(f"audit evidence manifest repeats path: {relative}")
        seen.add(relative)
        digest = member["sha256"]
        size = member["byteLength"]
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"invalid evidence digest: {relative}")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError(f"invalid evidence size: {relative}")
        entry = {"bytes": size, "sha256": digest.removeprefix("sha256:")}
        target = _safe_path(root, relative)
        if target.exists():
            if not is_current(target, entry):
                raise ValueError(f"existing evidence differs; refusing overwrite: {relative}")
            planned.append((member, entry, target, None))
            continue
        if not member.get("retainedPath"):
            raise ValueError(f"missing evidence has no retainedPath: {relative}")
        source = _safe_path(retained_root, member["retainedPath"])
        if not is_current(source, entry):
            raise ValueError(f"retained evidence is missing or differs: {relative}")
        planned.append((member, entry, target, source))

    results = []
    for member, entry, target, source in planned:
        if source is not None:
            # Check paths again after preflight; source bytes are authenticated
            # again after copying, and os.link refuses a newly existing target.
            _safe_path(root, member["path"])
            _safe_path(retained_root, member["retainedPath"])
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix=".atlas-audit-", dir=target.parent, delete=False) as stream:
                staged = Path(stream.name)
            try:
                shutil.copyfile(source, staged)
                if not is_current(staged, entry):
                    raise ValueError(f"retained evidence changed during staging: {member['path']}")
                os.link(staged, target)
            finally:
                staged.unlink(missing_ok=True)
        results.append(
            {
                "path": member["path"],
                "sha256": member["sha256"],
                "byteLength": member["byteLength"],
                "action": "staged" if source is not None else "already-present",
            }
        )
    return {
        "type": "AtlasAuditEvidenceStaging",
        "manifestSha256": manifest_sha256,
        "status": "passed",
        "members": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--retained-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    result = stage_evidence(
        root=args.root, retained_root=args.retained_root, manifest=args.manifest, manifest_sha256=args.manifest_sha256
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
