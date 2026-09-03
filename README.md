# Compendio

The complete record of Europe's top club competition. Every fixture of every season since 1955-56, each linked to the best publicly listed highlight video found for it.

## What's inside

- index.html - the archive site (static, no build step)
- archive_data.js - inlined dataset the site reads (same as matches_full.json plus a lineup-availability flag)
- matches_full.json - 6,039 matches across 71 seasons, 1955-56 to 2025-26, with goalscorers, venues, attendances, and video IDs
- lineups_1950s.json ... lineups_2020s.json - starting XIs with pitch positions for 6,021 matches, loaded per decade on demand
- logos.js - club crest URLs
- scripts/ - fixture parsers and yt-dlp based video search (no API key)

## Coverage status

Videos: 4,897 of 6,039 matches (81%). By decade:

| Decade | Matches with video |
|--------|--------------------|
| 1950s | 55 / 154 (36%) |
| 1960s | 189 / 424 (45%) |
| 1970s | 285 / 599 (48%) |
| 1980s | 395 / 603 (66%) |
| 1990s | 676 / 791 (85%) |
| 2000s | 1,200 / 1,346 (89%) |
| 2010s | 1,227 / 1,244 (99%) |
| 2020s | 878 / 878 (100%) |

Matches without a video show a targeted YouTube search link and a UEFA.com match page link.

## Video matching

scripts/backfill_verified.py searches YouTube via yt-dlp and only accepts a result whose title contains both club names, a matching season year or date, and a consistent score. Video-game and preview uploads are filtered by keyword. Results are ranked by official-channel bonus and view count. scripts/apply_backfill.py merges results into the dataset and regenerates archive_data.js.

## Notes

No video is hosted or copied. The site embeds public YouTube uploads via youtube-nocookie and credits the uploader. A blank player means the uploader removed or restricted the video.
