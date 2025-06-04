import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import logging

logger = logging.getLogger('queimadas.relatorios')

def main(df: pd.DataFrame, output_dir: str = "output/relatorios") -> str:
    """
    Gera um relatório em PDF com as análises dos focos de queimada.

    Args:
        df (pd.DataFrame): DataFrame com os dados de focos
        output_dir (str): Diretório onde salvar o relatório

    Returns:
        str: Caminho do arquivo PDF gerado
    """
    try:
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"relatorio_{timestamp}.html")

        # Gerar gráficos
        serie = df.groupby('data').size().reset_index(name='focos')
        fig_temporal = px.line(serie, x='data', y='focos',
                             title="Evolução dos Focos de Queimada")

        top_ufs = df.groupby('uf').size().nlargest(10)
        fig_ufs = px.bar(top_ufs, title="Top 10 Estados com Mais Focos")

        focos_bioma = df.groupby('bioma').size()
        fig_bioma = px.pie(values=focos_bioma.values,
                          names=focos_bioma.index,
                          title="Distribuição por Bioma")

        # Gerar HTML
        html_content = f"""
        <html>
            <head>
                <title>Relatório de Queimadas</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    .metrics {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                    .metric {{ text-align: center; padding: 10px; background: #f5f5f5; }}
                </style>
            </head>
            <body>
                <h1>Relatório de Monitoramento de Queimadas</h1>
                <p>Período: {df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}</p>
                
                <div class="metrics">
                    <div class="metric">
                        <h3>Total de Focos</h3>
                        <p>{len(df):,}</p>
                    </div>
                    <div class="metric">
                        <h3>Média Diária</h3>
                        <p>{len(df)/len(serie):.1f}</p>
                    </div>
                    <div class="metric">
                        <h3>Estados Afetados</h3>
                        <p>{len(df['uf'].unique())}</p>
                    </div>
                </div>
                
                {fig_temporal.to_html(full_html=False)}
                {fig_ufs.to_html(full_html=False)}
                {fig_bioma.to_html(full_html=False)}
            </body>
        </html>
        """

        # Salvar relatório
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Relatório gerado com sucesso: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return None
