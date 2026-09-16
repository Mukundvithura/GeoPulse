"""Phase 2 collector: RSS headlines -> GLiNER NER -> country tagging -> Postgres.

Usage:  python rss_collector.py
Safe to re-run any time; duplicate URLs are skipped.
"""

import re
import sys
from pathlib import Path
from datetime import datetime, timezone

import feedparser
import psycopg
from psycopg.types.json import Jsonb

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DB_URL
from ner import extract

FEEDS = {
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "The Guardian World": "https://www.theguardian.com/world/rss",
    "DW": "https://rss.dw.com/rdf/rss-en-world",
    "France24": "https://www.france24.com/en/rss",
    "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
    "UN News": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
}

INSERT_SQL = """
    INSERT INTO articles (url, source, title, summary, published, entities, countries)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING
    RETURNING id
"""


def clean_text(html: str) -> str:
    """RSS summaries carry HTML and links; NER must only ever see prose."""
    text = re.sub(r"<[^>]+>", " ", html)          # strip tags
    text = re.sub(r"https?://\S+", " ", text)     # strip URLs
    return re.sub(r"\s+", " ", text).strip()


def parse_time(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return datetime(*t[:6], tzinfo=timezone.utc) if t else None


def main() -> None:
    total_new = 0
    with psycopg.connect(DB_URL) as conn:
        for source, url in FEEDS.items():
            feed = feedparser.parse(url)
            new = 0
            for entry in feed.entries[:30]:
                link = entry.get("link")
                title = (entry.get("title") or "").strip()
                if not link or not title:
                    continue
                summary = clean_text(entry.get("summary") or "")[:1000]
                # NER runs on title + summary; that's where the signal is
                entities, countries = extract(f"{title}. {summary}")
                with conn.cursor() as cur:
                    cur.execute(INSERT_SQL, (
                        link, source, title, summary or None,
                        parse_time(entry), Jsonb(entities), countries,
                    ))
                    if cur.fetchone():
                        new += 1
            conn.commit()
            total_new += new
            print(f"{source}: {new} new articles")
    print(f"\nDone. {total_new} new articles stored.")


if __name__ == "__main__":
    sys.exit(main())
