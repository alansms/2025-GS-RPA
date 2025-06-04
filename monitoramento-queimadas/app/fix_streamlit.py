#!/usr/bin/env python3
# Script para corrigir o dicionário map_styles com chaves não fechadas

with open('streamlit_app.py', 'r') as file:
    lines = file.readlines()

# Encontrar as linhas do dicionário map_styles
start_line = -1
for i, line in enumerate(lines):
    if 'map_styles = {' in line:
        start_line = i
        break

if start_line >= 0:
    # Substituir as linhas do dicionário por uma versão correta
    correct_dict = [
        '                # Opções de estilo de mapa simplificadas\n',
        '                map_styles = {\n',
        '                    "Carto Positron (Claro)": "carto-positron",\n',
        '                    "Carto Darkmatter (Escuro)": "carto-darkmatter",\n',
        '                    "Stamen Terrain": "stamen-terrain"\n',
        '                }\n'
    ]

    # Substituir as linhas do dicionário
    lines[start_line-1:start_line+5] = correct_dict

    # Escrever o arquivo corrigido
    with open('streamlit_app.py', 'w') as file:
        file.writelines(lines)

    print("Correção aplicada com sucesso: dicionário map_styles foi corrigido!")
else:
    print("Não foi possível encontrar o dicionário map_styles no arquivo!")
