import os
import sys
import logging
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from glob import glob
import folium
from streamlit_folium import folium_static

# Configuração da página Streamlit
st.set_page_config(
    page_title="Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar tema e estilos
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo-container {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Adicionar diretório src ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)

# Importar módulos do projeto (agora usando os caminhos corretos)
from coleta.utils_coleta import coletar_dados_inpe
from analise.analise_temporal import gerar_serie_temporal
from analise.analise_espacial import criar_mapa_focos
from relatorios.relatorio import main as gerar_relatorio

# Criar diretórios necessários
for dir_path in ['output/logs', 'output/dados_brutos', 'output/dados_limpos', 'output/relatorios']:
    os.makedirs(dir_path, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/logs/streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('queimadas')

# Título e descrição
st.title("Sistema de Monitoramento de Queimadas")
st.markdown("""
Este sistema monitora focos de queimadas em todo o Brasil, fornecendo visualizações 
interativas e análises detalhadas por estado e bioma.
""")

# Sidebar
with st.sidebar:
    # Logo da FIAP
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    logo_paths = ["Fiap-logo-branco.jpg", "logo_fiap.jpg"]
    logo_path = next((path for path in logo_paths if os.path.exists(path)), None)
    if logo_path:
        st.image(logo_path, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.title("Filtros")

    # Data atual e período padrão
    data_atual = datetime.now()
    data_fim = st.date_input("Data Final", data_atual)
    data_inicio = st.date_input("Data Inicial", data_atual - timedelta(days=30))

    # Carregar dados
    @st.cache_data(ttl=3600)
    def carregar_dados():
        try:
            df = coletar_dados_inpe(
                data_inicio.strftime("%Y-%m-%d"),
                data_fim.strftime("%Y-%m-%d")
            )
            if df is not None and not df.empty:
                return df
            else:
                return pd.read_csv("output/dados_limpos/dados_exemplo.csv")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return None

    df = carregar_dados()

    if df is not None:
        # Filtros de UF e Bioma
        ufs = sorted(df['uf'].unique())
        biomas = sorted(df['bioma'].unique())

        ufs_selecionadas = st.multiselect("Estados", ufs)
        biomas_selecionados = st.multiselect("Biomas", biomas)

        # Filtrar dados
        if ufs_selecionadas:
            df = df[df['uf'].isin(ufs_selecionadas)]
        if biomas_selecionados:
            df = df[df['bioma'].isin(biomas_selecionados)]

        # Mostrar contagens
        st.metric("Total de Focos", len(df))

        # Botão para gerar relatório
        if st.button("Gerar Relatório"):
            try:
                relatorio_path = gerar_relatorio(df, "output/relatorios")
                with open(relatorio_path, "rb") as file:
                    st.download_button(
                        "Baixar Relatório",
                        file,
                        file_name="relatorio_queimadas.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")

# Layout principal
if df is not None and not df.empty:
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média Diária", f"{len(df)/30:.1f}")
    with col2:
        st.metric("Estados Afetados", len(df['uf'].unique()))
    with col3:
        st.metric("Biomas Afetados", len(df['bioma'].unique()))

    # Gráfico de série temporal
    st.subheader("Série Temporal de Focos")
    serie = df.groupby('data').size().reset_index(name='focos')
    fig = px.line(serie, x='data', y='focos',
                  title="Evolução dos Focos de Queimada")
    st.plotly_chart(fig, use_container_width=True)

    # Gráficos de barras e pizza lado a lado
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de barras - Top 10 Estados
        top_ufs = df.groupby('uf').size().nlargest(10)
        fig_uf = px.bar(top_ufs, title="Top 10 Estados com Mais Focos")
        st.plotly_chart(fig_uf, use_container_width=True)

    with col2:
        # Gráfico de pizza - Biomas
        focos_bioma = df.groupby('bioma').size()
        fig_bioma = px.pie(values=focos_bioma.values,
                          names=focos_bioma.index,
                          title="Distribuição por Bioma")
        st.plotly_chart(fig_bioma, use_container_width=True)

    # Mapa de calor
    st.subheader("Distribuição Geográfica dos Focos")

    # Criar mapa base
    mapa = folium.Map(
        location=[-15.7801, -47.9292],  # Centro do Brasil
        zoom_start=4,
        tiles='CartoDB positron'
    )

    # Criar cluster de marcadores
    marker_cluster = folium.plugins.MarkerCluster(
        name='Focos de Queimada',
        overlay=True,
        control=True,
        options={
            'maxClusterRadius': 30,
            'disableClusteringAtZoom': 8
        }
    )

    # Limites do Brasil
    BRASIL_BOUNDS = {
        'lat_min': -33.75,
        'lat_max': 5.27,
        'lon_min': -73.99,
        'lon_max': -34.79
    }

    # Adicionar pontos ao mapa (apenas pontos válidos)
    for _, row in df.iterrows():
        try:
            lat, lon = float(row['latitude']), float(row['longitude'])

            # Validar coordenadas
            if (BRASIL_BOUNDS['lat_min'] <= lat <= BRASIL_BOUNDS['lat_max'] and
                BRASIL_BOUNDS['lon_min'] <= lon <= BRASIL_BOUNDS['lon_max']):

                # Criar popup informativo
                popup_html = f"""
                    <div style='font-family: Arial; font-size: 12px; width: 150px;'>
                        <b>UF:</b> {row['uf']}<br>
                        <b>Bioma:</b> {row['bioma']}<br>
                        <b>Data:</b> {pd.to_datetime(row['data']).strftime('%d/%m/%Y')}
                    </div>
                """

                # Adicionar marcador ao cluster
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    color='red',
                    fill=True,
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=200),
                    weight=1
                ).add_to(marker_cluster)

        except (ValueError, TypeError):
            continue

    # Adicionar cluster e controles ao mapa
    marker_cluster.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    # Exibir mapa
    folium_static(mapa)

else:
    st.warning("Nenhum dado disponível para o período selecionado.")

