# 🎬 Ciné Scraper Paris

App perso pour regrouper les séances de cinéma du jour à Paris (salles UGC Illimité, Mk2, indépendantes) sans visiter chaque site.

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # puis renseigner GEMINI_API_KEY
```

## Lancer l'app

```bash
streamlit run src/ui/app.py
```

## Structure

```
src/
  config.py                   # env vars, constantes (BASE_URL, BASE_PROMPT, SELECTORS_CACHE_PATH)
  models/schemas.py           # schémas Pydantic (Cinema, CinemaList, Showtime, ScrapeError, CinemaResult, DomainSelectors)
  scraping/
    discover_cinemas.py       # liste des salles + lien site officiel
    extract_showtimes.py      # séances du jour
    selectors_cache.py        # cache de sélecteurs CSS/XPath par domaine (data/cache/selectors_cache.json, git-ignoré)
  ui/
    app.py                    # entrypoint Streamlit
    components.py             # rendu de la grille de cinémas
```

## Tests

```bash
pytest
```