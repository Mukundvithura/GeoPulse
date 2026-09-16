"""GeoPulse Phase 1 collector.

Downloads GDELT 2.0 event files (published every 15 minutes), cleans the rows,
and stores structured events in Postgres.

Pipeline stages (per the SDD, scoped for Phase 1):
  fetch -> clean/filter -> entity mapping (GDELT pre-extracted) -> geocode
  (FIPS->ISO3 + lat/lon from GDELT) -> store.

Usage:
  python gdelt_collector.py               # latest 15-min file only
  python gdelt_collector.py --backfill 6  # also last 6 hours of files
"""

import argparse
import csv
import io
import sys
import zipfile
from datetime import datetime, timedelta, timezone

import psycopg
import requests

from fips_iso import FIPS_TO_ISO3

GDELT_BASE = "http://data.gdeltproject.org/gdeltv2"
DB_URL = "postgresql://geopulse:geopulse@localhost:6543/geopulse"

# Column indexes in GDELT 2.0 export CSV (61 tab-separated columns, no header)
COL_ID, COL_DATE = 0, 1
COL_ACTOR1_NAME, COL_ACTOR2_NAME = 6, 16
COL_EVENT_CODE, COL_ROOT_CODE, COL_QUAD = 26, 28, 29
COL_GOLDSTEIN, COL_NUM_SOURCES, COL_NUM_ARTICLES, COL_AVG_TONE = 30, 32, 33, 34
COL_GEO_NAME, COL_GEO_COUNTRY, COL_GEO_LAT, COL_GEO_LON = 52, 53, 56, 57
COL_SOURCE_URL = 60


def latest_export_url() -> str:
    """GDELT publishes the URL of the newest file in lastupdate.txt."""
    txt = requests.get(f"{GDELT_BASE}/lastupdate.txt", timeout=30).text
    for line in txt.splitlines():
        if line.endswith(".export.CSV.zip"):
            return line.split()[-1]
    raise RuntimeError("No export URL found in lastupdate.txt")


def backfill_urls(hours: int) -> list[str]:
    """GDELT file names are predictable: one per 15-minute mark (UTC)."""
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    now -= timedelta(minutes=now.minute % 15 + 15)  # last completed slot
    urls = []
    for i in range(hours * 4):
        ts = (now - timedelta(minutes=15 * i)).strftime("%Y%m%d%H%M%S")
        urls.append(f"{GDELT_BASE}/{ts}.export.CSV.zip")
    return urls


def parse_rows(csv_bytes: bytes) -> list[tuple]:
    """Clean + filter: keep rows with a known country and valid event code."""
    rows = []
    text = csv_bytes.decode("utf-8", errors="replace")
    for rec in csv.reader(io.StringIO(text), delimiter="\t"):
        if len(rec) < 61:
            continue
        iso3 = FIPS_TO_ISO3.get(rec[COL_GEO_COUNTRY])
        if not iso3 or not rec[COL_EVENT_CODE]:
            continue
        try:
            rows.append((
                int(rec[COL_ID]),
                datetime.strptime(rec[COL_DATE], "%Y%m%d").date(),
                rec[COL_ACTOR1_NAME] or None,
                rec[COL_ACTOR2_NAME] or None,
                rec[COL_EVENT_CODE],
                rec[COL_ROOT_CODE],
                int(rec[COL_QUAD]),
                float(rec[COL_GOLDSTEIN] or 0),
                int(rec[COL_NUM_SOURCES] or 0),
                int(rec[COL_NUM_ARTICLES] or 0),
                float(rec[COL_AVG_TONE] or 0),
                iso3,
                rec[COL_GEO_NAME] or None,
                float(rec[COL_GEO_LAT]) if rec[COL_GEO_LAT] else None,
                float(rec[COL_GEO_LON]) if rec[COL_GEO_LON] else None,
                rec[COL_SOURCE_URL] or None,
            ))
        except (ValueError, IndexError):
            continue  # malformed row -> skip
    return rows


INSERT_SQL = """
    INSERT INTO events (id, event_date, actor1, actor2, cameo_code, cameo_root,
                        quad_class, goldstein, num_sources, num_articles, avg_tone,
                        country_iso3, place, lat, lon, source_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING
"""


def ingest(url: str, conn) -> int:
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        return 0
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_bytes = zf.read(zf.namelist()[0])
    rows = parse_rows(csv_bytes)
    if rows:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, rows)
        conn.commit()
    return len(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", type=int, default=0, metavar="HOURS",
                    help="also ingest the last N hours of 15-min files")
    args = ap.parse_args()

    urls = [latest_export_url()]
    if args.backfill:
        urls += backfill_urls(args.backfill)

    with psycopg.connect(DB_URL) as conn:
        total = 0
        for i, url in enumerate(dict.fromkeys(urls), 1):  # dedupe, keep order
            n = ingest(url, conn)
            total += n
            print(f"[{i}/{len(urls)}] {url.rsplit('/', 1)[-1]}: {n} events")
        print(f"\nDone. {total} events ingested (duplicates skipped by Postgres).")


if __name__ == "__main__":
    sys.exit(main())
