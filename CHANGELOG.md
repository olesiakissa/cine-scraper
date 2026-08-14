# Changelog

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), versioning [SemVer](https://semver.org/lang/fr/).

## [0.1.0] - 2026-08-14

### Ajouté
- Découplage de `main.py` en modules `src/config.py`, `src/models/schemas.py`, `src/scraping/discover_cinemas.py`, `src/ui/app.py`, `src/ui/components.py`
- `.env.example`
- Schémas Pydantic stricts `ScrapeError`, `Showtime`, `CinemaShowtimes`/`CinemaFailure` (union discriminée `CinemaResult`) dans `src/models/schemas.py`
- Tests unitaires `tests/test_schemas.py`
- Cache de sélecteurs CSS/XPath par domaine (`src/scraping/selectors_cache.py`, `data/cache/selectors_cache.json`)
- Schéma Pydantic `DomainSelectors`, constante `SELECTORS_CACHE_PATH`
- `.gitignore` (venv, `.env`, `data/cache/`)
- Tests unitaires `tests/test_selectors_cache.py`