#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções auxiliares para o módulo de tratamento de dados de focos de queimadas.

Este módulo contém funções genéricas para normalizar colunas, preencher nulos
e conversão de tipos.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.tratamento.utils')

def normalizar_colunas(df):
    """
    Normaliza os nomes das colunas do DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados brutos.
    
    Returns:
        pandas.DataFrame: DataFrame com nomes de colunas normalizados.
    """
    # Mapeamento de nomes de colunas possíveis para nomes padronizados
    mapeamento_colunas = {
        'data': 'data',
        'data_hora': 'data',
        'datahora': 'data',
        'data_hora_gmt': 'data',
        'timestamp': 'data',
        
        'latitude': 'latitude',
        'lat': 'latitude',
        'latidude': 'latitude',
        
        'longitude': 'longitude',
        'long': 'longitude',
        'lon': 'longitude',
        
        'satelite': 'satelite',
        'satellite': 'satelite',
        'sat': 'satelite',
        
        'pais': 'pais',
        'country': 'pais',
        'país': 'pais',
        
        'estado': 'uf',
        'uf': 'uf',
        'estado_sigla': 'uf',
        'sigla_estado': 'uf',
        'state': 'uf',
        
        'municipio': 'municipio',
        'cidade': 'municipio',
        'city': 'municipio',
        'município': 'municipio',
        
        'bioma': 'bioma',
        'biome': 'bioma',
        
        'frp': 'frp',
        'potencia_radiativa_fogo': 'frp',
        'fire_radiative_power': 'frp',
        
        'confianca': 'confianca',
        'confidence': 'confianca',
        'conf': 'confianca',
        'confiança': 'confianca'
    }
    
    # Normalizar nomes das colunas
    df_normalizado = df.copy()
    
    # Converter todos os nomes para minúsculas e remover espaços
    df_normalizado.columns = [col.lower().strip().replace(' ', '_') for col in df_normalizado.columns]
    
    # Mapear para nomes padronizados
    colunas_renomeadas = {}
    for col in df_normalizado.columns:
        if col in mapeamento_colunas:
            colunas_renomeadas[col] = mapeamento_colunas[col]
    
    # Renomear colunas
    if colunas_renomeadas:
        df_normalizado = df_normalizado.rename(columns=colunas_renomeadas)
        logger.info(f"Colunas renomeadas: {colunas_renomeadas}")
    
    return df_normalizado

def preencher_nulos(df):
    """
    Preenche valores nulos no DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame com valores nulos.
    
    Returns:
        pandas.DataFrame: DataFrame com valores nulos preenchidos.
    """
    df_preenchido = df.copy()
    
    # Verificar valores nulos
    nulos_por_coluna = df_preenchido.isnull().sum()
    colunas_com_nulos = nulos_por_coluna[nulos_por_coluna > 0]
    
    if not colunas_com_nulos.empty:
        logger.info(f"Colunas com valores nulos: {colunas_com_nulos.to_dict()}")
        
        # Preencher valores nulos de acordo com o tipo de coluna
        for coluna in colunas_com_nulos.index:
            # Colunas numéricas: preencher com a mediana
            if pd.api.types.is_numeric_dtype(df_preenchido[coluna]):
                mediana = df_preenchido[coluna].median()
                df_preenchido[coluna] = df_preenchido[coluna].fillna(mediana)
                logger.info(f"Preenchendo valores nulos na coluna '{coluna}' com a mediana: {mediana}")
            
            # Colunas de data: não preencher (manter como NaT)
            elif coluna == 'data':
                logger.info(f"Mantendo valores nulos na coluna de data '{coluna}'")
            
            # Colunas categóricas: preencher com "Desconhecido"
            elif coluna in ['uf', 'municipio', 'bioma', 'pais', 'satelite']:
                df_preenchido[coluna] = df_preenchido[coluna].fillna('Desconhecido')
                logger.info(f"Preenchendo valores nulos na coluna '{coluna}' com 'Desconhecido'")
            
            # Outras colunas: preencher com string vazia
            else:
                df_preenchido[coluna] = df_preenchido[coluna].fillna('')
                logger.info(f"Preenchendo valores nulos na coluna '{coluna}' com string vazia")
    
    return df_preenchido

def converter_tipos(df):
    """
    Converte os tipos de dados das colunas do DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame com tipos de dados originais.
    
    Returns:
        pandas.DataFrame: DataFrame com tipos de dados convertidos.
    """
    df_convertido = df.copy()
    
    # Converter coluna de data para datetime
    if 'data' in df_convertido.columns:
        try:
            # Tentar diferentes formatos de data
            formatos = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y'
            ]
            
            for formato in formatos:
                try:
                    df_convertido['data'] = pd.to_datetime(df_convertido['data'], format=formato, errors='raise')
                    logger.info(f"Coluna 'data' convertida para datetime com formato: {formato}")
                    break
                except ValueError:
                    continue
            
            # Se nenhum formato específico funcionar, tentar conversão automática
            if not pd.api.types.is_datetime64_dtype(df_convertido['data']):
                df_convertido['data'] = pd.to_datetime(df_convertido['data'], errors='coerce')
                logger.info("Coluna 'data' convertida para datetime com detecção automática de formato")
        
        except Exception as e:
            logger.warning(f"Erro ao converter coluna 'data' para datetime: {str(e)}")
    
    # Converter colunas de coordenadas para float
    for col in ['latitude', 'longitude']:
        if col in df_convertido.columns:
            try:
                df_convertido[col] = pd.to_numeric(df_convertido[col], errors='coerce')
                logger.info(f"Coluna '{col}' convertida para float")
            except Exception as e:
                logger.warning(f"Erro ao converter coluna '{col}' para float: {str(e)}")
    
    # Converter coluna de confiança para int
    if 'confianca' in df_convertido.columns:
        try:
            df_convertido['confianca'] = pd.to_numeric(df_convertido['confianca'], errors='coerce').fillna(0).astype(int)
            logger.info("Coluna 'confianca' convertida para int")
        except Exception as e:
            logger.warning(f"Erro ao converter coluna 'confianca' para int: {str(e)}")
    
    # Converter coluna FRP para float
    if 'frp' in df_convertido.columns:
        try:
            df_convertido['frp'] = pd.to_numeric(df_convertido['frp'], errors='coerce')
            logger.info("Coluna 'frp' convertida para float")
        except Exception as e:
            logger.warning(f"Erro ao converter coluna 'frp' para float: {str(e)}")
    
    return df_convertido

def validar_coordenadas_brasil(latitude, longitude):
    """
    Valida se as coordenadas estão dentro dos limites do Brasil.

    Args:
        latitude (float): Latitude do ponto
        longitude (float): Longitude do ponto

    Returns:
        bool: True se as coordenadas estão dentro dos limites do Brasil, False caso contrário
    """
    # Limites aproximados do Brasil
    LIMITE_SUL = -33.75
    LIMITE_NORTE = 5.27
    LIMITE_OESTE = -73.99
    LIMITE_LESTE = -34.79

    return (LIMITE_SUL <= latitude <= LIMITE_NORTE and
            LIMITE_OESTE <= longitude <= LIMITE_LESTE)

def validar_uf(uf):
    """
    Valida se a UF é válida no Brasil.

    Args:
        uf (str): Sigla do estado

    Returns:
        bool: True se a UF é válida, False caso contrário
    """
    ufs_validas = {
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    }
    return uf.upper() in ufs_validas

