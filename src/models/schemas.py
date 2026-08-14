"""
Pydantic schemas for cinema discovery and showtime extraction.
"""

from datetime import date
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class Cinema(BaseModel):
    """A single cinema theater and its official website link."""

    name: str = Field(description="The name of the cinema theater")
    url: Optional[str] = Field(
        None, description="The url link of the cinema theater website, or null/None if there is no link")


class CinemaList(BaseModel):
    """Wrapper list returned by the discovery scraper."""

    cinemas: List[Cinema]


class ScrapeErrorType(str, Enum):
    """Categorized reasons an extraction can fail for a cinema.

    Kept as a closed set (rather than a free-form string) so every failure
    mode is explicitly handled instead of silently stringified.
    """

    NOT_FOUND = "not_found"  # showtime/program page could not be located
    SELECTOR_FAILED = "selector_failed"  # cached CSS/XPath selector no longer matches (site structure changed)
    PDF_UNREADABLE = "pdf_unreadable"  # independent theater's PDF program could not be parsed
    NETWORK_ERROR = "network_error"  # request failed (timeout, DNS, HTTP error, ...)


class ScrapeError(BaseModel):
    """
    Explicit failure result for a cinema whose showtime extraction failed.
    """

    model_config = ConfigDict(extra="forbid")

    error_type: ScrapeErrorType = Field(description="Categorized reason for the failure")
    source: str = Field(description="Domain or URL the extraction was attempted on")
    message: Optional[str] = Field(
        None, description="Optional human-readable detail, or null/None if not available")


class Showtime(BaseModel):
    """A single film screening.

    Note: `date` and `time` are kept as plain strings on purpose — parsing,
    format validation and cross-field coherence checks belong to ticket 7,
    not to this schema definition.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Film title")
    date: str = Field(description="Screening date")
    time: str = Field(description="Screening time")
    booking_url: Optional[str] = Field(
        None, description="Booking link for this screening, or null/None if there is no link")


class CinemaShowtimes(BaseModel):
    """Successful result: at least one showtime found for a cinema.

    `showtimes` requires at least one entry: a cinema with zero screenings
    for the day must be reported as a `ScrapeError` (e.g. NOT_FOUND) instead
    of an empty list standing in silently for "nothing found".
    """

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    cinema_name: str = Field(description="Name of the cinema these showtimes belong to")
    showtimes: List[Showtime] = Field(min_length=1, description="Today's screenings for this cinema")


class CinemaFailure(BaseModel):
    """Failed result: extraction error for a cinema."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["error"] = "error"
    cinema_name: str = Field(description="Name of the cinema the extraction failed for")
    error: ScrapeError


# Discriminated union: a cinema result is either showtimes or an error,
# never both, never neither — enforced structurally via the `status` tag
# rather than with two side-by-side optional fields.
CinemaResult = Annotated[Union[CinemaShowtimes, CinemaFailure], Field(discriminator="status")]


class DomainSelectors(BaseModel):
    """CSS/XPath selectors identified once for a cinema's program domain.

    Persisted so the LLM selector-identification step runs a single time per
    domain instead of on every scrape; subsequent extractions reuse these
    selectors directly (BeautifulSoup/XPath, no LLM call) until they stop
    matching (0 results found), which signals the site changed structure and
    should trigger a fresh LLM identification pass.
    """

    model_config = ConfigDict(extra="forbid")

    domain: str = Field(description="Normalized domain these selectors were identified for")
    showtime_container_selector: str = Field(
        description="Selector matching each individual screening block on the program page")
    title_selector: str = Field(description="Selector for the film title within a screening block")
    date_selector: str = Field(description="Selector for the screening date within a screening block")
    time_selector: str = Field(description="Selector for the screening time within a screening block")
    booking_url_selector: str = Field(
        description="Selector for the booking link within a screening block")
    last_updated: Optional[date] = Field(
        None, description="Date these selectors were last identified by the LLM, or null/None if unknown")