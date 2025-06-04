import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger('queimadas.analise')

def gerar_serie_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera uma série temporal dos focos de queimada.

    Args:
        df (pd.DataFrame): DataFrame com os dados de focos

    Returns:
        pd.DataFrame: DataFrame com a série temporal
    """
    try:
        serie = df.groupby('data').size().reset_index(name='focos')
        serie['media_movel'] = serie['focos'].rolling(window=7).mean()
        logger.info(f"Série temporal gerada com {len(serie)} pontos")
        return serie
    except Exception as e:
        logger.error(f"Erro ao gerar série temporal: {str(e)}")
        return None
