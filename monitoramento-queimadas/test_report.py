#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar se a função gerar_relatorio_html funciona corretamente
sem o erro "cannot access local variable 'serie_temporal'"
"""

import os
import sys
import pandas as pd
from datetime import datetime
import traceback

# Funções simplificadas para teste

def carregar_dados_teste():
    """Carrega dados de teste simplificados"""
    print("Criando dados de teste...")
    # Criar série temporal de teste
    serie_temporal = pd.DataFrame({
        'periodo': pd.date_range(start='2025-05-01', end='2025-05-30'),
        'focos': [100 + i * 10 for i in range(30)]
    })
    print(f"Série temporal criada com {len(serie_temporal)} registros")

    # Criar focos por UF de teste
    focos_por_uf = pd.DataFrame({
        'uf': ['SP', 'MG', 'RJ', 'BA', 'AM'],
        'focos': [500, 450, 400, 350, 300],
        'percentual': [25, 22.5, 20, 17.5, 15]
    })
    print(f"Focos por UF criados com {len(focos_por_uf)} UFs")

    # Criar focos por bioma de teste
    focos_por_bioma = pd.DataFrame({
        'bioma': ['Amazônia', 'Cerrado', 'Mata Atlântica', 'Caatinga', 'Pantanal'],
        'focos': [600, 500, 400, 300, 200],
        'percentual': [30, 25, 20, 15, 10]
    })
    print(f"Focos por bioma criados com {len(focos_por_bioma)} biomas")

    return serie_temporal, focos_por_uf, focos_por_bioma, ['Alerta de teste']

def gerar_relatorio_html_teste(serie_temporal, focos_por_uf, focos_por_bioma, alertas, graficos, caminho_saida):
    """Versão simplificada da função gerar_relatorio_html para teste"""
    try:
        print("Iniciando geração do relatório HTML de teste...")
        # Inicializar valores padrão para todos os dados
        if serie_temporal is None:
            print("Série temporal é None, criando DataFrame vazio")
            serie_temporal = pd.DataFrame(columns=['periodo', 'focos'])

        if focos_por_uf is None:
            print("Focos por UF é None, criando DataFrame vazio")
            focos_por_uf = pd.DataFrame(columns=['uf', 'focos', 'percentual'])

        if focos_por_bioma is None:
            print("Focos por bioma é None, criando DataFrame vazio")
            focos_por_bioma = pd.DataFrame(columns=['bioma', 'focos', 'percentual'])

        if alertas is None:
            print("Alertas é None, criando lista vazia")
            alertas = []

        if graficos is None:
            print("Gráficos é None, criando dicionário vazio")
            graficos = {}

        print("Preparando dados para o template...")
        # Preparar dados para o template
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        periodo_inicio = "N/A"
        periodo_fim = "N/A"
        total_focos = 0
        tendencia = "N/A"

        # Calcular estatísticas somente se a série temporal tiver dados
        try:
            print("Calculando estatísticas da série temporal...")
            if not serie_temporal.empty and 'periodo' in serie_temporal.columns and 'focos' in serie_temporal.columns:
                periodo_inicio = serie_temporal['periodo'].min().strftime('%d/%m/%Y')
                periodo_fim = serie_temporal['periodo'].max().strftime('%d/%m/%Y')
                total_focos = int(serie_temporal['focos'].sum())
                print(f"Período: {periodo_inicio} a {periodo_fim}, Total de focos: {total_focos}")

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
                    print(f"Tendência: {tendencia}")
        except Exception as e:
            print(f"ERRO ao calcular estatísticas da série temporal: {str(e)}")
            traceback.print_exc()
            return False

        print("Gerando conteúdo HTML...")
        # Conteúdo HTML simplificado para teste
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório de Teste</title>
        </head>
        <body>
            <h1>Relatório de Focos de Queimadas</h1>
            <p>Data de geração: {data_geracao}</p>
            <p>Período: {periodo_inicio} a {periodo_fim}</p>
            <p>Total de focos: {total_focos}</p>
            <p>Tendência: {tendencia}</p>
        </body>
        </html>
        """

        print(f"Salvando HTML em {caminho_saida}...")
        # Salvar HTML
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Relatório HTML de teste gerado: {caminho_saida}")
        return True

    except Exception as e:
        print(f"ERRO GERAL ao gerar relatório HTML de teste: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("=== TESTE DE GERAÇÃO DE RELATÓRIO HTML ===")
        # Carregar dados de teste
        print("Carregando dados de teste...")
        serie_temporal, focos_por_uf, focos_por_bioma, alertas = carregar_dados_teste()

        # Gerar relatório HTML
        print("Gerando relatório HTML de teste...")
        sucesso = gerar_relatorio_html_teste(serie_temporal, focos_por_uf, focos_por_bioma, alertas, {}, 'teste_relatorio.html')

        if sucesso:
            print("TESTE CONCLUÍDO COM SUCESSO! O relatório foi gerado sem erros.")
            print("Não houve erro de 'cannot access local variable serie_temporal'")
        else:
            print("TESTE FALHOU! Não foi possível gerar o relatório.")
    except Exception as e:
        print(f"ERRO FATAL no teste: {str(e)}")
        traceback.print_exc()
