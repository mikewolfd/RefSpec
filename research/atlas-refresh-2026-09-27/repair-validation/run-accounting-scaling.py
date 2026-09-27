import subprocess,json,re
from pathlib import Path
out=Path('output/atlas-refresh-repair-validation');results=[]
for axis in ('records','releases'):
 for scale in (1,2,4):
  pair=[]
  for method in ('old','compact'):
   run=subprocess.run(['/usr/bin/time','-l','.venv/bin/python',str(Path(__file__).with_name('accounting-scaling-worker.py')),axis,str(scale),method],capture_output=True,text=True,check=True)
   row=json.loads(run.stdout)
   row['nativeTimeRaw']=run.stderr
   pair.append(row);results.append(row)
   (out/f'accounting-{axis}-{scale}x-{method}.json').write_text(json.dumps(row,indent=2)+'\n')
  assert pair[0]['accountingDigest']==pair[1]['accountingDigest']
(out/'accounting-scaling.json').write_text(json.dumps({'scope':'bounded synthetic accounting only, cold interpreter per measurement','parity':'all old and compact accounting digests match','measurements':results},indent=2)+'\n')
print(json.dumps([ {k:r[k] for k in ('axis','scale','method','accountingWallSeconds','tracedPeakBytes','maximumExpectedGraphTriples','expectedGraphCalls')} for r in results],indent=2))
