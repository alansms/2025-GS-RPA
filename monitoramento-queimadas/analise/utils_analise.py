#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções auxiliares para o módulo de análise de focos de queimadas.

Este módulo contém funções para cálculo de média móvel, desvio padrão,
filtragem por período e estatísticas descritivas.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.analise.utils')

def calcular_media_movel(serie, janela):
    """
    Calcula a média móvel de uma série temporal.
    
    Args:
        serie (pandas.Series): Série temporal para cálculo da média móvel.
        janela (int): Tamanho da janela para cálculo da média móvel.
    
    Returns:
        pandas.Series: Série com a média móvel calculada.
    """
    try:
        # Verificar se a janela é válida
        if janela <= 0:
            logger.warning(f"Tamanho de janela inválido: {janela}. Usando janela = 1.")
            janela = 1
        
        # Calcular média móvel
        media_movel = serie.rolling(window=janela, min_periods=1).mean()
        return media_movel
        
    except Exception as e:
        logger.error(f"Erro ao calcular média móvel: {str(e)}")
        return pd.Series(np.nan, index=serie.index)

def calcular_estatisticas(serie):
    """
    Calcula estatísticas descritivas de uma série temporal.
    
    Args:
        serie (pandas.Series): Série temporal para cálculo das estatísticas.
    
    Returns:
        dict: Dicionário com as estatísticas calculadas.
    """
    try:
        estatisticas = {
            'media': serie.mean(),
            'mediana': serie.median(),
            'desvio_padrao': serie.std(),
            'minimo': serie.min(),
            'maximo': serie.max(),
            'total': serie.sum(),
            'contagem': len(serie),
            'quartis': [
                serie.quantile(0.25),
                serie.quantile(0.5),
                serie.quantile(0.75)
            ]
        }
        return estatisticas
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")
        return {
            'media': np.nan,
            'mediana': np.nan,
            'desvio_padrao': np.nan,
            'minimo': np.nan,
            'maximo': np.nan,
            'total': np.nan,
            'contagem': 0,
            'quartis': [np.nan, np.nan, np.nan]
        }

def filtrar_por_periodo(df, data_inicio=None, data_fim=None):
    """
    Filtra um DataFrame por um período específico.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser filtrado.
        data_inicio (datetime, optional): Data inicial do período.
        data_fim (datetime, optional): Data final do período.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    try:
        # Verificar se a coluna de data existe
        if 'data' not in df.columns:
            logger.error("Coluna 'data' não encontrada no DataFrame")
            return df
        
        # Criar cópia do DataFrame
        df_filtrado = df.copy()
        
        # Filtrar por data de início, se especificada
        if data_inicio is not None:
            df_filtrado = df_filtrado[df_filtrado['data'] >= data_inicio]
            logger.info(f"Dados filtrados a partir de {data_inicio}")
        
        # Filtrar por data de fim, se especificada
        if data_fim is not None:
            df_filtrado = df_filtrado[df_filtrado['data'] <= data_fim]
            logger.info(f"Dados filtrados até {data_fim}")
        
        logger.info(f"Filtro por período aplicado: {len(df_filtrado)} registros restantes")
        return df_filtrado
        
    except Exception as e:
        logger.error(f"Erro ao filtrar por período: {str(e)}")
        return df

def detectar_anomalias(serie, limiar=2.0):
    """
    Detecta anomalias em uma série temporal usando o método do desvio padrão.
    
    Args:
        serie (pandas.Series): Série temporal para detecção de anomalias.
        limiar (float, optional): Número de desvios padrão para considerar um valor como anomalia.
    
    Returns:
        pandas.Series: Série booleana indicando quais valores são anomalias.
    """
    try:
        # Calcular média e desvio padrão
        media = serie.mean()
        desvio = serie.std()
        
        # Calcular limites
        limite_superior = media + limiar * desvio
        limite_inferior = media - limiar * desvio
        
        # Identificar anomalias
        anomalias = (serie > limite_superior) | (serie < limite_inferior)
        
        logger.info(f"Detecção de anomalias: {anomalias.sum()} anomalias encontradas (limiar = {limiar})")
        return anomalias
        
    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {str(e)}")
        return pd.Series(False, index=serie.index)

def calcular_tendencia(serie):
    """
    Calcula a tendência de uma série temporal usando regressão linear.
    
    Args:
        serie (pandas.Series): Série temporal para cálculo da tendência.
    
    Returns:
        tuple: (coeficiente_angular, intercepto) da reta de tendência.
    """
    try:
        # Criar array de índices
        x = np.arange(len(serie))
        
        # Calcular coeficientes da regressão linear
        coef = np.polyfit(x, serie, 1)
        
        # Extrair coeficiente angular e intercepto
        coef_angular = coef[0]
        intercepto = coef[1]
        
        # Determinar direção da tendência
        if coef_angular > 0:
            direcao = "crescente"
        elif coef_angular < 0:
            direcao = "decrescente"
        else:
            direcao = "estável"
        
        logger.info(f"Tendência calculada: {direcao} (coef. angular = {coef_angular:.4f})")
        return coef_angular, intercepto, direcao
        
    except Exception as e:
        logger.error(f"Erro ao calcular tendência: {str(e)}")
        return 0, 0, "indeterminada"
