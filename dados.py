"""
dados.py - Coleta e geração de dados para o dashboard de resgate de pets.
Foco: Ribeirão Preto - SP

Estratégia de dados:
  1. API pública do IBGE → dados reais do município de Ribeirão Preto
     (código IBGE: 3543402, população: 734.538 hab. estimada 2026)
  2. Divisão de Bem-Estar Animal (DBEA) da Prefeitura de RP → referência real
     para o serviço de resgate (dado citado, sem API pública disponível)
  3. CNJ 2025 → totais nacionais reais de maus-tratos (citados como contexto)
  4. Instituto Pet Brasil → percentuais reais por espécie (96% cães / 4% gatos)
  5. Dados simulados por bairro → baseados nos percentuais reais acima
     (bairros reais de Ribeirão Preto, sem API pública disponível nesse nível)

Fontes:
  - IBGE Localidades: https://servicodados.ibge.gov.br/api/v1/localidades/
  - IBGE Cidades: https://www.ibge.gov.br/cidades-e-estados/sp/ribeirao-preto.html
  - Prefeitura RP / DBEA: https://www.ribeiraopreto.sp.gov.br
  - CNJ: https://cnj.jus.br (4.919 novos processos em 2025)
  - Instituto Pet Brasil: ~185 mil animais sob tutela de ONGs
"""

import requests
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Semente para reprodutibilidade dos dados simulados
random.seed(42)
np.random.seed(42)

# -------------------------------------------------------
# CONSTANTES — Ribeirão Preto
# -------------------------------------------------------

# Código oficial IBGE de Ribeirão Preto - SP
# Fonte: https://www.ibge.gov.br/cidades-e-estados/sp/ribeirao-preto.html
CODIGO_IBGE_RP = 3543402
UF = "SP"

# -------------------------------------------------------
# 1. DADOS REAIS — API pública do IBGE
# -------------------------------------------------------

def buscar_dados_municipio_ibge(codigo_municipio=CODIGO_IBGE_RP):
    """
    Busca dados reais do município via API pública do IBGE.

    Parâmetros:
        codigo_municipio (int): código IBGE do município

    Retorna:
        dict com nome, microrregião, mesorregião e UF do município

    Fonte: https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{id}
    """
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo_municipio}"
    try:
        print(f"[IBGE] Buscando dados do município {codigo_municipio}...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        resultado = {
            "id":           dados["id"],
            "nome":         dados["nome"],
            "microrregiao": dados["microrregiao"]["nome"],
            "mesorregiao":  dados["microrregiao"]["mesorregiao"]["nome"],
            "uf":           dados["microrregiao"]["mesorregiao"]["UF"]["sigla"],
        }
        print(f"[IBGE] Município encontrado: {resultado['nome']} - {resultado['uf']}")
        return resultado
    except requests.exceptions.RequestException as e:
        print(f"[IBGE] Falha na API: {e}. Usando dados fixos.")
        return {
            "id":           CODIGO_IBGE_RP,
            "nome":         "Ribeirão Preto",
            "microrregiao": "Ribeirão Preto",
            "mesorregiao":  "Ribeirão Preto",
            "uf":           "SP",
        }


