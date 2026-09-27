"""Bounded PDF-source comparison. Exit 0 means diagnostics completed, not qualification."""
import argparse,collections,copy,dataclasses,datetime,hashlib,json,subprocess,sys,tempfile,uuid
from pathlib import Path
from collections.abc import Mapping
import pyarrow.parquet as pq
PINS={
 'classes':('output/registry-real-data-sources/ferc-class-types-january-2025.pdf','af632c9c6adbf0e7919d17e018b3a65078d0746bd1ab69a8d9fa65043720d688',193934,'https://www.ferc.gov/sites/default/files/2025-06/Document%20Class%20Types%20January%202025.pdf'),
 'dockets':('output/registry-real-data-sources/ferc-docket-prefix-june-2025.pdf','c32efae9f51a70b6f955821d2fb3d3025995ef0e17e57bf2d32dfa16c2508dcb',282729,'https://elibrary.ferc.gov/eLibrary/assets/docket-prefix.pdf'),
 'ua':('tests/fixtures/unified_agenda_codes/risc-preamble-202210.pdf','b7372fec456cf0c346bd23528ae227913e37f546bb1c03689da19ee6a44cb2a5',148467,'https://www.reginfo.gov/public/jsp/eAgenda/StaticContent/202210/RiscPreamble.pdf')}
