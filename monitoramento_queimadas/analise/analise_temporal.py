#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de análise temporal de focos de queimadas.

Este script agrega focos por data (dia/mês/ano), gera séries temporais,
calcula médias móveis, identifica picos e retorna DataFrame com métricas temporais.
"""

import os
import sys
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from glob import glob

from analise.utils_analise import calcular_media_movel, calcular_estatisticas, filtrar_por_periodo

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.analise.temporal')

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
    
    # Filtrar por período, se especificado
    if periodo:
        df_completo = filtrar_por_periodo(df_completo, periodo[0], periodo[1])
    
    logger.info(f"Total de registros carregados: {len(df_completo)}")
    return df_completo

def analisar_serie_temporal(df, periodo='dia', janela_media_movel=7):
    """
    Realiza análise temporal dos focos de queimadas.
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados de focos.
        periodo (str, optional): Período de agregação ('dia', 'semana', 'mes', 'ano').
        janela_media_movel (int, optional): Tamanho da janela para cálculo da média móvel.
    
    Returns:
        pandas.DataFrame: DataFrame com a série temporal e métricas calculadas.
    """
    if df is None or len(df) == 0:
        logger.warning("Sem dados para análise temporal")
        return None
    
    logger.info(f"Realizando análise temporal com agregação por {periodo}")
    
    # Verificar se a coluna de data existe
    if 'data' not in df.columns:
        logger.error("Coluna 'data' não encontrada no DataFrame")
        return None
    
    # Definir formato de agregação com base no período
    if periodo == 'dia':
        df['periodo'] = df['data'].dt.date
    elif periodo == 'semana':
        df['periodo'] = df['data'].dt.to_period('W').dt.start_time.dt.date
    elif periodo == 'mes':
        df['periodo'] = df['data'].dt.to_period('M').dt.start_time.dt.date
    elif periodo == 'ano':
        df['periodo'] = df['data'].dt.to_period('Y').dt.start_time.dt.date
    else:
        logger.warning(f"Período inválido: {periodo}. Usando 'dia' como padrão.")
        df['periodo'] = df['data'].dt.date
    
    # Agregar focos por período
    serie_temporal = df.groupby('periodo').size().reset_index(name='focos')
    
    # Converter período para datetime para facilitar operações
    serie_temporal['periodo'] = pd.to_datetime(serie_temporal['periodo'])
    
    # Ordenar por período
    serie_temporal = serie_temporal.sort_values('periodo')
    
    # Calcular média móvel
    serie_temporal['media_movel'] = calcular_media_movel(serie_temporal['focos'], janela_media_movel)
    
    # Calcular estatísticas
    estatisticas = calcular_estatisticas(serie_temporal['focos'])
    
    # Identificar picos (valores acima de 2 desvios padrão da média)
    limite_pico = estatisticas['media'] + 2 * estatisticas['desvio_padrao']
    serie_temporal['pico'] = serie_temporal['focos'] > limite_pico
    
    # Adicionar coluna com percentual em relação ao máximo
    serie_temporal['percentual_max'] = (serie_temporal['focos'] / estatisticas['maximo']) * 100
    
    logger.info(f"Análise temporal concluída. {len(serie_temporal)} períodos analisados.")
    logger.info(f"Estatísticas: {estatisticas}")
    
    return serie_temporal, estatisticas

def gerar_grafico_temporal(serie_temporal, titulo, caminho_saida=None):
    """
    Gera gráfico da série temporal de focos de queimadas.
    
    Args:
        serie_temporal (pandas.DataFrame): DataFrame com a série temporal.
        titulo (str): Título do gráfico.
        caminho_saida (str, optional): Caminho para salvar o gráfico. Se None, apenas exibe.
    
    Returns:
        bool: True se o gráfico foi gerado com sucesso, False caso contrário.
    """
    try:
        plt.figure(figsize=(12, 6))
        
        # Plotar série original
        plt.plot(serie_temporal['periodo'], serie_temporal['focos'], 'b-', label='Focos diários')
        
        # Plotar média móvel
        if 'media_movel' in serie_temporal.columns:
            plt.plot(serie_temporal['periodo'], serie_temporal['media_movel'], 'r-', label='Média móvel')
        
        # Destacar picos
        if 'pico' in serie_temporal.columns:
            picos = serie_temporal[serie_temporal['pico']]
            if not picos.empty:
                plt.scatter(picos['periodo'], picos['focos'], color='red', s=50, label='Picos')
        
        # Configurar gráfico
        plt.title(titulo)
        plt.xlabel('Data')
        plt.ylabel('Número de focos')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Ajustar layout
        plt.tight_layout()
        
        # Salvar ou exibir
        if caminho_saida:
            os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
            plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho_saida}")
        
        plt.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico temporal: {str(e)}")
        return False

def main(diretorio_dados='output/dados_limpos', periodo='dia', data_inicio=None, data_fim=None, janela_media_movel=7):
    """
    Função principal do módulo de análise temporal.
    
    Args:
        diretorio_dados (str, optional): Diretório com os dados limpos.
        periodo (str, optional): Período de agregação ('dia', 'semana', 'mes', 'ano').
        data_inicio (str, optional): Data inicial para filtro (formato YYYY-MM-DD).
        data_fim (str, optional): Data final para filtro (formato YYYY-MM-DD).
        janela_media_movel (int, optional): Tamanho da janela para cálculo da média móvel.
    
    Returns:
        tuple: (serie_temporal, estatisticas) com os resultados da análise.
    """
    logger.info("Iniciando análise temporal de focos de queimadas")
    
    try:
        # Converter datas para datetime
        periodo_filtro = None
        if data_inicio or data_fim:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d') if data_inicio else None
            fim = datetime.strptime(data_fim, '%Y-%m-%d') if data_fim else None
            periodo_filtro = (inicio, fim)
        
        # Carregar dados
        df = carregar_dados(diretorio_dados, periodo_filtro)
        
        if df is None or len(df) == 0:
            logger.warning("Sem dados para análise")
            return None, None
        
        # Realizar análise temporal
        serie_temporal, estatisticas = analisar_serie_temporal(df, periodo, janela_media_movel)
        
        if serie_temporal is None:
            logger.warning("Falha na análise temporal")
            return None, None
        
        # Gerar gráfico
        titulo = f"Série Temporal de Focos de Queimadas (Agregação: {periodo.capitalize()})"
        caminho_grafico = f"output/relatorios/serie_temporal_{periodo}.png"
        gerar_grafico_temporal(serie_temporal, titulo, caminho_grafico)
        
        # Salvar resultados
        os.makedirs('output/dados_limpos/analises', exist_ok=True)
        caminho_csv = f"output/dados_limpos/analises/serie_temporal_{periodo}.csv"
        serie_temporal.to_csv(caminho_csv, index=False)
        logger.info(f"Resultados salvos em: {caminho_csv}")
        
        logger.info("Análise temporal concluída com sucesso")
        return serie_temporal, estatisticas
        
    except Exception as e:
        logger.error(f"Erro durante a análise temporal: {str(e)}", exc_info=True)
        return None, None

if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Análise temporal de focos de queimadas')
    parser.add_argument('--diretorio', type=str, default='output/dados_limpos', help='Diretório com os dados limpos')
    parser.add_argument('--periodo', type=str, default='dia', choices=['dia', 'semana', 'mes', 'ano'], help='Período de agregação')
    parser.add_argument('--data-inicio', type=str, help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--data-fim', type=str, help='Data final (YYYY-MM-DD)')
    parser.add_argument('--janela', type=int, default=7, help='Tamanho da janela para média móvel')
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/analise_temporal.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar análise
    main(args.diretorio, args.periodo, args.data_inicio, args.data_fim, args.janela)
