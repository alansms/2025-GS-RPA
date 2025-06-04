# Manual de Uso - Monitoramento de Queimadas

Este manual detalha o uso de cada módulo do sistema de monitoramento de queimadas, incluindo exemplos de linha de comando, instruções de agendamento e dicas de personalização.

## Índice
1. [Instalação](#instalação)
2. [Módulo de Coleta](#módulo-de-coleta)
3. [Módulo de Tratamento](#módulo-de-tratamento)
4. [Módulo de Análise](#módulo-de-análise)
5. [Módulo de Alertas](#módulo-de-alertas)
6. [Módulo de Relatórios](#módulo-de-relatórios)
7. [Interface Streamlit](#interface-streamlit)
8. [Agendamento](#agendamento)
9. [Personalização](#personalização)

## Instalação

### Requisitos do Sistema
- Python 3.8 ou superior
- Acesso à internet para download dos dados
- Espaço em disco para armazenamento dos dados e relatórios

### Passo a Passo
1. Clone o repositório:
   ```bash
   git clone https://seu-repo.git
   cd monitoramento-queimadas
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Módulo de Coleta

O módulo de coleta é responsável por baixar os dados de focos de queimadas do TerraBrasilis/INPE.

### Uso Básico
```bash
python -m coleta.coleta
```

### Parâmetros
- `--data-inicio`: Data inicial para coleta (formato YYYY-MM-DD)
- `--data-fim`: Data final para coleta (formato YYYY-MM-DD)
- `--fonte`: Fonte dos dados (padrão: "terrabrasilis")

### Exemplos
```bash
# Coletar dados do dia atual
python -m coleta.coleta

# Coletar dados de um período específico
python -m coleta.coleta --data-inicio 2023-01-01 --data-fim 2023-01-31
```

## Módulo de Tratamento

O módulo de tratamento limpa e padroniza os dados coletados.

### Uso Básico
```bash
python -m tratamento.tratamento
```

### Parâmetros
- `--input-dir`: Diretório de entrada (padrão: "output/dados_brutos")
- `--output-dir`: Diretório de saída (padrão: "output/dados_limpos")
- `--force`: Força o reprocessamento de arquivos já tratados

### Exemplos
```bash
# Tratar todos os arquivos não processados
python -m tratamento.tratamento

# Forçar o reprocessamento de todos os arquivos
python -m tratamento.tratamento --force
```

## Módulo de Análise

O módulo de análise realiza análises temporais e espaciais dos focos de queimadas.

### Análise Temporal
```bash
python -m analise.analise_temporal
```

### Análise Espacial
```bash
python -m analise.analise_espacial
```

### Parâmetros
- `--periodo`: Período de análise (dia, semana, mes, ano)
- `--uf`: Filtrar por UF específica
- `--bioma`: Filtrar por bioma específico

### Exemplos
```bash
# Análise temporal por mês
python -m analise.analise_temporal --periodo mes

# Análise espacial para um estado específico
python -m analise.analise_espacial --uf SP
```

## Módulo de Alertas

O módulo de alertas monitora os dados e gera notificações quando limites são ultrapassados.

### Uso Básico
```bash
python -m alertas.alertas
```

### Configuração
Os parâmetros de alerta são definidos no arquivo `alertas/config_alertas.json`:

```json
{
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
      "ativo": true,
      "destinatarios": ["exemplo@email.com"],
      "assunto": "Alerta de Queimadas"
    },
    "arquivo": {
      "ativo": true,
      "caminho": "output/logs/alertas.log"
    }
  }
}
```

## Módulo de Relatórios

O módulo de relatórios gera relatórios em PDF ou HTML com gráficos e tabelas.

### Uso Básico
```bash
python -m relatorios.relatorio
```

### Parâmetros
- `--formato`: Formato do relatório (pdf, html)
- `--periodo`: Período do relatório (dia, semana, mes, ano)
- `--output`: Caminho de saída do relatório

### Exemplos
```bash
# Gerar relatório PDF do último mês
python -m relatorios.relatorio --formato pdf --periodo mes

# Gerar relatório HTML com caminho personalizado
python -m relatorios.relatorio --formato html --output /caminho/personalizado/relatorio.html
```

## Interface Streamlit

A interface Streamlit permite a visualização interativa dos dados.

### Iniciar a Interface
```bash
streamlit run app/streamlit_app.py
```

### Funcionalidades
- Seleção de período (data de início e fim)
- Filtros por UF e bioma
- Gráficos interativos (linha, barra, pizza)
- Mapa de dispersão dos focos
- Tabelas resumidas

## Agendamento

### Usando cron (Linux/Mac)
Para executar o pipeline completo diariamente às 8h:

```bash
# Editar o crontab
crontab -e

# Adicionar a linha
0 8 * * * cd /caminho/para/monitoramento-queimadas && /caminho/para/python main.py >> output/logs/cron.log 2>&1
```

### Usando o Task Scheduler (Windows)
1. Abra o Task Scheduler
2. Crie uma nova tarefa
3. Configure para executar diariamente
4. Adicione uma ação para executar: `python.exe` com argumento `main.py`

### Usando a biblioteca schedule
O projeto inclui um script `scheduler.py` que pode ser executado como um serviço:

```bash
python scheduler.py
```

## Personalização

### Personalização de Alertas
Edite o arquivo `alertas/config_alertas.json` para ajustar os limites e configurações de notificação.

### Personalização de Relatórios
Os templates de relatório estão em `relatorios/templates/`. Você pode editar esses arquivos para personalizar o layout e o conteúdo dos relatórios.

### Personalização da Interface
A interface Streamlit pode ser personalizada editando o arquivo `app/streamlit_app.py`. Consulte a [documentação do Streamlit](https://docs.streamlit.io/) para mais informações.
