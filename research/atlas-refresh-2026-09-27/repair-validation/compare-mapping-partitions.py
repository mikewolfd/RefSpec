"""Authenticate and compare sorted RDF bytes before and after pack partitioning."""
import contextlib
import hashlib
import heapq
import json
from pathlib import Path
from backports import zstd

baseline = Path('/Users/mikewolfd/Work/spicy-stack/RefSpec/output/atlas-3.1-full-2026-08-21d')
fresh = Path('output/atlas-3.1-full-2026-09-27-repaired/distribution')
old_manifest = json.loads((baseline / 'atlas-manifest.json').read_text())
new_manifest = json.loads((fresh / 'atlas-manifest.json').read_text())
results = []

def verified_lines(root, pack):
    path = root / pack['path']
    with path.open('rb') as raw:
        actual = 'sha256:' + hashlib.file_digest(raw, 'sha256').hexdigest()
    assert actual == pack['transport']['digest'], path
    digest = hashlib.sha256()
    count = length = 0
    previous = None
    with zstd.open(path, 'rb') as stream:
        for line in stream:
            assert previous is None or previous < line, path
            previous = line
            digest.update(line)
            count += 1
            length += len(line)
            yield line
    assert count == pack['content']['quadCount'], path
    assert length == pack['content']['byteLength'], path
    assert 'sha256:' + digest.hexdigest() == pack['content']['digest'], path

for key in ('fast-lcsh-adopted-2026-08-15', 'lcsh-external-links-mappings-2026-08-15'):
    old = next(p for p in old_manifest['packs'] if p['path'] == f'packs/mappings/{key}.nq.zst')
    new = [p for p in new_manifest['packs'] if p['path'].startswith(f'packs/mappings/{key}/')]
    assert len(new) == 16
    before_hash = hashlib.sha256()
    before_count = before_bytes = 0
    for line in verified_lines(baseline, old):
        before_hash.update(line)
        before_count += 1
        before_bytes += len(line)
    after_hash = hashlib.sha256()
    after_count = after_bytes = 0
    previous = None
    with contextlib.ExitStack() as stack:
        streams = [stack.enter_context(contextlib.closing(verified_lines(fresh, p))) for p in new]
        for line in heapq.merge(*streams):
            assert previous is None or previous < line, key
            previous = line
            after_hash.update(line)
            after_count += 1
            after_bytes += len(line)
    assert (before_hash.digest(), before_count, before_bytes) == (after_hash.digest(), after_count, after_bytes), key
    results.append({'unit': key, 'status': 'passed', 'canonicalContentDigest': 'sha256:' + after_hash.hexdigest(), 'quadCount': after_count, 'byteLength': after_bytes, 'beforePackCount': 1, 'afterPackCount': len(new), 'transportAndContentPinsChecked': True})
result = {'status': 'passed', 'scope': 'exact authenticated sorted RDF bytes across mapping repartitioning; not complete artifact qualification', 'comparisons': results, 'cost': 'O(B log p) merge work, bounded to one current line per pack plus reader buffers'}
(fresh.parent / 'mapping-partition-equivalence.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
