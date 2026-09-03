import json, subprocess, time, sys

m = json.load(open('matches.json'))
targets = [i for i,x in enumerate(m) if x['stage'] in ('Semifinals','Quarterfinals') and x['season'] in ('2024-25','2025-26') and not x['video_id']]
print(f"scraping {len(targets)} matches", flush=True)

def search(q, n=4):
    cmd = ["yt-dlp", f"ytsearch{n}:{q}", "--flat-playlist","-J","--no-warnings","--no-check-certificates"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if out.returncode != 0: return []
        return [e for e in json.loads(out.stdout).get("entries",[]) if e]
    except Exception:
        return []

OFFICIAL = ["uefa","tnt sports","cbs sports","bt sport","paramount","dazn","movistar","real madrid","liverpool","bayern","barcelona","psg","chelsea","inter","juventus","milan","manchester","arsenal","dortmund"]
def pick(es):
    def sc(e):
        ch=(e.get("channel") or "").lower(); s=e.get("view_count") or 0
        if any(o in ch for o in OFFICIAL): s+=10_000_000
        d=e.get("duration") or 0
        if d and d<90: s-=5_000_000
        return s
    es=sorted(es,key=sc,reverse=True)
    return es[0] if es else None

ok=0
for i in targets:
    x=m[i]
    yr=x['date'][:4] if x['date'] else x['season'][:4]
    q=f"{x['home']} {x['away']} {x['score']} Champions League {x['stage']} {yr} highlights"
    e=pick(search(q))
    if e:
        x['video_id']=e['id']; x['video_title']=e['title']; x['channel']=e.get('channel'); ok+=1
    print(f"{x['season']} {x['stage']}: {x['home']} v {x['away']} -> {'OK' if e else 'MISS'}", flush=True)
    time.sleep(0.3)

json.dump(m, open('matches.json','w'), indent=1)
print(f"done {ok}/{len(targets)}")
