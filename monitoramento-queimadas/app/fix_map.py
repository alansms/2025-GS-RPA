import streamlit as st
import folium
from streamlit_folium import folium_static
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def criar_mapa(df_mapa):
    try:
        logger.debug("Iniciando criação do mapa com %d pontos", len(df_mapa))

        # Criar mapa base
        m = folium.Map(
            location=[-15.8, -47.9],  # Centro do Brasil
            zoom_start=4,
            tiles='CartoDB positron'  # Estilo mais leve e limpo
        )

        # Adicionar marcadores
        for idx, row in df_mapa.iterrows():
            try:
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color='red',
                    fill=True,
                    popup=f"Município: {row['municipio']}<br>Bioma: {row['bioma']}<br>UF: {row['uf']}<br>Data: {row['data']}"
                ).add_to(m)
            except Exception as e:
                logger.error(f"Erro ao adicionar marcador: {e}", exc_info=True)

        logger.debug("Mapa criado com sucesso")
        return m

    except Exception as e:
        logger.error("Erro ao criar mapa: %s", str(e), exc_info=True)
        st.error("Ocorreu um erro ao criar o mapa. Verifique os logs para mais detalhes.")
        return None

def exibir_mapa(df_mapa):
    try:
        if df_mapa is not None and not df_mapa.empty:
            mapa = criar_mapa(df_mapa)
            if mapa:
                folium_static(mapa)
        else:
            st.warning("Não há dados disponíveis para exibir no mapa.")
    except Exception as e:
        logger.error("Erro ao exibir mapa: %s", str(e), exc_info=True)
        st.error("Ocorreu um erro ao exibir o mapa. Verifique os logs para mais detalhes.")

# Exibir mapa
exibir_mapa(df_mapa)
