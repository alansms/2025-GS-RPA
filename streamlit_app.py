import os
import sys
import logging
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from glob import glob
import folium
from streamlit_folium import folium_static

# Adicionar diretório do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "monitoramento-queimadas"))

# Importar módulos do projeto
from monitoramento-queimadas.relatorios.relatorio import main as gerar_relatorio
from monitoramento-queimadas.coleta.utils_coleta import coletar_dados_inpe

# Criar diretórios necessários
for dir_path in ['output/logs', 'output/dados_brutos', 'output/dados_limpos', 'output/relatorios']:
    os.makedirs(os.path.join(project_root, dir_path), exist_ok=True)

# Restante do código do streamlit_app.py
# ...existing code...
