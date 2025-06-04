#!/bin/bash

echo "Corrigindo problemas do WeasyPrint no macOS..."

# Verificar e criar links simbólicos necessários
if [ -d "/opt/homebrew/lib" ]; then
    # Criar links simbólicos para bibliotecas
    ln -sf /opt/homebrew/lib/libpango-1.0.dylib /usr/local/lib/
    ln -sf /opt/homebrew/lib/libcairo.dylib /usr/local/lib/
    ln -sf /opt/homebrew/lib/libffi.dylib /usr/local/lib/
fi

# Configurar variáveis de ambiente permanentemente
echo 'export FONTCONFIG_PATH="/opt/homebrew/etc/fonts"' >> ~/.zshrc
echo 'export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc

# Recarregar variáveis de ambiente
source ~/.zshrc

# Verificar instalação do WeasyPrint
echo "Testando instalação do WeasyPrint..."
python3 -c "import weasyprint; print('WeasyPrint instalado com sucesso!')" || echo "Erro ao importar WeasyPrint"

echo "Correção concluída! Por favor, reinicie seu terminal para aplicar todas as mudanças."
