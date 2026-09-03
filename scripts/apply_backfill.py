import json, re

d=json.load(open('matches_full.json'))
r=json.load(open('backfill_results.json'))
src=open('archive_data.js').read()
extra={m['uefa_id']:{k:m[k] for k in ('lu','alts') if k in m} for m in json.loads(src[src.index('=')+1:].rstrip().rstrip(';'))}

n=0
for m in d:
    v=r.get(m['uefa_id'])
    if v and not m['video_id']:
        m.update(v); n+=1
print('applied',n,'total with video',sum(1 for m in d if m['video_id']))

json.dump(d,open('matches_full.json','w'),ensure_ascii=False,separators=(',',':'))
out=[dict(m,**extra.get(m['uefa_id'],{})) for m in d]
open('archive_data.js','w').write('const MATCHES='+json.dumps(out,separators=(',',':'))+';\n')

h=open('index.html').read()
h=re.sub(r'archive_data\.js\?v=\d+','archive_data.js?v=8',h)
open('index.html','w').write(h)
