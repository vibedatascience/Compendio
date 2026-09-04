import json, subprocess, sys, re, unicodedata, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC='matches_full.json'
OUT='backfill_results.json'
WORKERS=int(sys.argv[1]) if len(sys.argv)>1 else 6
LIMIT=int(sys.argv[2]) if len(sys.argv)>2 else 10**9

OFFICIAL=["uefa","tnt sports","cbs sports","bt sport","paramount","dazn","movistar","real madrid","liverpool","bayern","barcelona","psg","chelsea","inter","juventus","milan","manchester","arsenal","dortmund","atletico","napoli","porto","benfica","ajax","celtic","tottenham"]
STOP={'fc','cf','sc','ac','as','sk','fk','nk','kv','rc','cd','ud','sv','bsc','vfb','vfl','tsv','ss','us','afc','rsc','ksc','club','de','di','the','la','le','real','sporting','dinamo','dynamo','spartak','lokomotiv','partizan','red','star','crvena','zvezda','athletic','atletico','united','city','town','rovers','borussia','fk','olympique','olympiacos'}
ALIAS={'barca':'barcelona','bucuresti':'bucharest','bucureşti':'bucharest','munchen':'munich','monchengladbach':'gladbach','koln':'cologne','beograd':'belgrade','lisboa':'lisbon','praha':'prague','warszawa':'warsaw','goteborg':'gothenburg','sevilla':'seville','torino':'turin','napoli':'naples','wien':'vienna','moskva':'moscow','kyiv':'kiev','kobenhavn':'copenhagen','athens':'athina','athina':'athens','saloniki':'thessaloniki','marseille':'marseilles'}

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return s.split()

def team_tokens(t):
    toks=[ALIAS.get(x,x) for x in norm(t)]
    core=[x for x in toks if x not in STOP and len(x)>2]
    return core if core else toks

def team_in_title(team,title_toks):
    core=team_tokens(team)
    tt=set(title_toks)|{ALIAS.get(x,x) for x in title_toks}
    return any(c in tt or any(w.startswith(c) or c.startswith(w) for w in tt if len(w)>3) for c in core)

def years_ok(m,title):
    y1=int(m['season'][:4]); y2=y1+1
    found=set(int(y) for y in re.findall(r'(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)',title))
    if not found:
        two=re.findall(r'(?<!\d)(\d{2})\s*[/\-]\s*(\d{2})(?!\d)',title)
        if two:
            return any(int(a)%100==y1%100 and int(b)%100==y2%100 for a,b in two)
        return None
    return bool(found & {y1,y2})

def score_ok(m,title,strict=False):
    if not m.get('score'): return not strict
    g=re.findall(r'(\d+)\s*[-:x–]\s*(\d+)',title)
    if not g: return not strict
    hs,as_=m['score'].split('-')[:2]
    if strict: return (hs,as_) in g
    return any((a,b) in ((hs,as_),(as_,hs)) for a,b in g)

BAD=['ea sports','golden era','fifa ','pes ','pes2','efootball','fifa 0','fifa 1','fifa 2','fifa1','fifa2','gameplay','ps2','ps3','ps4','ps5','xbox','football manager','dream league','top eleven','prediction','preview','press conference','reaction','tribute','podcast','simulation','sim ','mod ','fc 24','fc 25','fc 26','tickets','lineup','line up','line-up','starting xi','squad','trailer','promo','intro']
MONTHS={m:i+1 for i,m in enumerate(['january','february','march','april','may','june','july','august','september','october','november','december'])}
for k,v in list(MONTHS.items()): MONTHS[k[:3]]=v
import datetime
def title_dates(title):
    t=title.lower(); out=set()
    for a,b,c in re.findall(r'(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)',t):
        for d_,mo in ((a,b),(b,a)):
            try: out.add(datetime.date(int(c),int(mo),int(d_)))
            except: pass
    for c,b,a in re.findall(r'(?<!\d)(\d{4})[./-](\d{1,2})[./-](\d{1,2})(?!\d)',t):
        try: out.add(datetime.date(int(c),int(b),int(a)))
        except: pass
    for y,mo,d_ in re.findall(r'(\d{4})\s*\(?\s*([a-z]{3,9})\.?\s+(\d{1,2})',t):
        if mo in MONTHS:
            try: out.add(datetime.date(int(y),MONTHS[mo],int(d_)))
            except: pass
    for mo,d_,y in re.findall(r'([a-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',t):
        if mo in MONTHS:
            try: out.add(datetime.date(int(y),MONTHS[mo],int(d_)))
            except: pass
    return out

def date_ok(m,title):
    ds=title_dates(title)
    if not ds: return None
    md=datetime.date.fromisoformat(m['date'])
    return any(abs((x-md).days)<=4 for x in ds)

