# Monitoramento de Queimadas - FIAP 2025

Sistema de monitoramento de queimadas desenvolvido como projeto para a Global Solution de AI FOR ROBOTIC PROCESS AUTOMATION da FIAP.

## 🔥 Sobre o Projeto

Este projeto consiste em um sistema de monitoramento de queimadas que coleta, processa e analisa dados de focos de incêndio no Brasil. O sistema inclui:

- Coleta automatizada de dados do INPE
- Processamento e limpeza dos dados
- Interface interativa com Streamlit
- Geração de relatórios automatizados
- Sistema de alertas

## 🚀 Como executar

1. Clone o repositório:
```bash
git clone https://github.com/alansms/GS-2025-AI-FOR-ROBOTIC-PROCESS-AUTOMATION.git
cd GS-2025-AI-FOR-ROBOTIC-PROCESS-AUTOMATION
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Execute a aplicação Streamlit:
```bash
streamlit run monitoramento-queimadas/app/streamlit_app.py
```

## 📊 Funcionalidades

- Visualização de dados em tempo real
- Mapas interativos de focos de queimada
- Gráficos e análises estatísticas
- Filtros por período, UF e bioma
- Geração de relatórios em PDF/HTML
- Sistema de alertas configurável

## 🔧 Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Folium
- WeasyPrint
- SQLite

## 👥 Equipe

- Alan S M Silva

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
