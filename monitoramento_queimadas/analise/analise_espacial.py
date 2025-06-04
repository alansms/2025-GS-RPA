#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de análise espacial de focos de queimadas.

Este script agrupa focos por Unidade Federativa (UF) e bioma, gera tabelas
com totais, e mapeia pontos geográficos usando geopandas ou Plotly.
"""

import os
import sys
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from glob import glob

try:
    import geopandas as gpd
    GEOPANDAS_DISPONIVEL = True
except ImportError:
    GEOPANDAS_DISPONIVEL = False
    logging.warning("Biblioteca geopandas não disponível. Alguns recursos de mapeamento serão limitados.")

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.analise.espacial')

def carregar_dados(diretorio_dados, periodo=None):
    """
    Carrega todos os dados limpos do diretório especificado.
    
    Args:
        diretorio_dados (str): Diretório contendo os arquivos CSV limpos.
        periodo (tuple, optional): Tupla (data_inicio, data_fim) para filtrar os dados.
    
    Returns:
        pandas.DataFrame: DataFrame com todos os dados carregados e filtrados.
    """
    # Listar arquivos CSV no diretório
    arquivos_csv = glob(os.path.join(diretorio_dados, '*.csv'))
    
    if not arquivos_csv:
        logger.warning(f"Nenhum arquivo CSV encontrado em {diretorio_dados}")
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
        logger.warning("Nenhum dado válido carregado")
        return None
    
    # Concatenar todos os DataFrames
    df_completo = pd.concat(dfs, ignore_index=True)
    
    # Filtrar por período
    if periodo:
        from analise.utils_analise import filtrar_por_periodo
        df_completo = filtrar_por_periodo(df_completo, periodo[0], periodo[1])
    
    logger.info(f"Total de registros carregados: {len(df_completo)}")
    return df_completo

def analisar_por_uf(df):
    """
    Agrupa e analisa focos de queimadas por Unidade Federativa (UF).
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados de focos.
    
    Returns:
        pandas.DataFrame: DataFrame com a contagem de focos por UF.
    """
    if df is None or len(df) == 0:
        logger.warning("Sem dados para análise por UF")
        return None
    
    # Verificar se a coluna de UF existe
    if 'uf' not in df.columns:
        logger.error("Coluna 'uf' não encontrada no DataFrame")
        return None
    
    logger.info("Realizando análise por UF")
    
    # Agrupar por UF
    focos_por_uf = df.groupby('uf').size().reset_index(name='focos')
    
    # Ordenar por número de focos (decrescente)
    focos_por_uf = focos_por_uf.sort_values('focos', ascending=False)
    
    # Calcular percentual
    total_focos = focos_por_uf['focos'].sum()
    focos_por_uf['percentual'] = (focos_por_uf['focos'] / total_focos) * 100
    
    logger.info(f"Análise por UF concluída. {len(focos_por_uf)} UFs analisadas.")
    return focos_por_uf

def analisar_por_bioma(df):
    """
    Agrupa e analisa focos de queimadas por bioma.
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados de focos.
    
    Returns:
        pandas.DataFrame: DataFrame com a contagem de focos por bioma.
    """
    if df is None or len(df) == 0:
        logger.warning("Sem dados para análise por bioma")
        return None
    
    # Verificar se a coluna de bioma existe
    if 'bioma' not in df.columns:
        logger.error("Coluna 'bioma' não encontrada no DataFrame")
        return None
    
    logger.info("Realizando análise por bioma")
    
    # Agrupar por bioma
    focos_por_bioma = df.groupby('bioma').size().reset_index(name='focos')
    
    # Ordenar por número de focos (decrescente)
    focos_por_bioma = focos_por_bioma.sort_values('focos', ascending=False)
    
    # Calcular percentual
    total_focos = focos_por_bioma['focos'].sum()
    focos_por_bioma['percentual'] = (focos_por_bioma['focos'] / total_focos) * 100
    
    logger.info(f"Análise por bioma concluída. {len(focos_por_bioma)} biomas analisados.")
    return focos_por_bioma

def gerar_mapa_focos(df, caminho_saida=None):
    """
    Gera mapa de dispersão dos focos de queimadas.
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados de focos.
        caminho_saida (str, optional): Caminho para salvar o mapa. Se None, apenas exibe.
    
    Returns:
        bool: True se o mapa foi gerado com sucesso, False caso contrário.
    """
    if df is None or len(df) == 0:
        logger.warning("Sem dados para geração de mapa")
        return False
    
    # Verificar se as colunas de coordenadas existem
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        logger.error("Colunas 'latitude' e/ou 'longitude' não encontradas no DataFrame")
        return False
    
    # Remover registros com coordenadas nulas
    df_mapa = df.dropna(subset=['latitude', 'longitude'])
    
    if len(df_mapa) == 0:
        logger.warning("Sem coordenadas válidas para geração de mapa")
        return False
    
    logger.info(f"Gerando mapa com {len(df_mapa)} pontos")
    
    try:
        # Usar Plotly para gerar mapa interativo
        fig = px.scatter_mapbox(
            df_mapa,
            lat='latitude',
            lon='longitude',
            hover_name='uf' if 'uf' in df_mapa.columns else None,
            hover_data=['bioma'] if 'bioma' in df_mapa.columns else None,
            color='uf' if 'uf' in df_mapa.columns else None,
            size_max=10,
            zoom=3,
            height=800,
            width=1000,
            title='Mapa de Focos de Queimadas'
        )
        
        fig.update_layout(mapbox_style='open-street-map')
        
        # Salvar ou exibir
        if caminho_saida:
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            fig.write_html(caminho_saida)
            logger.info(f"Mapa salvo em: {caminho_saida}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa: {str(e)}")
        return False

def gerar_graficos_espaciais(focos_por_uf, focos_por_bioma, diretorio_saida):
    """
    Gera gráficos de barras e pizza para análise espacial.
    
    Args:
        focos_por_uf (pandas.DataFrame): DataFrame com focos por UF.
        focos_por_bioma (pandas.DataFrame): DataFrame com focos por bioma.
        diretorio_saida (str): Diretório para salvar os gráficos.
    
    Returns:
        list: Lista de caminhos para os gráficos gerados.
    """
    graficos_gerados = []
    
    try:
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Gráfico de barras por UF
        if focos_por_uf is not None and not focos_por_uf.empty:
            plt.figure(figsize=(12, 8))
            
            # Limitar para as 10 UFs com mais focos
            df_plot = focos_por_uf.head(10).copy()
            
            # Plotar barras
            bars = plt.bar(df_plot['uf'], df_plot['focos'])
            
            # Adicionar rótulos
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                        f'{height:,}', ha='center', va='bottom')
            
            # Configurar gráfico
            plt.title('Top 10 UFs com Mais Focos de Queimadas')
            plt.xlabel('UF')
            plt.ylabel('Número de Focos')
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar
            caminho_grafico = os.path.join(diretorio_saida, 'focos_por_uf.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de barras por UF salvo em: {caminho_grafico}")
            graficos_gerados.append(caminho_grafico)
        
        # Gráfico de pizza por bioma
        if focos_por_bioma is not None and not focos_por_bioma.empty:
            plt.figure(figsize=(10, 10))
            
            # Plotar pizza
            plt.pie(
                focos_por_bioma['focos'],
                labels=focos_por_bioma['bioma'],
                autopct='%1.1f%%',
                startangle=90,
                shadow=True
            )
            
            # Configurar gráfico
            plt.title('Distribuição de Focos de Queimadas por Bioma')
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar
            caminho_grafico = os.path.join(diretorio_saida, 'focos_por_bioma.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de pizza por bioma salvo em: {caminho_grafico}")
            graficos_gerados.append(caminho_grafico)
        
        return graficos_gerados
        
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos espaciais: {str(e)}")
        return graficos_gerados

def main(diretorio_dados='output/dados_limpos', uf=None, bioma=None, data_inicio=None, data_fim=None):
    """
    Função principal do módulo de análise espacial.
    
    Args:
        diretorio_dados (str, optional): Diretório com os dados limpos.
        uf (str, optional): Filtrar por UF específica.
        bioma (str, optional): Filtrar por bioma específico.
        data_inicio (str, optional): Data inicial para filtro (formato YYYY-MM-DD).
        data_fim (str, optional): Data final para filtro (formato YYYY-MM-DD).
    
    Returns:
        tuple: (focos_por_uf, focos_por_bioma) com os resultados da análise.
    """
    logger.info("Iniciando análise espacial de focos de queimadas")
    
    try:
        # Converter datas para datetime
        periodo_filtro = None
        if data_inicio or data_fim:
            from datetime import datetime
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d') if data_inicio else None
            fim = datetime.strptime(data_fim, '%Y-%m-%d') if data_fim else None
            periodo_filtro = (inicio, fim)
        
        # Carregar dados
        df = carregar_dados(diretorio_dados, periodo_filtro)
        
        if df is None or len(df) == 0:
            logger.warning("Sem dados para análise")
            return None, None
        
        # Filtrar por UF, se especificado
        if uf:
            df = df[df['uf'] == uf]
            logger.info(f"Dados filtrados para UF: {uf}")
        
        # Filtrar por bioma, se especificado
        if bioma:
            df = df[df['bioma'] == bioma]
            logger.info(f"Dados filtrados para bioma: {bioma}")
        
        # Realizar análise por UF
        focos_por_uf = analisar_por_uf(df)
        
        # Realizar análise por bioma
        focos_por_bioma = analisar_por_bioma(df)
        
        # Gerar mapa
        os.makedirs('output/relatorios', exist_ok=True)
        gerar_mapa_focos(df, 'output/relatorios/mapa_focos.html')
        
        # Gerar gráficos
        gerar_graficos_espaciais(focos_por_uf, focos_por_bioma, 'output/relatorios')
        
        # Salvar resultados
        os.makedirs('output/dados_limpos/analises', exist_ok=True)
        
        if focos_por_uf is not None:
            focos_por_uf.to_csv('output/dados_limpos/analises/focos_por_uf.csv', index=False)
            logger.info("Resultados por UF salvos")
        
        if focos_por_bioma is not None:
            focos_por_bioma.to_csv('output/dados_limpos/analises/focos_por_bioma.csv', index=False)
            logger.info("Resultados por bioma salvos")
        
        logger.info("Análise espacial concluída com sucesso")
        return focos_por_uf, focos_por_bioma
        
    except Exception as e:
        logger.error(f"Erro durante a análise espacial: {str(e)}", exc_info=True)
        return None, None

if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Análise espacial de focos de queimadas')
    parser.add_argument('--diretorio', type=str, default='output/dados_limpos', help='Diretório com os dados limpos')
    parser.add_argument('--uf', type=str, help='Filtrar por UF específica')
    parser.add_argument('--bioma', type=str, help='Filtrar por bioma específico')
    parser.add_argument('--data-inicio', type=str, help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--data-fim', type=str, help='Data final (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/analise_espacial.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar análise
    main(args.diretorio, args.uf, args.bioma, args.data_inicio, args.data_fim)
