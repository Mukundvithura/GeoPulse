"""GeoPulse Phase 1 API.

Two endpoints + the static globe page:
  GET /api/countries        -> risk level per country (drives globe colors)
  GET /api/country/{iso3}   -> score breakdown + recent events (dashboard)

Risk scoring is deliberately transparent (SDD section 6.8): counts of
conflict-class events in the last 3 days, weighted, with the numbers
returned so the UI can always show *why* a country has its color.
"""

import sys
from pathlib import Path

import psycopg
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DB_URL

MEMGRAPH_URL = "bolt://localhost:7687"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
SUMMARY_TTL_HOURS = 6
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
WINDOW_DAYS = 3

app = FastAPI(title="GeoPulse API", version="0.1")


def query(sql: str, params: tuple = ()) -> list[tuple]:
    with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def risk_level(quad4: int, quad3: int, violent: int, total: int) -> str:
    """Transparent thresholds. Raw counts track media volume (USA would always
    be red), so levels use the *share* of violent events (CAMEO 18/19/20)
    alongside a minimum count."""
    share = violent / total if total else 0.0
    if violent >= 40 and share >= 0.10:
        return "conflict"
    if violent >= 15 and share >= 0.08:
        return "breaking"
    if (violent >= 5 and share >= 0.04) or quad4 >= 30:
        return "elevated"
    return "stable"


@app.get("/api/countries")
def countries():
    rows = query(
        """
        SELECT country_iso3,
               COUNT(*) FILTER (WHERE quad_class = 4)                    AS quad4,
               COUNT(*) FILTER (WHERE quad_class = 3)                    AS quad3,
               COUNT(*) FILTER (WHERE cameo_root IN ('18','19','20'))    AS violent,
               COUNT(*)                                                  AS total,
               COUNT(*) FILTER (WHERE num_sources >= 2)                  AS multi_source
        FROM events
        WHERE event_date >= CURRENT_DATE - %s
        GROUP BY country_iso3
        """,
        (WINDOW_DAYS,),
    )
    return [
        {
            "iso3": iso3,
            "level": risk_level(quad4, quad3, violent, total),
            "quad4": quad4,
            "quad3": quad3,
            "violent": violent,
            "total": total,
            "multi_source": multi_source,
        }
        for iso3, quad4, quad3, violent, total, multi_source in rows
    ]


@app.get("/api/country/{iso3}")
def country(iso3: str):
    iso3 = iso3.upper()
    summary = query(
        """
        SELECT COUNT(*) FILTER (WHERE quad_class = 4),
               COUNT(*) FILTER (WHERE quad_class = 3),
               COUNT(*) FILTER (WHERE cameo_root IN ('18','19','20')),
               COUNT(*),
               COUNT(*) FILTER (WHERE num_sources >= 2)
        FROM events
        WHERE country_iso3 = %s AND event_date >= CURRENT_DATE - %s
        """,
        (iso3, WINDOW_DAYS),
    )
    quad4, quad3, violent, total, multi_source = summary[0]
    if total == 0:
        raise HTTPException(404, f"No recent events for {iso3}")

    events = query(
        """
        SELECT event_date, actor1, actor2, cameo_root, quad_class,
               goldstein, num_articles, num_sources, place, source_url
        FROM events
        WHERE country_iso3 = %s AND event_date >= CURRENT_DATE - %s
        ORDER BY num_articles DESC, event_date DESC
        LIMIT 25
        """,
        (iso3, WINDOW_DAYS),
    )
    headlines = query(
        """
        SELECT title, source, url, published, entities
        FROM articles
        WHERE %s = ANY(countries)
        ORDER BY published DESC NULLS LAST
        LIMIT 10
        """,
        (iso3,),
    )
    return {
        "iso3": iso3,
        "level": risk_level(quad4, quad3, violent, total),
        "headlines": [
            {
                "title": t,
                "source": s,
                "url": u,
                "published": str(p) if p else None,
                "entities": ents,
            }
            for t, s, u, p, ents in headlines
        ],
        "window_days": WINDOW_DAYS,
        "breakdown": {"quad4": quad4, "quad3": quad3, "violent": violent,
                      "total": total, "multi_source": multi_source},
        "events": [
            {
                "date": str(d),
                "actor1": a1,
                "actor2": a2,
                "cameo_root": root,
                "quad_class": quad,
                "goldstein": gold,
                "articles": arts,
                "confidence": "high" if srcs >= 5 else "medium" if srcs >= 2 else "low",
                "place": place,
                "url": url,
            }
            for d, a1, a2, root, quad, gold, arts, srcs, place, url in events
        ],
    }


