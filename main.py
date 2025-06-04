import streamlit as st
import sys
import os

# Adiciona o diretório do projeto ao PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(project_root, "monitoramento-queimadas", "app")
sys.path.append(project_root)
sys.path.append(app_path)

# Importa o aplicativo Streamlit
from monitoramento_queimadas.app.streamlit_app import main

if __name__ == "__main__":
    main()
