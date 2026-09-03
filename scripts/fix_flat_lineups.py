import json, glob, re

s=open('archive_data.js').read()
season={str(m['uefa_id']):m['season'] for m in json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))}

def shape(season_str):
    y=int(season_str[:4])
    if y<1962: return [('DEF',[2,5,3],260),('MID',[4,6],430),('AM',[8,10],600),('FW',[7,9,11],800)]
    if y<1980: return [('DEF',[2,5,6,3],260),('MID',[4,8,10],520),('FW',[7,9,11],800)]
    return [('DEF',[2,5,6,3],260),('MID',[7,4,8,11],520),('FW',[9,10],780)]

def is_flat(xi):
    return len(xi)>=8 and len({p['y'] for p in xi})<=2

def layout(xi,season_str):
    rows=shape(season_str)
    gk=next((p for p in xi if p['n']==1),None) or xi[0]
    rest=[p for p in xi if p is not gk]
    placed={i:[] for i in range(len(rows))}
    left=[]
    for p in rest:
        idx=next((i for i,(_,nums,_) in enumerate(rows) if p['n'] in nums),None)
        if idx is None: left.append(p)
        else: placed[idx].append(p)
    for p in left:
        i=min(placed,key=lambda i:(len(placed[i])-len(rows[i][1]),i))
        placed[i].append(p)
    gk['x'],gk['y']=500,60
    for i,(_,nums,y) in enumerate(rows):
        ps=sorted(placed[i],key=lambda p:(nums.index(p['n']) if p['n'] in nums else 99))
        n=len(ps)
        for j,p in enumerate(ps):
            p['x']=round(1000*(j+1)/(n+1)); p['y']=y
    return '-'.join(str(len(placed[i])) for i in range(len(rows)))

fixed=0
for f in sorted(glob.glob('lineups_*.json')):
    lu=json.load(open(f)); ch=False
    for k,l in lu.items():
        for side in 'ha':
            xi=l[side]['xi']
            if is_flat(xi) and k in season:
                fm=layout(xi,season[k]); l[side]['formation_est']=fm; fixed+=1; ch=True
    if ch: json.dump(lu,open(f,'w'),ensure_ascii=False,separators=(',',':'))
print('fixed',fixed)
