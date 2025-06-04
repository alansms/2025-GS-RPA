import pandas as pd
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('queimadas.coleta')

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
        # Simular dados para demonstração
        datas = pd.date_range(start=data_inicio, end=data_fim)
        ufs = ['SP', 'MG', 'RJ', 'ES', 'PR', 'SC', 'RS']
        biomas = ['Mata Atlântica', 'Cerrado', 'Amazônia', 'Caatinga']

        dados = []
        for data in datas:
            # Gerar alguns pontos aleatórios para cada data
            n_pontos = np.random.randint(5, 20)
            for _ in range(n_pontos):
                dados.append({
                    'data': data,
                    'latitude': np.random.uniform(-33.75, 5.27),
                    'longitude': np.random.uniform(-73.99, -34.79),
                    'uf': np.random.choice(ufs),
                    'bioma': np.random.choice(biomas)
                })

        df = pd.DataFrame(dados)
        logger.info(f"Dados gerados com sucesso: {len(df)} registros")
        return df

    except Exception as e:
        logger.error(f"Erro ao coletar dados: {str(e)}")
        return None
