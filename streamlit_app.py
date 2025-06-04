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

# Adicionar diretório src ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)

# Importar módulos do projeto
from coleta.utils_coleta import coletar_dados_inpe
from relatorios.relatorio import main as gerar_relatorio
from analise.analise_temporal import gerar_serie_temporal
from analise.analise_espacial import criar_mapa_focos

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

# Configuração da página Streamlit
st.set_page_config(
    page_title="Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("Sistema de Monitoramento de Queimadas")
st.markdown("""
Este sistema monitora focos de queimadas em todo o Brasil, fornecendo visualizações 
interativas e análises detalhadas por estado e bioma.
""")

# Sidebar
with st.sidebar:
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
    mapa = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)

    # Adicionar clusters de pontos
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='red',
            fill=True,
            popup=f"UF: {row['uf']}<br>Bioma: {row['bioma']}"
        ).add_to(mapa)

    folium_static(mapa)

else:
    st.warning("Nenhum dado disponível para o período selecionado.")

