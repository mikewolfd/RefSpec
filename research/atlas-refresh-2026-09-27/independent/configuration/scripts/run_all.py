"""Run the retained failure-reproduction probes and record their exact evidence."""

from pathlib import Path
import sys

import sys

sys.dont_write_bytecode = True
from _probe import arguments, write_json

args = arguments()
baseline = args.baseline_dir.resolve() if args.baseline_dir else None
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

scripts = Path(__file__).resolve().parent
names = ["check_config.py", "check_lc_cache.py", "check_agency_identity.py", "check_repairs.py", "capture_context.py"]
results = []
for name in names:
    result = subprocess.run(
        [sys.executable, str(scripts / name), "--repo", str(args.repo), "--output-dir", str(args.output_dir)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    results.append(
        {
            "script": name,
            "exitCode": result.returncode,
            "stdoutBytes": len(result.stdout.encode()),
            "stderr": result.stderr,
        }
    )
    print(f"{name}: exit {result.returncode}")
    if result.returncode:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
comparison = []
for name in ["config.json", "lc-cache.json", "agency-identity.json", "repair-probe.json"]:
    generated = args.output_dir / name
    if baseline is not None:
        original = baseline / name
        comparison.append(
            {
                "file": name,
                "baselineSha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                "jsonEqual": json.loads(generated.read_text()) == json.loads(original.read_text()),
            }
        )
revision = subprocess.run(
    ["git", "-C", str(args.repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
).stdout.strip()
receipt = {
    "checkedAtUtc": datetime.now(timezone.utc).isoformat(),
    "sourceRevision": revision,
    "meaning": "Exit zero means historical failure conditions reproduced; this is not an Atlas fidelity pass.",
    "scripts": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(scripts.glob("*.py"))},
    "results": results,
    "originalDiagnosticComparison": comparison,
    "allPassed": all(r["exitCode"] == 0 for r in results) and all(r["jsonEqual"] for r in comparison),
}
write_json(args.output_dir, "replay.json", receipt)
raise SystemExit(0 if receipt["allPassed"] else 1)
