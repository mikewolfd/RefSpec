import runpy,copy,json,gzip,hashlib
from dataclasses import replace
from pathlib import Path
s=runpy.run_path(str(Path(__file__).with_name('replay_provenance.py')))
v=s['v']; pair=s['pair']; ctx=s['ctx']; digest=s['digest']; canon=s['canon']; rows=s['rows']; raw=s['raw_by_resource'];out=s['out']
errors=[]; trans={'fromPredicate':v.SKOS+'related','reason':'SKOS-S27-hierarchy-path','rule':'preserveAuthoredAssociationOutsideSkosProjection','toPredicate':v.ATLAS+'thesaurusRelated'}
relations=[r for r in rows if not r['represents_resource']]
for r in relations:
 p=json.loads(r['native_payload']); relation=p['publisherRelation']; expected=digest(raw[relation['subjectIri']][0])
 if relation.get('responseDigest')!=expected: errors.append({'id':r['id'],'error':'responseDigest'})
 if p['editorialTransformation']!=trans: errors.append({'id':r['id'],'error':'transformation'})
print('DIRECT_RELATION_FIELDS',len(relations),errors,flush=True)
adjacency={}
for subject,predicate,obj in s['all_triples']:
 if subject not in raw or obj not in raw:continue
 if predicate==v.SKOS+'broader':adjacency.setdefault(subject,set()).add(obj)
 if predicate==v.SKOS+'narrower':adjacency.setdefault(obj,set()).add(subject)
def reaches(a,b):
 seen=set();todo=list(adjacency.get(a,()))
 while todo:
  n=todo.pop()
  if n==b:return True
  if n not in seen:seen.add(n);todo.extend(adjacency.get(n,()))
 return False
expected_relations={}
for subject,predicate,obj in s['all_triples']:
 if subject in raw and obj in raw and predicate==v.SKOS+'related' and (reaches(subject,obj) or reaches(obj,subject)):
  pr={'subjectIri':subject,'predicateIri':predicate,'objectIri':obj,'responseDigest':digest(raw[subject][0])}
  inner=digest(canon(pr));expected_relations[inner]={'editorialTransformation':trans,'publisherRelation':pr,'publisherRelationDigest':inner}
observed_relations={json.loads(r['native_payload'])['publisherRelationDigest']:json.loads(r['native_payload']) for r in relations}
relation_reconstruction={'expected_count':len(expected_relations),'observed_count':len(observed_relations),'exact_match':expected_relations==observed_relations}
print('RELATION_RECONSTRUCTION',relation_reconstruction,flush=True)
def make_ctx(a):
 return replace(ctx,pairs=(replace(pair,atlas=a),),atlas_views=((pair.spec,a),),specs=(pair.spec,),comparison_claim_scope_cache={})
base_checks=v.run_checks(make_ctx(pair.atlas)); base={c.name:set(c.failures) for c in base_checks}
(out/'relation-baseline-checks.json.gz').write_bytes(gzip.compress((json.dumps([c.as_dict() for c in base_checks],indent=2,sort_keys=True)+'\n').encode(),mtime=0))
record=relations[0]['id']; original=pair.atlas.native_payloads[record]; cases=[]
for name in ('responseDigest','editorialReason','relationObject'):
 p=copy.deepcopy(original)
 if name=='responseDigest':p['publisherRelation']['responseDigest']='sha256:'+'0'*64
 elif name=='editorialReason':p['editorialTransformation']['reason']='invented'
 else:p['publisherRelation']['objectIri']='https://sns.uba.de/umthes/_wrong'
 inner=digest(canon(p['publisherRelation']));p['publisherRelationDigest']=inner
 a=replace(pair.atlas,native_payloads={**pair.atlas.native_payloads,record:p},record_source_digests={**pair.atlas.record_source_digests,record:digest(canon(p))},record_source_locators={**pair.atlas.record_source_locators,record:'urn:ref:publisher-relation:'+inner[7:]})
 checks=v.run_checks(make_ctx(a)); added={c.name:sorted(set(c.failures)-base[c.name]) for c in checks if set(c.failures)-base[c.name]}
 removed={c.name:sorted(base[c.name]-set(c.failures)) for c in checks if base[c.name]-set(c.failures)}
 (out/f'relation-{name}-checks.json.gz').write_bytes(gzip.compress((json.dumps({'changed_record':record,'original_payload':original,'changed_payload':p,'changed_locator':a.record_source_locators[record],'changed_source_digest':a.record_source_digests[record],'checks':[c.as_dict() for c in checks]},indent=2,sort_keys=True)+'\n').encode(),mtime=0))
 cases.append({'mutation':name,'new_failures':added,'removed_failures':removed,'identical_failure_sets':all(set(c.failures)==base[c.name] for c in checks)})
result={'uses_unmodified_source_spec':pair.spec==next(x for x in v.SOURCES if x.name==pair.spec.name),'record_digest_policy_flag':pair.spec.rdf_source.record_digest_is_native_payload_digest,'independent_relation_reconstruction':relation_reconstruction,'independent_raw_relation_fields_checked':len(relations),'independent_raw_relation_field_errors':errors,'baseline_failures':{c.name:len(c.failures) for c in base_checks if c.failures},'mutations':cases,'expected_relation_payloads':len(pair.publisher.expected_relation_payloads)}
(out/'relation-mutation-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2),flush=True)
