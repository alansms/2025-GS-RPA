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

# Importar módulos do projeto (usando underscores ao invés de hífens)
from monitoramento_queimadas.relatorios.relatorio import main as gerar_relatorio
from monitoramento_queimadas.coleta.utils_coleta import coletar_dados_inpe

# Criar diretórios necessários
for dir_path in ['output/logs', 'output/dados_brutos', 'output/dados_limpos', 'output/relatorios']:
    os.makedirs(dir_path, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/logs/streamlit_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('monitoramento_queimadas')

# Configurar a página
st.set_page_config(
    page_title="Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide"
)

# Título principal
st.title("Sistema de Monitoramento de Queimadas")

# Texto explicativo
st.markdown("""
Este sistema monitora focos de queimadas em todo o Brasil, fornecendo visualizações 
interativas e análises detalhadas por estado e bioma.
""")

# Placeholder para desenvolvimento
st.info("Sistema em desenvolvimento. Versão inicial.")