def first_pos(team,tt):
    core=team_tokens(team)
    for i,w in enumerate(tt):
        w2=ALIAS.get(w,w)
        if any(c==w2 or (len(w2)>3 and (w2.startswith(c) or c.startswith(w2))) for c in core): return i
    return None

def loose_score_ok(m,title):
    if not m.get('score'): return True
    t=re.sub(r'(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})(?!\d)',' ',title.lower())
    t=re.sub(r'(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)',' ',t)
    t=re.sub(r'(\d{2})\s*[/\-]\s*(\d{2})',' ',t)
    t=re.sub(r'\b\d{1,2}(?:st|nd|rd|th)\b',' ',t)
    t=re.sub(r'(?<=[a-z])\d+',' ',t)
    nums=re.findall(r'(?<![a-z\d])(\d{1,2})(?![a-z\d])',t)
    nums=[n for n in nums if int(n)<20]
    if len(nums)!=2: return True
    hs,as_=m['score'].split('-')[:2]
    return (nums[0],nums[1]) in ((hs,as_),(as_,hs))

def order_ok(m,title):
    if not m.get('score'): return True
    tt=norm(title)
    g=re.findall(r'(\d+)\s*[-:x–]\s*(\d+)',title)
    hs,as_=m['score'].split('-')[:2]
    if hs==as_: return True
    ph,pa=first_pos(m['home'],tt),first_pos(m['away'],tt)
    if ph is None or pa is None: return True
    exact=(hs,as_) in g; rev=(as_,hs) in g
    if exact and not rev: return ph<pa
    if rev and not exact: return pa<ph
    return True

def verify(m,e):
    title=e.get('title') or ''
    tl=title.lower()
    if any(b in tl for b in BAD): return False
    dok=date_ok(m,title)
    if dok is False: return False
    if not loose_score_ok(m,title): return False
    if not order_ok(m,title): return False
    return verify_core(m,e)

def verify_core(m,e):
    title=e.get('title') or ''
    tt=norm(title)
    if not (team_in_title(m['home'],tt) and team_in_title(m['away'],tt)): return False
    y=years_ok(m,title)
    if y is False: return False
    if y is None: return score_ok(m,title,strict=True)
    return score_ok(m,title)

import urllib.request
def embeddable(vid):
    try:
        urllib.request.urlopen(urllib.request.Request(f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json',headers={'User-Agent':'Mozilla/5.0'}),timeout=10); return True
    except Exception: return False
def rank(m,es):
    good=[e for e in es if verify(m,e)]
    def sc(e):
        ch=(e.get('channel') or '').lower(); s=e.get('view_count') or 0
        if any(o in ch for o in OFFICIAL): s+=10_000_000
        d=e.get('duration') or 0
        if d and d<30: s-=5_000_000
        if d and d>3600: s-=8_000_000
        return s
    good.sort(key=sc,reverse=True)
    for e in good:
        if embeddable(e['id']): return e
    return None

def search(q,n=5):
    cmd=['yt-dlp',f'ytsearch{n}:{q}','--flat-playlist','-J','--no-warnings','--no-check-certificates']
    try:
        out=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        if out.returncode!=0: return []
        return [e for e in json.loads(out.stdout).get('entries',[]) if e]
    except Exception:
        return []

def comp(m):
    return 'Champions League' if m['season']>='1992-93' else 'European Cup'

def fetch(m):
    yr=m['date'][:4]
    q1=f"{m['home']} vs {m['away']} {m['score'] or ''} {comp(m)} {yr} highlights".strip()
    es=search(q1)
    best=rank(m,es)
    if not best:
        q2=f"{m['home']} {m['away']} {m['season']} {comp(m)}"
        best=rank(m,search(q2))
    return m['uefa_id'],best

if __name__=='__main__':
    d=json.load(open(SRC))
    try: results=json.load(open(OUT))
    except Exception: results={}
    import os
    tset=set(json.load(open('research_targets.json'))) if os.path.exists('research_targets.json') else None
    targets=[m for m in d if ((m['uefa_id'] in tset) if tset else not m['video_id']) and m['uefa_id'] not in results][:LIMIT]
    print(f'{len(targets)} to fetch, {len(results)} already done',flush=True)
    lock=threading.Lock(); n=[0]; hits=[0]; t0=time.time()
    with ThreadPoolExecutor(WORKERS) as ex:
        futs=[ex.submit(fetch,m) for m in targets]
        for f in as_completed(futs):
            uid,best=f.result()
            with lock:
                results[uid]=({'video_id':best['id'],'video_title':best.get('title'),'channel':best.get('channel')} if best else None)
                n[0]+=1
                if best: hits[0]+=1
                if n[0]%50==0:
                    json.dump(results,open(OUT,'w'))
                    print(f'{n[0]}/{len(targets)} hits={hits[0]} {time.time()-t0:.0f}s',flush=True)
    json.dump(results,open(OUT,'w'))
    print(f'done {n[0]} hits={hits[0]}',flush=True)
