#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface interativa em Streamlit para visualização de dados de focos de queimadas.

Este script carrega automaticamente todos os arquivos CSV em output/dados_limpos,
permite seleção de período, exibe filtros de UF e bioma, e mostra gráficos
interativos e mapa de dispersão dos focos.
"""

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

# Adicionar diretório pai ao PYTHONPATH para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relatorios.relatorio import main as gerar_relatorio

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coleta.utils_coleta import coletar_dados_inpe

# Criar diretório de logs se não existir
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'streamlit_app.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('monitoramento_queimadas.streamlit')

logger.debug("Iniciando aplicação Streamlit")

# Configuração da página Streamlit
st.set_page_config(
    page_title="Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para a sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #fdfdfd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# CSS minimalista para garantir a visualização correta
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
    }
    .stApp {
        background-color: #ffffff;
    }
    .css-1d391kg {
        background-color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Função para exibir alertas personalizados
def exibir_alerta(mensagem, tipo="info"):
    """
    Exibe um alerta personalizado e estilizado.

    Args:
        mensagem (str): Mensagem a ser exibida.
        tipo (str): Tipo de alerta ('info', 'warning', 'danger').
    """
    if tipo not in ["info", "warning", "danger"]:
        tipo = "info"

    html = f"""
    <div class="alert alert-{tipo}">
        {mensagem}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache por 1 hora
def atualizar_dados():
    """
    Atualiza os dados do INPE para os últimos 30 dias.
    """
    try:
        # Calcular datas
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=30)

        # Formatar datas
        data_inicio_str = data_inicio.strftime('%Y-%m-%d')
        data_fim_str = data_fim.strftime('%Y-%m-%d')

        logger.info(f"Atualizando dados do período: {data_inicio_str} a {data_fim_str}")

        # Coletar dados do INPE
        df = coletar_dados_inpe(data_inicio_str, data_fim_str)

        if df is not None and not df.empty:
            # Salvar dados atualizados
            os.makedirs("output/dados_brutos", exist_ok=True)
            arquivo_saida = f"output/dados_brutos/focos_{data_fim_str}.csv"
            df.to_csv(arquivo_saida, index=False)
            logger.info(f"Dados salvos em {arquivo_saida}")
            return df
        else:
            logger.error("Falha ao atualizar dados do INPE")
            return None

    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {str(e)}")
        return None

# Modificar a função carregar_dados para usar os dados atualizados
@st.cache_data(ttl=3600)
def carregar_dados():
    """
    Carrega dados, tentando primeiro atualizar do INPE e, se falhar, usa dados locais.
    """
    try:
        # Tentar atualizar dados do INPE
        df = atualizar_dados()
        if df is not None:
            return df

        # Se falhar, tentar carregar dados locais
        logger.warning("Usando dados locais como fallback")
        return carregar_dados_locais()

    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return None

def carregar_dados_locais(diretorio='output/dados_brutos'):
    """
    Carrega dados dos arquivos CSV locais.
    """
    try:
        # Construir caminho absoluto para o diretório
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_absoluto = os.path.join(caminho_base, diretorio)

        # Listar arquivos CSV no diretório
        arquivos_csv = glob(os.path.join(caminho_absoluto, '*.csv'))

        if not arquivos_csv:
            exibir_alerta(f"Nenhum arquivo CSV encontrado em {diretorio}", tipo="danger")
            logger.error(f"Nenhum arquivo CSV encontrado em {caminho_absoluto}")
            return None
        
        logger.info(f"Carregando {len(arquivos_csv)} arquivos CSV")
        
        # Lista para armazenar DataFrames
        dfs = []
        
        # Carregar cada arquivo
        for arquivo in arquivos_csv:
            try:
                df = pd.read_csv(arquivo)
                
                # Verificar se a coluna de data existe
                if 'data' not in df.columns:
                    logger.warning(f"Coluna 'data' não encontrada no arquivo {arquivo}. Pulando.")
                    continue
                
                # Converter coluna de data para datetime
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
                
                # Adicionar à lista
                dfs.append(df)
                
            except Exception as e:
                logger.error(f"Erro ao carregar arquivo {arquivo}: {str(e)}")
        
        if not dfs:
            exibir_alerta("Nenhum dado válido carregado", tipo="danger")
            return None
        
        # Concatenar todos os DataFrames
        df_completo = pd.concat(dfs, ignore_index=True)
        
        logger.info(f"Total de registros carregados: {len(df_completo)}")
        return df_completo
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        exibir_alerta(f"Erro ao carregar dados: {str(e)}", tipo="danger")
        return None

