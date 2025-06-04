#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de tratamento de dados de focos de queimadas.

Este script é responsável por ler CSV(s) brutos, corrigir encoding, remover duplicados,
tratar valores nulos, converter colunas de data para datetime, padronizar nomes de colunas
e salvar dados limpos em output/dados_limpos/YYYY-MM-DD.csv.
"""

import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime
from glob import glob

from tratamento.utils_tratamento import normalizar_colunas, preencher_nulos, converter_tipos

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.tratamento')

def validar_coordenadas_brasil(latitude, longitude):
    """
    Valida se as coordenadas estão dentro do Brasil.

    Args:
        latitude (float): Latitude a ser validada.
        longitude (float): Longitude a ser validada.

    Returns:
        bool: True se as coordenadas estão dentro do Brasil, False caso contrário.
    """
    return -33.7500 <= latitude <= 5.2725 and -73.9900 <= longitude <= -34.7930

def validar_uf(uf):
    """
    Valida se a UF é válida.

    Args:
        uf (str): UF a ser validada.

    Returns:
        bool: True se a UF é válida, False caso contrário.
    """
    ufs_validas = [
        'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT',
        'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
    ]
    return uf in ufs_validas

def tratar_arquivo(caminho_arquivo, diretorio_saida, force=False):
    """
    Trata um arquivo CSV bruto e salva o resultado no diretório de saída.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV bruto.
        diretorio_saida (str): Diretório onde o arquivo tratado será salvo.
        force (bool, optional): Se True, força o reprocessamento mesmo se o arquivo já existir.
    
    Returns:
        str: Caminho para o arquivo tratado, ou None se ocorrer um erro.
    """
    try:
        # Extrair data do nome do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        data_str = nome_arquivo.split('_')[-1].split('.')[0]  # Assumindo formato "focos_YYYY-MM-DD.csv"
        
        # Verificar se a data está no formato esperado
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
            data_formatada = data.strftime('%Y-%m-%d')
        except ValueError:
            # Se não conseguir extrair a data do nome, usar a data atual
            logger.warning(f"Não foi possível extrair a data do nome do arquivo: {nome_arquivo}. Usando data atual.")
            data_formatada = datetime.now().strftime('%Y-%m-%d')
        
        # Definir caminho de saída
        caminho_saida = os.path.join(diretorio_saida, f"{data_formatada}.csv")
        
        # Verificar se o arquivo já existe e não está sendo forçado o reprocessamento
        if os.path.exists(caminho_saida) and not force:
            logger.info(f"Arquivo já tratado: {caminho_saida}. Use --force para reprocessar.")
            return caminho_saida
        
        logger.info(f"Tratando arquivo: {caminho_arquivo}")
        
        # Ler o arquivo CSV com diferentes encodings
        df = None
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(caminho_arquivo, encoding=encoding, low_memory=False)
                logger.info(f"Arquivo lido com encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            logger.error(f"Não foi possível ler o arquivo com nenhum dos encodings testados: {caminho_arquivo}")
            return None
        
        # Normalizar nomes das colunas
        df = normalizar_colunas(df)
        
        # Remover duplicados
        n_duplicados = df.duplicated().sum()
        if n_duplicados > 0:
            logger.info(f"Removendo {n_duplicados} registros duplicados")
            df = df.drop_duplicates()
        
        # Preencher valores nulos
        df = preencher_nulos(df)
        
        # Converter tipos de dados
        df = converter_tipos(df)
        
        # Validar e filtrar coordenadas do Brasil
        df['coords_validas'] = df.apply(
            lambda row: validar_coordenadas_brasil(row['latitude'], row['longitude'])
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude'])
            else False,
            axis=1
        )

        # Validar UFs
        df['uf_valida'] = df['uf'].apply(
            lambda x: validar_uf(x) if pd.notnull(x) else False
        )

        # Filtrar apenas dados válidos
        df_valido = df[df['coords_validas'] & df['uf_valida']].copy()

        # Remover colunas auxiliares
        df_valido = df_valido.drop(['coords_validas', 'uf_valida'], axis=1)

        # Log de registros removidos
        total_removidos = len(df) - len(df_valido)
        if total_removidos > 0:
            logger.warning(f"Removidos {total_removidos} registros com coordenadas fora do Brasil ou UFs inválidas")

        # Preencher nulos
        df_valido = preencher_nulos(df_valido)

        # Garantir que o diretório de saída existe
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Salvar arquivo tratado
        df_valido.to_csv(caminho_saida, index=False, encoding='utf-8')
        logger.info(f"Arquivo tratado salvo: {caminho_saida}")
        
        return caminho_saida
        
    except Exception as e:
        logger.error(f"Erro ao tratar arquivo {caminho_arquivo}: {str(e)}", exc_info=True)
        return None

def main(input_dir='output/dados_brutos', output_dir='output/dados_limpos', force=False):
    """
    Função principal do módulo de tratamento.
    
    Args:
        input_dir (str, optional): Diretório de entrada com os arquivos brutos.
        output_dir (str, optional): Diretório de saída para os arquivos tratados.
        force (bool, optional): Se True, força o reprocessamento de todos os arquivos.
    
    Returns:
        list: Lista de caminhos para os arquivos tratados.
    """
    logger.info("Iniciando tratamento de dados de focos de queimadas")
    
    try:
        # Garantir que os diretórios existem
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Listar arquivos CSV no diretório de entrada
        arquivos_csv = glob(os.path.join(input_dir, '*.csv'))
        
        if not arquivos_csv:
            logger.warning(f"Nenhum arquivo CSV encontrado em {input_dir}")
            return []
        
        logger.info(f"Encontrados {len(arquivos_csv)} arquivos CSV para tratamento")
        
        # Tratar cada arquivo
        arquivos_tratados = []
        for arquivo in arquivos_csv:
            caminho_tratado = tratar_arquivo(arquivo, output_dir, force)
            if caminho_tratado:
                arquivos_tratados.append(caminho_tratado)
        
        logger.info(f"Tratamento concluído. {len(arquivos_tratados)} arquivos tratados.")
        return arquivos_tratados
        
    except Exception as e:
        logger.error(f"Erro durante o tratamento de dados: {str(e)}", exc_info=True)
        return []

if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Tratamento de dados de focos de queimadas')
    parser.add_argument('--input-dir', type=str, default='output/dados_brutos', help='Diretório de entrada')
    parser.add_argument('--output-dir', type=str, default='output/dados_limpos', help='Diretório de saída')
    parser.add_argument('--force', action='store_true', help='Força o reprocessamento de todos os arquivos')
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/tratamento.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar tratamento
    main(args.input_dir, args.output_dir, args.force)
