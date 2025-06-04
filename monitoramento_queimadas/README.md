# Monitoramento de Queimadas - Brasil

Este projeto implementa um fluxo completo de coleta, tratamento, análise, geração de alertas e visualização web de focos de queimadas a partir dos dados abertos do TerraBrasilis/INPE.

## Estrutura do Projeto

```
monitoramento-queimadas/
  ├── coleta/               # Scripts para coleta de dados do TerraBrasilis
  ├── tratamento/           # Scripts para limpeza e tratamento dos dados
  ├── analise/              # Scripts para análise temporal e espacial
  ├── alertas/              # Sistema de alertas baseado em limites configuráveis
  ├── relatorios/           # Geração de relatórios em PDF/HTML
  ├── output/               # Diretório para armazenamento de dados e resultados
  ├── app/                  # Interface interativa com Streamlit
  ├── docs/                 # Documentação detalhada
  ├── main.py               # Orquestrador do pipeline completo
  ├── requirements.txt      # Dependências do projeto
  └── .gitignore            # Arquivos a serem ignorados pelo Git
```

## Requisitos

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

## Instalação

```bash
# Clonar o repositório
git clone https://seu-repo.git
cd monitoramento-queimadas

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### Pipeline Completo

Para executar o pipeline completo (coleta, tratamento, análise, alertas e relatórios):

```bash
python main.py
```

### Interface Streamlit

Para iniciar a interface interativa:

```bash
streamlit run app/streamlit_app.py
```

## Funcionalidades

- **Coleta**: Download automático de dados de focos de queimadas do TerraBrasilis/INPE
- **Tratamento**: Limpeza, normalização e padronização dos dados coletados
- **Análise**: Análises temporais e espaciais dos focos de queimadas
- **Alertas**: Sistema configurável de alertas baseado em limites predefinidos
- **Relatórios**: Geração automática de relatórios com gráficos e tabelas
- **Visualização**: Interface interativa para exploração dos dados

## Documentação

Para instruções detalhadas sobre cada módulo, consulte o [Manual de Uso](docs/MANUAL_DE_USO.md).

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo LICENSE para obter detalhes.

Monitoramento de Queimadas - FIAP 2025

Sistema de monitoramento de queimadas desenvolvido como projeto para a Global Solution de AI FOR ROBOTIC PROCESS AUTOMATION da FIAP.

🔥 Sobre o Projeto

Este projeto consiste em um sistema de monitoramento de queimadas que coleta, processa e analisa dados de focos de incêndio no Brasil. O sistema inclui:

Coleta automatizada de dados do INPE
Processamento e limpeza dos dados
Interface interativa com Streamlit
Geração de relatórios automatizados
Sistema de alertas
🚀 Como executar

Clone o repositório:
git clone https://github.com/alansms/GS-2025-AI-FOR-ROBOTIC-PROCESS-AUTOMATION.git
cd GS-2025-AI-FOR-ROBOTIC-PROCESS-AUTOMATION
Crie um ambiente virtual e instale as dependências:
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
Execute a aplicação Streamlit:
streamlit run monitoramento-queimadas/app/streamlit_app.py
📊 Funcionalidades

Visualização de dados em tempo real
Mapas interativos de focos de queimada
Gráficos e análises estatísticas
Filtros por período, UF e bioma
Geração de relatórios em PDF/HTML
Sistema de alertas configurável
🔧 Tecnologias Utilizadas

Python
Streamlit
Pandas
Plotly
Folium
WeasyPrint
SQLite
👥 Equipe

Alan S M Silva
📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.