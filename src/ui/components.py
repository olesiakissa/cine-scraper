"""
Reusable Streamlit rendering components for the cinema data grid.
"""

import pandas as pd
import streamlit as st


def render_data_table(df: pd.DataFrame) -> None:
    """Render the cinema list as a sortable, clickable Streamlit table.

    Args:
        df: DataFrame with at least "name" and "url" columns.
    """
    st.dataframe(
        df,
        column_config={
            "name": st.column_config.TextColumn("Nom du Cinéma"),
            # Rend les liens directement cliquables
            "url": st.column_config.LinkColumn("Lien"),
        },
        use_container_width=True,  # Prend toute la largeur de la page
        # Masque la colonne d'index (0, 1, 2...) pour un rendu plus propre
        hide_index=True,
    )