@app.get("/api/country/{iso3}/related")
def related(iso3: str):
    """Countries linked through shared actors. Reads the precomputed table
    (populated by graph_writer.py from Memgraph) so this also works on a
    cloud deploy where Memgraph isn't running."""
    rows = query(
        "SELECT other, links, via FROM related_countries "
        "WHERE iso3 = %s ORDER BY links DESC LIMIT 5",
        (iso3.upper(),),
    )
    return [{"iso3": o, "links": l, "via": v} for o, l, v in rows]


@app.get("/api/country/{iso3}/relations")
def relations(iso3: str):
    """Who-did-what-to-whom, extracted by the local LLM from headlines."""
    rows = query(
        """
        SELECT DISTINCT r.actor, r.action, r.target, r.instrument, a.url
        FROM relations r JOIN articles a ON a.id = r.article_id
        WHERE %s = ANY(a.countries) AND r.action != 'none'
        ORDER BY r.actor LIMIT 15
        """,
        (iso3.upper(),),
    )
    return [
        {"actor": a, "action": act, "target": t, "instrument": i, "url": u}
        for a, act, t, i, u in rows
    ]


@app.get("/api/search")
def search(q: str):
    """Full-text search over headlines plus actor search over events."""
    if not q.strip():
        return {"articles": [], "events": []}
    articles = query(
        """
        SELECT title, source, url, countries FROM articles
        WHERE to_tsvector('english', title || ' ' || coalesce(summary, ''))
              @@ websearch_to_tsquery('english', %s)
        ORDER BY published DESC NULLS LAST LIMIT 15
        """,
        (q,),
    )
    events = query(
        """
        SELECT event_date, actor1, actor2, country_iso3, place, source_url
        FROM events
        WHERE (actor1 ILIKE %s OR actor2 ILIKE %s OR place ILIKE %s)
          AND event_date >= CURRENT_DATE - %s
        ORDER BY num_articles DESC LIMIT 15
        """,
        (f"%{q}%", f"%{q}%", f"%{q}%", WINDOW_DAYS),
    )
    return {
        "articles": [
            {"title": t, "source": s, "url": u, "countries": c}
            for t, s, u, c in articles
        ],
        "events": [
            {"date": str(d), "actor1": a1, "actor2": a2, "iso3": i,
             "place": p, "url": u}
            for d, a1, a2, i, p, u in events
        ],
    }


PROMPT = """You are an intelligence analyst. Using ONLY the data below, write a
3-4 sentence situation summary for {name}. State only facts present in the
data. No speculation, no advice, no preamble. Write flowing prose — never
quote the raw data lines, arrows, or mention counts.

Recent conflict events (actor -> actor, type, mentions):
{events}

Recent headlines:
{headlines}
"""


@app.get("/api/country/{iso3}/summary")
def summary(iso3: str):
    """Grounded LLM summary via local Ollama, cached for a few hours."""
    iso3 = iso3.upper()
    cached = query(
        "SELECT summary, model, generated_at FROM summaries WHERE iso3 = %s "
        "AND generated_at > now() - make_interval(hours => %s)",
        (iso3, SUMMARY_TTL_HOURS),
    )
    if cached:
        return {"iso3": iso3, "summary": cached[0][0],
                "model": cached[0][1], "cached": True}

    events = query(
        """
        SELECT actor1, actor2, cameo_root, num_articles FROM events
        WHERE country_iso3 = %s AND event_date >= CURRENT_DATE - %s
          AND quad_class = 4
        ORDER BY num_articles DESC LIMIT 12
        """,
        (iso3, WINDOW_DAYS),
    )
    heads = query(
        "SELECT title FROM articles WHERE %s = ANY(countries) "
        "ORDER BY published DESC NULLS LAST LIMIT 8",
        (iso3,),
    )
    if not events and not heads:
        raise HTTPException(404, f"No data to summarize for {iso3}")

    cameo = {"18": "assault", "19": "fight", "20": "mass violence",
             "17": "coercion", "15": "show of force", "14": "protest"}
    ev_lines = "\n".join(
        f"- {a1 or '?'} -> {a2 or '?'}: {cameo.get(root, 'conflict')} ({n} mentions)"
        for a1, a2, root, n in events) or "- none"
    hl_lines = "\n".join(f"- {t[0]}" for t in heads) or "- none"

    resp = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": PROMPT.format(name=iso3, events=ev_lines, headlines=hl_lines),
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 220},
    }, timeout=180)
    resp.raise_for_status()
    text = resp.json()["response"].strip()

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            INSERT INTO summaries (iso3, summary, model) VALUES (%s, %s, %s)
            ON CONFLICT (iso3) DO UPDATE
              SET summary = EXCLUDED.summary, model = EXCLUDED.model,
                  generated_at = now()
            """,
            (iso3, text, OLLAMA_MODEL),
        )
        conn.commit()
    return {"iso3": iso3, "summary": text, "model": OLLAMA_MODEL, "cached": False}


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=WEB_DIR), name="web")
