#!/usr/bin/env python3
# Script para corrigir o dicionário map_styles com chaves não fechadas

with open('streamlit_app.py', 'r') as file:
    lines = file.readlines()

# Localizar as linhas do dicionário map_styles
map_styles_start = -1
for i, line in enumerate(lines):
    if 'map_styles = {' in line:
        map_styles_start = i
        break

if map_styles_start >= 0:
    # Reconstruir o arquivo
    new_lines = lines[:map_styles_start]

    # Adicionar o dicionário correto
    new_lines.append('                # Opções de estilo de mapa simplificadas\n')
    new_lines.append('                map_styles = {\n')
    new_lines.append('                    "Carto Positron (Claro)": "carto-positron",\n')
    new_lines.append('                    "Carto Darkmatter (Escuro)": "carto-darkmatter",\n')
    new_lines.append('                    "Stamen Terrain": "stamen-terrain"\n')
    new_lines.append('                }\n')

    # Encontrar onde o dicionário termina (ou deveria terminar)
    found_end = False
    for i in range(map_styles_start + 1, len(lines)):
        if '}' in lines[i] and 'map_styles' not in lines[i]:
            map_styles_end = i
            found_end = True
            break

    # Adicionar o resto do arquivo
    if found_end:
        new_lines.extend(lines[map_styles_end + 1:])
    else:
        # Se não encontrar o fechamento, adicionar o resto do arquivo após a definição do dicionário
        new_lines.extend(lines[map_styles_start + 5:])

    # Escrever o arquivo corrigido
    with open('streamlit_app.py', 'w') as file:
        file.writelines(new_lines)

    print("Correção aplicada com sucesso!")
else:
    print("Não foi possível encontrar o dicionário map_styles no arquivo!")
