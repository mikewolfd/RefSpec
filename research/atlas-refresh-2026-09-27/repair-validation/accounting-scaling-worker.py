import sys,time,json,dataclasses,tempfile,hashlib,tracemalloc
from pathlib import Path
root=Path.cwd()
sys.path.insert(0,str(root))
sys.path.insert(0,str(root/'tests'));sys.path.insert(0,str(root/'tools'))
import test_generate_atlas_v3_full as fixture
import atlas_builder_accounting_oracle as oracle
g=fixture.generator
axis,scale,method=sys.argv[1],int(sys.argv[2]),sys.argv[3]
with tempfile.TemporaryDirectory() as tmp:
 _,template=fixture._compiled_mapping_case(Path(tmp))
 count=128*scale if axis=='records' else 128
 releases=[]
 for ri in range(scale if axis=='releases' else 1):
  mappings=[]
  for index in range(count):
   original=template.mappings[0];subject=original.subject+f':{ri}:{index}'
   evidence=original.evidence[0];payload=dict(evidence.native_payload)
   payload['subjectIri']=subject
   payload['mappingTripleDigest']=g.mapping_triple_digest(subject_iri=subject,predicate_iri=original.predicate,object_iri=original.object)
   mappings.append(dataclasses.replace(original,subject=subject,evidence=(dataclasses.replace(evidence,native_payload=payload),)))
  releases.append(dataclasses.replace(template,key=template.key+f'-{ri}',source_release_iri=template.source_release_iri+f':{ri}',mappings=tuple(mappings)))
 g._STREAM_CONSTRUCTION_BATCH_SIZE=32
 calls=[];original_graph=g._expected_mapping_asserted_graph
 def measured(releases):
  graph=original_graph(releases);calls.append({'claims':sum(len(r.mappings) for r in releases),'triples':len(graph)})
  return graph
 if method=='compact':g._expected_mapping_asserted_graph=measured
 else:oracle._expected_mapping_asserted_graph=measured
 tracemalloc.start();wall=time.perf_counter();cpu=time.process_time()
 result=(g if method=='compact' else oracle)._mapping_accounting_expectations(releases)
 elapsed=time.perf_counter()-wall;cpu_elapsed=time.process_time()-cpu;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
 payload=json.dumps({k:{r:sorted(a) for r,a in v.items()} for k,v in result.items()},sort_keys=True,separators=(',',':')).encode()
 print(json.dumps({'axis':axis,'scale':scale,'method':method,'records':count*len(releases),'releases':len(releases),'accountingWallSeconds':elapsed,'accountingCpuSeconds':cpu_elapsed,'tracedPeakBytes':peak,'expectedGraphCalls':len(calls),'maximumExpectedGraphClaims':max(c['claims'] for c in calls),'maximumExpectedGraphTriples':max(c['triples'] for c in calls),'accountingDigest':'sha256:'+hashlib.sha256(payload).hexdigest(),'compactSourceRecordEntries':sum(len(v) for v in result.values()),'derivationMeasured':False}))
