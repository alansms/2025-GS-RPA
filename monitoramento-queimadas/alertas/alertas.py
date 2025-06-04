#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de alertas para focos de queimadas.

Este script lê métricas geradas pelos scripts de análise, compara com limites
definidos em config_alertas.json, gera notificações e grava registros em
output/logs/alertas.log.
"""

import os
import sys
import json
import logging
import argparse
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger('monitoramento_queimadas.alertas')

def carregar_config(caminho_config):
    """
    Carrega a configuração de alertas do arquivo JSON.
    
    Args:
        caminho_config (str): Caminho para o arquivo de configuração.
    
    Returns:
        dict: Configuração de alertas carregada.
    """
    try:
        with open(caminho_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Configuração carregada: {caminho_config}")
        return config
    
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {str(e)}")
        
        # Criar configuração padrão
        config_padrao = {
            "limites": {
                "global": {
                    "diario": 1000,
                    "semanal": 5000
                },
                "por_uf": {
                    "AM": 200,
                    "PA": 300,
                    "default": 100
                },
                "por_bioma": {
                    "Amazonia": 500,
                    "Cerrado": 300,
                    "default": 100
                }
            },
            "notificacao": {
                "email": {
                    "ativo": False,
                    "destinatarios": ["exemplo@email.com"],
                    "assunto": "Alerta de Queimadas"
                },
                "arquivo": {
                    "ativo": True,
                    "caminho": "output/logs/alertas.log"
                }
            }
        }
        
        # Salvar configuração padrão
        os.makedirs(os.path.dirname(caminho_config), exist_ok=True)
        with open(caminho_config, 'w', encoding='utf-8') as f:
            json.dump(config_padrao, f, indent=2)
        
        logger.warning(f"Configuração padrão criada: {caminho_config}")
        return config_padrao

def carregar_dados_analise():
    """
    Carrega os dados de análise para verificação de alertas.
    
    Returns:
        tuple: (serie_temporal, focos_por_uf, focos_por_bioma) com os dados carregados.
    """
    try:
        # Diretório de análises
        diretorio_analises = 'output/dados_limpos/analises'
        os.makedirs(diretorio_analises, exist_ok=True)
        
        # Carregar série temporal
        caminho_serie = os.path.join(diretorio_analises, 'serie_temporal_dia.csv')
        serie_temporal = None
        if os.path.exists(caminho_serie):
            serie_temporal = pd.read_csv(caminho_serie)
            serie_temporal['periodo'] = pd.to_datetime(serie_temporal['periodo'])
            logger.info(f"Série temporal carregada: {len(serie_temporal)} registros")
        else:
            logger.warning(f"Arquivo de série temporal não encontrado: {caminho_serie}")
        
        # Carregar focos por UF
        caminho_uf = os.path.join(diretorio_analises, 'focos_por_uf.csv')
        focos_por_uf = None
        if os.path.exists(caminho_uf):
            focos_por_uf = pd.read_csv(caminho_uf)
            logger.info(f"Focos por UF carregados: {len(focos_por_uf)} UFs")
        else:
            logger.warning(f"Arquivo de focos por UF não encontrado: {caminho_uf}")
        
        # Carregar focos por bioma
        caminho_bioma = os.path.join(diretorio_analises, 'focos_por_bioma.csv')
        focos_por_bioma = None
        if os.path.exists(caminho_bioma):
            focos_por_bioma = pd.read_csv(caminho_bioma)
            logger.info(f"Focos por bioma carregados: {len(focos_por_bioma)} biomas")
        else:
            logger.warning(f"Arquivo de focos por bioma não encontrado: {caminho_bioma}")
        
        return serie_temporal, focos_por_uf, focos_por_bioma
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados de análise: {str(e)}")
        return None, None, None

def verificar_alertas(serie_temporal, focos_por_uf, focos_por_bioma, config):
    """
    Verifica se há alertas com base nos limites configurados.
    
    Args:
        serie_temporal (pandas.DataFrame): Série temporal de focos.
        focos_por_uf (pandas.DataFrame): Focos por UF.
        focos_por_bioma (pandas.DataFrame): Focos por bioma.
        config (dict): Configuração de alertas.
    
    Returns:
        list: Lista de alertas gerados.
    """
    alertas = []
    
    try:
        # Verificar alertas globais
        if serie_temporal is not None and not serie_temporal.empty:
            # Alerta diário
            limite_diario = config['limites']['global']['diario']
            ultimo_dia = serie_temporal.iloc[-1]
            if ultimo_dia['focos'] > limite_diario:
                alerta = {
                    'tipo': 'global_diario',
                    'data': ultimo_dia['periodo'].strftime('%Y-%m-%d'),
                    'valor': int(ultimo_dia['focos']),
                    'limite': limite_diario,
                    'mensagem': f"Alerta global diário: {int(ultimo_dia['focos'])} focos em {ultimo_dia['periodo'].strftime('%Y-%m-%d')} (limite: {limite_diario})"
                }
                alertas.append(alerta)
                logger.warning(alerta['mensagem'])
            
            # Alerta semanal
            limite_semanal = config['limites']['global']['semanal']
            ultimos_7_dias = serie_temporal.iloc[-7:] if len(serie_temporal) >= 7 else serie_temporal
            total_semanal = ultimos_7_dias['focos'].sum()
            if total_semanal > limite_semanal:
                periodo_inicio = ultimos_7_dias.iloc[0]['periodo'].strftime('%Y-%m-%d')
                periodo_fim = ultimos_7_dias.iloc[-1]['periodo'].strftime('%Y-%m-%d')
                alerta = {
                    'tipo': 'global_semanal',
                    'data_inicio': periodo_inicio,
                    'data_fim': periodo_fim,
                    'valor': int(total_semanal),
                    'limite': limite_semanal,
                    'mensagem': f"Alerta global semanal: {int(total_semanal)} focos entre {periodo_inicio} e {periodo_fim} (limite: {limite_semanal})"
                }
                alertas.append(alerta)
                logger.warning(alerta['mensagem'])
        
        # Verificar alertas por UF
        if focos_por_uf is not None and not focos_por_uf.empty:
            limites_uf = config['limites']['por_uf']
            limite_default = limites_uf['default']
            
            for _, row in focos_por_uf.iterrows():
                uf = row['uf']
                focos = row['focos']
                
                # Determinar limite para esta UF
                limite = limites_uf.get(uf, limite_default)
                
                if focos > limite:
                    alerta = {
                        'tipo': 'uf',
                        'uf': uf,
                        'valor': int(focos),
                        'limite': limite,
                        'mensagem': f"Alerta por UF: {int(focos)} focos em {uf} (limite: {limite})"
                    }
                    alertas.append(alerta)
                    logger.warning(alerta['mensagem'])
        
        # Verificar alertas por bioma
        if focos_por_bioma is not None and not focos_por_bioma.empty:
            limites_bioma = config['limites']['por_bioma']
            limite_default = limites_bioma['default']
            
            for _, row in focos_por_bioma.iterrows():
                bioma = row['bioma']
                focos = row['focos']
                
                # Determinar limite para este bioma
                limite = limites_bioma.get(bioma, limite_default)
                
                if focos > limite:
                    alerta = {
                        'tipo': 'bioma',
                        'bioma': bioma,
                        'valor': int(focos),
                        'limite': limite,
                        'mensagem': f"Alerta por bioma: {int(focos)} focos em {bioma} (limite: {limite})"
                    }
                    alertas.append(alerta)
                    logger.warning(alerta['mensagem'])
        
        logger.info(f"Verificação de alertas concluída: {len(alertas)} alertas gerados")
        return alertas
    
    except Exception as e:
        logger.error(f"Erro ao verificar alertas: {str(e)}")
        return alertas

def enviar_email_alerta(alertas, config):
    """
    Envia e-mail com alertas.
    
    Args:
        alertas (list): Lista de alertas a serem enviados.
        config (dict): Configuração de alertas.
    
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário.
    """
    if not alertas:
        logger.info("Sem alertas para enviar por e-mail")
        return True
    
    # Verificar se o envio de e-mail está ativo
    if not config['notificacao']['email']['ativo']:
        logger.info("Envio de e-mail desativado na configuração")
        return True
    
    try:
        # Configuração de e-mail
        destinatarios = config['notificacao']['email']['destinatarios']
        assunto = config['notificacao']['email']['assunto']
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['Subject'] = assunto
        msg['From'] = 'monitoramento-queimadas@exemplo.com'
        msg['To'] = ', '.join(destinatarios)
        
        # Corpo do e-mail
        corpo = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #d9534f; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .alerta { color: #d9534f; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Alerta de Focos de Queimadas</h1>
            <p>O sistema de monitoramento detectou os seguintes alertas:</p>
            <table>
                <tr>
                    <th>Tipo</th>
                    <th>Detalhes</th>
                    <th>Valor</th>
                    <th>Limite</th>
                </tr>
        """
        
        for alerta in alertas:
            tipo = alerta['tipo']
            detalhes = ""
            
            if tipo == 'global_diario':
                detalhes = f"Global diário ({alerta['data']})"
            elif tipo == 'global_semanal':
                detalhes = f"Global semanal ({alerta['data_inicio']} a {alerta['data_fim']})"
            elif tipo == 'uf':
                detalhes = f"UF: {alerta['uf']}"
            elif tipo == 'bioma':
                detalhes = f"Bioma: {alerta['bioma']}"
            
            corpo += f"""
                <tr>
                    <td>{tipo}</td>
                    <td>{detalhes}</td>
                    <td class="alerta">{alerta['valor']}</td>
                    <td>{alerta['limite']}</td>
                </tr>
            """
        
        corpo += """
            </table>
            <p>Este é um e-mail automático. Por favor, não responda.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo, 'html'))
        
        # Enviar e-mail (simulado)
        logger.info(f"Simulando envio de e-mail para: {', '.join(destinatarios)}")
        logger.info(f"Assunto: {assunto}")
        logger.info(f"Conteúdo: {len(alertas)} alertas")
        
        # Descomente o código abaixo para enviar e-mail real
        """
        with smtplib.SMTP('smtp.exemplo.com', 587) as server:
            server.starttls()
            server.login('usuario@exemplo.com', 'senha')
            server.send_message(msg)
        """
        
        logger.info("E-mail enviado com sucesso (simulado)")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {str(e)}")
        return False

def salvar_alertas_arquivo(alertas, config):
    """
    Salva alertas em arquivo de log.
    
    Args:
        alertas (list): Lista de alertas a serem salvos.
        config (dict): Configuração de alertas.
    
    Returns:
        bool: True se os alertas foram salvos com sucesso, False caso contrário.
    """
    if not alertas:
        logger.info("Sem alertas para salvar em arquivo")
        return True
    
    # Verificar se o salvamento em arquivo está ativo
    if not config['notificacao']['arquivo']['ativo']:
        logger.info("Salvamento em arquivo desativado na configuração")
        return True
    
    try:
        # Caminho do arquivo de alertas
        caminho_arquivo = config['notificacao']['arquivo']['caminho']
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        
        # Data e hora atual
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Abrir arquivo em modo append
        with open(caminho_arquivo, 'a', encoding='utf-8') as f:
            f.write(f"\n--- ALERTAS: {data_hora} ---\n")
            
            for alerta in alertas:
                f.write(f"{alerta['mensagem']}\n")
            
            f.write(f"--- FIM ALERTAS: {data_hora} ---\n")
        
        logger.info(f"Alertas salvos em arquivo: {caminho_arquivo}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao salvar alertas em arquivo: {str(e)}")
        return False

def main(caminho_config='alertas/config_alertas.json'):
    """
    Função principal do módulo de alertas.
    
    Args:
        caminho_config (str, optional): Caminho para o arquivo de configuração.
    
    Returns:
        list: Lista de alertas gerados.
    """
    logger.info("Iniciando verificação de alertas")
    
    try:
        # Carregar configuração
        config = carregar_config(caminho_config)
        
        # Carregar dados de análise
        serie_temporal, focos_por_uf, focos_por_bioma = carregar_dados_analise()
        
        # Verificar alertas
        alertas = verificar_alertas(serie_temporal, focos_por_uf, focos_por_bioma, config)
        
        if alertas:
            logger.warning(f"Foram gerados {len(alertas)} alertas")
            
            # Enviar e-mail
            enviar_email_alerta(alertas, config)
            
            # Salvar em arquivo
            salvar_alertas_arquivo(alertas, config)
        else:
            logger.info("Nenhum alerta gerado")
        
        logger.info("Verificação de alertas concluída")
        return alertas
    
    except Exception as e:
        logger.error(f"Erro durante a verificação de alertas: {str(e)}", exc_info=True)
        return []

if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Verificação de alertas de focos de queimadas')
    parser.add_argument('--config', type=str, default='alertas/config_alertas.json', help='Caminho para o arquivo de configuração')
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/alertas.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar verificação de alertas
    main(args.config)
