"""Run from the repository root: .venv/bin/python output/atlas-audit-simplification/benchmark_sample_scan.py"""
import hashlib
import json
import sys
import tempfile
import time
from itertools import islice
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(root), str(root / 'tests')]
import test_atlas_parquet_sample_scan as test

pack = root / 'output/atlas-3.1-umthes-2026-09-27/distribution/packs/sources/umthes-gemet-endpoints-2026-08-15/all.nq.zst'
with test.generator.zstd.open(pack, 'rt') as stream:
    lines = list(islice(stream, 50_000))
identities = list(dict.fromkeys(line.partition(' ')[0][1:-1] for line in lines))[:45]
subjects = [(identity, test.CompactRecordRole.RESOURCE) for identity in identities]
report = {
    'command': '.venv/bin/python output/atlas-audit-simplification/benchmark_sample_scan.py',
    'source': str(pack.relative_to(root)),
    'lines': len(lines),
    'subjects': len(subjects),
    'selection': 'First 50,000 retained canonical lines; first 45 complete Resource subject groups',
    'historicalInMemorySelectorSeconds': {'old': 0.4584289999984321, 'new': 0.07912816700263647},
    'implementation': 'One RDF pass into temporary per-sample files; one sample Dataset at a time; bounded expected-row list',
    'limitations': 'Bounded warm local-file comparison, not a full build or full-scale memory test. Includes row parsing and reconstruction.',
}
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'sample.nq'
    path.write_text(''.join(lines))
    report['bytes'] = path.stat().st_size
    report['selectedInputSha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    spool = test.spool_at(path)
    rows, seconds = {}, {}
    for name, call in (
        ('old', lambda: [test.old_independent_row_for_subject(spool, *subject) for subject in subjects]),
        ('new', lambda: test.new_rows(spool, subjects)),
    ):
        started = time.perf_counter()
        rows[name] = call()
        seconds[name] = time.perf_counter() - started
    assert rows['old'] == rows['new']
    report.update(seconds=seconds, exactRowAgreement=True, speedup=seconds['old'] / seconds['new'])
output = Path(__file__).with_name('sample-scan-benchmark.json')
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
