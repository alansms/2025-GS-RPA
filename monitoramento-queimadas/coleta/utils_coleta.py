#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções auxiliares para o módulo de coleta de dados de focos de queimadas.

Este módulo contém funções para montar URLs por data, baixar arquivos via
requests e descompactar ZIPs.
"""

import os
import logging
import requests
import zipfile
from datetime import datetime
from tqdm import tqdm
import pandas as pd

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.coleta.utils')

def montar_url(data, fonte="terrabrasilis"):
    """
    Monta a URL para download dos dados de focos de queimadas.
    
    Args:
        data (datetime): Data para a qual se deseja obter os dados.
        fonte (str, optional): Fonte dos dados. Padrão é "terrabrasilis".
    
    Returns:
        str: URL para download dos dados.
    """
    data_str = data.strftime('%Y-%m-%d')
    ano = data.strftime('%Y')
    mes = data.strftime('%m')
    dia = data.strftime('%d')
    
    if fonte.lower() == "terrabrasilis":
        # URL fictícia - deve ser substituída pela URL real do TerraBrasilis
        return f"https://queimadas.dgi.inpe.br/api/focos/csv/{ano}/{mes}/{dia}/focos_{data_str}.csv"
    else:
        raise ValueError(f"Fonte de dados não suportada: {fonte}")

def baixar_arquivo(url, caminho_saida, timeout=30, tentativas=3):
    """
    Baixa um arquivo da URL especificada e salva no caminho indicado.
    
    Args:
        url (str): URL para download do arquivo.
        caminho_saida (str): Caminho onde o arquivo será salvo.
        timeout (int, optional): Tempo limite em segundos para a requisição.
        tentativas (int, optional): Número de tentativas em caso de falha.
    
    Returns:
        bool: True se o download foi bem-sucedido, False caso contrário.
    """
    for tentativa in range(1, tentativas + 1):
        try:
            logger.info(f"Baixando {url} (tentativa {tentativa}/{tentativas})")
            
            # Fazer requisição com streaming para arquivos grandes
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                
                # Obter tamanho total do arquivo (se disponível)
                total_size = int(r.headers.get('content-length', 0))
                
                # Configurar barra de progresso
                progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(caminho_saida))
                
                # Salvar arquivo em chunks para evitar consumo excessivo de memória
                with open(caminho_saida, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))
                
                progress_bar.close()
                
                # Verificar se o arquivo foi baixado corretamente
                if os.path.exists(caminho_saida) and os.path.getsize(caminho_saida) > 0:
                    logger.info(f"Download concluído: {caminho_saida}")
                    return True
                else:
                    logger.warning(f"Arquivo baixado está vazio: {caminho_saida}")
                    return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Erro ao baixar arquivo (tentativa {tentativa}/{tentativas}): {str(e)}")
            
            # Se for a última tentativa, retornar False
            if tentativa == tentativas:
                return False
    
    return False

def descompactar_zip(arquivo_zip, diretorio_destino):
    """
    Descompacta um arquivo ZIP no diretório especificado.
    
    Args:
        arquivo_zip (str): Caminho para o arquivo ZIP.
        diretorio_destino (str): Diretório onde os arquivos serão extraídos.
    
    Returns:
        list: Lista de caminhos para os arquivos extraídos.
    """
    try:
        logger.info(f"Descompactando {arquivo_zip} em {diretorio_destino}")
        
        # Garantir que o diretório de destino existe
        os.makedirs(diretorio_destino, exist_ok=True)
        
        # Lista para armazenar caminhos dos arquivos extraídos
        arquivos_extraidos = []
        
        # Extrair arquivos
        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
            # Listar arquivos no ZIP
            for arquivo in zip_ref.namelist():
                logger.info(f"Extraindo {arquivo}")
                zip_ref.extract(arquivo, diretorio_destino)
                arquivos_extraidos.append(os.path.join(diretorio_destino, arquivo))
        
        logger.info(f"Descompactação concluída: {len(arquivos_extraidos)} arquivos extraídos")
        return arquivos_extraidos
        
    except zipfile.BadZipFile as e:
        logger.error(f"Erro ao descompactar arquivo ZIP: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Erro inesperado ao descompactar arquivo ZIP: {str(e)}")
        return []

def validar_arquivo(caminho_arquivo):
    """
    Valida se um arquivo é válido (não está corrompido ou vazio).
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo a ser validado.
    
    Returns:
        bool: True se o arquivo é válido, False caso contrário.
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            logger.warning(f"Arquivo não existe: {caminho_arquivo}")
            return False
        
        # Verificar se o arquivo não está vazio
        if os.path.getsize(caminho_arquivo) == 0:
            logger.warning(f"Arquivo está vazio: {caminho_arquivo}")
            return False
        
        # Se for um arquivo ZIP, verificar integridade
        if caminho_arquivo.endswith('.zip'):
            try:
                with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                    # Testar integridade do ZIP
                    result = zip_ref.testzip()
                    if result is not None:
                        logger.warning(f"Arquivo ZIP corrompido: {caminho_arquivo}, primeiro arquivo com erro: {result}")
                        return False
            except zipfile.BadZipFile:
                logger.warning(f"Arquivo ZIP inválido: {caminho_arquivo}")
                return False
        
        # Se for um arquivo CSV, verificar se tem pelo menos um cabeçalho e uma linha
        elif caminho_arquivo.endswith('.csv'):
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                # Ler as primeiras duas linhas
                header = f.readline()
                first_line = f.readline()
                
                # Verificar se tem cabeçalho e pelo menos uma linha de dados
                if not header or not first_line:
                    logger.warning(f"Arquivo CSV inválido (sem cabeçalho ou dados): {caminho_arquivo}")
                    return False
        
        # Arquivo válido
        return True
        
    except Exception as e:
        logger.error(f"Erro ao validar arquivo {caminho_arquivo}: {str(e)}")
        return False

def coletar_dados_inpe(data_inicio, data_fim):
    """
    Coleta dados de focos de queimada do INPE via API TerraBrasilis.

    Args:
        data_inicio (str): Data inicial no formato YYYY-MM-DD
        data_fim (str): Data final no formato YYYY-MM-DD

    Returns:
        pandas.DataFrame: DataFrame com os dados coletados
    """
    try:
        # URL base da API do INPE
        base_url = "https://terrabrasilis.dpi.inpe.br/queimadas/dados-abertos/api/focos"

        # Parâmetros da requisição
        params = {
            'inicio': data_inicio,
            'fim': data_fim,
            'pais': 'Brasil',
            'formato': 'json'
        }

        logger.info(f"Coletando dados do INPE para o período {data_inicio} a {data_fim}")

        # Fazer requisição à API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Levanta exceção para erros HTTP

        # Converter resposta para DataFrame
        dados = pd.DataFrame(response.json())

        # Processar e limpar os dados
        if not dados.empty:
            # Converter data para datetime
            dados['data'] = pd.to_datetime(dados['data_hora'])

            # Renomear e selecionar colunas relevantes
            colunas = {
                'latitude': 'latitude',
                'longitude': 'longitude',
                'estado': 'uf',
                'municipio': 'municipio',
                'bioma': 'bioma',
                'data': 'data'
            }

            dados = dados.rename(columns=colunas)[colunas.values()]

            logger.info(f"Dados coletados com sucesso: {len(dados)} registros")
            return dados
        else:
            logger.warning("Nenhum dado encontrado para o período especificado")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao coletar dados do INPE: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao processar dados: {str(e)}")
        return None

