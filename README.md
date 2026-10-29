# 🐾 Resgate Pets — Dashboard de Ribeirão Preto

> Projeto desenvolvido para o desafio de hackathon de **Resgate de PETs ou Segurança Pública**.

## Apresentação do projeto

O **Team 4** criou um dashboard interativo para visualizar e acompanhar ocorrências de animais em situação de risco em Ribeirão Preto (SP). A solução reúne dados públicos do IBGE com uma base demonstrativa de ocorrências por bairro, sempre identificada como simulada. O painel foi pensado para equipes de resgate, organizações de proteção animal, poder público e cidadãos que precisem identificar regiões e casos prioritários. Na prática, os usuários aplicam filtros por zona, bairro, espécie e status para acompanhar indicadores, comparar áreas e apoiar a organização das ações de resgate.

## Equipe — Team 4

- Pedro Henrique Tunis de Paula Leão
- Brenda Azevedo da Silva
- Lorenzo de Souza Machado

## O problema

Informações sobre abandono, maus-tratos e animais feridos costumam ficar dispersas. Isso dificulta enxergar padrões territoriais, priorizar atendimentos e comunicar resultados de forma simples.

## A solução

O dashboard transforma os registros em uma visão operacional com:

- indicadores de ocorrências, resgates, tratamentos e adoções;
- filtros interativos por zona, bairro, espécie e status;
- gráficos por bairro, zona, espécie, situação e andamento;
- tabela detalhada, filtrável e ordenável;
- contexto regional obtido pela API pública do IBGE;
- contatos da Divisão de Bem-Estar Animal de Ribeirão Preto.

## Quem vai utilizar

- equipes e voluntários de resgate animal;
- ONGs e protetores independentes;
- gestores públicos e órgãos de bem-estar animal;
- cidadãos interessados em compreender e reportar o problema.

## Como será usado

Ao abrir o painel, a pessoa seleciona os filtros desejados e acompanha a atualização automática dos indicadores, gráficos e registros. A visualização ajuda a identificar concentrações de ocorrências, casos aguardando atendimento e resultados já alcançados. Nesta versão de demonstração, o painel apoia análise e apresentação; ele não substitui os canais oficiais de denúncia ou emergência.

## Dados e transparência

- **API de Localidades do IBGE:** dados reais do município e da microrregião, consultados ao iniciar o aplicativo.
- **Ocorrências por bairro:** dados simulados e reproduzíveis, usados apenas para demonstrar a experiência do dashboard porque não foi localizada uma API pública municipal com esse nível de detalhe.
- **Referências contextuais:** CNJ, Instituto Pet Brasil, Corpo de Bombeiros e Prefeitura de Ribeirão Preto, conforme comentários e constantes em `dados.py`.

> Importante: números simulados não devem ser interpretados como estatísticas oficiais nem usados isoladamente para decisões operacionais reais.

## Tecnologias

- Python
- Dash
- Plotly
- Pandas
- NumPy
- Requests

## Como executar

Pré-requisito: Python 3.10 ou superior.

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Instale as dependências e inicie o dashboard:

```bash
python -m pip install -r requirements.txt
python app.py
```

Depois, acesse [http://127.0.0.1:8050](http://127.0.0.1:8050).

Se a API do IBGE estiver indisponível, o projeto usa automaticamente valores locais de contingência para continuar funcionando.

## Estrutura do projeto

```text
.
├── app.py             # Interface, gráficos, filtros e callbacks do dashboard
├── dados.py           # Consulta ao IBGE e geração da base demonstrativa
├── requirements.txt   # Dependências fixadas
├── .gitignore         # Arquivos locais ignorados pelo Git
└── README.md          # Apresentação e instruções do projeto
```

## Critérios do hackathon atendidos

- **Insight da solução:** visão territorial e operacional das ocorrências.
- **Execução técnica:** dashboard funcional, filtros combináveis e atualização dinâmica.
- **Comunicação:** dados reais e simulados são diferenciados explicitamente.
- **Originalidade:** foco local em Ribeirão Preto e apoio visual à priorização de resgates.

## Aviso de uso

Este é um protótipo educacional de hackathon. Em uma versão de produção, registros reais exigiriam autenticação, autorização no servidor, minimização de dados pessoais, trilha de auditoria e validação do fluxo com os órgãos responsáveis.

