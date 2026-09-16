# Product

## Platform

web

## Users

OSINT and news analysts as real users, not demo viewers. They arrive wanting to
know what is happening in a specific country right now, or to notice which
countries have changed state since they last looked. The working session is
scan-then-investigate: read the globe for where activity is, open a country,
read the evidence behind the color, follow source links out.

## Product Purpose

GeoPulse turns raw GDELT event records and world news feeds into a live,
country-level read of geopolitical activity on a 3D globe. Success is an
analyst being able to answer "what is going on in X, and how do I know" from
the interface alone, with every claim traceable to a source URL.

## Positioning

The risk score is transparent by design, not a black box. Levels come from
published thresholds on conflict-class CAMEO event counts plus the *share* of
violent events (so high-media-volume countries like the USA do not sit
permanently red), and the raw counts are returned to the UI so the interface can
always show why a country has its color. LLM summaries are grounded: the prompt
is constructed only from the real events and headlines on hand, and is
instructed to state nothing absent from that data. Per-event confidence
(high/medium/low) is derived from source count, and per-country "% multi-source"
is exposed.

## Operating Context

- Ingest: GDELT 2.0 export files (every 15 min) plus 7 world-news RSS feeds.
- Entity extraction: GLiNER zero-shot NER (person / org / country / location /
  weapon / military unit); country tagging maps entities and text mentions to ISO3.
- Knowledge graph: Memgraph holds actors/events/countries; related-countries via
  shared actors are precomputed into Postgres so the read path does not need it.
- Summaries and relation extraction: local Ollama (`llama3.2:3b`), summaries
  cached 6 hours.
- Sharing today: `cloudflared tunnel --url http://localhost:8000` gives a public
  URL while the laptop runs.
- Rolling window is 3 days everywhere (`WINDOW_DAYS`).

## Capabilities and Constraints

Shipped: country choropleth globe with click-to-open country panel; risk levels
(stable / elevated / breaking / conflict / no signal); score breakdown and up to
25 recent events with source links; country headlines with entities; related
countries via shared actors; actor→action→target relations from headlines;
grounded AI situation summary; full-text search over news plus actor/place
search over events; per-country Watch with a browser notification when risk
level changes; globe recolors every 60s.

Stack: FastAPI + psycopg + Postgres 16, Memgraph, globe.gl 2.34.5 loaded from
unpkg, single static `web/index.html`, no build step and no frontend framework.

Not yet built: historical replay and country comparison.

**Open decision — deployment.** Whether GeoPulse stays a laptop-hosted app
shared via cloudflared or moves to a real cloud deploy is undecided. This
matters: a cloud deploy has no local Ollama or Memgraph, so it would run on
precomputed `related_countries` rows and cached `summaries` only. Do not assume
either answer.

## Evidence on Hand

All displayed data is real and live: GDELT event rows, RSS headlines with source
names and URLs, and model-generated summaries labeled with the model that wrote
them. There are no users, customers, testimonials, press mentions, benchmarks,
or usage numbers — none exist, and none may be invented. There is no logo,
wordmark, or brand asset file; the current identity is the plain "GeoPulse"
text lockup in `web/index.html`.

## Product Principles

1. **Never show a conclusion without its evidence.** Every color, level, and
   summary must be openable into the counts, events, and source links behind it.
2. **Uncertainty is displayed, not hidden.** Confidence, source counts, and
   "no signal" are first-class states, not omissions.
3. **Scan first, investigate second.** The globe answers "where"; the panel
   answers "what and how do I know".
4. **Fabricate nothing.** Generated text is grounded in retrieved rows and
   labeled as generated; absent data reads as absent.
5. **Live means live.** The view reflects the last 3 days and refreshes itself;
   staleness must be visible when it happens.
