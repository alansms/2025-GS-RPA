import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger('queimadas.alertas')

def calcular_media_historica(df: pd.DataFrame, dias_base: int = 7) -> float:
    """
    Calcula a média histórica dos últimos X dias para comparação
    """
    data_atual = df['data'].max()
    data_inicio = data_atual - timedelta(days=dias_base)
    df_periodo = df[df['data'] >= data_inicio]
    return df_periodo.groupby('data').size().mean()

def detectar_anomalias(df: pd.DataFrame, limite_desvio: float = 1.5) -> pd.DataFrame:
    """
    Detecta anomalias nos focos de queimada baseado em desvios da média
    """
    try:
        # Agrupa dados por data
        serie_diaria = df.groupby('data').size().reset_index(name='focos')

        # Calcula média móvel e desvio padrão
        serie_diaria['media_movel'] = serie_diaria['focos'].rolling(window=7, min_periods=1).mean()
        serie_diaria['desvio_padrao'] = serie_diaria['focos'].rolling(window=7, min_periods=1).std()

        # Define limites para anomalias
        serie_diaria['limite_superior'] = serie_diaria['media_movel'] + (serie_diaria['desvio_padrao'] * limite_desvio)

        # Identifica anomalias
        serie_diaria['is_anomalia'] = serie_diaria['focos'] > serie_diaria['limite_superior']

        return serie_diaria[serie_diaria['is_anomalia']]

    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {str(e)}")
        return pd.DataFrame()

def gerar_alerta_por_regiao(df: pd.DataFrame, data_ref: datetime = None) -> list:
    """
    Gera alertas por região com base em aumentos significativos
    """
    if data_ref is None:
        data_ref = df['data'].max()

    alertas = []

    try:
        # Análise por UF
        for uf in df['uf'].unique():
            df_uf = df[df['uf'] == uf]
            anomalias = detectar_anomalias(df_uf)

            if not anomalias.empty and data_ref in anomalias['data'].values:
                focos_hoje = anomalias.loc[anomalias['data'] == data_ref, 'focos'].iloc[0]
                media = anomalias.loc[anomalias['data'] == data_ref, 'media_movel'].iloc[0]
                aumento = ((focos_hoje - media) / media) * 100

                alertas.append({
                    'tipo': 'UF',
                    'local': uf,
                    'data': data_ref,
                    'focos': int(focos_hoje),
                    'media': round(media, 1),
                    'aumento': round(aumento, 1),
                    'nivel': 'ALTO' if aumento > 100 else 'MÉDIO'
                })

        # Análise por bioma
        for bioma in df['bioma'].unique():
            df_bioma = df[df['bioma'] == bioma]
            anomalias = detectar_anomalias(df_bioma)

            if not anomalias.empty and data_ref in anomalias['data'].values:
                focos_hoje = anomalias.loc[anomalias['data'] == data_ref, 'focos'].iloc[0]
                media = anomalias.loc[anomalias['data'] == data_ref, 'media_movel'].iloc[0]
                aumento = ((focos_hoje - media) / media) * 100

                alertas.append({
                    'tipo': 'Bioma',
                    'local': bioma,
                    'data': data_ref,
                    'focos': int(focos_hoje),
                    'media': round(media, 1),
                    'aumento': round(aumento, 1),
                    'nivel': 'ALTO' if aumento > 100 else 'MÉDIO'
                })

        return alertas

    except Exception as e:
        logger.error(f"Erro ao gerar alertas por região: {str(e)}")
        return []

def salvar_alertas(alertas: list, output_dir: str = None) -> str:
    """
    Salva os alertas em um arquivo HTML para visualização
    """
    if not alertas:
        return ""

    try:
        if output_dir is None:
            output_dir = os.path.join('output', 'alertas')

        os.makedirs(output_dir, exist_ok=True)

        data_ref = alertas[0]['data']
        arquivo = os.path.join(output_dir, f"alertas_{data_ref.strftime('%Y%m%d')}.html")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alertas de Queimadas - {data_ref.strftime('%d/%m/%Y')}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .alerta {{
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                }}
                .ALTO {{
                    border-left: 5px solid #ff4444;
                }}
                .MÉDIO {{
                    border-left: 5px solid #ffbb33;
                }}
                h1 {{
                    color: #333;
                }}
                .info {{
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <h1>Alertas de Queimadas - {data_ref.strftime('%d/%m/%Y')}</h1>
        """

        for alerta in alertas:
            html_content += f"""
            <div class="alerta {alerta['nivel']}">
                <h3>{alerta['tipo']}: {alerta['local']}</h3>
                <p><strong>Nível de Alerta:</strong> {alerta['nivel']}</p>
                <p><strong>Focos detectados:</strong> {alerta['focos']:,}</p>
                <p><strong>Média histórica:</strong> {alerta['media']:,.1f}</p>
                <p><strong>Aumento:</strong> {alerta['aumento']}%</p>
                <p class="info">Data de referência: {alerta['data'].strftime('%d/%m/%Y')}</p>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return arquivo

    except Exception as e:
        logger.error(f"Erro ao salvar alertas: {str(e)}")
        return ""
