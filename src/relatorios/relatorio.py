import pandas as pd
import os
import logging
import weasyprint
from datetime import datetime
import base64

logger = logging.getLogger('queimadas.relatorios')

def get_logo_base64(logo_path):
    """Converte o logo para base64 para incluir no HTML"""
    with open(logo_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def get_css():
    return """
:root {
    --primary-color: #1a75ff;
    --secondary-color: #00246c;
    --bg-color: #ffffff;
    --text-color: #333333;
    --accent-color: #f0f4f8;
    --border-color: #e0e4e8;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
}

body { 
    font-family: 'Segoe UI', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    margin: 0;
    padding: 0;
    background-color: var(--accent-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: var(--bg-color);
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
    min-height: 100vh;
}

.header-container {
    background-color: var(--secondary-color);
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.header-content {
    display: grid;
    grid-template-columns: auto 1fr;
    align-items: center;
    gap: 2rem;
    max-width: 1160px;
    margin: 0 auto;
}

.logo-container {
    width: 180px;
    background: var(--secondary-color);
    padding: 0.5rem;
    border-radius: 4px;
}

.logo-container img {
    width: 100%;
    height: auto;
    display: block;
}

.header-text {
    color: white;
    padding-left: 2rem;
    border-left: 3px solid rgba(255,255,255,0.2);
}

.header-text h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
    line-height: 1.2;
}

.header-text p {
    margin: 0.5rem 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

.content {
    padding: 0 2rem 2rem;
    max-width: 1160px;
    margin: 0 auto;
}

.resumo {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid var(--primary-color);
    font-size: 1.05rem;
    line-height: 1.6;
    color: #444;
}

.metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--accent-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.metric-content h3 {
    margin: 0;
    font-size: 0.95rem;
    color: #666;
    font-weight: 500;
}

.metric-content p {
    margin: 0.3rem 0 0;
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--primary-color);
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.chart {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.data-tables {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.table-section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

h2 {
    font-size: 1.3rem;
    color: var(--secondary-color);
    margin: 0 0 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 0;
    font-size: 0.95rem;
}

th {
    background: var(--accent-color);
    padding: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.85rem;
    color: var(--secondary-color);
    text-align: left;
}

td {
    padding: 0.8rem;
    border-bottom: 1px solid var(--border-color);
}

tr:last-child td {
    border-bottom: none;
}

tr:hover td {
    background: var(--accent-color);
}

.footer {
    text-align: center;
    padding: 1.5rem;
    color: #666;
    font-size: 0.9rem;
    border-top: 1px solid var(--border-color);
    margin-top: 2rem;
    background: var(--accent-color);
}

.trend-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.9rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    margin-top: 0.5rem;
}

.trend-up {
    color: var(--danger-color);
    background: rgba(220, 53, 69, 0.1);
}

.trend-down {
    color: var(--success-color);
    background: rgba(40, 167, 69, 0.1);
}

@media print {
    body {
        background: white;
    }
    .container {
        box-shadow: none;
    }
    .header-container {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .metric, .table-section {
        break-inside: avoid;
    }
}
"""

def main(df: pd.DataFrame, output_dir: str = None) -> str:
    """
    Gera um relatório com as análises dos focos de queimada.
    """
    html_file = None
    try:
        # Usar caminho absoluto para o diretório de saída e logo
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if output_dir is None:
            output_dir = os.path.join(project_root, 'output', 'relatorios')
            graficos_dir = os.path.join(output_dir, 'graficos')

        # Caminho do logo
        logo_path = os.path.join(project_root, 'logo_fiap.jpg')

        # Criar diretórios necessários
        for dir_path in [output_dir, graficos_dir]:
            os.makedirs(dir_path, exist_ok=True)

        # Verificar permissões de escrita
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Sem permissão de escrita no diretório: {output_dir}")

        # Nome do arquivo com período do relatório
        periodo = 'ano' if len(df['data'].unique()) > 30 else 'mês'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = os.path.join(output_dir, f"relatorio_{periodo}_{timestamp}.html")
        pdf_file = os.path.join(output_dir, f"relatorio_{periodo}_{timestamp}.pdf")

        # Preparar dados para o relatório
        total_focos = len(df)
        media_diaria = total_focos / len(df['data'].unique())
        estados_afetados = len(df['uf'].unique())
        biomas_afetados = len(df['bioma'].unique())

        # Gerar estatísticas por UF e bioma
        stats_uf = df.groupby('uf').size().sort_values(ascending=False)
        stats_bioma = df.groupby('bioma').size().sort_values(ascending=False)

        # Criar tabelas HTML
        tabela_uf_rows = "\n".join(f"<tr><td>{uf}</td><td>{focos:,}</td></tr>" for uf, focos in stats_uf.items())
        tabela_bioma_rows = "\n".join(f"<tr><td>{bioma}</td><td>{focos:,}</td></tr>" for bioma, focos in stats_bioma.items())

        # Converter logo para base64
        logo_base64 = get_logo_base64(logo_path)

        # Gerar resumo geral
        periodo_dias = (df['data'].max() - df['data'].min()).days + 1
        estados_mais_afetados = ", ".join(stats_uf.head(3).index.tolist())
        bioma_mais_afetado = stats_bioma.index[0]

        resumo = f"""
        No período analisado de {periodo_dias} dias, foram registrados {total_focos:,} focos de queimadas no Brasil,
        resultando em uma média diária de {media_diaria:.1f} focos. Os estados mais afetados foram {estados_mais_afetados},
        e o bioma com maior concentração de queimadas foi {bioma_mais_afetado}. O monitoramento abrangeu {estados_afetados}
        estados e {biomas_afetados} biomas diferentes.
        """

        # Gerar estatísticas adicionais
        variacao_diaria = stats_uf.pct_change().fillna(0)
        tendencia = "▲ Aumento" if variacao_diaria.mean() > 0 else "▼ Redução"
        tendencia_class = "trend-up" if variacao_diaria.mean() > 0 else "trend-down"

        # Gerar conteúdo HTML atualizado
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Queimadas</title>
        <style>{get_css()}</style>
    </head>
    <body>
        <div class="container">
            <div class="header-container">
                <div class="header-content">
                    <div class="logo-container">
                        <img src="data:image/png;base64,{get_logo_base64(os.path.join(project_root, 'FIAP-transparente.png'))}" alt="FIAP Logo">
                    </div>
                    <div class="header-text">
                        <h1>Monitoramento de Queimadas</h1>
                        <p>Relatório Analítico • {df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}</p>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <div class="resumo">
                    {resumo}
                    <div class="trend-indicator {tendencia_class}">
                        {tendencia} nos últimos dias
                    </div>
                </div>

                <div class="metrics">
                    <div class="metric">
                        <div class="metric-icon">🔥</div>
                        <div class="metric-content">
                            <h3>Total de Focos</h3>
                            <p>{total_focos:,}</p>
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-icon">📊</div>
                        <div class="metric-content">
                            <h3>Média Diária</h3>
                            <p>{media_diaria:.1f}</p>
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-icon">🗺️</div>
                        <div class="metric-content">
                            <h3>Estados Monitorados</h3>
                            <p>{estados_afetados}</p>
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-icon">🌳</div>
                        <div class="metric-content">
                            <h3>Biomas Afetados</h3>
                            <p>{biomas_afetados}</p>
                        </div>
                    </div>
                </div>

                <div class="data-tables">
                    <div class="table-section">
                        <h2>🏠 Distribuição por Estado</h2>
                        <table>
                            <tr><th>UF</th><th>Focos</th></tr>
                            {tabela_uf_rows}
                        </table>
                    </div>

                    <div class="table-section">
                        <h2>🌿 Distribuição por Bioma</h2>
                        <table>
                            <tr><th>Bioma</th><th>Focos</th></tr>
                            {tabela_bioma_rows}
                        </table>
                    </div>
                </div>

                <div class="footer">
                    <p>Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} • Sistema de Monitoramento de Queimadas</p>
                </div>
            </div>
        </div>
    </body>
</html>"""

        # Salvar HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Gerar PDF
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)

        logger.info(f"Relatório gerado com sucesso: HTML={html_file}, PDF={pdf_file}")
        return pdf_file

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return html_file if html_file else ""
