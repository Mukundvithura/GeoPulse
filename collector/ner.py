"""Phase 2 NER: GLiNER (zero-shot, custom labels) + country tagging.

The model downloads (~600 MB) on first run and is cached by HuggingFace.
Country tagging maps entity/text mentions to ISO3 using names from the
same countries.geojson the globe uses, plus common aliases.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

LABELS = ["person", "organization", "country", "location", "weapon", "military unit"]

ALIASES = {
    "us": "USA", "u.s.": "USA", "united states": "USA", "america": "USA",
    "uk": "GBR", "u.k.": "GBR", "britain": "GBR", "united kingdom": "GBR",
    "russia": "RUS", "ukraine": "UKR", "china": "CHN", "iran": "IRN",
    "israel": "ISR", "gaza": "PSE", "palestine": "PSE", "west bank": "PSE",
    "north korea": "PRK", "south korea": "KOR", "uae": "ARE", "syria": "SYR",
    "turkey": "TUR", "türkiye": "TUR", "saudi arabia": "SAU", "myanmar": "MMR",
    "drc": "COD", "dr congo": "COD", "ivory coast": "CIV", "czechia": "CZE",
    "netherlands": "NLD", "bolivia": "BOL", "venezuela": "VEN", "laos": "LAO",
    "vietnam": "VNM", "moldova": "MDA", "tanzania": "TZA", "eswatini": "SWZ",
}


@lru_cache(maxsize=1)
def country_lookup() -> dict:
    """name (lowercase) -> ISO3, built from the globe's own geojson."""
    geo = json.loads(
        (Path(__file__).resolve().parent.parent / "web" / "countries.geojson")
        .read_text(encoding="utf-8")
    )
    lut = dict(ALIASES)
    for f in geo["features"]:
        p = f["properties"]
        iso3 = p.get("ADM0_A3")
        for key in ("NAME", "NAME_LONG", "ADMIN"):
            if p.get(key):
                lut[p[key].lower()] = iso3
    return lut


@lru_cache(maxsize=1)
def get_model():
    from gliner import GLiNER
    print("Loading GLiNER model (first run downloads ~600 MB)...")
    return GLiNER.from_pretrained("urchade/gliner_small-v2.1")


def extract(text: str) -> tuple[list[dict], list[str]]:
    """Returns (deduplicated entities, iso3 countries) for a piece of text."""
    raw = get_model().predict_entities(text[:1500], LABELS, threshold=0.4)
    seen, entities = set(), []
    for e in raw:
        key = (e["text"].lower(), e["label"])
        if key not in seen:
            seen.add(key)
            entities.append({"text": e["text"], "label": e["label"]})

    lut = country_lookup()
    countries = set()
    for e in entities:
        if e["label"] in ("country", "location"):
            iso3 = lut.get(e["text"].lower().strip())
            if iso3:
                countries.add(iso3)
    # catch plain-text mentions NER missed (e.g. "Gaza" mid-sentence)
    lowered = " " + re.sub(r"[^\w\s.]", " ", text.lower()) + " "
    for name, iso3 in lut.items():
        if len(name) > 3 and f" {name} " in lowered:
            countries.add(iso3)
    return entities, sorted(countries)
