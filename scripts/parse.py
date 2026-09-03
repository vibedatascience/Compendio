import re, json, glob

def clean_team(t):
    t = re.sub(r'\s*\([A-Z]{3}\)\s*$', '', t.strip())
    return t

matches = []
for path in sorted(glob.glob('raw_*.txt')):
    season = path[4:11]
    year_start = int(season[:4])
    stage, matchday, cur_date = None, None, None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\r\n')
        if not line.strip() or line.strip().startswith('#') or line.strip().startswith('='):
            continue
        s = line.strip()
        m = re.match(r'^[▪»]\s*(.+)$', s)
        if m:
            hdr = m.group(1)
            md = re.search(r'Matchday\s+(\d+)', hdr)
            if md:
                stage = hdr.split(',')[0].strip()
                matchday = int(md.group(1))
            else:
                stage = hdr.strip()
                matchday = None
            continue
        dm = re.match(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?$', s)
        if dm:
            mon = dm.group(2); day = int(dm.group(3))
            yr = int(dm.group(4)) if dm.group(4) else (year_start if mon in ('Jul','Aug','Sep','Oct','Nov','Dec') else year_start+1)
            cur_date = f"{yr}-{mon}-{day:02d}"
            continue
        mm = re.match(r'^(?:(\d{1,2}[.:]\d{2})\s+)?(.+?)\s+v\s+(.+?)\s+(\d+-\d+(?:\s*\([^)]*\))?(?:\s+(?:a\.e\.t\.|pen\.).*)?|\-\-)?\s*$', s)
        if mm and ' v ' in s:
            home, away = clean_team(mm.group(2)), clean_team(mm.group(3))
            score = (mm.group(4) or '').strip()
            paren = re.search(r'^(\d+-\d+)', score)
            main_score = paren.group(1) if paren else None
            extra = score[len(main_score):].strip() if main_score else ''
            matches.append({
                "season": season, "stage": stage, "matchday": matchday,
                "date": cur_date, "home": home, "away": away,
                "score": main_score, "score_detail": extra or None,
                "video_id": None, "video_title": None, "channel": None
            })

json.dump(matches, open('matches.json','w'), indent=1)
from collections import Counter
print(len(matches), "matches")
c = Counter(m['season'] for m in matches)
for k in sorted(c): print(k, c[k])
print("stages:", sorted(set(m['stage'] for m in matches if m['stage'])))
print("no-score:", sum(1 for m in matches if not m['score']))
