import json, subprocess, time, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

m=json.load(open('matches.json'))
KO={'Final','Semifinals','Quarterfinals','Round of 16','Knockout Playoffs'}
phase=sys.argv[1] if len(sys.argv)>1 else 'ko'
limit=int(sys.argv[2]) if len(sys.argv)>2 else 10**9
if phase=='ko': targets=[x for x in m if x['stage'] in KO and not x['video_id']]
else: targets=[x for x in m if x['stage'] not in KO and not x['video_id']]
targets=targets[:limit]
print(f"{phase}: {len(targets)} to fetch",flush=True)

OFFICIAL=["uefa","tnt sports","cbs sports","bt sport","paramount","dazn","movistar","real madrid","liverpool","bayern","barcelona","psg","chelsea","inter","juventus","milan","manchester","arsenal","dortmund","atletico","napoli","porto","benfica","ajax","celtic","tottenham"]
lock=threading.Lock()
done=[0]

def fetch(x):
    yr=x['date'][:4] if x['date'] else x['season'][:4]
    q=f"{x['home']} vs {x['away']} {x['score']} Champions League {yr} highlights"
    cmd=["yt-dlp",f"ytsearch4:{q}","--flat-playlist","-J","--no-warnings","--no-check-certificates"]
    try:
        out=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        if out.returncode!=0: return x,None
        es=[e for e in json.loads(out.stdout).get("entries",[]) if e]
    except Exception:
        return x,None
    def sc(e):
        ch=(e.get("channel") or "").lower(); s=e.get("view_count") or 0
        if any(o in ch for o in OFFICIAL): s+=10_000_000
        d=e.get("duration") or 0
        if d and d<90: s-=5_000_000
        return s
    es=sorted(es,key=sc,reverse=True)
    return x,(es[0] if es else None)

t0=time.time()
with ThreadPoolExecutor(max_workers=6) as pool:
    futs=[pool.submit(fetch,x) for x in targets]
    for f in as_completed(futs):
        x,e=f.result()
        with lock:
            if e:
                x['video_id']=e['id'];x['video_title']=e['title'];x['channel']=e.get('channel')
            done[0]+=1
            if done[0]%50==0:
                json.dump(m,open('matches.json','w'),indent=1)
                got=sum(1 for t in targets if t['video_id'])
                rate=done[0]/(time.time()-t0)
                print(f"{done[0]}/{len(targets)} ok:{got} {rate:.1f}/s",flush=True)
json.dump(m,open('matches.json','w'),indent=1)
print(f"DONE {sum(1 for t in targets if t['video_id'])}/{len(targets)} in {time.time()-t0:.0f}s",flush=True)
