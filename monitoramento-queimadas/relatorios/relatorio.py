#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de geração de relatórios para focos de queimadas.

Este script monta relatório PDF ou HTML contendo sumário executivo, gráficos
(séries temporais, barras por UF, pizza por bioma), tabelas e possíveis alertas,
usando matplotlib, Plotly ou Jinja2 + WeasyPrint.
"""

import os
import sys
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from glob import glob
import jinja2

# Tentativa de importar WeasyPrint com tratamento de erro
try:
    from weasyprint import HTML
    WEASYPRINT_DISPONIVEL = True
except (ImportError, OSError) as e:
    logging.warning(f"WeasyPrint não pôde ser importado: {str(e)}")
    logging.warning("A conversão para PDF não estará disponível. Use o formato HTML ou instale as dependências necessárias.")
    logging.warning("Para macOS, execute: brew install pango libffi")
    logging.warning("Para mais informações, consulte: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#macos")
    WEASYPRINT_DISPONIVEL = False

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.relatorios')

def carregar_dados_analise():
    """
    Carrega os dados de análise para geração do relatório.
    
    Returns:
        tuple: (serie_temporal, focos_por_uf, focos_por_bioma, alertas) com os dados carregados.
    """
    try:
        # Diretório de análises
        diretorio_analises = 'output/dados_limpos/analises'
        os.makedirs(diretorio_analises, exist_ok=True)
        
        # Carregar série temporal
        caminho_serie = os.path.join(diretorio_analises, 'serie_temporal_dia.csv')
        serie_temporal = None
        if os.path.exists(caminho_serie):
            serie_temporal = pd.read_csv(caminho_serie)
            serie_temporal['periodo'] = pd.to_datetime(serie_temporal['periodo'])
            logger.info(f"Série temporal carregada: {len(serie_temporal)} registros")
        else:
            logger.warning(f"Arquivo de série temporal não encontrado: {caminho_serie}")
        
        # Carregar focos por UF
        caminho_uf = os.path.join(diretorio_analises, 'focos_por_uf.csv')
        focos_por_uf = None
        if os.path.exists(caminho_uf):
            focos_por_uf = pd.read_csv(caminho_uf)
            logger.info(f"Focos por UF carregados: {len(focos_por_uf)} UFs")
        else:
            logger.warning(f"Arquivo de focos por UF não encontrado: {caminho_uf}")
        
        # Carregar focos por bioma
        caminho_bioma = os.path.join(diretorio_analises, 'focos_por_bioma.csv')
        focos_por_bioma = None
        if os.path.exists(caminho_bioma):
            focos_por_bioma = pd.read_csv(caminho_bioma)
            logger.info(f"Focos por bioma carregados: {len(focos_por_bioma)} biomas")
        else:
            logger.warning(f"Arquivo de focos por bioma não encontrado: {caminho_bioma}")
        
        # Carregar alertas
        alertas = []
        caminho_alertas = 'output/logs/alertas.log'
        if os.path.exists(caminho_alertas):
            with open(caminho_alertas, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                # Extrair alertas do log (simplificado)
                if 'ALERTAS:' in conteudo:
                    alertas_raw = conteudo.split('ALERTAS:')[-1].split('FIM ALERTAS:')[0]
                    alertas = [linha.strip() for linha in alertas_raw.split('\n') if linha.strip()]
                    logger.info(f"Alertas carregados: {len(alertas)}")
        else:
            logger.warning(f"Arquivo de alertas não encontrado: {caminho_alertas}")
        
        return serie_temporal, focos_por_uf, focos_por_bioma, alertas
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados de análise: {str(e)}")
        return None, None, None, []

def gerar_graficos_relatorio(serie_temporal, focos_por_uf, focos_por_bioma, diretorio_saida):
    """
    Gera gráficos para o relatório.
    
    Args:
        serie_temporal (pandas.DataFrame): Série temporal de focos.
        focos_por_uf (pandas.DataFrame): Focos por UF.
        focos_por_bioma (pandas.DataFrame): Focos por bioma.
        diretorio_saida (str): Diretório para salvar os gráficos.
    
    Returns:
        dict: Dicionário com caminhos para os gráficos gerados.
    """
    graficos = {}
    
    try:
        os.makedirs(diretorio_saida, exist_ok=True)

        # Configuração estética para todos os gráficos
        plt.style.use('seaborn-v0_8-whitegrid')

        # Paleta de cores suaves para combinar com o novo esquema de cores do relatório
        cores_principal = ['#a8dadc', '#457b9d', '#1d3557', '#8ecae6', '#219ebc', '#023047']
        cores_secundaria = ['#e9c46a', '#f4a261', '#e76f51', '#ffb703', '#fb8500', '#d1c7be']

        # Gráfico de série temporal
        if serie_temporal is not None and not serie_temporal.empty:
            plt.figure(figsize=(12, 6))

            # Plotar série original
            plt.plot(serie_temporal['periodo'], serie_temporal['focos'],
                    color=cores_principal[1], linewidth=2,
                    marker='o', markersize=4, alpha=0.7,
                    label='Focos diários')

            # Plotar média móvel
            if 'media_movel' in serie_temporal.columns:
                plt.plot(serie_temporal['periodo'], serie_temporal['media_movel'],
                        color=cores_principal[2], linewidth=3,
                        label='Média Móvel (7 dias)')

            # Melhorar estética
            plt.title('Evolução Temporal dos Focos de Queimadas', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Data', fontsize=12)
            plt.ylabel('Número de Focos', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(frameon=True, fontsize=10)

            # Adicionar anotações para valores importantes
            if len(serie_temporal) > 0:
                # Encontrar valor máximo
                idx_max = serie_temporal['focos'].idxmax()
                data_max = serie_temporal.loc[idx_max, 'periodo']
                valor_max = serie_temporal.loc[idx_max, 'focos']

                # Anotar o valor máximo
                plt.annotate(f'Máximo: {valor_max:,}',
                            xy=(data_max, valor_max),
                            xytext=(10, 20),
                            textcoords='offset points',
                            arrowprops=dict(arrowstyle='->', color=cores_principal[0]),
                            bbox=dict(boxstyle='round,pad=0.3', fc='#e8f4f8', ec=cores_principal[1], alpha=0.7))

            # Melhorar o formato das datas no eixo x
            plt.gcf().autofmt_xdate()

            # Ajustar layout
            plt.tight_layout()
            
            # Salvar
            caminho_grafico = os.path.join(diretorio_saida, 'serie_temporal.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            graficos['serie_temporal'] = caminho_grafico
            logger.info(f"Gráfico de série temporal salvo: {caminho_grafico}")
        
        # Gráfico de barras por UF
        if focos_por_uf is not None and not focos_por_uf.empty:
            plt.figure(figsize=(12, 8))
            
            # Limitar para as 10 UFs com mais focos
            df_plot = focos_por_uf.head(10).copy()
            
            # Criar gradiente de cores mais suaves
            cores = plt.cm.Blues(np.linspace(0.3, 0.9, len(df_plot)))

            # Plotar barras
            bars = plt.bar(df_plot['uf'], df_plot['focos'], color=cores)

            # Adicionar rótulos
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                        f'{int(height):,}', ha='center', va='bottom',
                        fontsize=10, fontweight='bold')

            # Melhorar estética
            plt.title('Top 10 UFs com Mais Focos de Queimadas', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Unidade Federativa (UF)', fontsize=12)
            plt.ylabel('Número de Focos', fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Adicionar porcentagem no topo do gráfico
            if 'percentual' in df_plot.columns:
                for i, (_, row) in enumerate(df_plot.iterrows()):
                    plt.text(i, row['focos'] + row['focos'] * 0.05,
                            f"{row['percentual']:.1f}%",
                            ha='center', va='bottom',
                            fontsize=9, color=cores_secundaria[2])

            # Ajustar layout
            plt.tight_layout()
            
            # Salvar
            caminho_grafico = os.path.join(diretorio_saida, 'focos_por_uf.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            graficos['focos_por_uf'] = caminho_grafico
            logger.info(f"Gráfico de barras por UF salvo: {caminho_grafico}")
        
        # Gráfico de pizza por bioma
        if focos_por_bioma is not None and not focos_por_bioma.empty:
            plt.figure(figsize=(10, 10))
            
            # Usar paleta de cores mais suaves em tons de azul e turquesa
            colors = plt.cm.GnBu(np.linspace(0.3, 0.9, len(focos_por_bioma)))

            # Preparar wedges (fatias)
            wedges, texts, autotexts = plt.pie(
                focos_por_bioma['focos'],
                labels=None,  # Vamos adicionar legenda separada
                autopct='%1.1f%%',
                startangle=90,
                shadow=True,
                colors=colors,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                textprops={'color': 'white', 'fontweight': 'bold', 'fontsize': 12}
            )

            # Adicionar legenda à direita
            plt.legend(
                wedges,
                focos_por_bioma['bioma'],
                title="Biomas",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1)
            )
            
            # Configurar gráfico
            plt.title('Distribuição de Focos por Bioma', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')  # Garantir que o gráfico seja circular

            # Ajustar layout
            plt.tight_layout()
            
            # Salvar
            caminho_grafico = os.path.join(diretorio_saida, 'focos_por_bioma.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            graficos['focos_por_bioma'] = caminho_grafico
            logger.info(f"Gráfico de pizza por bioma salvo: {caminho_grafico}")
        
        return graficos
    
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos para relatório: {str(e)}")
        return graficos

def gerar_relatorio_html(serie_temporal, focos_por_uf, focos_por_bioma, alertas, graficos, caminho_saida):
    """
    Gera relatório em formato HTML.
    
    Args:
        serie_temporal (pandas.DataFrame): Série temporal de focos.
        focos_por_uf (pandas.DataFrame): Focos por UF.
        focos_por_bioma (pandas.DataFrame): Focos por bioma.
        alertas (list): Lista de alertas.
        graficos (dict): Dicionário com caminhos para os gráficos.
        caminho_saida (str): Caminho para salvar o relatório.
    
    Returns:
        bool: True se o relatório foi gerado com sucesso, False caso contrário.
    """
    try:
        # Inicializar valores padrão para todos os dados
        # Isso garante que nenhuma variável seja None quando passada para o template
        if serie_temporal is None:
            serie_temporal = pd.DataFrame(columns=['periodo', 'focos'])

        if focos_por_uf is None:
            focos_por_uf = pd.DataFrame(columns=['uf', 'focos', 'percentual'])

        if focos_por_bioma is None:
            focos_por_bioma = pd.DataFrame(columns=['bioma', 'focos', 'percentual'])

        if alertas is None:
            alertas = []

        if graficos is None:
            graficos = {}

        # Preparar dados para o template
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        periodo_inicio = "N/A"
        periodo_fim = "N/A"
        total_focos = 0
        tendencia = "N/A"

        # Calcular estatísticas somente se a série temporal tiver dados
        try:
            if not serie_temporal.empty and 'periodo' in serie_temporal.columns and 'focos' in serie_temporal.columns:
                periodo_inicio = serie_temporal['periodo'].min().strftime('%d/%m/%Y')
                periodo_fim = serie_temporal['periodo'].max().strftime('%d/%m/%Y')
                total_focos = int(serie_temporal['focos'].sum())

                # Determinar tendência
                if len(serie_temporal) > 1:
                    ultimos_dias = serie_temporal.iloc[-7:] if len(serie_temporal) >= 7 else serie_temporal
                    primeiro_valor = ultimos_dias['focos'].iloc[0]
                    ultimo_valor = ultimos_dias['focos'].iloc[-1]

                    if ultimo_valor > primeiro_valor * 1.2:
                        tendencia = "Crescente ↑"
                    elif ultimo_valor < primeiro_valor * 0.8:
                        tendencia = "Decrescente ↓"
                    else:
                        tendencia = "Estável →"
        except Exception as e:
            logger.warning(f"Erro ao calcular estatísticas da série temporal: {str(e)}")

        # Caminhos dos recursos estáticos
        logo_path = "/Users/alansms/CLionProjects/GS-2025-RPA/logo_fiap.jpg"
        favicon_path = "/Users/alansms/CLionProjects/GS-2025-RPA/favicons-4/favicon-16x16.png"

        # Renderizar HTML com um design mais moderno e cores mais suaves
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Focos de Queimadas</title>
            <link rel="icon" type="image/png" href="{favicon_path}">
            <style>
                :root {{
                    --primary-color: #7d5a50;
                    --secondary-color: #4a4a4a;
                    --accent-color: #b4846c;
                    --light-color: #f8f9fa;
                    --dark-color: #343a40;
                    --success-color: #6c9e7f;
                    --warning-color: #d9b44a;
                    --danger-color: #b56357;
                    --info-color: #5c8d89;
                    --header-color: #353535;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }}
                
                header {{
                    background-color: var(--header-color);
                    color: white;
                    padding: 20px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .logo {{
                    max-width: 150px;
                    height: auto;
                }}
                
                h1 {{
                    font-size: 2.2rem;
                    margin-bottom: 5px;
                    color: white;
                }}
                
                h2 {{
                    font-size: 1.5rem;
                    margin: 30px 0 15px 0;
                    color: var(--primary-color);
                    border-bottom: 2px solid var(--primary-color);
                    padding-bottom: 5px;
                }}
                
                .meta-info {{
                    font-size: 0.9rem;
                    color: rgba(255, 255, 255, 0.8);
                }}
                
                .content {{
                    padding: 20px;
                }}
                
                .card {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                    overflow: hidden;
                }}
                
                .card-header {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 15px 20px;
                    font-weight: bold;
                }}
                
                .card-body {{
                    padding: 20px;
                }}
                
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                
                .summary-item {{
                    background-color: #f8f9fa;
                    border-left: 4px solid var(--primary-color);
                    padding: 15px;
                    border-radius: 4px;
                }}
                
                .summary-item h3 {{
                    font-size: 1rem;
                    color: var(--dark-color);
                    margin-bottom: 5px;
                }}
                
                .summary-item p {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--primary-color);
                }}
                
                .alert {{
                    background-color: #fff8e6;
                    color: #856404;
                    padding: 15px;
                    border-left: 4px solid var(--warning-color);
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                
                .alert-danger {{
                    background-color: #f8e6e6;
                    color: #721c24;
                    border-left-color: var(--danger-color);
                }}
                
                .alert-list {{
                    list-style-type: none;
                    margin: 10px 0 0 0;
                }}
                
                .alert-list li {{
                    padding: 5px 0;
                }}
                
                .grafico {{
                    max-width: 100%;
                    height: auto;
                    margin: 20px 0;
                    border-radius: 4px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-size: 0.9rem;
                }}
                
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                    color: var(--dark-color);
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                tr:hover {{
                    background-color: rgba(181, 136, 99, 0.1);
                }}
                
                .footer {{
                    margin-top: 30px;
                    padding: 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: center;
                    font-size: 0.85rem;
                    color: #777;
                }}
                
                .grid-2 {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                
                .grid-item {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                
                .tendencia {{
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                
                .tendencia-crescente {{
                    background-color: #f8e6e6;
                    color: #721c24;
                }}
                
                .tendencia-decrescente {{
                    background-color: #e6f8ea;
                    color: #155724;
                }}
                
                .tendencia-estavel {{
                    background-color: #fff8e6;
                    color: #856404;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}
                    
                    header {{
                        flex-direction: column;
                        text-align: center;
                    }}
                    
                    .logo {{
                        margin-bottom: 15px;
                    }}
                    
                    .summary-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .grid-2 {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
            <!-- Adicionando o favicon diretamente no head para garantir que apareça na barra de endereços -->
            <link rel="shortcut icon" type="image/png" href="{favicon_path}">
        </head>
        <body>
            <div class="container">
                <header>
                    <div>
                        <h1>Relatório de Focos de Queimadas</h1>
                        <p class="meta-info">Período: {periodo_inicio} a {periodo_fim}</p>
                    </div>
                    <img src="{logo_path}" alt="FIAP" class="logo">
                </header>
                
                <div class="content">
                    <div class="card">
                        <div class="card-header">Sumário Executivo</div>
                        <div class="card-body">
                            <p>Este relatório apresenta uma análise dos focos de queimadas detectados no período selecionado.</p>
                            
                            <div class="summary-grid">
                                <div class="summary-item">
                                    <h3>Total de Focos</h3>
                                    <p>{total_focos:,}</p>
                                </div>
        """

        # Adicionar tendência formatada com a classe apropriada
        if tendencia != "N/A":
            tendencia_class = ""
            if "Crescente" in tendencia:
                tendencia_class = "tendencia-crescente"
            elif "Decrescente" in tendencia:
                tendencia_class = "tendencia-decrescente"
            else:
                tendencia_class = "tendencia-estavel"

            html_content += f"""
                                <div class="summary-item">
                                    <h3>Tendência</h3>
                                    <p><span class="tendencia {tendencia_class}">{tendencia}</span></p>
                                </div>
            """

        html_content += f"""
                                <div class="summary-item">
                                    <h3>Data do Relatório</h3>
                                    <p style="font-size: 1rem;">{data_geracao}</p>
                                </div>
                            </div>
                        </div>
                    </div>
        """

        # Adicionar alertas se existirem
        if alertas and len(alertas) > 0:
            html_content += """
                    <div class="card">
                        <div class="card-header">Alertas</div>
                        <div class="card-body">
                            <div class="alert alert-danger">
                                <strong>Atenção!</strong> Os seguintes alertas foram detectados:
                                <ul class="alert-list">
            """

            for alerta in alertas:
                html_content += f"<li>{alerta}</li>"

            html_content += """
                                </ul>
                            </div>
                        </div>
                    </div>
            """

        html_content += f"""
                    <div class="card">
                        <div class="card-header">Gráficos</div>
                        <div class="card-body">
                            <div class="grid-2">
        """

        # Adicionar gráficos se existirem
        if 'serie_temporal' in graficos:
            html_content += f"""
                                <div class="grid-item">
                                    <img src="{graficos['serie_temporal']}" alt="Série Temporal" class="grafico">
                                </div>
            """

        if 'focos_por_uf' in graficos:
            html_content += f"""
                                <div class="grid-item">
                                    <img src="{graficos['focos_por_uf']}" alt="Focos por UF" class="grafico">
                                </div>
            """

        if 'focos_por_bioma' in graficos:
            html_content += f"""
                                <div class="grid-item">
                                    <img src="{graficos['focos_por_bioma']}" alt="Focos por Bioma" class="grafico">
                                </div>
            """

        html_content += """
                            </div>
                        </div>
                    </div>
        """

        # Adicionar tabelas se existirem
        if not focos_por_uf.empty:
            html_content += """
                    <div class="card">
                        <div class="card-header">Tabela de Focos por UF</div>
                        <div class="card-body">
                            <table>
                                <thead>
                                    <tr>
                                        <th>UF</th>
                                        <th>Focos</th>
                                        <th>Percentual</th>
                                    </tr>
                                </thead>
                                <tbody>
            """

            for _, row in focos_por_uf.iterrows():
                html_content += f"""
                                    <tr>
                                        <td>{row['uf']}</td>
                                        <td>{int(row['focos']):,}</td>
                                        <td>{row['percentual']:.1f}%</td>
                                    </tr>
                """

            html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
            """

        if not focos_por_bioma.empty:
            html_content += """
                    <div class="card">
                        <div class="card-header">Tabela de Focos por Bioma</div>
                        <div class="card-body">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Bioma</th>
                                        <th>Focos</th>
                                        <th>Percentual</th>
                                    </tr>
                                </thead>
                                <tbody>
            """

            for _, row in focos_por_bioma.iterrows():
                html_content += f"""
                                    <tr>
                                        <td>{row['bioma']}</td>
                                        <td>{int(row['focos']):,}</td>
                                        <td>{row['percentual']:.1f}%</td>
                                    </tr>
                """

            html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
            """

        html_content += f"""
                </div>
                <div class="footer">
                    <p>Relatório gerado em {data_geracao}</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Salvar HTML
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Relatório HTML gerado: {caminho_saida}")
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar relatório HTML: {str(e)}")
        return False

def gerar_relatorio_pdf(caminho_html, caminho_pdf):
    """
    Converte um relatório HTML para PDF usando WeasyPrint.

    Args:
        caminho_html (str): Caminho do arquivo HTML.
        caminho_pdf (str): Caminho para salvar o arquivo PDF.

    Returns:
        bool: True se o PDF foi gerado com sucesso, False caso contrário.
    """
    try:
        if not WEASYPRINT_DISPONIVEL:
            logger.warning("WeasyPrint não está disponível. Instale as dependências necessárias para gerar PDF.")
            return False

        HTML(caminho_html).write_pdf(caminho_pdf)
        logger.info(f"Relatório PDF gerado: {caminho_pdf}")
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar relatório PDF: {str(e)}")
        return False

def main(formato='html', periodo='dia', output=None):
    """
    Função principal para geração de relatórios.

    Args:
        formato (str): Formato do relatório ('html' ou 'pdf').
        periodo (str): Período de análise ('dia', 'semana', 'mes', 'ano').
        output (str): Diretório de saída para o relatório. Se None, usa o diretório padrão.

    Returns:
        str: Caminho para o relatório gerado, ou None em caso de erro.
    """
    try:
        # Verificar se estamos no macOS e forçar formato HTML caso o WeasyPrint não esteja disponível
        import platform
        if platform.system() == 'Darwin' and not WEASYPRINT_DISPONIVEL and formato.lower() == 'pdf':
            logger.info("Sistema macOS detectado e WeasyPrint não disponível. Alterando formato para HTML automaticamente.")
            formato = 'html'

        # Configuração de diretório de saída
        if output is None:
            output = 'output/relatorios'

        # Garantir que o diretório de saída exista
        os.makedirs(output, exist_ok=True)

        # Carregar dados de análise
        serie_temporal, focos_por_uf, focos_por_bioma, alertas = carregar_dados_analise()

        # Diretório para os gráficos
        diretorio_graficos = os.path.join(output, 'graficos')
        os.makedirs(diretorio_graficos, exist_ok=True)

        # Gerar gráficos
        graficos = gerar_graficos_relatorio(serie_temporal, focos_por_uf, focos_por_bioma, diretorio_graficos)

        # Caminho do relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"relatorio_{periodo}_{timestamp}"

        # Gerar relatório HTML
        caminho_relatorio_html = os.path.join(output, f"{nome_arquivo}.html")
        sucesso_html = gerar_relatorio_html(serie_temporal, focos_por_uf, focos_por_bioma, alertas, graficos, caminho_relatorio_html)

        # Converter para PDF se necessário
        if formato.lower() == 'pdf' and sucesso_html and WEASYPRINT_DISPONIVEL:
            caminho_relatorio_pdf = os.path.join(output, f"{nome_arquivo}.pdf")
            sucesso_pdf = gerar_relatorio_pdf(caminho_relatorio_html, caminho_relatorio_pdf)

            if sucesso_pdf:
                logger.info(f"Relatório PDF gerado com sucesso: {caminho_relatorio_pdf}")
                return caminho_relatorio_pdf
            else:
                logger.warning("Falha ao gerar PDF, retornando versão HTML.")
                return caminho_relatorio_html
        else:
            if formato.lower() == 'pdf' and not WEASYPRINT_DISPONIVEL:
                logger.warning("WeasyPrint não disponível. Gerando apenas HTML.")

            if sucesso_html:
                logger.info(f"Relatório HTML gerado com sucesso: {caminho_relatorio_html}")
                return caminho_relatorio_html
            else:
                logger.error("Falha ao gerar relatório HTML.")
                return None

    except Exception as e:
        logger.error(f"Erro na geração do relatório: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    # Quando executado diretamente como script, usar o parser de argumentos
    parser = argparse.ArgumentParser(description="Geração de relatórios de focos de queimadas.")
    parser.add_argument('--formato', choices=['html', 'pdf'], default='html', help="Formato do relatório (html ou pdf).")
    parser.add_argument('--periodo', choices=['dia', 'semana', 'mes', 'ano'], default='dia', help="Período de análise.")
    parser.add_argument('--saida', default='output/relatorios', help="Diretório de saída para o relatório.")
    args = parser.parse_args()

    # Configuração de logging básica quando executado como script
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Chamar a função principal com os argumentos do parser
    resultado = main(formato=args.formato, periodo=args.periodo, output=args.saida)

    if resultado:
        print(f"Relatório gerado com sucesso: {resultado}")
    else:
        print("Falha ao gerar relatório. Verifique os logs para mais detalhes.")
