#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para gerar dados de teste para o sistema de monitoramento de queimadas.

Este script cria dados sintéticos de focos de queimadas para testar o pipeline
completo sem depender de conexão com o TerraBrasilis/INPE.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuração
NUM_DIAS = 30  # Número de dias para gerar dados
NUM_FOCOS_BASE = 500  # Número base de focos por dia
VARIACAO = 0.3  # Variação percentual aleatória no número de focos
DATA_FIM = datetime.now()  # Data final (hoje)
DATA_INICIO = DATA_FIM - timedelta(days=NUM_DIAS)  # Data inicial

# UFs e biomas para dados sintéticos
UFS = [
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
    'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
]

BIOMAS = [
    'Amazonia', 'Caatinga', 'Cerrado', 'Mata Atlantica', 
    'Pampa', 'Pantanal'
]

# Distribuição de probabilidade para UFs (algumas UFs têm mais focos)
UF_PESOS = {
    'MT': 0.15, 'PA': 0.15, 'AM': 0.12, 'RO': 0.10, 'TO': 0.08,
    'MA': 0.07, 'GO': 0.06, 'MS': 0.05, 'BA': 0.05, 'PI': 0.04,
    'MG': 0.03, 'SP': 0.02, 'PR': 0.02, 'RS': 0.01
}

# Preencher UFs restantes com pesos menores
peso_restante = 1.0 - sum(UF_PESOS.values())
peso_individual = peso_restante / (len(UFS) - len(UF_PESOS))
for uf in UFS:
    if uf not in UF_PESOS:
        UF_PESOS[uf] = peso_individual

# Distribuição de probabilidade para biomas
BIOMA_PESOS = {
    'Amazonia': 0.35, 'Cerrado': 0.30, 'Caatinga': 0.15,
    'Mata Atlantica': 0.10, 'Pantanal': 0.07, 'Pampa': 0.03
}

# Função para gerar dados de um dia
def gerar_dados_dia(data, num_focos):
    """
    Gera dados sintéticos de focos de queimadas para um dia específico.
    
    Args:
        data (datetime): Data para a qual gerar os dados.
        num_focos (int): Número de focos a gerar.
    
    Returns:
        pandas.DataFrame: DataFrame com os dados gerados.
    """
    # Criar listas para cada coluna
    datas = []
    latitudes = []
    longitudes = []
    ufs = []
    biomas = []
    satelites = []
    confiancas = []
    
    # Gerar dados aleatórios
    for _ in range(num_focos):
        # Data e hora aleatória dentro do dia
        hora = random.randint(0, 23)
        minuto = random.randint(0, 59)
        segundo = random.randint(0, 59)
        data_hora = data.replace(hour=hora, minute=minuto, second=segundo)
        datas.append(data_hora)
        
        # Coordenadas (Brasil: aproximadamente entre -35 e -73 de longitude, -33 e 5 de latitude)
        latitude = random.uniform(-33, 5)
        longitude = random.uniform(-73, -35)
        latitudes.append(latitude)
        longitudes.append(longitude)
        
        # UF (com base nos pesos)
        uf = random.choices(list(UF_PESOS.keys()), weights=list(UF_PESOS.values()), k=1)[0]
        ufs.append(uf)
        
        # Bioma (com base nos pesos)
        bioma = random.choices(list(BIOMA_PESOS.keys()), weights=list(BIOMA_PESOS.values()), k=1)[0]
        biomas.append(bioma)
        
        # Satélite
        satelite = random.choice(['NOAA-20', 'AQUA', 'TERRA', 'GOES-16', 'SUOMI-NPP'])
        satelites.append(satelite)
        
        # Confiança (0-100)
        confianca = random.randint(1, 100)
        confiancas.append(confianca)
    
    # Criar DataFrame
    df = pd.DataFrame({
        'data': datas,
        'latitude': latitudes,
        'longitude': longitudes,
        'uf': ufs,
        'bioma': biomas,
        'satelite': satelites,
        'confianca': confiancas
    })
    
    return df

# Função principal
def main():
    """
    Função principal para gerar dados de teste.
    """
    print(f"Gerando dados sintéticos de {DATA_INICIO.strftime('%Y-%m-%d')} a {DATA_FIM.strftime('%Y-%m-%d')}")
    
    # Garantir que o diretório de saída existe
    os.makedirs('output/dados_brutos', exist_ok=True)
    
    # Gerar dados para cada dia
    data_atual = DATA_INICIO
    while data_atual <= DATA_FIM:
        # Calcular número de focos para este dia (com variação aleatória)
        variacao_percentual = random.uniform(-VARIACAO, VARIACAO)
        num_focos = int(NUM_FOCOS_BASE * (1 + variacao_percentual))
        
        # Adicionar tendência sazonal (mais focos em agosto-outubro)
        mes = data_atual.month
        if mes in [8, 9, 10]:  # Agosto a Outubro (pico da temporada de queimadas)
            num_focos = int(num_focos * 1.5)
        elif mes in [11, 12, 1]:  # Novembro a Janeiro (redução gradual)
            num_focos = int(num_focos * 1.2)
        elif mes in [2, 3, 4]:  # Fevereiro a Abril (baixa temporada)
            num_focos = int(num_focos * 0.7)
        elif mes in [5, 6, 7]:  # Maio a Julho (aumento gradual)
            num_focos = int(num_focos * 0.9)
        
        # Gerar dados para este dia
        df_dia = gerar_dados_dia(data_atual, num_focos)
        
        # Salvar em CSV
        data_str = data_atual.strftime('%Y-%m-%d')
        caminho_saida = f'output/dados_brutos/focos_{data_str}.csv'
        df_dia.to_csv(caminho_saida, index=False)
        print(f"Gerados {num_focos} focos para {data_str} -> {caminho_saida}")
        
        # Avançar para o próximo dia
        data_atual += timedelta(days=1)
    
    print("Geração de dados concluída!")

if __name__ == "__main__":
    main()
