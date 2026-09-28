"""Cold, bounded A/B: identical packs and gates, original facts vs shared graph."""
import gc
import json
import resource
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(root / "bindings/atlas/3.1/tools"), str(root / "tests")]
import validate as v
from atlas_asserted_facts_oracle import _AssertedFacts as FrozenFacts

mode = sys.argv[1]
path = root / "output/atlas-3.1-umthes-2026-09-27/distribution"
if mode == "old":
    readers = {}
    class OriginalFacts(FrozenFacts):
        @classmethod
        def for_graph(cls, graph):
            if graph.identifier not in readers:
                readers[graph.identifier] = cls(graph.identifier)
            return readers[graph.identifier]
    v._AssertedFacts = OriginalFacts
    original_observe = v._AssertedPlacementObservation.observe
    def observe(self, subject, predicate, obj):
        original_observe(self, subject, predicate, obj)
        self.facts.observe(subject, predicate, obj)
    v._AssertedPlacementObservation.observe = observe

manifest = json.loads((path / "atlas-manifest.json").read_text())
ids = v._check_pack_manifest(manifest)
placement = v._AssertedPlacementObservation(ids["asserted"], v._projection_only_predicates())
digests = v._AssertedNodeDigests(ids["asserted"])
start = time.perf_counter()
dataset, graphs = v._parse_packed_dataset(path, manifest, ids, asserted_placement=placement, node_digests=digests)
parsed = time.perf_counter()
asserted = graphs["asserted"]
inventory = v._check_graph_roles(graphs, asserted_placement=placement)
accounting = json.loads((path / "atlas-source-accounting.json").read_text())
placed = time.perf_counter()
v._check_profile_conformance(asserted, inventory)
v._check_identifier_uniqueness(asserted, inventory)
v._check_release_membership(asserted, inventory)
v._check_label_integrity(asserted, inventory)
v._check_evidence_bindings(asserted, inventory, node_digests=digests)
v._validate_assertions(asserted, inventory)
v._check_source_accounting(asserted, accounting, inventory)
finished = time.perf_counter()
print(json.dumps({"mode": mode, "distributionId": manifest["distributionId"], "quads": sum(len(g) for g in graphs.values()), "assertedSubjects": sum(len(s) for s in inventory.asserted_by_carrier.values()), "parseSeconds": parsed-start, "placementSeconds": placed-parsed, "gatesSeconds": finished-placed, "elapsedSeconds": finished-start, "peakRssBytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "peakMetric": "macOS getrusage ru_maxrss (RSS, not physical footprint)", "gates": ["profile", "identifier-uniqueness", "release-membership", "label-integrity", "evidence-bindings", "assertions", "source-accounting"]}))
