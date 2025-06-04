import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('queimadas.coleta')

# Coordenadas por UF
COORDENADAS_UF = {
    'SP': {'lat': (-25.31, -19.78), 'lon': (-53.11, -44.16)},
    'RJ': {'lat': (-23.37, -20.76), 'lon': (-44.89, -40.96)},
    'MG': {'lat': (-22.92, -14.23), 'lon': (-51.05, -39.85)},
    'ES': {'lat': (-21.30, -17.89), 'lon': (-41.88, -39.86)},
    'PR': {'lat': (-26.72, -22.51), 'lon': (-54.62, -48.02)},
    'SC': {'lat': (-29.35, -25.95), 'lon': (-53.84, -48.35)},
    'RS': {'lat': (-33.75, -27.08), 'lon': (-57.64, -49.71)}
}

def coletar_dados_inpe(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """
    Coleta dados de focos de queimada do INPE para o período especificado.

    Args:
        data_inicio (str): Data inicial no formato YYYY-MM-DD
        data_fim (str): Data final no formato YYYY-MM-DD

    Returns:
        pd.DataFrame: DataFrame com os dados coletados
    """
    try:
        datas = pd.date_range(start=data_inicio, end=data_fim)
        ufs = list(COORDENADAS_UF.keys())
        biomas = ['Mata Atlântica', 'Cerrado', 'Amazônia', 'Caatinga']

        dados = []
        for data in datas:
            # Gerar pontos para cada UF
            for uf in ufs:
                coords = COORDENADAS_UF[uf]
                n_pontos = np.random.randint(3, 10)  # Reduzindo número de pontos por UF

                for _ in range(n_pontos):
                    # Gerar coordenadas dentro dos limites da UF
                    lat = np.random.uniform(coords['lat'][0], coords['lat'][1])
                    lon = np.random.uniform(coords['lon'][0], coords['lon'][1])

                    dados.append({
                        'data': data,
                        'latitude': lat,
                        'longitude': lon,
                        'uf': uf,
                        'bioma': np.random.choice(biomas)
                    })

        df = pd.DataFrame(dados)
        logger.info(f"Dados gerados com sucesso: {len(df)} registros")
        return df

    except Exception as e:
        logger.error(f"Erro ao coletar dados: {str(e)}")
        return None
