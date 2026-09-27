import sys,json,hashlib,zipfile,importlib.util,collections,copy
from pathlib import Path
from dataclasses import replace
import pyarrow.parquet as pq
import rdflib
import argparse
parser=argparse.ArgumentParser(description='Bounded independent UMTHES provenance replay; no repository writes.')
parser.add_argument('--repo', type=Path, default=Path.cwd())
parser.add_argument('--output-dir', type=Path, required=True)
args=parser.parse_args()
root=args.repo.resolve(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('fidelity_probe_module',root/'tools/verify_atlas_source_fidelity.py'); v=importlib.util.module_from_spec(spec); sys.modules[spec.name]=v; spec.loader.exec_module(v)
selected,scoped=v.select_scope(['umthes-gemet-endpoints-2026-08-15'],v.SOURCES)
ctx=v.build_context(root/'output/atlas-3.1-umthes-2026-09-27/distribution',v.DEFAULT_SOURCE_ROOT,specs=selected,scoped_out_specs=scoped)
checks=v.run_checks(ctx); receipt=v._receipt(ctx,checks)
(out/'fresh-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('FRESH_CHECKS',[(c.name,c.passed,len(c.failures)) for c in checks],flush=True)
pair=ctx.pairs[0]; baseline=v._rdf_provenance_failures(pair)
flag_pair=replace(pair,spec=replace(pair.spec,rdf_source=replace(pair.spec.rdf_source,record_digest_is_native_payload_digest=True)))
flag_errors=v._rdf_provenance_failures(flag_pair)
print('PROVENANCE_COUNTS',len(baseline),len(flag_errors),flush=True)
rows=pq.read_table(root/'output/atlas-3.1-umthes-2026-09-27/parquet-view/tables/source-records.parquet').to_pylist()
print('ROW_KEYS',rows[0].keys(),flush=True)
def canon(x): return json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()
def digest(x): return 'sha256:'+hashlib.sha256(x).hexdigest()
raw_by_resource={}; descriptor_by_resource={}; all_triples=set(); discrepancies=[]; id_errors=[]; payload_hash_errors=[]; fidelity_errors=[]; rdf_parquet_errors=[]; rows_by_id={r['id']:r for r in rows}
with zipfile.ZipFile(root/'output/registry-real-data-sources/umthes-gemet-endpoints-2026-08-15.zip') as z:
 m=json.loads(z.read('manifest.json'))
 for d in m['records']:
  raw=z.read(d['member']); resource='https://sns.uba.de/umthes/'+d['legacyIri'].rsplit('/',1)[1]
  g=rdflib.Graph().parse(data=raw,format='nt'); subject=rdflib.URIRef(resource)
  raw_by_resource[resource]=(raw,g); descriptor_by_resource[resource]=d
  all_triples.update((str(s),str(p),str(o)) for s,p,o in g if isinstance(o,rdflib.URIRef))
  if digest(raw)!=d['sha256'] or len(raw)!=d['byteLength']: discrepancies.append(resource)
 targetless=[]; samples=[]
 for r in rows:
  p=json.loads(r['native_payload']); pd=digest(canon(p)); stored='sha256:'+r['source_digest'].hex(); target=r['represents_resource']
  if pd!=stored or r['native_payload']!=canon(p): payload_hash_errors.append(r['id'])
  if (pair.atlas.native_payloads.get(r['id'])!=p or pair.atlas.record_source_digests.get(r['id'])!=stored or pair.atlas.record_source_locators.get(r['id'])!=r['source_locator'] or pair.atlas.record_targets.get(r['id'])!=target):rdf_parquet_errors.append(r['id'])
  if target:
   raw,g=raw_by_resource[target]; d=descriptor_by_resource[target]; s=rdflib.URIRef(target)
   expected_labels=[]
   for pred,role in ((rdflib.SKOS.prefLabel,'preferred'),(rdflib.SKOS.altLabel,'alternate'),(rdflib.SKOS.hiddenLabel,'hidden')):
    expected_labels.extend({'language':o.language.lower(),'predicateIri':str(pred),'role':role,'value':str(o).strip()} for o in sorted(g.objects(s,pred),key=lambda o:(o.language.lower(),str(o).strip())))
   rel=sorted((str(pred),str(o)) for pred in (rdflib.SKOS.broader,rdflib.SKOS.narrower,rdflib.SKOS.related) for o in g.objects(s,pred) if isinstance(o,rdflib.URIRef) and str(o).startswith('https://sns.uba.de/umthes/'))
   expected={'definitions':[],'deprecated':any(str(o).lower()=='true' for o in g.objects(s,rdflib.OWL.deprecated)),'labels':expected_labels,'legacyIri':d['legacyIri'],'relations':[{'objectIri':o,'predicateIri':pred} for pred,o in rel],'responseByteLength':len(raw),'responseDigest':digest(raw),'retrievedAt':m['retrievedAt']}
   if p!=expected or r['source_locator']!=d['url']: fidelity_errors.append({'id':r['id'],'fields':[k for k in set(p)|set(expected) if p.get(k)!=expected.get(k)]})
   original_digest=digest(raw)
   if target.endswith('_00028834'):
    (out/'specimen.nt').write_bytes(raw); (out/'specimen-native.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n'); samples.append({'id':r['id'],'target':target,'payload_digest':pd,'response_digest':original_digest,'locator':r['source_locator']})
  else:
   targetless.append(r['id']); rel=p['publisherRelation']; original_digest=digest(canon(rel))
   triple=(rel['subjectIri'],rel['predicateIri'],rel['objectIri'])
   # Keep the actual Atlas namespace in this probe's evidence; source triple truth is independent.
   if triple not in all_triples or p['publisherRelationDigest']!=original_digest or r['source_locator']!='urn:ref:publisher-relation:'+original_digest[7:]: fidelity_errors.append({'id':r['id'],'relation':triple})
   if len(targetless)==1:
    (out/'relation-specimen.json').write_text(json.dumps({'id':r['id'],'native_payload':p,'source_digest':stored,'source_locator':r['source_locator'],'source_release':r['source_release'],'publisher_triple_present':triple in all_triples},indent=2)+'\n')
  basis={'nativePayloadDigest':pd,'sourceDigest':original_digest,'sourceLocator':r['source_locator'],'sourceRelease':r['source_release']}
  expected_id='urn:ref:atlas-source-record:'+hashlib.sha256(canon(basis)+b'\n').hexdigest()
  if r['id']!=expected_id:id_errors.append({'id':r['id'],'expected':expected_id})
 # Mutate one retained response digest, rehash own payload (thus self-consistent) and verify publisher inverse still refuses it.
 rid=samples[0]['id']; orig=pair.atlas.native_payloads[rid]
 mutation_results=[]
 for field,new in [('responseDigest','sha256:'+'0'*64),('responseByteLength',0),('retrievedAt','1900-01-01T00:00:00Z'),('legacyIri','http://data.uba.de/umt/_wrong')]:
  mutated=copy.deepcopy(orig); mutated[field]=new
  mutated_atlas=replace(pair.atlas,native_payloads={**pair.atlas.native_payloads,rid:mutated},record_source_digests={**pair.atlas.record_source_digests,rid:digest(canon(mutated))})
  failures=v._rdf_provenance_failures(replace(flag_pair,atlas=mutated_atlas))
  added=sorted(set(failures)-set(flag_errors))
  mutation_results.append({'field':field,'added_failures':added})
 evidence_rows=pq.read_table(root/'output/atlas-3.1-umthes-2026-09-27/parquet-view/tables/evidence-bindings.parquet').to_pylist()
 evidence_pins={'bindings':len(evidence_rows),'pins_matching_source_record_content_digest':sum(e['evidence_source_digest']==rows_by_id[e['source_record']]['content_digest'] for e in evidence_rows),'pins_matching_native_payload_digest':sum(e['evidence_source_digest']==rows_by_id[e['source_record']]['source_digest'] for e in evidence_rows)}
 result={'evidence_pins':evidence_pins,'fresh_failed_checks':[c.name for c in checks if not c.passed],'baseline_provenance_failures':len(baseline),'flag_only_provenance_failures':len(flag_errors),'flag_only_examples':flag_errors[:2],'rdf_parquet_errors':rdf_parquet_errors,'records':len(rows),'resource_records':len(rows)-len(targetless),'transformed_relation_records':len(targetless),'archive_manifest_errors':discrepancies,'payload_hash_errors':payload_hash_errors,'raw_source_fidelity_errors':fidelity_errors,'source_id_errors':id_errors,'samples':samples,'mutations':mutation_results,'declared_no_payload_digest_policy':[s.name for s in v.SOURCES if s.rdf_source and not s.rdf_source.record_digest_is_native_payload_digest]}
 (out/'probe-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='declared_no_payload_digest_policy'},indent=2),flush=True)
