# GeoPulse — Phase 1

Real-time geopolitical activity on a 3D globe. GDELT events → Postgres → FastAPI → globe.gl.

## Run it

```powershell
# 1. Start the database
docker compose up -d

# 2. Install Python deps
pip install -r requirements.txt

# 3. Ingest events (latest file + last 6 hours)
python collector/gdelt_collector.py --backfill 6

# 3b. Ingest news headlines with NER (Phase 2)
python collector/rss_collector.py

# 3c. Build the knowledge graph (Phase 3; needs `docker compose up -d graph`)
python collector/graph_writer.py

# 4. Start the API + globe
uvicorn api.main:app --port 8000
```

Open http://localhost:8000 — click any colored country.

## What's in Phase 1 (per the SDD)

- **Collector**: GDELT 2.0 export files (every 15 min)
- **Clean/filter**: drop malformed rows, dedupe by GlobalEventID
- **Entities/geocode**: GDELT pre-extracted actors + FIPS→ISO3 + lat/lon
- **Store**: Postgres (`events` table)
- **Risk scoring**: transparent thresholds on conflict-class event counts (last 3 days)
- **Globe**: country choropleth, click → event breakdown

## Phase 2 (done)

- **RSS collector**: 7 world-news feeds → `articles` table
- **Real NER**: GLiNER zero-shot (person / org / country / location / weapon / military unit)
- **Country tagging**: entities + text mentions → ISO3, headlines shown in the country panel

## Phase 3 (done)

- **Knowledge graph**: Memgraph (Docker) — actors/events/countries, related-countries via shared actors
- **AI summaries**: removed from the interface. Generated prose over thin,
  single-sourced event rows read as a confident account of a country without
  traceable evidence behind each claim.
- **Live globe**: recolors every 60s

## Phase 4 (done)

- **Relation extraction**: local LLM turns headlines into `actor → action → target (instrument)` rows — `python collector/relation_extractor.py`
- **Alerts**: Watch button per country; browser notification when a watched country's risk level changes
- **Search**: full-text over news + actor/place search over events (search box, press Enter)
- **Confidence**: per-event high/medium/low from source count; % multi-source per country
