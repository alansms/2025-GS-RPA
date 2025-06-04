#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de coleta de dados de focos de queimadas do TerraBrasilis/INPE.

Este script é responsável por montar URLs do TerraBrasilis para baixar
arquivos diários (CSV ou ZIP) com focos de queimadas e salvá-los em
output/dados_brutos/YYYY-MM-DD.csv ou .zip.
"""

import os
import sys
import logging
import time
import pandas as pd
from datetime import datetime, timedelta

from utils_coleta import montar_url, baixar_arquivo, descompactar_zip, validar_arquivo

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.coleta')

def coletar_dados(data_inicio=None, data_fim=None, fonte="terrabrasilis"):
    """
    Coleta dados de focos de queimadas para o período especificado.
    
    Args:
        data_inicio (str, optional): Data inicial no formato YYYY-MM-DD.
            Se não for fornecida, usa a data atual.
        data_fim (str, optional): Data final no formato YYYY-MM-DD.
            Se não for fornecida, usa a data atual.
        fonte (str, optional): Fonte dos dados. Padrão é "terrabrasilis".
    
    Returns:
        list: Lista de caminhos para os arquivos baixados.
    """
    # Converter strings de data para objetos datetime
    if data_inicio is None:
        data_inicio = datetime.now().strftime('%Y-%m-%d')
    if data_fim is None:
        data_fim = datetime.now().strftime('%Y-%m-%d')
    
    data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
    data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
    
    # Garantir que o diretório de saída existe
    os.makedirs('output/dados_brutos', exist_ok=True)
    
    # Lista para armazenar caminhos dos arquivos baixados
    arquivos_baixados = []
    
    # Iterar sobre o intervalo de datas
    data_atual = data_inicio
    while data_atual <= data_fim:
        data_str = data_atual.strftime('%Y-%m-%d')
        logger.info(f"Coletando dados para a data: {data_str}")
        
        # Montar URL para a data atual
        url = montar_url(data_atual, fonte)
        
        # Definir caminho de saída
        extensao = '.zip' if url.endswith('.zip') else '.csv'
        caminho_saida = f'output/dados_brutos/{data_str}{extensao}'
        
        # Verificar se o arquivo já existe e é válido
        if os.path.exists(caminho_saida) and validar_arquivo(caminho_saida):
            logger.info(f"Arquivo para {data_str} já existe e é válido. Pulando download.")
            arquivos_baixados.append(caminho_saida)
        else:
            # Baixar arquivo
            sucesso = baixar_arquivo(url, caminho_saida)
            
            if sucesso:
                logger.info(f"Download concluído: {caminho_saida}")
                
                # Descompactar se for ZIP
                if extensao == '.zip':
                    descompactar_zip(caminho_saida, 'output/dados_brutos')
                    # Adicionar arquivos descompactados à lista
                    for arquivo in os.listdir('output/dados_brutos'):
                        if arquivo.startswith(data_str) and arquivo.endswith('.csv'):
                            arquivos_baixados.append(f'output/dados_brutos/{arquivo}')
                else:
                    arquivos_baixados.append(caminho_saida)
            else:
                logger.warning(f"Falha ao baixar dados para {data_str}")
        
        # Avançar para o próximo dia
        data_atual += timedelta(days=1)
    
    return arquivos_baixados

def main(data_inicio=None, data_fim=None, fonte="terrabrasilis"):
    """
    Função principal do módulo de coleta.
    
    Args:
        data_inicio (str, optional): Data inicial no formato YYYY-MM-DD.
        data_fim (str, optional): Data final no formato YYYY-MM-DD.
        fonte (str, optional): Fonte dos dados. Padrão é "terrabrasilis".
    
    Returns:
        list: Lista de caminhos para os arquivos baixados.
    """
    logger.info("Iniciando coleta de dados de focos de queimadas")
    
    try:
        arquivos = coletar_dados(data_inicio, data_fim, fonte)
        logger.info(f"Coleta concluída. {len(arquivos)} arquivos baixados.")
        return arquivos
    except Exception as e:
        logger.error(f"Erro durante a coleta de dados: {str(e)}", exc_info=True)
        return []

if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Coleta de dados de focos de queimadas')
    parser.add_argument('--data-inicio', type=str, help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--data-fim', type=str, help='Data final (YYYY-MM-DD)')
    parser.add_argument('--fonte', type=str, default='terrabrasilis', help='Fonte dos dados')
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/coleta.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar coleta
    main(args.data_inicio, args.data_fim, args.fonte)
