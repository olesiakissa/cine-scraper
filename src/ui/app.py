"""
Entrypoint Streamlit
"""

import sys
from pathlib import Path

# `streamlit run src/ui/app.py` only adds this file's own folder to sys.path,
# never the project root, so `from src...` imports below would otherwise fail
# with ModuleNotFoundError. Must run before any `src.*` import.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd  
import streamlit as st

from src.config import API_KEY, BASE_PROMPT, BASE_URL
from src.scraping.discover_cinemas import scrape_cinema_data
from src.ui.components import render_data_table

st.set_page_config(page_title="Ciné Scraper", page_icon="🎬", layout="wide")
st.title("🎬 Ciné Scraper")


# Lancement du scraping (Streamlit va lire le cache ou lancer l'extraction)
if API_KEY:
    result, exec_info = scrape_cinema_data(
        target_url=BASE_URL, prompt_query=BASE_PROMPT, api_key=API_KEY)

    st.subheader("Résultats de l’extraction")

    with st.expander("Statistiques d'exécution (Tokens, temps...)"):
        st.write(exec_info)

    if "cinemas" in result:
        cinemas_data = result["cinemas"]

        df = pd.DataFrame(cinemas_data)

        # Améliorer la lisibilité (remplacer les valeurs None/null par du texte)
        df["url"] = df["url"].fillna("Aucun lien disponible")

        st.subheader("🎬 Liste des cinémas partenaires")

        render_data_table(df)

        # Proposer le téléchargement en CSV (comme dans la démo officielle ScrapeGraphAI)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger la liste au format CSV",
            data=csv_data,
            file_name="cinemas_partenaires.csv",
            mime="text/csv"
        )
    else:
        st.warning("Aucune donnée de cinéma n'a été trouvée dans le résultat.")

else:
    st.error("Clé GEMINI_API_KEY manquante dans votre fichier .env")



# Bouton pour forcer la mise à jour (vider le cache pendant les tests)
if st.button("Forcer la mise à jour (Vider le cache)"):
    st.cache_data.clear()
    st.rerun()
