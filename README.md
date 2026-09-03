# Compendio

The complete record of Europe's top club competition. Every fixture of every season, each linked to the best publicly listed highlight video found for it.

## What's inside

- index.html - the archive site (static, no build step)
- archive_data.js - inlined dataset the site reads
- matches.json - 1,997 matches across seasons 2011-12 to 2025-26 (league phase, groups, playoffs, knockouts, finals)
- finals.json - all 71 finals 1956-2026 with matched highlight videos
- scripts/ - fixture parser and video scrapers (yt-dlp based, no API key)

## Coverage status

- Fixtures: 2011-12 onward complete (source: openfootball, public domain). Pre-2011 has finals only.
- Videos: all 71 finals plus recent knockout rounds. Remaining matches show a targeted YouTube search link until scraped.

## Notes

No video is hosted or copied. The site embeds public YouTube uploads via youtube-nocookie and credits the uploader. A blank player means the uploader removed or restricted the video.
