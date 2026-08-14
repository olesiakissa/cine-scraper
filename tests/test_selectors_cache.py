"""
Unit tests for src/scraping/selectors_cache.py : per-domain
selectors persistence, independent of network and LLM calls.
"""

import pytest

from src.models.schemas import DomainSelectors
from src.scraping import selectors_cache


@pytest.fixture(autouse=True)
def isolated_cache_path(tmp_path, monkeypatch):
    """Point the module's cache path at a temp file for every test.

    Prevents tests from touching the real data/cache/selectors_cache.json.
    """
    monkeypatch.setattr(selectors_cache, "SELECTORS_CACHE_PATH", tmp_path / "selectors_cache.json")


def _sample_selectors(domain: str = "mk2.com") -> DomainSelectors:
    return DomainSelectors(
        domain=domain,
        showtime_container_selector=".showtime",
        title_selector=".showtime .title",
        date_selector=".showtime .date",
        time_selector=".showtime .time",
        booking_url_selector=".showtime .book a",
    )


def test_save_then_get_round_trips():
    """save_selectors followed by get_selectors on the same domain returns the same data."""
    selectors = _sample_selectors()
    selectors_cache.save_selectors("mk2.com", selectors)

    result = selectors_cache.get_selectors("mk2.com")

    assert result == selectors


def test_get_selectors_missing_domain_returns_none():
    """A domain never saved resolves to None, not an exception."""
    assert selectors_cache.get_selectors("unknown.fr") is None


def test_get_selectors_corrupted_cache_returns_none():
    """Invalid JSON on disk resolves to None instead of raising."""
    selectors_cache.SELECTORS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    selectors_cache.SELECTORS_CACHE_PATH.write_text("{not valid json", encoding="utf-8")

    assert selectors_cache.get_selectors("mk2.com") is None


def test_invalidate_selectors_removes_only_target_domain():
    """invalidate_selectors drops the targeted entry and leaves others intact."""
    selectors_cache.save_selectors("mk2.com", _sample_selectors("mk2.com"))
    selectors_cache.save_selectors("ugc.fr", _sample_selectors("ugc.fr"))

    selectors_cache.invalidate_selectors("mk2.com")

    assert selectors_cache.get_selectors("mk2.com") is None
    assert selectors_cache.get_selectors("ugc.fr") is not None


def test_invalidate_selectors_missing_domain_does_not_raise():
    """Invalidating a domain that was never cached is a no-op, not an error."""
    selectors_cache.invalidate_selectors("never-cached.fr")


@pytest.mark.parametrize(
    "url",
    ["https://www.mk2.com/programme", "https://mk2.com/salle/xyz", "http://MK2.com/"],
)
def test_normalize_domain_same_site_same_key(url):
    """URLs on the same site (with/without www., any case) normalize to the same key."""
    assert selectors_cache._normalize_domain(url) == "mk2.com"