# Função para filtrar dados por período
def filtrar_por_periodo(df, data_inicio, data_fim):
    """
    Filtra o DataFrame pelo período especificado.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser filtrado.
        data_inicio (datetime): Data inicial do período.
        data_fim (datetime): Data final do período.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    if df is None:
        return None
    
    try:
        # Verificar se a coluna de data existe
        if 'data' not in df.columns:
            exibir_alerta("Coluna 'data' não encontrada no DataFrame", tipo="danger")
            return df
        
        # Filtrar por período
        df_filtrado = df[(df['data'] >= data_inicio) & (df['data'] <= data_fim)]
        
        logger.info(f"Dados filtrados por período: {len(df_filtrado)} registros")
        return df_filtrado
    
    except Exception as e:
        logger.error(f"Erro ao filtrar por período: {str(e)}")
        st.error(f"Erro ao filtrar por período: {str(e)}")
        return df

# Função para filtrar dados por UF
def filtrar_por_uf(df, ufs_selecionadas):
    """
    Filtra o DataFrame pelas UFs selecionadas.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser filtrado.
        ufs_selecionadas (list): Lista de UFs selecionadas.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    if df is None:
        return None

    try:
        # Verificar se a coluna de UF existe
        if 'uf' not in df.columns:
            exibir_alerta("Coluna 'uf' não encontrada no DataFrame", tipo="danger")
            return df

        # Filtrar por UF apenas se houver UFs selecionadas
        if ufs_selecionadas and len(ufs_selecionadas) > 0:  # Corrigido de && para and
            df_filtrado = df[df['uf'].isin(ufs_selecionadas)]
            logger.info(f"Dados filtrados por UF: {len(df_filtrado)} registros")
            return df_filtrado
        else:
            return df

    except Exception as e:
        logger.error(f"Erro ao filtrar por UF: {str(e)}")
        st.error(f"Erro ao filtrar por UF: {str(e)}")
        return df

