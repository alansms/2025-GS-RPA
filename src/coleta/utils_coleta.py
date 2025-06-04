import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('queimadas.coleta')

# Coordenadas por UF
COORDENADAS_UF = {
    'AC': {'lat': (-11.14, -7.11), 'lon': (-74.00, -66.62)},
    'AL': {'lat': (-10.50, -8.81), 'lon': (-38.24, -35.15)},
    'AM': {'lat': (-9.49, 2.25), 'lon': (-73.80, -56.09)},
    'AP': {'lat': (-1.23, 4.44), 'lon': (-54.87, -49.87)},
    'BA': {'lat': (-18.34, -8.53), 'lon': (-46.61, -37.34)},
    'CE': {'lat': (-7.86, -2.78), 'lon': (-41.42, -37.25)},
    'DF': {'lat': (-16.05, -15.50), 'lon': (-48.25, -47.33)},
    'ES': {'lat': (-21.30, -17.89), 'lon': (-41.88, -39.86)},
    'GO': {'lat': (-19.47, -12.39), 'lon': (-53.25, -45.90)},
    'MA': {'lat': (-10.26, -1.05), 'lon': (-48.73, -41.79)},
    'MG': {'lat': (-22.92, -14.23), 'lon': (-51.05, -39.85)},
    'MS': {'lat': (-24.07, -17.16), 'lon': (-58.17, -50.92)},
    'MT': {'lat': (-18.04, -7.35), 'lon': (-61.60, -50.23)},
    'PA': {'lat': (-9.84, 2.59), 'lon': (-58.89, -46.06)},
    'PB': {'lat': (-8.28, -6.02), 'lon': (-38.77, -34.79)},
    'PE': {'lat': (-9.48, -7.15), 'lon': (-41.35, -34.82)},
    'PI': {'lat': (-10.92, -2.74), 'lon': (-45.99, -40.37)},
    'PR': {'lat': (-26.72, -22.51), 'lon': (-54.62, -48.02)},
    'RJ': {'lat': (-23.37, -20.76), 'lon': (-44.89, -40.96)},
    'RN': {'lat': (-6.98, -4.83), 'lon': (-38.58, -34.96)},
    'RO': {'lat': (-13.69, -7.96), 'lon': (-66.81, -59.77)},
    'RR': {'lat': (-1.58, 5.27), 'lon': (-64.82, -58.89)},
    'RS': {'lat': (-33.75, -27.08), 'lon': (-57.64, -49.71)},
    'SC': {'lat': (-29.35, -25.95), 'lon': (-53.84, -48.35)},
    'SE': {'lat': (-11.57, -9.51), 'lon': (-38.24, -36.39)},
    'SP': {'lat': (-25.31, -19.78), 'lon': (-53.11, -44.16)},
    'TO': {'lat': (-13.46, -5.22), 'lon': (-50.73, -45.70)}
}

def coletar_dados_inpe(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """
    Simula a coleta de dados de focos de queimada para demonstração.
    Garante que todas as UFs estejam presentes no conjunto de dados.
    """
    try:
        datas = pd.date_range(start=data_inicio, end=data_fim)
        ufs = sorted(list(COORDENADAS_UF.keys()))  # Garante ordem consistente
        biomas = ['Mata Atlântica', 'Cerrado', 'Amazônia', 'Caatinga', 'Pampa', 'Pantanal']

        dados = []
        for data in datas:
            # Garante pontos mínimos para cada UF
            for uf in ufs:
                coords = COORDENADAS_UF[uf]
                # Garante pelo menos 2 pontos por UF para visualização
                n_pontos = max(2, np.random.randint(2, 8))

                for _ in range(n_pontos):
                    # Gerar coordenadas dentro dos limites da UF
                    lat = np.random.uniform(coords['lat'][0], coords['lat'][1])
                    lon = np.random.uniform(coords['lon'][0], coords['lon'][1])

                    # Atribuir bioma de acordo com a região e localização
                    bioma = None

                    # Amazônia Legal
                    if uf in ['AM', 'AC', 'RR', 'RO', 'PA', 'AP', 'TO', 'MT', 'MA']:
                        bioma = 'Amazônia'
                    # Caatinga
                    elif uf in ['PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA']:
                        bioma = 'Caatinga'
                    # Cerrado Central
                    elif uf in ['GO', 'DF', 'MG', 'SP', 'MS']:
                        bioma = 'Cerrado'
                    # Sul
                    elif uf in ['PR', 'SC', 'RS']:
                        bioma = 'Mata Atlântica' if np.random.random() > 0.3 else 'Pampa'
                    # Pantanal
                    elif uf in ['MT', 'MS']:
                        bioma = 'Pantanal' if np.random.random() > 0.7 else 'Cerrado'
                    # Costa
                    else:
                        bioma = 'Mata Atlântica'

                    dados.append({
                        'data': data,
                        'latitude': lat,
                        'longitude': lon,
                        'uf': uf,
                        'bioma': bioma
                    })

        df = pd.DataFrame(dados)

        # Validação final para garantir que todas as UFs estão presentes
        ufs_presentes = set(df['uf'].unique())
        if len(ufs_presentes) != len(COORDENADAS_UF):
            logger.warning(f"Algumas UFs estão faltando. Encontradas: {len(ufs_presentes)}/{len(COORDENADAS_UF)}")
            ufs_faltantes = set(COORDENADAS_UF.keys()) - ufs_presentes
            logger.warning(f"UFs faltantes: {ufs_faltantes}")

        logger.info(f"Dados gerados com sucesso: {len(df)} registros em {len(df['uf'].unique())} UFs")
        return df

    except Exception as e:
        logger.error(f"Erro ao coletar dados: {str(e)}")
        return None
