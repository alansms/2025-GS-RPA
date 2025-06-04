#!/bin/bash

# Configuração de variáveis de ambiente para o WeasyPrint no macOS
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export LD_LIBRARY_PATH="/opt/homebrew/lib:$LD_LIBRARY_PATH"
export PATH="/opt/homebrew/bin:$PATH"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH"

# Diretório atual
cd "$(dirname "$0")"

# Usar o Python do ambiente virtual
VENV_PYTHON="/Users/alansms/CLionProjects/untitled2/.venv/bin/python"

# Executar a aplicação Streamlit usando o Python do ambiente virtual
$VENV_PYTHON -m streamlit run app/streamlit_app.py "$@"
