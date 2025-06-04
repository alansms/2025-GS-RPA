# Monitoramento de Queimadas - FIAP 2025

Sistema de monitoramento de queimadas desenvolvido como projeto para a Global Solution da FIAP.

## 🔥 Sobre o Projeto

Este projeto consiste em um sistema de monitoramento de queimadas que coleta, processa e analisa dados de focos de incêndio no Brasil. O sistema inclui:

- Coleta automatizada de dados de focos de queimadas
- Processamento e análise dos dados
- Interface interativa com Streamlit
- Geração de relatórios em PDF e HTML
- Sistema de alertas para anomalias
- Visualização geográfica dos focos

## 🚀 Como executar

### Localmente

1. Clone o repositório:
```bash
git clone https://github.com/alansms/2025-GS-RPA.git
cd 2025-GS-RPA
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run streamlit_app.py
```

### Online

O projeto está disponível online através do Streamlit Cloud: [Link para o aplicativo](https://2025-gs-rpa.streamlit.app/)

## 📊 Funcionalidades

### Monitoramento em Tempo Real
- Visualização de focos de queimada em mapa interativo
- Filtros por estado e bioma
- Série temporal de ocorrências

### Sistema de Alertas
- Detecção automática de anomalias
- Alertas por estado e bioma
- Níveis de alerta (MÉDIO e ALTO)

### Relatórios Automáticos
- Geração de relatórios em PDF
- Análises detalhadas por região
- Estatísticas e gráficos

### Análise de Dados
- Distribuição geográfica dos focos
- Análise por bioma
- Tendências temporais

## 🛠 Estrutura do Projeto

```
src/
├── alertas/          # Sistema de detecção de anomalias
├── analise/          # Módulos de análise de dados
├── coleta/           # Coleta e processamento de dados
├── relatorios/       # Geração de relatórios
└── utils/            # Utilitários gerais

output/               # Dados gerados
├── dados_brutos/     # Dados coletados
├── dados_limpos/     # Dados processados
├── relatorios/       # Relatórios gerados
└── logs/            # Logs do sistema
```

## 📝 Requisitos do Sistema

- Python 3.8 ou superior
- Navegador web moderno
- Conexão com internet

Para sistemas Linux, instale as dependências do sistema:
```bash
apt-get update && apt-get install -y \
    libpango1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi7 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libcairo2
```

## 👥 Equipe

- Alan Santos (RM: 353687)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
