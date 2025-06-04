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

# Configurações do Streamlit
st.set_page_config(
    page_title="Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações de estilo para expandir a página
st.markdown("""
    <style>
        .reportview-container .main .block-container {
            max-width: 95%;
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }
        .stApp > header {
            background-color: transparent;
        }
        .stApp {
            margin: 0 auto;
        }
        .st-bx {
            background-color: transparent;
        }
        /* Estilo para a barra lateral */
        [data-testid="stSidebar"] {
            background-color: #fdfdfd;
        }
        /* Ajuste de cores para textos e elementos da barra lateral */
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            color: #333333;
        }
        .css-6qob1r.e1fqkh3o3 {
            background-color: #fdfdfd;
        }
        .sidebar .sidebar-content {
            background-color: #fdfdfd;
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
from alertas.alertas import gerar_alerta_por_regiao, salvar_alertas

# Criar diretórios necessários logo no início
output_dirs = [
    'output/logs',
    'output/dados_brutos',
    'output/dados_limpos',
    'output/relatorios',
    'output/relatorios/graficos'
]

for dir_path in output_dirs:
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
                # Garantir que o diretório existe usando caminho absoluto
                relatorios_dir = os.path.join(project_root, 'output', 'relatorios')
                graficos_dir = os.path.join(relatorios_dir, 'graficos')

                # Criar diretórios se não existirem
                os.makedirs(relatorios_dir, exist_ok=True)
                os.makedirs(graficos_dir, exist_ok=True)

                with st.spinner('Gerando relatório...'):
                    relatorio_path = gerar_relatorio(df)  # Removendo o parâmetro output_dir

                    if relatorio_path and os.path.exists(relatorio_path):
                        with open(relatorio_path, "rb") as file:
                            if relatorio_path.endswith('.pdf'):
                                mime = "application/pdf"
                                ext = "pdf"
                            else:
                                mime = "text/html"
                                ext = "html"

                            st.download_button(
                                "📄 Baixar Relatório",
                                file,
                                file_name=f"relatorio_queimadas.{ext}",
                                mime=mime,
                                help="Clique para baixar o relatório"
                            )
                            st.success("✅ Relatório gerado com sucesso!")
                    else:
                        st.error("❌ Erro: Arquivo do relatório não encontrado")

            except Exception as e:
                logger.error(f"Erro ao gerar relatório: {str(e)}")
                st.error(f"❌ Erro ao gerar relatório: {str(e)}")

# Após carregar os dados, antes do layout principal
if df is not None:
    # Verificar alertas
    alertas = gerar_alerta_por_regiao(df)
    if alertas:
        st.sidebar.warning("⚠️ Alertas Ativos")
        with st.sidebar.expander("Ver Alertas", expanded=True):
            for alerta in alertas:
                if alerta['nivel'] == 'ALTO':
                    st.error(f"""
                        **{alerta['tipo']}: {alerta['local']}**
                        - Nível: {alerta['nivel']}
                        - Focos: {alerta['focos']:,}
                        - Aumento: {alerta['aumento']}%
                    """)
                else:
                    st.warning(f"""
                        **{alerta['tipo']}: {alerta['local']}**
                        - Nível: {alerta['nivel']}
                        - Focos: {alerta['focos']:,}
                        - Aumento: {alerta['aumento']}%
                    """)

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
        top_ufs = df.groupby('uf').size().sort_values(ascending=True)
        fig_uf = px.bar(
            x=top_ufs.values,
            y=top_ufs.index,
            orientation='h',
            title="Estados com Mais Focos",
            labels={'x': 'Número de Focos', 'y': 'Estado'}
        )
        fig_uf.update_layout(showlegend=False)
        st.plotly_chart(fig_uf, use_container_width=True)

    with col2:
        # Gráfico de pizza - Biomas
        focos_bioma = df.groupby('bioma').size()
        fig_bioma = px.pie(
            values=focos_bioma.values,
            names=focos_bioma.index,
            title="Distribuição por Bioma",
            hole=0.3
        )
        fig_bioma.update_traces(textposition='inside', textinfo='percent+label')
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

