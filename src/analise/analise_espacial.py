import pandas as pd
import folium
from folium import plugins
import logging

logger = logging.getLogger('queimadas.analise')

def criar_mapa_focos(df: pd.DataFrame) -> folium.Map:
    """
    Cria um mapa interativo com os focos de queimada.

    Args:
        df (pd.DataFrame): DataFrame com os dados de focos

    Returns:
        folium.Map: Mapa interativo com os focos
    """
    try:
        # Criar mapa base
        mapa = folium.Map(
            location=[-15.7801, -47.9292],
            zoom_start=4,
            tiles='CartoDB positron'
        )

        # Criar cluster de marcadores
        marker_cluster = plugins.MarkerCluster()

        # Adicionar pontos ao mapa
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color='red',
                fill=True,
                popup=f"UF: {row['uf']}<br>Bioma: {row['bioma']}"
            ).add_to(marker_cluster)

        marker_cluster.add_to(mapa)

        logger.info(f"Mapa criado com {len(df)} pontos")
        return mapa

    except Exception as e:
        logger.error(f"Erro ao criar mapa: {str(e)}")
        return None
