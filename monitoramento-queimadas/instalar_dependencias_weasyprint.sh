#!/bin/bash
# Script para instalar dependências do WeasyPrint no macOS

echo "Instalando dependências do WeasyPrint para macOS..."

# Verificar se o Homebrew está instalado
if ! command -v brew &> /dev/null
then
    echo "Homebrew não encontrado. Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew já está instalado. Atualizando..."
    brew update
fi

# Instalar as dependências necessárias
echo "Instalando pango, libffi e outras dependências do WeasyPrint..."
brew install pango libffi cairo harfbuzz

# Instalar ou reinstalar o WeasyPrint via pip
echo "Reinstalando WeasyPrint no ambiente Python..."
pip uninstall -y weasyprint
pip install --no-cache-dir weasyprint

# Configurar variáveis de ambiente
echo "Configurando variáveis de ambiente..."
export FONTCONFIG_PATH="/opt/homebrew/etc/fonts"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Criar diretório de fontes se não existir
mkdir -p ~/Library/Fonts

echo "Instalação concluída!"
echo "Por favor, execute 'source ~/.bashrc' ou abra um novo terminal para aplicar as mudanças."
