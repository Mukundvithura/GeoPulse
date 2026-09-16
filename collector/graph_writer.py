"""Phase 3: project Postgres events into the Memgraph knowledge graph.

Graph shape (per the SDD):
  (Actor)-[:PERFORMED]->(Event)-[:TARGETED]->(Actor)
                         (Event)-[:IN]->(Country)

GDELT actor names are raw strings; generic ones ("POLICE", "GOVERNMENT")
would create bogus cross-country links, so they are skipped. Real relation
extraction replaces this heuristic in a later phase.

Usage:  python graph_writer.py     (re-runs are idempotent via MERGE)
"""

import sys

import psycopg
from neo4j import GraphDatabase

PG_URL = "postgresql://geopulse:geopulse@localhost:6543/geopulse"
MEMGRAPH_URL = "bolt://localhost:7687"
WINDOW_DAYS = 3

GENERIC_ACTORS = {
    "POLICE", "GOVERNMENT", "AUTHORITIES", "PRESIDENT", "MINISTER", "COURT",
    "MILITARY", "ARMY", "SOLDIER", "CITIZEN", "PROTESTER", "COMPANY", "MEDIA",
    "SCHOOL", "STUDENT", "COMMUNITY", "OFFICIAL", "LAWMAKER", "SENATE",
    "PARLIAMENT", "JUDGE", "LAWYER", "DOCTOR", "WORKER", "FARMER", "BUSINESS",
    "UNITED NATIONS", "EUROPEAN UNION",
}

UPSERT_CYPHER = """
UNWIND $rows AS r
MERGE (c:Country {iso3: r.iso3})
MERGE (e:Event {id: r.id})
  ON CREATE SET e.cameo_root = r.root, e.quad = r.quad, e.date = r.date
MERGE (e)-[:IN]->(c)
WITH e, r
FOREACH (_ IN CASE WHEN r.a1 IS NULL THEN [] ELSE [1] END |
  MERGE (a1:Actor {name: r.a1}) MERGE (a1)-[:PERFORMED]->(e))
FOREACH (_ IN CASE WHEN r.a2 IS NULL THEN [] ELSE [1] END |
  MERGE (a2:Actor {name: r.a2}) MERGE (e)-[:TARGETED]->(a2))
"""


def clean_actor(name: str | None) -> str | None:
    if not name or name.upper() in GENERIC_ACTORS:
        return None
    return name.upper()


def main() -> None:
    with psycopg.connect(PG_URL) as pg, pg.cursor() as cur:
        cur.execute(
            """
            SELECT id, actor1, actor2, cameo_root, quad_class,
                   event_date::text, country_iso3
            FROM events
            WHERE event_date >= CURRENT_DATE - %s
              AND quad_class IN (3, 4)      -- graph only carries conflict events
            """,
            (WINDOW_DAYS,),
        )
        rows = [
            {
                "id": rid, "a1": clean_actor(a1), "a2": clean_actor(a2),
                "root": root, "quad": quad, "date": date, "iso3": iso3,
            }
            for rid, a1, a2, root, quad, date, iso3 in cur.fetchall()
        ]

    driver = GraphDatabase.driver(MEMGRAPH_URL, auth=("", ""))
    with driver.session() as s:
        s.run("CREATE INDEX ON :Country(iso3)").consume()
        s.run("CREATE INDEX ON :Event(id)").consume()
        s.run("CREATE INDEX ON :Actor(name)").consume()
        for i in range(0, len(rows), 2000):
            s.run(UPSERT_CYPHER, rows=rows[i:i + 2000]).consume()
        counts = s.run(
            "MATCH (n) RETURN labels(n)[0] AS l, count(*) AS c ORDER BY l"
        ).data()
        # precompute related-countries into Postgres so the API (and a cloud
        # deploy without Memgraph) reads a plain table
        pairs = s.run(
            """
            MATCH (c1:Country)<-[:IN]-(:Event)<-[:PERFORMED]-(a:Actor)
                  -[:PERFORMED]->(:Event)-[:IN]->(c2:Country)
            WHERE c1 <> c2
            RETURN c1.iso3 AS iso3, c2.iso3 AS other, count(*) AS links,
                   collect(DISTINCT a.name)[..3] AS via
            """
        ).data()
    driver.close()

    with psycopg.connect(PG_URL) as pg:
        pg.execute("TRUNCATE related_countries")
        with pg.cursor() as cur:
            cur.executemany(
                "INSERT INTO related_countries (iso3, other, links, via) "
                "VALUES (%s, %s, %s, %s)",
                [(p["iso3"], p["other"], p["links"], p["via"]) for p in pairs],
            )
        pg.commit()

    print(f"Projected {len(rows)} conflict events into Memgraph:")
    for row in counts:
        print(f"  {row['l']}: {row['c']}")
    print(f"Precomputed {len(pairs)} related-country pairs into Postgres.")


if __name__ == "__main__":
    sys.exit(main())
