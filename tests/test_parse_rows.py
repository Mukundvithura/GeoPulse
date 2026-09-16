"""parse_rows() -- the clean/filter stage of the GDELT collector.

GDELT export rows are 61 tab-separated columns with no header. parse_rows is
the project's "skip, never guess" boundary (product principle 4): a row that
cannot be trusted is dropped, never defaulted into existence. These tests pin
what gets dropped and what survives.
"""

from datetime import date

import pytest

from gdelt_collector import parse_rows

# Column indexes parse_rows actually reads, by the names used in the collector.
IDX = {
    "id": 0, "date": 1, "actor1": 6, "actor2": 16, "code": 26, "root": 28,
    "quad": 29, "goldstein": 30, "sources": 32, "articles": 33, "tone": 34,
    "place": 52, "fips": 53, "lat": 56, "lon": 57, "url": 60,
}
NCOLS = 61

GOOD = {
    "id": "999000001", "date": "20260916", "actor1": "UNITED STATES",
    "actor2": "RUSSIA", "code": "190", "root": "19", "quad": "4",
    "goldstein": "-9.0", "sources": "7", "articles": "20", "tone": "-5.5",
    "place": "Washington", "fips": "US", "lat": "38.9", "lon": "-77.0",
    "url": "https://example.test/story",
}

# The tuple parse_rows builds, in order, for a GOOD row.
EXPECTED_GOOD = (
    999000001, date(2026, 9, 16), "UNITED STATES", "RUSSIA", "190", "19",
    4, -9.0, 7, 20, -5.5, "USA", "Washington", 38.9, -77.0,
    "https://example.test/story",
)


def make_row(**over) -> list:
    """A 61-column GDELT row, valid unless a field is overridden."""
    row = [""] * NCOLS
    for name, value in {**GOOD, **over}.items():
        row[IDX[name]] = value
    return row


def to_csv(*rows) -> bytes:
    return "\n".join("\t".join(r) for r in rows).encode("utf-8")


# --------------------------------------------------------------- happy path

def test_a_valid_row_parses_to_the_expected_tuple():
    assert parse_rows(to_csv(make_row())) == [EXPECTED_GOOD]


def test_fips_is_translated_to_iso3():
    (parsed,) = parse_rows(to_csv(make_row(fips="UK")))
    assert parsed[11] == "GBR"


def test_several_valid_rows_keep_their_order():
    rows = [make_row(id=str(i)) for i in (1, 2, 3)]
    assert [r[0] for r in parse_rows(to_csv(*rows))] == [1, 2, 3]


# ------------------------------------------------------------- empty input

@pytest.mark.parametrize("payload", [b"", b"\n", b"\n\n\n", b"   "],
                         ids=["empty", "one-newline", "blank-lines", "spaces"])
def test_empty_input_yields_no_rows(payload):
    assert parse_rows(payload) == []


def test_trailing_newline_does_not_produce_a_phantom_row():
    assert parse_rows(to_csv(make_row()) + b"\n") == [EXPECTED_GOOD]


# ------------------------------------------------------------ short rows

@pytest.mark.parametrize("ncols", [0, 1, 26, 53, 60],
                         ids=lambda n: f"{n}-columns")
def test_rows_with_too_few_columns_are_dropped(ncols):
    assert parse_rows(to_csv(make_row()[:ncols])) == []


def test_extra_columns_are_tolerated():
    """A row longer than 61 columns still parses; only >= 61 is required."""
    assert parse_rows(to_csv(make_row() + ["extra", "more"])) == [EXPECTED_GOOD]


# ------------------------------------------------------- unmapped / missing

@pytest.mark.parametrize("fips", ["ZZ", "XX", "", "us", "USA", "1"],
                         ids=["ZZ", "XX", "empty", "lowercase", "iso3", "digit"])
def test_unmapped_or_missing_fips_codes_are_dropped(fips):
    """Only the ~168 FIPS codes in the lookup survive. An unknown country is
    skipped rather than stored with a guessed or null ISO3."""
    assert parse_rows(to_csv(make_row(fips=fips))) == []


def test_missing_event_code_is_dropped():
    assert parse_rows(to_csv(make_row(code=""))) == []


# ------------------------------------------------------------- malformed

@pytest.mark.parametrize("over", [
    {"date": "notadate"},
    {"date": "2026-09-16"},
    {"date": ""},
    {"date": "20261347"},
    {"id": "abc"},
    {"id": ""},
    {"id": "12.5"},
    {"quad": ""},
    {"quad": "high"},
    {"goldstein": "minus nine"},
    {"sources": "many"},
    {"articles": "lots"},
    {"tone": "grim"},
    {"lat": "north"},
    {"lon": "west"},
], ids=lambda o: "-".join(f"{k}={v!r}" for k, v in o.items()))
def test_malformed_fields_drop_the_row(over):
    """Anything that fails to coerce is skipped, not defaulted."""
    assert parse_rows(to_csv(make_row(**over))) == []


def test_one_bad_row_does_not_lose_the_good_ones():
    payload = to_csv(
        make_row(id="1"),
        make_row(id="2", date="notadate"),   # dropped
        make_row(id="3", fips="ZZ"),         # dropped
        make_row(id="4")[:10],               # dropped, too short
        make_row(id="5"),
    )
    assert [r[0] for r in parse_rows(payload)] == [1, 5]


# ------------------------------------------------- empty optional fields

def test_empty_numeric_fields_default_to_zero():
    (parsed,) = parse_rows(
        to_csv(make_row(goldstein="", sources="", articles="", tone="")))
    assert parsed[7] == 0.0    # goldstein
    assert parsed[8] == 0      # num_sources
    assert parsed[9] == 0      # num_articles
    assert parsed[10] == 0.0   # avg_tone


def test_empty_text_and_coordinates_become_none():
    (parsed,) = parse_rows(
        to_csv(make_row(actor1="", actor2="", place="", url="", lat="", lon="")))
    assert parsed[2] is None    # actor1
    assert parsed[3] is None    # actor2
    assert parsed[12] is None   # place
    assert parsed[13] is None   # lat
    assert parsed[14] is None   # lon
    assert parsed[15] is None   # source_url


# ------------------------------------------------------------- encoding

def test_invalid_utf8_does_not_raise():
    """The collector decodes with errors='replace'; a mangled byte must not
    take down the whole file."""
    payload = to_csv(make_row()).replace(b"Washington", b"Wash\xffngton")
    parsed = parse_rows(payload)
    assert len(parsed) == 1
    assert parsed[0][12].startswith("Wash")


def test_non_ascii_place_names_survive():
    (parsed,) = parse_rows(to_csv(make_row(place="Kyiv, Ukraïna", fips="UP")))
    assert parsed[12] == "Kyiv, Ukraïna"
    assert parsed[11] == "UKR"
