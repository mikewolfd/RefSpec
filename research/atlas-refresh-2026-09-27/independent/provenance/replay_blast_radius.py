import importlib.util,sys,inspect,json,hashlib,collections
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Bounded authenticated reader probes; no full-source audit.')
parser.add_argument('--repo', type=Path, default=Path.cwd())
parser.add_argument('--output-dir', type=Path, required=True)
args=parser.parse_args()
root=args.repo.resolve();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
s=importlib.util.spec_from_file_location('fidelity_radius',root/'tools/verify_atlas_source_fidelity.py');v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
rows=[]
for spec in v.SOURCES:
 if spec.rdf_source and not spec.rdf_source.record_digest_is_native_payload_digest:
  reader=v._PUBLISHER_READERS.get(spec.reader); src=inspect.getsource(reader) if reader else ''
  rows.append({'name':spec.name,'kind':spec.kind,'reader':spec.reader,'function':reader.__name__ if reader else None,'explicit_false_reader_flag':'source_digest_is_native_payload_digest=False' in src,'raw_digest_assignment':'source_digest=pin.sha256' in src})
selected=[]
for name in ('eurovoc-mesh-alignment-20171215','federal-register-api-topics-2026-08-03','gcmd-science-keywords-24-4','billstatus-bill-types','govinfo-collections','gao-published-topics-capture-subset-2026-09-01'):
 spec=next(s for s in v.SOURCES if s.name==name)
 payloads={pin:v.read_verified_file_pin(v._resolve_source_pin(v.DEFAULT_SOURCE_ROOT,pin),expected_sha256=pin.sha256,expected_byte_length=pin.byte_length,logical_path=pin.path) for pin in spec.inputs}
 publisher=v._PUBLISHER_READERS[spec.reader](spec,payloads)
 if spec.kind=='mapping':
  ev=[e for es in publisher.expected_mapping_evidence.values() for e in es]
  mismatches=sum(e.source_digest!=v._canonical_json_digest(e.native_payload) for e in ev)
  selected.append({'name':name,'kind':spec.kind,'evidence_rows':len(ev),'source_digest_differs_payload':mismatches,'sample':{'expected_source_digest':ev[0].source_digest,'expected_native_payload_digest':v._canonical_json_digest(ev[0].native_payload),'native_payload':ev[0].native_payload}})
 else:
  mismatches=[]
  for iri,p in publisher.expected_native_payloads.items():
   expected=publisher.resource_input_digest_values.get(iri) or next(iter(publisher.resource_input_digests.get(iri,())))
   if expected!=v._canonical_json_digest(p):mismatches.append(iri)
  selected.append({'name':name,'kind':spec.kind,'resources':len(publisher.concepts),'retained_payloads':len(publisher.expected_native_payloads),'reader_source_digest_is_native_payload_digest':publisher.source_digest_is_native_payload_digest,'source_digest_differs_payload':len(mismatches)})
result={'declarations_without_policy_flag':len(rows),'by_kind':dict(collections.Counter(r['kind'] for r in rows)),'explicit_reader_false_declarations':[r for r in rows if r['explicit_false_reader_flag']],'bounded_reader_probes':selected}
(out/'blast-radius-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
