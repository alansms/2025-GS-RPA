#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo principal para orquestração do pipeline de monitoramento de queimadas.

Este script coordena a execução sequencial dos módulos de coleta, tratamento,
análise, alertas e relatórios, garantindo o fluxo completo de processamento
dos dados de focos de queimadas do TerraBrasilis/INPE.
"""

import os
import sys
import logging
import argparse
import importlib
import subprocess
from datetime import datetime

# Configuração de logging
def setup_logging():
    """Configura o sistema de logging para o pipeline."""
    os.makedirs('output/logs', exist_ok=True)
    log_file = f'output/logs/execucao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('monitoramento_queimadas')

# Verificação e instalação automática de dependências
def check_dependencies():
    """
    Verifica e instala automaticamente as dependências necessárias.
    
    Returns:
        bool: True se todas as dependências estão instaladas, False caso contrário.
    """
    logger = logging.getLogger('monitoramento_queimadas.dependencies')
    logger.info("Verificando dependências...")
    
    try:
        with open('requirements.txt', 'r') as f:
            required_packages = [line.strip() for line in f if line.strip()]
        
        # Verificar pacotes instalados
        installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
        installed_packages = [pkg.split('==')[0].lower() for pkg in installed_packages.split('\n') if pkg]
        
        # Identificar pacotes faltantes
        missing_packages = []
        for package in required_packages:
            pkg_name = package.split('>=')[0].split('==')[0].lower()
            if pkg_name not in installed_packages:
                missing_packages.append(package)
        
        # Instalar pacotes faltantes
        if missing_packages:
            logger.warning(f"Dependências faltantes: {', '.join(missing_packages)}")
            logger.info("Instalando dependências faltantes...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            logger.info("Dependências instaladas com sucesso!")
            return True
        else:
            logger.info("Todas as dependências já estão instaladas.")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao verificar/instalar dependências: {str(e)}")
        return False

# Função principal
def main():
    """
    Função principal que orquestra o pipeline completo de monitoramento de queimadas.
    
    Executa sequencialmente os módulos de coleta, tratamento, análise, alertas e relatórios,
    garantindo o fluxo completo de processamento dos dados.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Pipeline de monitoramento de queimadas')
    parser.add_argument('--data-inicio', type=str, help='Data inicial (YYYY-MM-DD)')
    parser.add_argument('--data-fim', type=str, help='Data final (YYYY-MM-DD)')
    parser.add_argument('--skip-coleta', action='store_true', help='Pular etapa de coleta')
    parser.add_argument('--skip-tratamento', action='store_true', help='Pular etapa de tratamento')
    parser.add_argument('--skip-analise', action='store_true', help='Pular etapa de análise')
    parser.add_argument('--skip-alertas', action='store_true', help='Pular etapa de alertas')
    parser.add_argument('--skip-relatorios', action='store_true', help='Pular etapa de relatórios')
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging()
    logger.info("Iniciando pipeline de monitoramento de queimadas")
    
    # Verificar dependências
    if not check_dependencies():
        logger.error("Falha na verificação de dependências. Abortando execução.")
        return 1
    
    try:
        # Criar diretórios de saída se não existirem
        os.makedirs('output/dados_brutos', exist_ok=True)
        os.makedirs('output/dados_limpos', exist_ok=True)
        os.makedirs('output/relatorios', exist_ok=True)
        
        # Importar módulos
        if not args.skip_coleta:
            logger.info("Iniciando módulo de coleta")
            from coleta.coleta import main as coleta_main
            coleta_args = {}
            if args.data_inicio:
                coleta_args['data_inicio'] = args.data_inicio
            if args.data_fim:
                coleta_args['data_fim'] = args.data_fim
            coleta_main(**coleta_args)
            logger.info("Módulo de coleta concluído com sucesso")
        
        if not args.skip_tratamento:
            logger.info("Iniciando módulo de tratamento")
            from tratamento.tratamento import main as tratamento_main
            tratamento_main()
            logger.info("Módulo de tratamento concluído com sucesso")
        
        if not args.skip_analise:
            logger.info("Iniciando módulo de análise temporal")
            from analise.analise_temporal import main as analise_temporal_main
            analise_temporal_main()
            logger.info("Módulo de análise temporal concluído com sucesso")
            
            logger.info("Iniciando módulo de análise espacial")
            from analise.analise_espacial import main as analise_espacial_main
            analise_espacial_main()
            logger.info("Módulo de análise espacial concluído com sucesso")
        
        if not args.skip_alertas:
            logger.info("Iniciando módulo de alertas")
            from alertas.alertas import main as alertas_main
            alertas_main()
            logger.info("Módulo de alertas concluído com sucesso")
        
        if not args.skip_relatorios:
            logger.info("Iniciando módulo de relatórios")
            from relatorios.relatorio import main as relatorio_main
            relatorio_main()
            logger.info("Módulo de relatórios concluído com sucesso")
        
        logger.info("Pipeline de monitoramento de queimadas concluído com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"Erro durante a execução do pipeline: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
