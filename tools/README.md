# Discover Dolomites build tools

Python scripts used to generate the site's journal, season pages and maps. Not used by Cloudflare.

- `articles.py`, `journal_index.py`, `season_pages.py`, `skimaps_page.py`: page generators (data in `articles.json`, `figspec.json`).
- `map.py`, `map_winter.py`: illustrated overview maps (SVG).
- `terrain.py`, `skimap.py`, `areas.py`: 3D panorama ski maps. Inputs: `mapdata/dem.*` (Mapzen/AWS Terrain Tiles) and `mapdata/osm_c.json` (© OpenStreetMap contributors, ODbL).
