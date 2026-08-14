"""
Discover partner cinemas and their official website link
"""

import streamlit as st
from scrapegraphai.graphs import SmartScraperGraph

from src.models.schemas import CinemaList


@st.cache_data(show_spinner="Recherche des cinémas en cours...")
def scrape_cinema_data(target_url: str, prompt_query: str, api_key: str):
    """Scrape the partner cinema list from `target_url` via an LLM-driven crawl.

    Args:
        target_url: Page listing the partner cinemas (BASE_URL).
        prompt_query: Extraction instructions for the LLM (BASE_PROMPT).
        api_key: Gemini API key.

    Returns:
        Tuple of (result dict matching CinemaList, execution info dict
        with token/time stats). Cached by Streamlit for the session.
    """
    graph_config = {
        "llm": {
            "api_key": api_key,
            "model": "google_genai/gemini-3.6-flash",
        },
        "verbose": True,
        "headless": True,
        "temperature": 0,
    }

    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt_query,
        source=target_url,
        schema=CinemaList,
        config=graph_config,
    )

    result = smart_scraper_graph.run()

    # Récupération des infos d'exécution (jetons, temps...)
    exec_info = smart_scraper_graph.get_execution_info()

    return result, exec_info
