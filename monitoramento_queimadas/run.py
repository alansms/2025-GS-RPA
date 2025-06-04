import os
import sys

# Adiciona o diretório do app ao PYTHONPATH
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
sys.path.append(app_dir)

# Importa a aplicação Streamlit diretamente
from streamlit_app import main

if __name__ == "__main__":
    main()
