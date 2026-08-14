"""
Un dictionnaire Python persisté sur disque en JSON :

{
  "mk2.com": { "container_selector": "...", "title_selector": "...", ... },
  "ugc.fr":  { "container_selector": "...", "title_selector": "...", ... },
  ...
}

Expose 3 fonctions qui sont l'équivalent de dict.get, dict[key] = value, et dict.pop(key),
mais qui persistent le changement dans le fichier JSON à chaque appel plutôt qu'en mémoire.

Couche de stockage pure : aucun appel LLM, aucune extraction BeautifulSoup/XPath
ici — extract_showtimes.py importera get_selectors/save_selectors/
invalidate_selectors depuis ce module.

La normalisation de domaine (_normalize_domain) n'est pas appelée par ces
3 fonctions : c'est la responsabilité de l'appelant de passer un
domaine déjà normalisé.
"""

import json
import os
from typing import Optional
from urllib.parse import urlparse

from pydantic import ValidationError

from src.config import SELECTORS_CACHE_PATH
from src.models.schemas import DomainSelectors


def _normalize_domain(url: str) -> str:
    """Extract a normalized cache key from any URL on a given site.

    Two URLs on the same site (e.g. `https://www.mk2.com/programme` and
    `https://mk2.com/salle/xyz`) must resolve to the same key, so the
    "www." prefix is stripped and the result is lowercased.
    """
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[len("www."):]
    return netloc


def _read_cache() -> dict:
    """Load the raw selectors cache as a plain dict.

    A missing file or invalid JSON both resolve to an empty dict rather than
    an exception — a corrupted/absent cache is treated as "nothing learned
    yet", never as an error to propagate.
    """
    try:
        raw = SELECTORS_CACHE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _write_cache(data: dict) -> None:
    """Atomically overwrite the selectors cache file with `data`.

    Writes to a temporary file first, then `os.replace()`s it into place, so
    a job interrupted mid-write never leaves a truncated/corrupted cache file
    behind.
    """
    SELECTORS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = SELECTORS_CACHE_PATH.with_name(SELECTORS_CACHE_PATH.name + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, SELECTORS_CACHE_PATH)


def get_selectors(domain: str) -> Optional[DomainSelectors]:
    """Return the cached selectors for `domain`, or None if not yet learned.

    A missing cache file, invalid JSON, an absent domain key, or a stored
    entry that no longer matches the DomainSelectors schema all resolve to
    None — never an exception. A cache miss simply means the next attempt
    should trigger a fresh LLM identification pass instead of
    breaking the scheduled job.
    """
    entry = _read_cache().get(domain)
    if entry is None:
        return None
    try:
        return DomainSelectors.model_validate(entry)
    except ValidationError:
        return None


def save_selectors(domain: str, selectors: DomainSelectors) -> None:
    """Upsert the selectors for `domain`, overwriting any existing entry."""
    data = _read_cache()
    data[domain] = selectors.model_dump(mode="json")
    _write_cache(data)


def invalidate_selectors(domain: str) -> None:
    """Remove the cached entry for `domain`, if any.

    Called when an extraction using the cached selectors returns 0 results
    (site restructured), forcing a fresh LLM identification pass on the next
    attempt for that domain.
    """
    data = _read_cache()
    data.pop(domain, None)
    _write_cache(data)
