import json, glob, urllib.request, time

s=open('archive_data.js').read()
season={str(m['uefa_id']):m['season'] for m in json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))}
ROWS={'DEFENDER':260,'MIDFIELDER':520,'FORWARD':780}

def get(mid):
    req=urllib.request.Request(f'https://match.uefa.com/v5/matches/{mid}/lineups',headers={'Accept':'application/json','User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req,timeout=20))

def apply(side,field):
    roles={}
    for p in field:
        r=p['player'].get('fieldPosition')
        if r: roles[p.get('jerseyNumber')]=r
    if len(roles)<10: return None
    groups={'GOALKEEPER':[],'DEFENDER':[],'MIDFIELDER':[],'FORWARD':[]}
    for p in side['xi']:
        groups.get(roles.get(p['n'],'MIDFIELDER'),groups['MIDFIELDER']).append(p)
    if not groups['GOALKEEPER']: return None
    for i,g in enumerate(groups['GOALKEEPER']): g['x'],g['y']=500,60
    lines=[]
    for r in ('DEFENDER','MIDFIELDER','FORWARD'):
        ps=groups[r]
        if r=='MIDFIELDER' and len(ps)>=5: lines+=[(ps[:len(ps)//2],420),(ps[len(ps)//2:],620)]
        elif ps: lines.append((ps,ROWS[r]))
    for ps,y in lines:
        n=len(ps)
        for j,p in enumerate(sorted(ps,key=lambda p:p['n'] or 0)): p['x'],p['y']=round(1000*(j+1)/(n+1)),y
    return '-'.join(str(len(groups[r])) for r in ('DEFENDER','MIDFIELDER','FORWARD'))

done=0;miss=[]
for f in sorted(glob.glob('lineups_*.json')):
    lu=json.load(open(f)); ch=False
    for k,l in lu.items():
        if season.get(k,'0')<'1990': continue
        if not any(l[sd].get('formation_est') for sd in 'ha'): continue
        try: d=get(k)
        except Exception as e: miss.append((k,str(e))); continue
        for sd,key in (('h','homeTeam'),('a','awayTeam')):
            if l[sd].get('formation_est'):
                fm=apply(l[sd],d[key]['field'])
                if fm: l[sd]['formation_est']=fm; l[sd]['formation_src']='roles'; done+=1; ch=True
                else: miss.append((k,sd))
        time.sleep(0.3)
    if ch: json.dump(lu,open(f,'w'),ensure_ascii=False,separators=(',',':'))
print('sides from roles',done,'missing',miss)
