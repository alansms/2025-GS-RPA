#!/usr/bin/env python
# Script para corrigir o valor não terminado no map_styles
import os
import re

# Usar caminho absoluto para o arquivo streamlit_app.py
script_dir = os.path.dirname(os.path.abspath(__file__))
arquivo_streamlit = os.path.join(script_dir, 'streamlit_app.py')

with open(arquivo_streamlit, 'r') as file:
    linhas = file.readlines()

# Encontrar e corrigir a linha com o problema
for i, linha in enumerate(linhas):
    if '"Stamen Terrain"' in linha:
        linhas[i] = '                    "Stamen Terrain": "stamen-terrain"\n'

with open(arquivo_streamlit, 'w') as file:
    file.writelines(linhas)
