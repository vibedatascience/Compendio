import json, subprocess, sys, time

FINALS = {
1956:("Real Madrid","Reims","4-3"),1957:("Real Madrid","Fiorentina","2-0"),1958:("Real Madrid","Milan","3-2"),
1959:("Real Madrid","Reims","2-0"),1960:("Real Madrid","Eintracht Frankfurt","7-3"),1961:("Benfica","Barcelona","3-2"),
1962:("Benfica","Real Madrid","5-3"),1963:("Milan","Benfica","2-1"),1964:("Inter","Real Madrid","3-1"),
1965:("Inter","Benfica","1-0"),1966:("Real Madrid","Partizan","2-1"),1967:("Celtic","Inter","2-1"),
1968:("Manchester United","Benfica","4-1"),1969:("Milan","Ajax","4-1"),1970:("Feyenoord","Celtic","2-1"),
1971:("Ajax","Panathinaikos","2-0"),1972:("Ajax","Inter","2-0"),1973:("Ajax","Juventus","1-0"),
1974:("Bayern Munich","Atletico Madrid","4-0"),1975:("Bayern Munich","Leeds United","2-0"),1976:("Bayern Munich","Saint-Etienne","1-0"),
1977:("Liverpool","Borussia Monchengladbach","3-1"),1978:("Liverpool","Club Brugge","1-0"),1979:("Nottingham Forest","Malmo","1-0"),
1980:("Nottingham Forest","Hamburg","1-0"),1981:("Liverpool","Real Madrid","1-0"),1982:("Aston Villa","Bayern Munich","1-0"),
1983:("Hamburg","Juventus","1-0"),1984:("Liverpool","Roma","1-1 (4-2p)"),1985:("Juventus","Liverpool","1-0"),
1986:("Steaua Bucharest","Barcelona","0-0 (2-0p)"),1987:("Porto","Bayern Munich","2-1"),1988:("PSV","Benfica","0-0 (6-5p)"),
1989:("Milan","Steaua Bucharest","4-0"),1990:("Milan","Benfica","1-0"),1991:("Red Star Belgrade","Marseille","0-0 (5-3p)"),
1992:("Barcelona","Sampdoria","1-0"),1993:("Marseille","Milan","1-0"),1994:("Milan","Barcelona","4-0"),
1995:("Ajax","Milan","1-0"),1996:("Juventus","Ajax","1-1 (4-2p)"),1997:("Borussia Dortmund","Juventus","3-1"),
1998:("Real Madrid","Juventus","1-0"),1999:("Manchester United","Bayern Munich","2-1"),2000:("Real Madrid","Valencia","3-0"),
2001:("Bayern Munich","Valencia","1-1 (5-4p)"),2002:("Real Madrid","Bayer Leverkusen","2-1"),2003:("Milan","Juventus","0-0 (3-2p)"),
2004:("Porto","Monaco","3-0"),2005:("Liverpool","Milan","3-3 (3-2p)"),2006:("Barcelona","Arsenal","2-1"),
2007:("Milan","Liverpool","2-1"),2008:("Manchester United","Chelsea","1-1 (6-5p)"),2009:("Barcelona","Manchester United","2-0"),
2010:("Inter","Bayern Munich","2-0"),2011:("Barcelona","Manchester United","3-1"),2012:("Chelsea","Bayern Munich","1-1 (4-3p)"),
2013:("Bayern Munich","Borussia Dortmund","2-1"),2014:("Real Madrid","Atletico Madrid","4-1"),2015:("Barcelona","Juventus","3-1"),
2016:("Real Madrid","Atletico Madrid","1-1 (5-3p)"),2017:("Real Madrid","Juventus","4-1"),2018:("Real Madrid","Liverpool","3-1"),
2019:("Liverpool","Tottenham","2-0"),2020:("Bayern Munich","PSG","1-0"),2021:("Chelsea","Manchester City","1-0"),
2022:("Real Madrid","Liverpool","1-0"),2023:("Manchester City","Inter","1-0"),2024:("Real Madrid","Borussia Dortmund","2-0"),
2025:("PSG","Inter","5-0"),2026:("Arsenal","Barcelona","2-1"),
}

OFFICIAL = ["real madrid","liverpool fc","fc bayern","manchester united","fc barcelona","psg","chelsea","inter","juventus","ac milan","manchester city","arsenal","borussia dortmund","fifa","uefa","tnt sports","cbs sports","bt sport"]

def search(query, n=6):
    cmd = ["yt-dlp", f"ytsearch{n}:{query}", "--flat-playlist", "-J", "--no-warnings", "--no-check-certificates"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if out.returncode != 0: return []
        return [e for e in json.loads(out.stdout).get("entries", []) if e]
    except Exception:
        return []

def pick(entries):
    def score(e):
        ch = (e.get("channel") or e.get("uploader") or "").lower()
        s = e.get("view_count") or 0
        if any(o in ch for o in OFFICIAL): s += 10_000_000
        dur = e.get("duration") or 0
        if dur and dur < 120: s -= 5_000_000
        return s
    entries = sorted(entries, key=score, reverse=True)
    return entries[0] if entries else None

dataset = []
for year, (winner, loser, sc) in sorted(FINALS.items()):
    comp = "Champions League" if year >= 1993 else "European Cup"
    q = f"{comp} final {year} {winner} {loser} highlights"
    e = pick(search(q))
    if e:
        dataset.append({
            "season": f"{year-1}-{str(year)[2:].zfill(2)}", "year": year, "stage": "Final",
            "home": winner, "away": loser, "score": sc,
            "video_id": e.get("id"), "video_title": e.get("title"),
            "channel": e.get("channel") or e.get("uploader"),
            "views": e.get("view_count"), "duration": e.get("duration"),
        })
        print(f"{year}: OK ({e.get('channel')})")
    else:
        print(f"{year}: MISS")
    time.sleep(0.5)

with open("finals.json","w") as f: json.dump(dataset, f, indent=2)
print(f"\n{len(dataset)}/{len(FINALS)} finals matched")