UNITS={'classes':'ferc-document-class-types','dockets':'ferc-docket-prefixes','ua':'unified-agenda-legal-authority-citation-types'}
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--view',type=Path,default=Path('output/atlas-3.1-omitted-vocabularies-2026-09-27/parquet-view'));a=parser.parse_args();root=a.repo.resolve();out=a.output_dir.resolve();view=a.view if a.view.is_absolute() else root/a.view
if out.is_relative_to(root):raise ValueError('Diagnostic output must be outside the checkout')
out.mkdir(parents=True,exist_ok=True)
def save(name,obj): (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def digest(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def plain(x):
 if dataclasses.is_dataclass(x):return {f.name:plain(getattr(x,f.name)) for f in dataclasses.fields(x)}
 if isinstance(x,Mapping):return {str(k):plain(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(plain,x))
 if isinstance(x,Path):return str(x)
 return x
pin_results={}; stale_pin_mutations=[]
for key,(path,sha,size,url) in PINS.items():
 raw=(root/path).read_bytes();assert digest(raw)==sha and len(raw)==size,(key,'pin mismatch')
 stale_pin_mutations.append({'source':key,'changed_last_byte_refused':digest(raw[:-1]+bytes([raw[-1]^1]))!=sha})
 pin_results[key]={'path':path,'sha256':sha,'byte_length':size,'source_url':url}
for kind,base in [('classes','class'),('dockets','docket')]:
 for mode,suffix in [('-layout','txt'),('-bbox-layout','html')]:subprocess.run(['pdftotext',mode,str(root/PINS[kind][0]),str(out/f'{base}-{mode[1:].removesuffix("-layout") if mode=="-bbox-layout" else "layout"}.{suffix}')],check=True)
subprocess.run(['pdftotext','-f','18','-l','19','-layout',str(root/PINS['ua'][0]),str(out/'ua-glossary.txt')],check=True)
subprocess.run([sys.executable,str(Path(__file__).with_name('extract_pdf_tables.py')),'--output-dir',str(out)],check=True)
e=json.loads((out/'independent-extraction.json').read_text())
# Expected content is complete before importing either producer loader.
expected={}
for kind in ('classes','dockets','ua'):
 key=UNITS[kind];url=PINS[kind][3];rows=[]
 inputs=e[kind] if kind!='ua' else [{'value':k,'definition':e['ua'][k]} for k in ('U.S.C.','Pub. L.','E.O.')]
 for i,r in enumerate(inputs):
  if kind=='classes':
   n=dict(r['native']);n['text']=' '.join(n[f] for f in ('category','library','classification','type_description'));label=n['type_description'];definition=None;notations=[];status=None
  elif kind=='dockets':
   n=dict(r['native']);label=n['definition'];definition=label;notations=[n['prefix']];status=n['status']
  else:
   label=r['value'];definition=r['definition'];notations=[label];status=None
   n={'value':label,'identifier':{'value':label,'kind':'legalAuthorityCitationType','authority_uri':'https://www.reginfo.gov/','source_uri':url,'observed_at':'2026-08-03T19:13:31Z','effective_at':None,'source_digest':'sha256:'+PINS[kind][1]}}
  n.update(sourceArtifact=url,sourceMedium='pdf')
  path=f'$.legalAuthorityCitationTypes[{i}]' if kind=='ua' else f'$.rows[{i}]'
  token='unified-agenda-legal-authority' if kind=='ua' else key;stamp='2026-08-03T19:13:31Z' if kind=='ua' else '2026-08-03T19:18:32Z'
  seed=canon({'source':url,'path':path,'notations':notations,'identityHint':label});bits=int.from_bytes(hashlib.sha256(seed).digest(),'big')>>(256-74);ms=int(datetime.datetime.fromisoformat(stamp.replace('Z','+00:00')).timestamp()*1000)
  ident=str(uuid.UUID(int=(ms<<80)|(7<<76)|((bits>>62)<<64)|(2<<62)|(bits&((1<<62)-1))))
  rows.append({'iri':f'urn:ref:source-concept:v2:{token}:{ident}','label':label,'definition':definition,'notations':notations,'status':status,'source_path':path,'native_payload':n,'source_locator':url,'source_digest':'sha256:'+PINS[kind][1]})
 expected[key]=rows
save('independent-expected.json',expected)
from refspec.atlas import v3_registry_codes as producer
with tempfile.TemporaryDirectory(dir=out) as temp:
 rels=(*producer._load_ferc(root),*producer._load_unified_agenda(root,Path(temp)))
 observed={r.key:plain(r) for r in rels if r.key in UNITS.values()}
save('producer-observed.json',observed)
view_manifest=json.loads((view/'view-manifest.json').read_text());member_checks=[]
for member in view_manifest['members']:
 body=(view/member['path']).read_bytes();ok=len(body)==member['byteLength'] and 'sha256:'+digest(body)==member['sha256'];member_checks.append({'path':member['path'],'byte_length':len(body),'sha256':digest(body),'pin_matches':ok});assert ok,member['path']
resources={r['id']:r for r in pq.read_table(view/'tables/resources.parquet').to_pylist()};sources={r['id']:r for r in pq.read_table(view/'tables/source-records.parquet').to_pylist()};labels=collections.defaultdict(list)
for r in pq.read_table(view/'tables/labels.parquet').to_pylist():labels[r['resource']].append(r)
artifact={};emission_failures=[];payload_digest_failures=[];record_identity_failures=[]
for key,release in observed.items():
 rows=[]
 for ordinal,r in enumerate(release['resources']):
  if r['iri'] not in resources:emission_failures.append((key,ordinal,'missing_resource'));continue
  resource=resources[r['iri']];source=sources[resource['source_record']];lab=labels[r['iri']]
  assert len(lab)==1 and lab[0]['label_role']=='preferred' and lab[0]['language']=='en',(key,ordinal,'label shape')
  payload=json.loads(source['native_payload']);pd=digest(canon(payload))
  record_basis={'nativePayloadDigest':'sha256:'+pd,'sourceDigest':r['source_digest'],'sourceLocator':r['source_locator'],'sourceRelease':release['source_release_iri']}
  if source['id']!='urn:ref:atlas-source-record:'+digest(canon(record_basis)+b'\n') or source['source_release']!=release['source_release_iri']:record_identity_failures.append(source['id'])
  if source['native_payload']!=canon(payload) or source['source_digest'].hex()!=pd:payload_digest_failures.append(source['id'])
  item={'iri':resource['id'],'label':lab[0]['value'],'definition':resource['definition'],'notations':resource['notations'] or [],'status':resource['record_status'],'source_path':r['labels'][0]['source_path'],'native_payload':payload,'source_locator':source['source_locator'],'source_digest':r['source_digest']}
  # source_path and upstream digest come from producer observations, not Parquet columns.
  producer_item={'iri':r['iri'],'label':r['labels'][0]['value'],'definition':r['definition'],'notations':r['notations'],'status':r['status'],'source_path':r['labels'][0]['source_path'],'native_payload':r['native_payload'],'source_locator':r['source_locator'],'source_digest':r['source_digest']}
  if item!=producer_item:emission_failures.append({'key':key,'row':ordinal,'observed':item,'producer':producer_item})
  rows.append(item)
 artifact[key]=rows
save('artifact-observed.json',artifact)
def compare(want,got):
 failures=[]
 for key in sorted(set(want)|set(got)):
  a=want.get(key,[]);b=got.get(key,[])
  if len(a)!=len(b):failures.append({'unit':key,'kind':'row_count','expected':len(a),'actual':len(b)})
  for i,(x,y) in enumerate(zip(a,b)):
   for field in sorted(set(x)|set(y)):
    if x.get(field)!=y.get(field):failures.append({'unit':key,'row':i,'field':field,'expected':x.get(field),'actual':y.get(field)})
 return failures
failures=compare(expected,artifact)
base={canon(x) for x in failures};mutations=[]
cases=[('docket_status','ferc-docket-prefixes',77,'status','active'),('docket_continuation','ferc-docket-prefixes',78,'definition','Certificates for Small Independent Natural Gas Producers &'),('docket_notation','ferc-docket-prefixes',0,'notations',['ZZZ']),('class_classification','ferc-document-class-types',0,'native_payload.classification','Wrong Class'),('ua_definition','unified-agenda-legal-authority-citation-types',0,'definition','Wrong definition'),('ua_identity','unified-agenda-legal-authority-citation-types',0,'iri','urn:wrong')]
for name,key,i,field,value in cases:
 changed=copy.deepcopy(artifact)
 if '.' in field:outer,inner=field.split('.');changed[key][i][outer][inner]=value
 else:changed[key][i][field]=value
 added=[x for x in compare(expected,changed) if canon(x) not in base];assert added,name;mutations.append({'name':name,'added_failures':added})
for name,key in [('dropped_discontinued','ferc-docket-prefixes'),('dropped_citation','unified-agenda-legal-authority-citation-types')]:
 changed=copy.deepcopy(artifact);changed[key].pop();added=[x for x in compare(expected,changed) if canon(x) not in base];assert added;mutations.append({'name':name,'added_failures':added})
changed=copy.deepcopy(artifact);dup=[i for i,r in enumerate(changed['ferc-document-class-types']) if r['label']=='Annual Charges Report'];changed['ferc-document-class-types'][dup[0]]['native_payload']['library']=changed['ferc-document-class-types'][dup[1]]['native_payload']['library'];added=[x for x in compare(expected,changed) if canon(x) not in base];assert added;mutations.append({'name':'duplicate_label_library_swap','added_failures':added})
changed=copy.deepcopy(artifact);changed['unified-agenda-legal-authority-citation-types'].append({**changed['unified-agenda-legal-authority-citation-types'][0],'label':'CFR'});added=[x for x in compare(expected,changed) if canon(x) not in base];assert added;mutations.append({'name':'extra_unselected_glossary_entry','added_failures':added})
manifest=(view/'view-manifest.json').read_bytes();distrib=view.parent/'distribution/atlas-manifest.json'
receipt={'qualification':'bounded comparison; FERC class/type source reading unresolved','source_revision':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'source_pins':pin_results,'view_member_checks':member_checks,'stale_pin_mutations':stale_pin_mutations,'source_record_identity_failures':record_identity_failures,'view_manifest_sha256':digest(manifest),'distribution_manifest_sha256':digest(distrib.read_bytes()) if distrib.exists() else None,'counts':{k:len(v) for k,v in artifact.items()},'unexpected_artifact_resources':sorted(set(resources)-{r['iri'] for rows in artifact.values() for r in rows}),'emission_failures':emission_failures,'payload_digest_failures':payload_digest_failures,'source_comparison_failures':failures,'mutations':mutations,'limits':['source_path and upstream digest comparison use observed loader fields because the Parquet view does not carry those fields directly','SourceRecord identity is recomputed from observed payload plus authenticated upstream input; that is identity consistency, not independent payload-field fidelity','The geometric PDF text extraction includes text that may be invisible in the rendered page; no such discrepancy is silently filtered','No generic audit adapter was installed; full source-fidelity qualification is not claimed']}
save('comparison-receipt.json',receipt);print(json.dumps({'counts':receipt['counts'],'source_failure_fields':[(f['unit'],f.get('row'),f.get('field')) for f in failures],'emission_failures':len(emission_failures),'payload_digest_failures':len(payload_digest_failures),'mutation_cases':len(mutations)},indent=2))
