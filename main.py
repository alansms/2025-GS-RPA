#!/usr/bin/env python3
"""
Script para criar a estrutura de pastas e arquivos iniciais do projeto
“monitoramento-queimadas”. Execute este script na raiz onde deseja gerar
o projeto. Ele criará diretórios, subdiretórios e arquivos Python com
conteúdo mínimo (docstrings e stubs) para começar o desenvolvimento.
"""

import os
from pathlib import Path

# Lista de pastas a serem criadas (relativas à raiz do projeto)
PASTAS = [
    "coleta",
    "coleta/utils_coleta",
    "tratamento",
    "tratamento/utils_tratamento",
    "analise",
    "analise/utils_analise",
    "alertas",
    "relatorios",
    "relatorios/templates",
    "relatorios/recursos",
    "output/dados_brutos",
    "output/dados_limpos",
    "output/relatorios",
    "output/logs",
    "docs",
    "app"
]

# Arquivos a serem criados, mapeados para o conteúdo inicial
ARQUIVOS = {
    "coleta/coleta.py": '''"""
Módulo de coleta de dados de focos de queimadas do TerraBrasilis/INPE.

Funções:
    baixar_dados(data: str) -> Path
        Baixa o arquivo (CSV ou ZIP) referente à data informada e retorna o Path salvo.
"""
import os
import requests
from datetime import datetime

def baixar_dados(data: str = None):
    """
    Baixa dados brutos do TerraBrasilis para a data fornecida (formato 'YYYY-MM-DD').
    Se data for None, usa a data de hoje.
    Retorna o Path do arquivo salvo em output/dados_brutos/.
    """
    # TODO: implementar lógica de montagem de URL e download
    raise NotImplementedError("Implementar função baixar_dados()")
''',

    "coleta/utils_coleta.py": '''"""
Funções auxiliares para o módulo de coleta.

- montar_url_por_data(data: str) -> str
- descompactar_arquivo(path_zip: Path, destino: Path) -> None
"""
import zipfile
from pathlib import Path

def montar_url_por_data(data: str) -> str:
    """
    Retorna a URL de download no TerraBrasilis para a data informada.
    Exemplo de retorno: "http://.../dados-YYYY-MM-DD.zip"
    """
    # TODO: implementar lógica para montar URL
    raise NotImplementedError("Implementar função montar_url_por_data()")

def descompactar_arquivo(path_zip: Path, destino: Path) -> None:
    """
    Recebe um Path para um arquivo ZIP e extrai seu conteúdo na pasta destino.
    """
    with zipfile.ZipFile(path_zip, 'r') as z:
        z.extractall(destino)
''',

    "tratamento/tratamento.py": '''"""
Módulo de tratamento de dados brutos de focos de queimadas.

Funções:
    limpar_dados(caminho_bruto: Path) -> pandas.DataFrame
        Lê CSV/ZIP bruto, faz limpeza, normalizações e retorna DataFrame tratado.
"""
import pandas as pd

def limpar_dados(caminho_bruto: str):
    """
    Lê o arquivo bruto (CSV ou ZIP), corrige encoding, remove duplicados,
    trata valores nulos, converte tipos e salva CSV tratado em output/dados_limpos/.
    Retorna o DataFrame limpo.
    """
    # TODO: implementar lógica de leitura e tratamento
    raise NotImplementedError("Implementar função limpar_dados()")
''',

    "tratamento/utils_tratamento.py": '''"""
Funções auxiliares para limpeza e transformação de dados.

- padronizar_nomes_colunas(df: pandas.DataFrame) -> pandas.DataFrame
- preencher_nulos(df: pandas.DataFrame) -> pandas.DataFrame
"""
import pandas as pd

def padronizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomeia colunas para snake_case e remove espaços.
    """
    # TODO: implementar padronização de colunas
    raise NotImplementedError("Implementar função padronizar_nomes_colunas()")

def preencher_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preenche valores nulos em colunas-chave (ex.: 'estado', 'bioma').
    """
    # TODO: implementar preenchimento de nulos
    raise NotImplementedError("Implementar função preencher_nulos()")
''',

    "analise/analise_temporal.py": '''"""
Módulo de análise temporal dos dados de focos de queimadas.

Funções:
    gerar_serie_temporal(df: pandas.DataFrame) -> pandas.DataFrame
        Agrupa dados por data e retorna DataFrame com quantidade de focos por dia.
"""
import pandas as pd

def gerar_serie_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe DataFrame limpo, agrupa por data (dia) e retorna DataFrame
    com colunas ['data', 'qtd_focos'] ordenado por data.
    """
    # TODO: implementar agregação temporal
    raise NotImplementedError("Implementar função gerar_serie_temporal()")
''',

    "analise/analise_espacial.py": '''"""
Módulo de análise espacial dos dados de focos de queimadas.

Funções:
    gerar_analise_espacial(df: pandas.DataFrame) -> dict
        Retorna dicionário com DataFrames de focos por UF e por bioma.
"""
import pandas as pd

def gerar_analise_espacial(df: pd.DataFrame) -> dict:
    """
    Recebe DataFrame limpo e retorna:
    {
        'focos_por_uf': DataFrame com colunas ['estado', 'qtd_focos'],
        'focos_por_bioma': DataFrame com colunas ['bioma', 'qtd_focos']
    }
    """
    # TODO: implementar agregação espacial
    raise NotImplementedError("Implementar função gerar_analise_espacial()")
''',

    "analise/utils_analise.py": '''"""
Funções auxiliares para análise (métricas, média móvel, desvio padrão).

- calcular_media_movel(serie: pandas.Series, window: int) -> pandas.Series
- detectar_picos(serie: pandas.Series, n_desvios: float) -> pandas.DatetimeIndex
"""
import pandas as pd

def calcular_media_movel(serie: pd.Series, window: int) -> pd.Series:
    """
    Retorna média móvel da série com janela definida.
    """
    return serie.rolling(window=window).mean()

def detectar_picos(serie: pd.Series, n_desvios: float) -> pd.DatetimeIndex:
    """
    Identifica datas onde a série ultrapassa média + n_desvios * desvio padrão.
    """
    media = serie.rolling(window=7).mean()
    desvio = serie.rolling(window=7).std()
    condicao = serie > (media + n_desvios * desvio)
    return serie[condicao].index
''',

    "alertas/alertas.py": '''"""
Módulo de alertas para focos de queimadas.

Funções:
    verificar_alertas(metrica: pandas.DataFrame) -> None
        Compara métricas com limites em config_alertas.json e gera notificações.
"""
import json
import os
from datetime import datetime

CONFIG_PATH = os.path.join("alertas", "config_alertas.json")

def verificar_alertas(metrica):
    """
    Recebe dicionário ou DataFrame com métricas (por UF, global, etc.)
    e compara com limites definidos em config_alertas.json.
    Gera alertas (log em TXT ou envio de e-mail) conforme criticidade.
    """
    # TODO: implementar leitura de config e lógica de alerta
    raise NotImplementedError("Implementar função verificar_alertas()")
''',

    "alertas/config_alertas.json": '''{
    "limite_focos_por_uf": {
        "AM": 500,
        "MT": 800,
        "AC": 300,
        "BA": 400
    },
    "limite_semanal_global": 5000,
    "email_destino": "seu.email@dominio.com"
}
''',

    "relatorios/relatorio.py": '''"""
Módulo de geração de relatórios (PDF ou HTML) com resultados de análise.

Funções:
    gerar_relatorio(serie_temporal: pandas.DataFrame, analise_espacial: dict) -> None
        Monta relatório final com gráficos, tabelas e sumário executivo.
"""
import os

def gerar_relatorio(serie_temporal, analise_espacial):
    """
    Recebe DataFrame de série temporal e dicionário de análise espacial,
    gera um arquivo PDF ou HTML em output/relatorios/.
    """
    # TODO: implementar geração de relatório usando matplotlib, plotly ou Jinja2
    raise NotImplementedError("Implementar função gerar_relatorio()")
''',

    "relatorios/templates/README.txt": '''Template folder for report.
Adicione aqui arquivos Jinja2 (*.html) ou LaTeX (*.tex) para montar relatórios.
''',

    "relatorios/recursos/README.txt": '''Recursos estáticos para relatórios.
Exemplo: logotipos (*.png), folhas de estilo (*.css) e ícones.
''',

    "docs/README.md": '''# Monitoramento de Queimadas

Este repositório contém um pipeline para:
1. Coleta de dados de focos de queimadas (TerraBrasilis/INPE).
2. Tratamento e limpeza dos dados brutos.
3. Análise temporal e espacial.
4. Geração de alertas automáticos.
5. Produção de relatórios (PDF/HTML).
6. Interface web interativa em Streamlit.

## Instalação

```bash
git clone https://seu-repo.git
cd monitoramento-queimadas
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# Windows (PowerShell):
# .\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
'''
,
    ".gitignore": '''__pycache__/
*.pyc
.venv/
output/
'''
}