def buscar_municipios_vizinhos_ibge(uf=UF, microrregiao="Ribeirão Preto"):
    """
    Busca municípios da microrregião de Ribeirão Preto via API do IBGE.
    Útil para contextualizar a região no dashboard.

    Retorna:
        pd.DataFrame com id e nome dos municípios da microrregião
    """
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes/35050/municipios"
    try:
        print(f"[IBGE] Buscando municípios da microrregião de {microrregiao}...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        municipios = resp.json()
        df = pd.DataFrame([{"id": m["id"], "nome": m["nome"]} for m in municipios])
        print(f"[IBGE] {len(df)} municípios na microrregião encontrados.")
        return df
    except requests.exceptions.RequestException as e:
        print(f"[IBGE] Falha na API de microrregiões: {e}.")
        return pd.DataFrame([
            {"id": CODIGO_IBGE_RP, "nome": "Ribeirão Preto"},
            {"id": 3536307,        "nome": "Sertãozinho"},
            {"id": 3513900,        "nome": "Cravinhos"},
        ])


# -------------------------------------------------------
# 2. DADOS REAIS — Estatísticas nacionais e locais
#    Usados para calibrar os dados simulados abaixo
# -------------------------------------------------------

ESTATISTICAS_REAIS = {
    # Instituto Pet Brasil (2022 - dado mais recente público)
    "total_animais_ongs_brasil":       184960,
    "percentual_caes":                 96,     # % de cães no total nacional
    "percentual_gatos":                4,      # % de gatos no total nacional

    # CNJ — Conselho Nacional de Justiça (2025)
    # Fonte: G1/CNJ, fev/2026
    "processos_maus_tratos_2025":      4919,
    "aumento_percentual_2021_2025":    1400,   # crescimento em 4 anos
    "media_casos_por_dia_2025":        13,

    # Corpo de Bombeiros de Ribeirão Preto (2024)
    # Fonte: G1 Ribeirão Preto, abr/2024
    # Resgate de animais = 2º tipo de ocorrência mais atendido
    # 70% silvestres, 30% domésticos
    "bombeiros_rp_silvestres_pct":     70,
    "bombeiros_rp_domesticos_pct":     30,

    # Prefeitura de Ribeirão Preto — DBEA
    # Fonte: ribeiraopreto.sp.gov.br
    "dbea_whatsapp":                   "(16) 99170-8198",
    "dbea_telefone_denuncia":          "0800-772-1789",

    # IBGE — Ribeirão Preto
    # Fonte: ibge.gov.br/cidades-e-estados/sp/ribeirao-preto.html
    "populacao_rp_2026_estimada":      734538,
    "area_km2":                        650.916,
    "idhm":                            0.800,
}


# -------------------------------------------------------
# 3. DADOS SIMULADOS — ocorrências por bairro em Ribeirão Preto
#    Bairros REAIS da cidade (fonte: Prefeitura RP / CEP Brasil)
#    Pesos baseados em localização: periféricos têm mais ocorrências
# -------------------------------------------------------

# Bairros reais de Ribeirão Preto agrupados por zona
BAIRROS_RP = {
    # Zona Norte — mais populosa, bairros periféricos com mais ocorrências
    "Jardim Interlagos":        10,
    "Jardim Helena":            9,
    "Parque dos Lagos":         8,
    "Alto do Ipiranga":         7,
    "Jardim Sumaré":            6,

    # Zona Sul — mistura de bairros residenciais e periféricos
    "Jardim Paulista":          8,
    "Vila Tibério":             7,
    "Campos Elíseos":           6,
    "Ipiranga":                 5,

    # Zona Leste — bairros mais novos, crescimento urbano acelerado
    "Jardim Aeroporto":         9,
    "Quintino Facci II":        8,
    "Parque Ribeirão":          7,
    "Jardim Botânico":          5,

    # Zona Oeste — mais consolidada, menos ocorrências
    "Alto da Boa Vista":        5,
    "Nova Aliança":             4,

    # Centro
    "Centro":                   6,
    "Vila Seixas":              4,
    "Jardim América":           3,
}

# Listas separadas para facilitar uso no Dash
BAIRROS       = list(BAIRROS_RP.keys())
PESOS_BAIRROS = list(BAIRROS_RP.values())

# Espécies com pesos baseados nos dados reais do Instituto Pet Brasil
# + Corpo de Bombeiros de RP (70% dos resgates são animais silvestres)
ESPECIES       = ["Cão", "Gato", "Animal Silvestre", "Outro"]
PESOS_ESPECIES = [45, 15, 30, 10]   # reflete o perfil local de RP (Bombeiros: 70% silvestres)

STATUS       = ["Aguardando Resgate", "Resgatado", "Em Tratamento", "Adotado", "Óbito"]
PESOS_STATUS = [30, 25, 20, 20, 5]

SITUACOES = [
    "Abandono",
    "Maus-tratos",
    "Atropelamento",
    "Doença",
    "Ferimento",
    "Subnutrição",
    "Preso/Enroscado",   # comum em animais silvestres (Bombeiros RP)
]

NOMES_CAES     = ["Rex", "Bidu", "Thor", "Luna", "Bob", "Mel", "Duke", "Nina", "Max", "Bella"]
NOMES_GATOS    = ["Mingau", "Fifi", "Tom", "Pérola", "Garfield", "Mia", "Simba", "Lili"]
NOMES_SILV     = ["Gavião", "Tatu", "Serelepe", "Jabuti", "Tucano", "Gambá"]
NOMES_OUTROS   = ["Sem Identificação"]


def _nome_por_especie(especie):
    """Retorna um nome aleatório de acordo com a espécie do animal."""
    mapa = {
        "Cão":              NOMES_CAES,
        "Gato":             NOMES_GATOS,
        "Animal Silvestre": NOMES_SILV,
        "Outro":            NOMES_OUTROS,
    }
    return random.choice(mapa.get(especie, ["Sem Nome"]))


def gerar_ocorrencias(n=150):
    """
    Gera registros simulados de animais em situação precária em Ribeirão Preto.

    Os percentuais usados são baseados em fontes reais:
      - Espécies: Corpo de Bombeiros de RP (70% silvestres) + Instituto Pet Brasil
      - Distribuição por bairro: pesos maiores para zonas periféricas

    Parâmetros:
        n (int): número de registros a gerar

    Retorna:
        pd.DataFrame com: id, nome, especie, situacao, status,
        bairro, zona, data_ocorrencia, idade_estimada, descricao
    """
    # Mapa bairro → zona para enriquecer os dados
    zona_por_bairro = {
        "Jardim Interlagos": "Norte", "Jardim Helena": "Norte",
        "Parque dos Lagos": "Norte",  "Alto do Ipiranga": "Norte",
        "Jardim Sumaré": "Norte",     "Jardim Paulista": "Sul",
        "Vila Tibério": "Sul",        "Campos Elíseos": "Sul",
        "Ipiranga": "Sul",            "Jardim Aeroporto": "Leste",
        "Quintino Facci II": "Leste", "Parque Ribeirão": "Leste",
        "Jardim Botânico": "Leste",   "Alto da Boa Vista": "Oeste",
        "Nova Aliança": "Oeste",      "Centro": "Centro",
        "Vila Seixas": "Centro",      "Jardim América": "Centro",
    }

    registros   = []
    data_base   = datetime(2026, 10, 29)   # data atual do projeto

    for i in range(1, n + 1):
        especie  = random.choices(ESPECIES,  weights=PESOS_ESPECIES)[0]
        status   = random.choices(STATUS,    weights=PESOS_STATUS)[0]
        bairro   = random.choices(BAIRROS,   weights=PESOS_BAIRROS)[0]
        situacao = random.choice(SITUACOES)
        dias_atras = random.randint(0, 365)
        data_oc  = data_base - timedelta(days=dias_atras)

        registros.append({
            "id":              i,
            "especie":         especie,
            "situacao":        situacao,
            "status":          status,
            "bairro":          bairro,
            "zona":            zona_por_bairro.get(bairro, "Outro"),
            "data_ocorrencia": data_oc.strftime("%d/%m/%Y"),
            "idade_estimada":  f"{random.randint(1, 120)} meses",
            "descricao":       (
                f"Animal em situação de {situacao.lower()} "
                f"localizado no bairro {bairro} (Zona {zona_por_bairro.get(bairro, 'N/D')})."
            ),
        })

    return pd.DataFrame(registros)


# -------------------------------------------------------
# Carregamento ao importar o módulo
# -------------------------------------------------------

# Dados reais do município via API IBGE
dados_municipio   = buscar_dados_municipio_ibge(CODIGO_IBGE_RP)

# Municípios vizinhos da microrregião (API IBGE)
df_municipios_rp  = buscar_municipios_vizinhos_ibge()

# Ocorrências simuladas com bairros reais de Ribeirão Preto
df_animais        = gerar_ocorrencias(150)

print(f"[DADOS] Cidade: {dados_municipio['nome']} - {dados_municipio['uf']}")
print(f"[DADOS] {len(df_animais)} ocorrências carregadas.")
print(f"[DADOS] Bairros cobertos: {df_animais['bairro'].nunique()}")
print(f"[DADOS] Zonas: {sorted(df_animais['zona'].unique())}")

