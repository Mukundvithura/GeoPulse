"""Threshold boundaries for risk_level().

PRODUCT.md commits to the scoring being transparent and published: levels come
from conflict-class CAMEO counts *plus the share* of violent events, "so
high-media-volume countries like the USA do not sit permanently red". PRODUCT.md
states that narratively; the numbers live in risk_level() itself:

    conflict  violent >= 40 and share >= 0.10
    breaking  violent >= 15 and share >= 0.08
    elevated  (violent >= 5 and share >= 0.04) or quad4 >= 30
    stable    otherwise

Every one of those six numbers is pinned below on both sides of its boundary,
so changing a published threshold cannot pass silently.
"""

import pytest

from api.main import risk_level

LEVELS = {"stable", "elevated", "breaking", "conflict"}


# (quad4, quad3, violent, total, expected)
CASES = [
    # --- conflict: violent >= 40 AND share >= 0.10 ---
    ((0, 0, 40, 400), "conflict", "both bounds exactly met (40 violent, share 0.10)"),
    ((0, 0, 41, 410), "conflict", "clear of both bounds"),
    ((0, 0, 39, 390), "breaking", "violent one below 40, share fine"),
    ((0, 0, 40, 401), "breaking", "violent met, share a hair under 0.10"),

    # --- breaking: violent >= 15 AND share >= 0.08 ---
    ((0, 0, 16, 200), "breaking", "share exactly 0.08"),
    ((0, 0, 15, 187), "breaking", "violent exactly 15, share just over 0.08"),
    ((0, 0, 15, 188), "elevated", "violent met, share a hair under 0.08"),
    ((0, 0, 14, 140), "elevated", "violent one below 15"),

    # --- elevated, violent arm: violent >= 5 AND share >= 0.04 ---
    ((0, 0, 5, 125), "elevated", "both bounds exactly met (5 violent, share 0.04)"),
    ((0, 0, 8, 200), "elevated", "share exactly 0.04 at a higher count"),
    ((0, 0, 5, 126), "stable", "violent met, share a hair under 0.04"),
    ((0, 0, 4, 40), "stable", "violent one below 5 despite a 0.10 share"),

    # --- elevated, quad4 arm: quad4 >= 30 regardless of share ---
    ((30, 0, 0, 1000), "elevated", "quad4 exactly 30"),
    ((29, 0, 0, 1000), "stable", "quad4 one below 30"),
    ((30, 0, 0, 0), "elevated", "quad4 arm still fires when nothing was filed"),

    # --- stable / empty ---
    ((0, 0, 0, 0), "stable", "no events at all, no division by zero"),
    ((0, 0, 0, 1000), "stable", "plenty filed, none violent"),

    # --- precedence: the most severe matching rule wins ---
    ((500, 0, 100, 500), "conflict", "meets all three rules, conflict wins"),
    ((500, 0, 20, 200), "breaking", "meets breaking and both elevated arms"),
]


@pytest.mark.parametrize(
    "counts,expected,reason",
    CASES,
    ids=[f"{c[1]}-{c[2]}" for c in CASES],
)
def test_threshold_boundaries(counts, expected, reason):
    assert risk_level(*counts) == expected, reason


def test_high_volume_country_is_not_permanently_red():
    """The explicit promise in PRODUCT.md: a country with an enormous raw
    violent count but a small *share* must not sit red."""
    # 1000 violent events, but only 1% of everything filed
    assert risk_level(0, 0, 1000, 100_000) == "stable"
    # and it still is not red just short of the quad4 arm
    assert risk_level(29, 0, 1000, 100_000) == "stable"
    # the same 1000 violent events at a 10% share *is* conflict
    assert risk_level(0, 0, 1000, 10_000) == "conflict"


def test_quad3_does_not_affect_the_level():
    """quad3 is accepted and returned to the UI but is not part of scoring.
    If that changes, it should change deliberately."""
    for quad3 in (0, 1, 50, 10_000):
        assert risk_level(0, quad3, 0, 1000) == "stable"
        assert risk_level(0, quad3, 40, 400) == "conflict"


def test_only_ever_returns_a_known_level():
    """"none" is a client-side state for a country with no row at all;
    the function itself must only ever produce the four scored levels."""
    for quad4 in (0, 29, 30, 500):
        for violent in (0, 4, 5, 14, 15, 39, 40, 500):
            for total in (0, 1, 100, 10_000):
                assert risk_level(quad4, 0, violent, total) in LEVELS


def test_share_is_never_a_zero_division():
    """total == 0 must short-circuit to a 0.0 share, not raise."""
    for violent in (0, 5, 40, 1000):
        assert risk_level(0, 0, violent, 0) in LEVELS
