"""Shared argument handling for read-only Atlas diagnostic probes."""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(os.environ.get("REFSPEC_REPO", Path.cwd())),
        help="RefSpec checkout (default: REFSPEC_REPO or cwd)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Diagnostic output directory outside the checkout"
    )
    parser.add_argument(
        "--baseline-dir", type=Path, help="Optional original diagnostic receipt directory for run_all.py"
    )
    args = parser.parse_args()
    args.repo = args.repo.resolve()
    args.output_dir = args.output_dir.resolve()
    if not (args.repo / "tools/verify_atlas_source_fidelity.py").is_file():
        parser.error("--repo must name a RefSpec checkout")
    if args.output_dir.is_relative_to(args.repo):
        parser.error("--output-dir must be outside --repo to keep the checkout read-only")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(args.repo), str(args.repo / "src")]
    os.chdir(args.repo)
    return args


def write_json(output_dir, name, value):
    (output_dir / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(value, indent=2))
