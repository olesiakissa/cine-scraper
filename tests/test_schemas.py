"""
Unit tests for src/models/schemas.py : strict Pydantic schemas
for showtimes and per-cinema scrape errors.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from src.models.schemas import (
    CinemaFailure,
    CinemaResult,
    CinemaShowtimes,
    ScrapeError,
    ScrapeErrorType,
    Showtime,
)


def test_scrape_error_valid_all_fields():
    """A ScrapeError builds with all fields, including an explicit message."""
    error = ScrapeError(
        error_type=ScrapeErrorType.SELECTOR_FAILED,
        source="https://example-cinema.fr/programme",
        message="CSS selector '.showtime' matched 0 elements",
    )
    assert error.error_type == ScrapeErrorType.SELECTOR_FAILED
    assert error.message == "CSS selector '.showtime' matched 0 elements"


def test_scrape_error_message_defaults_to_none():
    """`message` is optional and explicitly null when omitted."""
    error = ScrapeError(error_type=ScrapeErrorType.NETWORK_ERROR, source="example.fr")
    assert error.message is None


def test_scrape_error_missing_required_field_raises():
    """Missing `source` (no default, no deduced value) must raise."""
    with pytest.raises(ValidationError):
        ScrapeError(error_type=ScrapeErrorType.NOT_FOUND)


def test_scrape_error_rejects_unexpected_field():
    """extra="forbid" rejects fields the LLM might invent."""
    with pytest.raises(ValidationError):
        ScrapeError(
            error_type=ScrapeErrorType.NOT_FOUND,
            source="example.fr",
            unexpected_field="surprise",
        )


def test_showtime_valid_all_fields():
    """A Showtime builds with all fields, including a booking link."""
    showtime = Showtime(
        title="Dune",
        date="2026-08-14",
        time="20:30",
        booking_url="https://example-cinema.fr/reserve/123",
    )
    assert showtime.title == "Dune"
    assert showtime.booking_url == "https://example-cinema.fr/reserve/123"


def test_showtime_booking_url_explicit_none():
    """`booking_url` accepts explicit None (no reservation link found)."""
    showtime = Showtime(title="Dune", date="2026-08-14", time="20:30", booking_url=None)
    assert showtime.booking_url is None


def test_showtime_missing_required_field_raises():
    """Missing `title` must raise, not be silently defaulted to "" ."""
    with pytest.raises(ValidationError):
        Showtime(date="2026-08-14", time="20:30")


def test_showtime_rejects_unexpected_field():
    """extra="forbid" rejects fields the LLM might invent."""
    with pytest.raises(ValidationError):
        Showtime(title="Dune", date="2026-08-14", time="20:30", room="Salle 3")


def test_cinema_showtimes_requires_at_least_one_showtime():
    """An empty showtimes list is not a valid "ok" result — must be a ScrapeError instead."""
    with pytest.raises(ValidationError):
        CinemaShowtimes(cinema_name="UGC Ciné Cité Les Halles", showtimes=[])


def test_cinema_result_discriminates_ok_from_error():
    """CinemaResult accepts either an ok payload or an error payload, tagged by `status`."""
    adapter = TypeAdapter(CinemaResult)

    ok_result = adapter.validate_python(
        {
            "status": "ok",
            "cinema_name": "Mk2 Bibliothèque",
            "showtimes": [{"title": "Dune", "date": "2026-08-14", "time": "20:30"}],
        }
    )
    assert isinstance(ok_result, CinemaShowtimes)

    error_result = adapter.validate_python(
        {
            "status": "error",
            "cinema_name": "Mk2 Bibliothèque",
            "error": {"error_type": "not_found", "source": "mk2.fr"},
        }
    )
    assert isinstance(error_result, CinemaFailure)


def test_cinema_result_rejects_unknown_status():
    """A `status` outside the "ok"/"error" tags must be rejected, not coerced."""
    adapter = TypeAdapter(CinemaResult)
    with pytest.raises(ValidationError):
        adapter.validate_python({"status": "partial", "cinema_name": "Mk2 Bibliothèque"})