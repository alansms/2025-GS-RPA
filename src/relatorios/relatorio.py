import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import logging
import weasyprint
from jinja2 import Template

logger = logging.getLogger('queimadas.relatorios')

def main(df: pd.DataFrame, output_dir: str = None) -> str:
    """
    Gera um relatório com as análises dos focos de queimada.
    """
    try:
        # Usar caminho absoluto para o diretório de saída
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'relatorios')

        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = os.path.join(output_dir, f"relatorio_{timestamp}.html")
        pdf_file = os.path.join(output_dir, f"relatorio_{timestamp}.pdf")

        # Preparar dados para o relatório
        total_focos = len(df)
        media_diaria = total_focos / len(df['data'].unique())
        estados_afetados = len(df['uf'].unique())
        biomas_afetados = len(df['bioma'].unique())

        # Gerar estatísticas por UF e bioma
        stats_uf = df.groupby('uf').size().sort_values(ascending=False)
        stats_bioma = df.groupby('bioma').size().sort_values(ascending=False)

        # Criar tabela HTML para estatísticas
        tabela_uf = "<table><tr><th>UF</th><th>Focos</th></tr>"
        for uf, focos in stats_uf.items():
            tabela_uf += f"<tr><td>{uf}</td><td>{focos}</td></tr>"
        tabela_uf += "</table>"

        tabela_bioma = "<table><tr><th>Bioma</th><th>Focos</th></tr>"
        for bioma, focos in stats_bioma.items():
            tabela_bioma += f"<tr><td>{bioma}</td><td>{focos}</td></tr>"
        tabela_bioma += "</table>"

        # Template HTML com estilos embutidos
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <title>Relatório de Queimadas</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 1000px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    h1, h2 { color: #444; }
                    .header {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .metrics {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin: 20px 0;
                    }
                    .metric {
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                    }
                    .metric h3 { margin: 0; color: #666; }
                    .metric p { 
                        margin: 10px 0 0;
                        font-size: 24px;
                        font-weight: bold;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }
                    th, td {
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }
                    th { background-color: #f5f5f5; }
                    tr:hover { background-color: #f9f9f9; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Relatório de Monitoramento de Queimadas</h1>
                    <p>Período: {inicio} a {fim}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <h3>Total de Focos</h3>
                        <p>{total}</p>
                    </div>
                    <div class="metric">
                        <h3>Média Diária</h3>
                        <p>{media:.1f}</p>
                    </div>
                    <div class="metric">
                        <h3>Estados Afetados</h3>
                        <p>{estados}</p>
                    </div>
                    <div class="metric">
                        <h3>Biomas Afetados</h3>
                        <p>{biomas}</p>
                    </div>
                </div>

                <h2>Distribuição por Estado</h2>
                {tabela_uf}

                <h2>Distribuição por Bioma</h2>
                {tabela_bioma}
            </body>
        </html>
        """.format(
            inicio=df['data'].min().strftime('%d/%m/%Y'),
            fim=df['data'].max().strftime('%d/%m/%Y'),
            total=total_focos,
            media=media_diaria,
            estados=estados_afetados,
            biomas=biomas_afetados,
            tabela_uf=tabela_uf,
            tabela_bioma=tabela_bioma
        )

        # Salvar HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Gerar PDF
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)

        logger.info(f"Relatório gerado com sucesso: HTML={html_file}, PDF={pdf_file}")
        return pdf_file

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return html_file  # Retorna HTML em caso de erro no PDF
