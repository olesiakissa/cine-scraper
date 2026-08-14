"""
Environment variables and global constants shared across the app.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")


# paramétrage du scraper
# a une liste de salles et chaque lien contient les séances + les programmes caché(s) dans d'autres onglets (voir plus tard)
BASE_URL = "https://salles-cinema.com/carte-abonnement-ugc-illimite-mk2"
BASE_PROMPT = "Extract the complete list of cinema theaters accepting the subscription card in Paris. For each link, navigate to the link and extract the link of cinema prices and schedule. The final dict should contain the cinema name and the link to schedule and prices."

# per-domain CSS/XPath selectors cache (does not expire on a TTL, only on
# extraction failure) — kept separate from the TTL-based results
# cache, which will live in the same data/cache/ folder under a different file
SELECTORS_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "cache" / "selectors_cache.json"