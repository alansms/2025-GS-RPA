import os
import sys
import streamlit as st

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

# Criar diretórios necessários
for dir_path in ['output/logs', 'output/dados_brutos', 'output/dados_limpos', 'output/relatorios']:
    os.makedirs(dir_path, exist_ok=True)

# Sidebar com logo FIAP
st.sidebar.title("Filtros")
st.sidebar.info("Configure os filtros desejados para visualizar os dados.")

# Placeholder para desenvolvimento
st.info("Sistema em desenvolvimento. Nova versão em breve!")
st.warning("Estamos atualizando o sistema para melhor atendê-lo.")
