"""Phase 4: relation extraction — who did what to whom, using what.

Runs the local LLM (Ollama) over stored articles with constrained JSON
output. Anything that fails validation is skipped, never stored (per the
SDD: quarantine, don't guess).

Usage:  python relation_extractor.py [--limit 40]
"""

import argparse
import json
import sys

import psycopg
import requests

DB_URL = "postgresql://geopulse:geopulse@localhost:5432/geopulse"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

ACTIONS = {
    "attacked", "struck", "bombed", "invaded", "sanctioned", "warned",
    "threatened", "met", "signed", "aided", "supplied", "condemned",
    "arrested", "killed", "seized", "negotiated", "withdrew", "deployed",
}

PROMPT = """Extract factual relations from this news text. Reply with ONLY
valid JSON, no other text:
{{"relations": [{{"actor": "...", "action": "...", "target": "...",
"location": "..." or null, "instrument": "..." or null}}]}}

Rules: action must be one of: {actions}.
Only include relations the text explicitly states. If none, return
{{"relations": []}}.

Text: {text}
"""


def extract(text: str) -> list[dict]:
    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": PROMPT.format(actions=", ".join(sorted(ACTIONS)), text=text[:1200]),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_predict": 300},
    }, timeout=180)
    resp.raise_for_status()
    try:
        data = json.loads(resp.json()["response"])
        out = []
        for r in data.get("relations", []):
            # schema validation: quarantine anything malformed
            if (isinstance(r, dict) and r.get("actor") and r.get("target")
                    and str(r.get("action", "")).lower() in ACTIONS):
                out.append({
                    "actor": str(r["actor"])[:120],
                    "action": str(r["action"]).lower(),
                    "target": str(r["target"])[:120],
                    "location": (str(r["location"])[:120] if r.get("location") else None),
                    "instrument": (str(r["instrument"])[:120] if r.get("instrument") else None),
                })
        return out
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40,
                    help="max articles to process this run")
    args = ap.parse_args()

    with psycopg.connect(DB_URL) as conn:
        rows = conn.execute(
            """
            SELECT a.id, a.title, a.summary FROM articles a
            WHERE a.countries != '{}'
              AND NOT EXISTS (SELECT 1 FROM relations r WHERE r.article_id = a.id)
            ORDER BY a.published DESC NULLS LAST
            LIMIT %s
            """,
            (args.limit,),
        ).fetchall()

        total = 0
        for i, (aid, title, summary) in enumerate(rows, 1):
            rels = extract(f"{title}. {summary or ''}")
            for r in rels:
                conn.execute(
                    "INSERT INTO relations (article_id, actor, action, target, "
                    "location, instrument) VALUES (%s, %s, %s, %s, %s, %s)",
                    (aid, r["actor"], r["action"], r["target"],
                     r["location"], r["instrument"]),
                )
            # mark processed even when empty, so re-runs skip this article
            if not rels:
                conn.execute(
                    "INSERT INTO relations (article_id, actor, action, target) "
                    "VALUES (%s, '', 'none', NULL)", (aid,))
            conn.commit()
            total += len(rels)
            print(f"[{i}/{len(rows)}] article {aid}: {len(rels)} relations")
        print(f"\nDone. {total} relations extracted.")


if __name__ == "__main__":
    sys.exit(main())
