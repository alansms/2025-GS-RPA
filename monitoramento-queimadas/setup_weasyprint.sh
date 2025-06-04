#!/bin/bash

# Definir variáveis de ambiente
export PKG_CONFIG_PATH="/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Reinstalar WeasyPrint com as variáveis de ambiente corretas
pip install --no-cache-dir --force-reinstall weasyprint

# Adicionar as variáveis ao perfil do shell se ainda não existirem
if ! grep -q "PKG_CONFIG_PATH.*libffi" ~/.zshrc; then
    echo 'export PKG_CONFIG_PATH="/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"' >> ~/.zshrc
fi

if ! grep -q "LDFLAGS.*homebrew" ~/.zshrc; then
    echo 'export LDFLAGS="-L/opt/homebrew/lib"' >> ~/.zshrc
fi

if ! grep -q "CPPFLAGS.*homebrew" ~/.zshrc; then
    echo 'export CPPFLAGS="-I/opt/homebrew/include"' >> ~/.zshrc
fi

if ! grep -q "DYLD_LIBRARY_PATH.*homebrew" ~/.zshrc; then
    echo 'export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"' >> ~/.zshrc
fi