# Função para filtrar dados por bioma
def filtrar_por_bioma(df, biomas_selecionados):
    """
    Filtra o DataFrame pelos biomas selecionados.

    Args:
        df (pandas.DataFrame): DataFrame a ser filtrado.
        biomas_selecionados (list): Lista de biomas selecionados.

    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    if df is None:
        return None

    try:
        # Verificar se a coluna de bioma existe
        if 'bioma' not in df.columns:
            exibir_alerta("Coluna 'bioma' não encontrada no DataFrame", tipo="danger")
            return df

        # Filtrar por bioma
        df_filtrado = df[df['bioma'].isin(biomas_selecionados)]

        logger.info(f"Dados filtrados por bioma: {len(df_filtrado)} registros")
        return df_filtrado

    except Exception as e:
        logger.error(f"Erro ao filtrar por bioma: {str(e)}")
        st.error(f"Erro ao filtrar por bioma: {str(e)}")
        return df

# Função para gerar série temporal
def gerar_serie_temporal(df):
    """
    Gera uma série temporal a partir do DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame com dados de focos de queimadas.

    Returns:
        pandas.DataFrame: DataFrame com a série temporal de focos por dia.
    """
    if df is None or len(df) == 0:
        logger.warning("Não foi possível gerar série temporal: DataFrame vazio ou nulo")
        return None

    try:
        # Verificar se a coluna de data existe
        if 'data' not in df.columns:
            logger.error("Coluna 'data' não encontrada para gerar série temporal")
            return None

        # Contar focos por dia
        serie_temporal = df.groupby(df['data'].dt.date).size().reset_index(name='focos')

        # Converter para datetime novamente para facilitar a plotagem
        serie_temporal['data'] = pd.to_datetime(serie_temporal['data'])

        # Ordenar por data
        serie_temporal = serie_temporal.sort_values('data')

        logger.info(f"Série temporal gerada com {len(serie_temporal)} pontos")
        return serie_temporal

    except Exception as e:
        logger.error(f"Erro ao gerar série temporal: {str(e)}")
        return None

# Função para contar focos por UF
def contar_por_uf(df):
    """
    Conta o número de focos por UF.

    Args:
        df (pandas.DataFrame): DataFrame com dados de focos de queimadas.

    Returns:
        pandas.DataFrame: DataFrame com contagem de focos por UF.
    """
    if df is None or len(df) == 0:
        logger.warning("Não foi possível contar focos por UF: DataFrame vazio ou nulo")
        return None

    try:
        # Verificar se a coluna de UF existe
        if 'uf' not in df.columns:
            logger.error("Coluna 'uf' não encontrada para contar focos por UF")
            return None

        # Contar focos por UF
        focos_por_uf = df.groupby('uf').size().reset_index(name='focos')

        # Ordenar por número de focos (decrescente)
        focos_por_uf = focos_por_uf.sort_values('focos', ascending=False)

        logger.info(f"Contagem por UF gerada com {len(focos_por_uf)} UFs")
        return focos_por_uf

    except Exception as e:
        logger.error(f"Erro ao contar focos por UF: {str(e)}")
        return None

# Função para contar focos por bioma
def contar_por_bioma(df):
    """
    Conta o número de focos por bioma.

    Args:
        df (pandas.DataFrame): DataFrame com dados de focos de queimadas.

    Returns:
        pandas.DataFrame: DataFrame com contagem de focos por bioma.
    """
    if df is None or len(df) == 0:
        logger.warning("Não foi possível contar focos por bioma: DataFrame vazio ou nulo")
        return None

    try:
        # Verificar se a coluna de bioma existe
        if 'bioma' not in df.columns:
            logger.error("Coluna 'bioma' não encontrada para contar focos por bioma")
            return None

        # Contar focos por bioma
        focos_por_bioma = df.groupby('bioma').size().reset_index(name='focos')

        # Ordenar por número de focos (decrescente)
        focos_por_bioma = focos_por_bioma.sort_values('focos', ascending=False)

        logger.info(f"Contagem por bioma gerada com {len(focos_por_bioma)} biomas")
        return focos_por_bioma

    except Exception as e:
        logger.error(f"Erro ao contar focos por bioma: {str(e)}")
        return None

def validar_coordenadas_brasil(lat, lon):
    """
    Valida se as coordenadas estão dentro dos limites do Brasil.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        bool: True se as coordenadas são válidas, False caso contrário
    """
    # Limites aproximados do Brasil
    BRASIL_BOUNDS = {
        'lat_min': -33.75,
        'lat_max': 5.27,
        'lon_min': -73.99,
        'lon_max': -34.79
    }

    try:
        lat = float(lat)
        lon = float(lon)

        # Verificar se está dentro dos limites do Brasil
        if (BRASIL_BOUNDS['lat_min'] <= lat <= BRASIL_BOUNDS['lat_max'] and
            BRASIL_BOUNDS['lon_min'] <= lon <= BRASIL_BOUNDS['lon_max']):
            return True

        return False

    except (ValueError, TypeError):
        return False

# Limites de coordenadas por UF
COORDENADAS_UF = {
    'AC': {'lat_min': -11.14, 'lat_max': -7.11, 'lon_min': -74.00, 'lon_max': -66.62},
    'AL': {'lat_min': -10.50, 'lat_max': -8.81, 'lon_min': -38.24, 'lon_max': -35.15},
    'AM': {'lat_min': -9.49, 'lat_max': 2.25, 'lon_min': -73.80, 'lon_max': -56.09},
    'AP': {'lat_min': -1.23, 'lat_max': 4.44, 'lon_min': -54.87, 'lon_max': -49.87},
    'BA': {'lat_min': -18.34, 'lat_max': -8.53, 'lon_min': -46.61, 'lon_max': -37.34},
    'CE': {'lat_min': -7.86, 'lat_max': -2.78, 'lon_min': -41.42, 'lon_max': -37.25},
    'DF': {'lat_min': -16.05, 'lat_max': -15.50, 'lon_min': -48.25, 'lon_max': -47.33},
    'ES': {'lat_min': -21.30, 'lat_max': -17.89, 'lon_min': -41.88, 'lon_max': -39.86},
    'GO': {'lat_min': -19.47, 'lat_max': -12.39, 'lon_min': -53.25, 'lon_max': -45.90},
    'MA': {'lat_min': -10.26, 'lat_max': -1.05, 'lon_min': -48.73, 'lon_max': -41.79},
    'MG': {'lat_min': -22.92, 'lat_max': -14.23, 'lon_min': -51.05, 'lon_max': -39.85},
    'MS': {'lat_min': -24.07, 'lat_max': -17.16, 'lon_min': -58.17, 'lon_max': -50.92},
    'MT': {'lat_min': -18.04, 'lat_max': -7.35, 'lon_min': -61.60, 'lon_max': -50.23},
    'PA': {'lat_min': -9.84, 'lat_max': 2.59, 'lon_min': -58.89, 'lon_max': -46.06},
    'PB': {'lat_min': -8.28, 'lat_max': -6.02, 'lon_min': -38.77, 'lon_max': -34.79},
    'PE': {'lat_min': -9.48, 'lat_max': -7.15, 'lon_min': -41.35, 'lon_max': -34.82},
    'PI': {'lat_min': -10.92, 'lat_max': -2.74, 'lon_min': -45.99, 'lon_max': -40.37},
    'PR': {'lat_min': -26.72, 'lat_max': -22.51, 'lon_min': -54.62, 'lon_max': -48.02},
    'RJ': {'lat_min': -23.37, 'lat_max': -20.76, 'lon_min': -44.89, 'lon_max': -40.96},
    'RN': {'lat_min': -6.98, 'lat_max': -4.83, 'lon_min': -38.58, 'lon_max': -34.96},
    'RO': {'lat_min': -13.69, 'lat_max': -7.96, 'lon_min': -66.81, 'lon_max': -59.77},
    'RR': {'lat_min': -1.58, 'lat_max': 5.27, 'lon_min': -64.82, 'lon_max': -58.89},
    'RS': {'lat_min': -33.75, 'lat_max': -27.08, 'lon_min': -57.64, 'lon_max': -49.71},
    'SC': {'lat_min': -29.35, 'lat_max': -25.95, 'lon_min': -53.84, 'lon_max': -48.35},
    'SE': {'lat_min': -11.57, 'lat_max': -9.51, 'lon_min': -38.24, 'lon_max': -36.39},
    'SP': {'lat_min': -25.31, 'lat_max': -19.78, 'lon_min': -53.11, 'lon_max': -44.16},
    'TO': {'lat_min': -13.46, 'lat_max': -5.22, 'lon_min': -50.73, 'lon_max': -45.70}
}

def validar_coordenadas_uf(lat, lon, uf):
    """
    Valida se as coordenadas estão dentro dos limites da UF especificada.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        uf (str): Sigla da UF

    Returns:
        bool: True se as coordenadas são válidas para a UF, False caso contrário
    """
    try:
        if uf not in COORDENADAS_UF:
            return False

        bounds = COORDENADAS_UF[uf]
        return (bounds['lat_min'] <= lat <= bounds['lat_max'] and
                bounds['lon_min'] <= lon <= bounds['lon_max'])
    except:
        return False

def criar_mapa_folium(df):
    """
    Cria um mapa interativo usando Folium com validação rigorosa de coordenadas por UF.
    """
    try:
        logger.debug("Iniciando criação do mapa com Folium")
        logger.debug(f"Total de pontos para processamento: {len(df)}")

        # Criar mapa base centralizado no Brasil
        m = folium.Map(
            location=[-15.8, -47.9],
            zoom_start=4,
            tiles='CartoDB positron'
        )

        # Criar cluster para pontos
        marker_cluster = folium.plugins.MarkerCluster(
            name='Focos de Queimada',
            overlay=True,
            control=True,
            options={
                'maxClusterRadius': 30,
                'disableClusteringAtZoom': 8
            }
        )

        # Agrupar pontos por coordenadas e UF
        df_agrupado = df.groupby(['latitude', 'longitude', 'uf', 'bioma']).size().reset_index(name='quantidade')
        logger.debug(f"Pontos agrupados: {len(df_agrupado)}")

        # Contadores para logging
        pontos_validos = 0
        pontos_invalidos = 0
        pontos_fora_uf = 0

        # Processar pontos
        for _, row in df_agrupado.iterrows():
            try:
                lat, lon = float(row['latitude']), float(row['longitude'])
                uf = row['uf']

                # Validar coordenadas para a UF específica
                if not validar_coordenadas_uf(lat, lon, uf):
                    logger.warning(f"Coordenadas inválidas para UF {uf}: lat={lat}, lon={lon}")
                    pontos_fora_uf += 1
                    continue

                # Calcular tamanho do círculo
                raio = min(8, 3 + (row['quantidade'] / 20))
                opacidade = min(0.7, 0.3 + (row['quantidade'] / 50))

                # Criar popup
                popup_html = f"""
                    <div style='font-family: Arial; font-size: 12px; width: 150px;'>
                        <b>Focos:</b> {row['quantidade']}<br>
                        <b>UF:</b> {uf}<br>
                        <b>Bioma:</b> {row['bioma']}
                    </div>
                """

                # Adicionar marcador
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=raio,
                    color='red',
                    fill=True,
                    fillOpacity=opacidade,
                    popup=folium.Popup(popup_html, max_width=200),
                    weight=1
                ).add_to(marker_cluster)

                pontos_validos += 1

            except Exception as e:
                logger.warning(f"Erro ao processar ponto: {str(e)}")
                pontos_invalidos += 1
                continue

        # Adicionar cluster e controles ao mapa
        marker_cluster.add_to(m)
        folium.LayerControl().add_to(m)

        # Logging final
        logger.debug(f"Mapa criado com {pontos_validos} pontos válidos")
        logger.debug(f"Pontos inválidos: {pontos_invalidos}")
        logger.debug(f"Pontos fora da UF: {pontos_fora_uf}")

        if pontos_validos == 0:
            logger.warning("Nenhum ponto válido para exibir no mapa")
            return None

        return m

    except Exception as e:
        logger.error(f"Erro ao criar mapa: {str(e)}", exc_info=True)
        return None

# Função principal da aplicação
def main():
    logger.debug("Iniciando função main()")
    try:
        """
        Função principal que executa o fluxo da aplicação Streamlit.
        Carrega os dados, renderiza a interface e aplica os filtros.
        """
        # Carregar dados
        df = carregar_dados()

        if df is not None:
            # Adicionar logo da FIAP na sidebar
            logo_path = "../Fiap-logo-branco.jpg"  # Caminho relativo para o novo logo com fundo branco
            if not os.path.exists(logo_path):
                logo_path = "/Users/alansms/CLionProjects/GS-2025-RPA/Fiap-logo-branco.jpg"  # Caminho absoluto

            if os.path.exists(logo_path):
                # Adicionar o logo com tamanho adaptativo
                st.sidebar.image(logo_path, use_container_width=True)
            else:
                # Tentar usar o logo original como fallback
                logo_path_fallback = "/Users/alansms/CLionProjects/GS-2025-RPA/logo_fiap.jpg"
                if os.path.exists(logo_path_fallback):
                    st.sidebar.image(logo_path_fallback, use_container_width=True)
                else:
                    st.sidebar.warning("Logo não encontrado.")

            # Sidebar para filtros
            st.sidebar.title("Filtros")

            # Filtro de período
            st.sidebar.subheader("Período")

            # Determinar datas mínima e máxima
            data_min = df['data'].min().date()
            data_max = df['data'].max().date()

            # Definir datas padrão (último mês)
            data_padrao_fim = data_max
            data_padrao_inicio = max(data_min, data_padrao_fim - timedelta(days=30))

            # Seletores de data
            data_inicio = st.sidebar.date_input("Data inicial", data_padrao_inicio, min_value=data_min, max_value=data_max)
            data_fim = st.sidebar.date_input("Data final", data_padrao_fim, min_value=data_min, max_value=data_max)

            # Converter para datetime
            data_inicio = pd.Timestamp(data_inicio)
            data_fim = pd.Timestamp(data_fim)

            # Filtro de UF
            st.sidebar.subheader("Unidades Federativas (UF)")

            # Obter lista de UFs
            if 'uf' in df.columns:
                ufs_disponiveis = sorted(df['uf'].unique())
                ufs_selecionadas = st.sidebar.multiselect("Selecione as UFs", ufs_disponiveis, key="multiselect_ufs")
            else:
                ufs_selecionadas = []
                st.sidebar.warning("Coluna 'uf' não encontrada nos dados")

            # Filtro de bioma
            st.sidebar.subheader("Biomas")

            # Obter lista de biomas
            if 'bioma' in df.columns:
                biomas_disponiveis = sorted(df['bioma'].unique())
                biomas_selecionados = st.sidebar.multiselect("Selecione os biomas", biomas_disponiveis, key="multiselect_biomas")
            else:
                biomas_selecionados = []
                st.sidebar.warning("Coluna 'bioma' não encontrada nos dados")

            # Adicionar seção de relatórios na sidebar
            st.sidebar.subheader("Relatórios")

            # Verificar se o WeasyPrint está disponível
            weasyprint_disponivel = False
            try:
                import weasyprint
                weasyprint_disponivel = True
            except Exception as e:
                logger.warning(f"WeasyPrint não está disponível: {str(e)}")
                st.sidebar.warning("A geração de PDF não está disponível no momento. Usando formato HTML.")

            formato_relatorio = st.sidebar.selectbox(
                "Formato do relatório",
                options=["HTML", "PDF"] if weasyprint_disponivel else ["HTML"],
                index=0
            )

            periodo_relatorio = st.sidebar.selectbox(
                "Período do relatório",
                options=["Dia", "Semana", "Mês", "Ano"],
                index=2
            )

            # Botão para gerar relatório
            if st.sidebar.button("Gerar Relatório"):
                with st.spinner("Gerando relatório..."):
                    try:
                        # Aplicar filtros primeiro, se ainda não tiver aplicado
                        if 'df_filtrado' not in locals() or df_filtrado is None:
                            df_filtrado = filtrar_por_periodo(df, data_inicio, data_fim)

                            if ufs_selecionadas:
                                df_filtrado = filtrar_por_uf(df_filtrado, ufs_selecionadas)

                            if biomas_selecionados:
                                df_filtrado = filtrar_por_bioma(df_filtrado, biomas_selecionados)

                        # Gerar série temporal se ainda não existir
                        if 'serie_temporal' not in locals() or serie_temporal is None:
                            serie_temporal = gerar_serie_temporal(df_filtrado)

                        # Gerar contagens por UF e bioma se ainda não existirem
                        if 'focos_por_uf' not in locals() or focos_por_uf is None:
                            focos_por_uf = contar_por_uf(df_filtrado)

                        if 'focos_por_bioma' not in locals() or focos_por_bioma is None:
                            focos_por_bioma = contar_por_bioma(df_filtrado)

                        # Preparar diretório para salvar análises
                        os.makedirs("output/dados_limpos/analises", exist_ok=True)

                        # Salvar série temporal para relatório
                        if serie_temporal is not None and not serie_temporal.empty:
                            # Renomear coluna 'data' para 'periodo' se necessário
                            if 'data' in serie_temporal.columns and 'periodo' not in serie_temporal.columns:
                                serie_temporal = serie_temporal.rename(columns={'data': 'periodo'})

                            serie_temporal.to_csv("output/dados_limpos/analises/serie_temporal_dia.csv", index=False)
                        else:
                            # Criar um substituto em caso de erro
                            serie_temporal_fallback = pd.DataFrame({
                                'periodo': pd.date_range(start=data_inicio, end=data_fim),
                                'focos': [0] * (1 + (data_fim - data_inicio).days)
                            })
                            serie_temporal_fallback.to_csv("output/dados_limpos/analises/serie_temporal_dia.csv", index=False)

                        # Salvar focos por UF para relatório
                        if focos_por_uf is not None and not focos_por_uf.empty:
                            # Adicionar percentual se não existir
                            if 'percentual' not in focos_por_uf.columns:
                                focos_por_uf['percentual'] = (focos_por_uf['focos'] / focos_por_uf['focos'].sum()) * 100
                            focos_por_uf.to_csv("output/dados_limpos/analises/focos_por_uf.csv", index=False)

                        # Salvar focos por bioma para relatório
                        if focos_por_bioma is not None and not focos_por_bioma.empty:
                            # Adicionar percentual se não existir
                            if 'percentual' not in focos_por_bioma.columns:
                                focos_por_bioma['percentual'] = (focos_por_bioma['focos'] / focos_por_bioma['focos'].sum()) * 100
                            focos_por_bioma.to_csv("output/dados_limpos/analises/focos_por_bioma.csv", index=False)

                        # Chamar função para gerar relatório
                        caminho_relatorio = gerar_relatorio(
                            formato=formato_relatorio.lower(),
                            periodo=periodo_relatorio.lower(),
                            output=None  # Usar caminho padrão
                        )

                        if caminho_relatorio:
                            # Permitir download do relatório gerado
                            with open(caminho_relatorio, "rb") as arquivo:
                                nome_arquivo = os.path.basename(caminho_relatorio)

                                st.sidebar.success(f"Relatório gerado com sucesso!")
                                st.sidebar.download_button(
                                    label=f"Baixar Relatório ({formato_relatorio})",
                                    data=arquivo,
                                    file_name=nome_arquivo,
                                    mime="application/pdf" if formato_relatorio.lower() == "pdf" else "text/html"
                                )
                        else:
                            st.sidebar.error("Falha ao gerar relatório. Verifique os logs para mais detalhes.")

                    except Exception as e:
                        logger.error(f"Erro ao gerar relatório: {str(e)}", exc_info=True)
                        st.sidebar.error(f"Erro ao gerar relatório: {str(e)}")

            # Aplicar filtros
            with st.spinner("Aplicando filtros..."):
                df_filtrado = filtrar_por_periodo(df, data_inicio, data_fim)

                if ufs_selecionadas:
                    df_filtrado = filtrar_por_uf(df_filtrado, ufs_selecionadas)

                if biomas_selecionados:
                    df_filtrado = filtrar_por_bioma(df_filtrado, biomas_selecionados)

            # Verificar se há dados após filtros
            if df_filtrado is None or len(df_filtrado) == 0:
                exibir_alerta("Nenhum dado encontrado para os filtros selecionados.", tipo="warning")
                st.stop()

            # Exibir informações gerais
            st.subheader("Informações Gerais")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total de Focos", f"{len(df_filtrado):,}")

            with col2:
                # Calcular média diária
                dias = (data_fim - data_inicio).days + 1
                media_diaria = len(df_filtrado) / dias if dias > 0 else 0
                st.metric("Média Diária", f"{media_diaria:.1f}")

            with col3:
                # Determinar tendência
                serie_temporal = gerar_serie_temporal(df_filtrado)
                if serie_temporal is not None and len(serie_temporal) > 1:
                    primeiro_valor = serie_temporal['focos'].iloc[0]
                    ultimo_valor = serie_temporal['focos'].iloc[-1]

                    if ultimo_valor > primeiro_valor * 1.2:
                        tendencia = "Crescente ↑"
                    elif ultimo_valor < primeiro_valor * 0.8:
                        tendencia = "Decrescente ↓"
                    else:
                        tendencia = "Estável →"

                    st.metric("Tendência", tendencia)

            # Gráfico de linha (série temporal)
            st.subheader("Série Temporal de Focos de Queimadas")

            # Gerar série temporal
            serie_temporal = gerar_serie_temporal(df_filtrado)

            if serie_temporal is not None and not serie_temporal.empty:
                # Criar gráfico interativo com Plotly
                fig = px.line(
                    serie_temporal,
                    x='data',
                    y='focos',
                    title='Focos de Queimadas por Dia',
                    labels={'data': 'Data', 'focos': 'Número de Focos'},
                    line_shape='linear'
                )

                # Adicionar linha de média móvel
                serie_temporal['media_movel'] = serie_temporal['focos'].rolling(window=7, min_periods=1).mean()

                fig.add_scatter(
                    x=serie_temporal['data'],
                    y=serie_temporal['media_movel'],
                    mode='lines',
                    name='Média Móvel (7 dias)',
                    line=dict(color='red', width=2)
                )

                # Configurar layout
                fig.update_layout(
                    xaxis_title='Data',
                    yaxis_title='Número de Focos',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    height=500
                )

                # Exibir gráfico
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Não foi possível gerar a série temporal.")

            # Criar duas colunas para os gráficos de UF e bioma
            col1, col2 = st.columns(2)

            with col1:
                # Gráfico de barras (focos por UF)
                st.subheader("Focos por UF")

                # Contar focos por UF
                focos_por_uf = contar_por_uf(df_filtrado)

                if focos_por_uf is not None and not focos_por_uf.empty:
                    # Limitar para as 10 UFs com mais focos
                    top_ufs = focos_por_uf.head(10)

                    # Criar gráfico interativo com Plotly
                    fig = px.bar(
                        top_ufs,
                        x='uf',
                        y='focos',
                        title='Top 10 UFs com Mais Focos de Queimadas',
                        labels={'uf': 'UF', 'focos': 'Número de Focos'},
                        color='focos',
                        color_continuous_scale='Reds',
                        hover_data={'uf': True, 'focos': True},
                        custom_data=['uf', 'focos']
                    )

                    # Configurar layout e hover template personalizado
                    fig.update_layout(
                        xaxis_title='UF',
                        yaxis_title='Número de Focos',
                        coloraxis_showscale=False,
                        height=500
                    )

                    # Definir formato de hover personalizado
                    fig.update_traces(
                        hovertemplate='<b>UF:</b> %{customdata[0]}<br><b>Número de Focos:</b> %{customdata[1]:,}<extra></extra>'
                    )

                    # Exibir gráfico
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foi possível gerar o gráfico de focos por UF.")

            with col2:
                # Gráfico de pizza (focos por bioma)
                st.subheader("Focos por Bioma")

                # Contar focos por bioma
                focos_por_bioma = contar_por_bioma(df_filtrado)

                if focos_por_bioma is not None and not focos_por_bioma.empty:
                    logger.debug(f"Criando gráfico de pizza com {len(focos_por_bioma)} biomas")
                    # Criar gráfico interativo com Plotly
                    fig = px.pie(
                        focos_por_bioma,
                        names='bioma',
                        values='focos',
                        title='Distribuição de Focos de Queimadas por Bioma',
                        color_discrete_sequence=px.colors.sequential.Reds,
                        custom_data=['bioma', 'focos']
                    )
                    logger.debug("Gráfico de pizza criado com sucesso")

                    # Configurar layout
                    fig.update_layout(
                        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
                        height=500
                    )

                    # Definir formato de hover personalizado
                    fig.update_traces(
                        hovertemplate='<b>Bioma:</b> %{customdata[0]}<br><b>Número de Focos:</b> %{customdata[1]:,}<extra></extra>'
                    )

                    # Exibir gráfico
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foi possível gerar o gráfico de focos por bioma.")

            # Após a exibição dos gráficos de UF e bioma, adicionar o mapa
            st.subheader("Distribuição Geográfica dos Focos")

            try:
                if df_filtrado is not None and len(df_filtrado) > 0:
                    logger.debug(f"Preparando dados para o mapa ({len(df_filtrado)} registros)")

                    # Verificar dados antes de criar o mapa
                    df_mapa = df_filtrado.dropna(subset=['latitude', 'longitude'])
                    logger.debug(f"Registros com coordenadas válidas: {len(df_mapa)}")

                    if len(df_mapa) > 0:
                        with st.spinner("Gerando mapa..."):
                            mapa = criar_mapa_folium(df_mapa)
                            if mapa:
                                try:
                                    folium_static(mapa)
                                    logger.debug("Mapa exibido com sucesso")
                                except Exception as e:
                                    logger.error(f"Erro ao exibir mapa: {str(e)}", exc_info=True)
                                    st.error("Erro ao exibir o mapa")
                            else:
                                st.warning("Não foi possível gerar o mapa")
                    else:
                        st.warning("Não há coordenadas válidas para exibir no mapa")
                else:
                    st.warning("Não há dados para exibir no mapa")

            except Exception as e:
                logger.error(f"Erro ao processar mapa: {str(e)}", exc_info=True)
                st.error("Erro ao processar o mapa")

    except Exception as e:
        logger.error(f"Erro na execução do main: {str(e)}", exc_info=True)
        st.error("Ocorreu um erro na aplicação. Por favor, verifique os logs.")

if __name__ == "__main__":
    logger.debug("Iniciando execução do script")
    main()
