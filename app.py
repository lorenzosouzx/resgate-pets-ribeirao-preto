"""
app.py - Dashboard interativo de resgate de pets — Ribeirão Preto / SP

Tecnologias:
    - Dash  : framework de dashboards web em Python
    - Plotly: gráficos interativos
    - Pandas: manipulação de dados

Para rodar:
    python app.py
    Acesse: http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.express as px
import pandas as pd

from dados import (
    df_animais,
    dados_municipio,
    ESTATISTICAS_REAIS,
    BAIRROS,
    ESPECIES,
    STATUS,
)

# -------------------------------------------------------
# Inicialização
# -------------------------------------------------------
app = dash.Dash(
    __name__,
    title="🐾 Resgate de Pets — Ribeirão Preto",
    suppress_callback_exceptions=True,
)
server = app.server

# -------------------------------------------------------
# Paleta — modo CLARO
# -------------------------------------------------------
TEMAS = {
    "claro": {
        "fundo":         "#f0f4f8",
        "card":          "#ffffff",
        "card_interno":  "#f8f9fa",
        "texto":         "#2d3436",
        "texto_sec":     "#636e72",
        "texto_tenue":   "#b2bec3",
        "borda_aviso":   "#ffc107",
        "fundo_aviso":   "#fff3cd",
        "cor_aviso":     "#856404",
        "plot_bg":       "white",
        "btn_bg":        "rgba(255,255,255,0.15)",
        "btn_texto":     "white",
        "btn_label":     "🌙 Modo Escuro",
        "grad_header":   "linear-gradient(135deg, #1a6bbf, #0d3d7a)",
    },
    "escuro": {
        "fundo":         "#1a1a2e",
        "card":          "#16213e",
        "card_interno":  "#0f3460",
        "texto":         "#e0e0e0",
        "texto_sec":     "#a0a0b0",
        "texto_tenue":   "#606080",
        "borda_aviso":   "#e9c46a",
        "fundo_aviso":   "#2a2510",
        "cor_aviso":     "#e9c46a",
        "plot_bg":       "#16213e",
        "btn_bg":        "rgba(255,255,255,0.15)",
        "btn_texto":     "white",
        "btn_label":     "☀️ Modo Claro",
        "grad_header":   "linear-gradient(135deg, #0d3d7a, #050e30)",
    },
}

COR_PRIMARIA = "#1a6bbf"
COR_PERIGO   = "#e63946"
COR_SUCESSO  = "#2a9d8f"
COR_ALERTA   = "#e9c46a"
COR_ROXO     = "#6c5ce7"
COR_CINZA    = "#636e72"

CORES_STATUS = {
    "Aguardando Resgate": COR_PERIGO,
    "Resgatado":          COR_SUCESSO,
    "Em Tratamento":      COR_ALERTA,
    "Adotado":            COR_ROXO,
    "Óbito":              COR_CINZA,
}

ZONAS = sorted(df_animais["zona"].unique())


def card_kpi(icone, titulo, valor, cor=COR_PRIMARIA, subtexto="", tema="claro"):
    """Card de indicador KPI com suporte a tema."""
    t = TEMAS[tema]
    return html.Div(
        style={
            "background":    t["card"],
            "borderRadius":  "12px",
            "padding":       "18px 20px",
            "boxShadow":     "0 2px 8px rgba(0,0,0,0.12)",
            "textAlign":     "center",
            "flex":          "1",
            "minWidth":      "150px",
        },
        children=[
            html.Div(icone, style={"fontSize": "28px", "marginBottom": "4px"}),
            html.P(titulo, style={
                "fontSize": "11px", "color": t["texto_sec"],
                "fontWeight": "700", "textTransform": "uppercase",
                "letterSpacing": "0.5px", "margin": "0 0 4px",
            }),
            html.H2(str(valor), style={
                "fontSize": "32px", "fontWeight": "bold",
                "color": cor, "margin": "0",
            }),
            html.P(subtexto, style={
                "fontSize": "11px", "color": t["texto_tenue"], "margin": "4px 0 0",
            }),
        ]
    )


# -------------------------------------------------------
# Layout
# -------------------------------------------------------
app.layout = html.Div(
    id="pagina-raiz",
    # data-tema guarda o estado atual ("claro" ou "escuro")
    **{"data-tema": "claro"},
    style={"fontFamily": "Segoe UI, Arial, sans-serif", "minHeight": "100vh",
           "backgroundColor": TEMAS["claro"]["fundo"]},
    children=[

        # ── Cabeçalho ────────────────────────────────────────
        html.Div(
            id="cabecalho",
            style={
                "background":   TEMAS["claro"]["grad_header"],
                "color":        "white",
                "padding":      "22px 32px",
                "marginBottom": "24px",
                "display":      "flex",
                "justifyContent": "space-between",
                "alignItems":   "center",
            },
            children=[
                html.Div([
                    html.H1("🐾 Dashboard de Resgate de Pets — Ribeirão Preto / SP",
                            style={"margin": "0", "fontSize": "22px"}),
                    html.P(
                        f"Município: {dados_municipio['nome']} · "
                        f"Código IBGE: {dados_municipio['id']} · "
                        "Dados municipais carregados via API pública do IBGE",
                        style={"margin": "6px 0 0", "opacity": "0.80", "fontSize": "12px"},
                    ),
                ]),
                # Botão de alternar tema
                html.Button(
                    id="btn-tema",
                    children="🌙 Modo Escuro",
                    n_clicks=0,
                    style={
                        "background":    "rgba(255,255,255,0.15)",
                        "color":         "white",
                        "border":        "1px solid rgba(255,255,255,0.4)",
                        "borderRadius":  "8px",
                        "padding":       "8px 16px",
                        "cursor":        "pointer",
                        "fontSize":      "13px",
                        "fontWeight":    "600",
                        "whiteSpace":    "nowrap",
                        "marginLeft":    "24px",
                    },
                ),
            ],
        ),

        # ── Corpo ────────────────────────────────────────────
        html.Div(
            style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px 48px"},
            children=[

                # Aviso de fontes
                html.Div(
                    id="aviso-fontes",
                    style={
                        "background":   TEMAS["claro"]["fundo_aviso"],
                        "border":       f"1px solid {TEMAS['claro']['borda_aviso']}",
                        "borderRadius": "8px",
                        "padding":      "10px 16px",
                        "marginBottom": "20px",
                        "fontSize":     "12px",
                        "color":        TEMAS["claro"]["cor_aviso"],
                    },
                    children=[
                        html.Strong("📌 Fontes: "),
                        "Dados do município carregados via API pública do IBGE (servicodados.ibge.gov.br). "
                        "Estatísticas de resgate baseadas em dados reais do CNJ, Corpo de Bombeiros de "
                        "Ribeirão Preto e Instituto Pet Brasil. Ocorrências por bairro são simuladas com "
                        "base nos percentuais reais (nenhuma prefeitura disponibiliza esse dado em API aberta).",
                    ],
                ),

                # ── Filtros ──────────────────────────────────
                html.Div(
                    style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"},
                    children=[
                        html.Div([
                            html.Label("Zona", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-zona",
                                options=[{"label": "Todas as Zonas", "value": "Todas"}] +
                                        [{"label": f"Zona {z}", "value": z} for z in ZONAS],
                                value="Todas", clearable=False, style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Bairro", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-bairro",
                                options=[{"label": "Todos os Bairros", "value": "Todos"}] +
                                        [{"label": b, "value": b} for b in sorted(BAIRROS)],
                                value="Todos", clearable=False, style={"width": "230px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Espécie", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-especie",
                                options=[{"label": "Todas", "value": "Todas"}] +
                                        [{"label": e, "value": e} for e in ESPECIES],
                                value="Todas", clearable=False, style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Status", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-status",
                                options=[{"label": "Todos", "value": "Todos"}] +
                                        [{"label": s, "value": s} for s in STATUS],
                                value="Todos", clearable=False, style={"width": "220px"},
                            ),
                        ]),
                    ],
                ),

                # ── Cards KPI ────────────────────────────────
                html.Div(id="cards-kpi",
                         style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "24px"}),

                # ── Como os animais são encontrados ──────────
                html.Div(
                    id="secao-como",
                    style={
                        "background":   TEMAS["claro"]["card"],
                        "borderRadius": "12px",
                        "padding":      "18px 22px",
                        "marginBottom": "24px",
                        "boxShadow":    "0 2px 8px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.H3("🔍 Como os animais em situação precária são identificados?",
                                style={"margin": "0 0 14px", "fontSize": "15px", "color": "#2d3436"}),
                        html.Div(
                            style={"display": "grid",
                                   "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                                   "gap": "16px"},
                            children=[
                                html.Div(style={"background": "#f8f9fa", "borderRadius": "10px",
                                                "padding": "14px", "borderLeft": f"4px solid {COR_PRIMARIA}"},
                                         children=[
                                             html.P("👥 Civis e moradores", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                             html.P("Qualquer pessoa pode denunciar um animal em situação de risco "
                                                    "pelo WhatsApp da DBEA: (16) 99170-8198 ou pelo telefone 0800-772-1789.",
                                                    style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"}),
                                         ]),
                                html.Div(style={"background": "#f8f9fa", "borderRadius": "10px",
                                                "padding": "14px", "borderLeft": f"4px solid {COR_SUCESSO}"},
                                         children=[
                                             html.P("🏠 ONGs e protetores independentes", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                             html.P("Organizações e protetores voluntários realizam rondas, monitoram "
                                                    "redes sociais e respondem chamados. No Brasil, mais de 184 mil "
                                                    "animais estão sob tutela dessas redes (Instituto Pet Brasil, 2022).",
                                                    style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"}),
                                         ]),
                                html.Div(style={"background": "#f8f9fa", "borderRadius": "10px",
                                                "padding": "14px", "borderLeft": f"4px solid {COR_ALERTA}"},
                                         children=[
                                             html.P("🚒 Corpo de Bombeiros", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                             html.P("Em Ribeirão Preto, resgate de animais é o 2º tipo de ocorrência "
                                                    "mais atendido — 70% são silvestres em vias públicas "
                                                    "(G1 / Bombeiros RP, abr/2024).",
                                                    style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"}),
                                         ]),
                                html.Div(style={"background": "#f8f9fa", "borderRadius": "10px",
                                                "padding": "14px", "borderLeft": f"4px solid {COR_ROXO}"},
                                         children=[
                                             html.P("🏛️ Prefeitura — DBEA", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                             html.P("A Divisão de Bem-Estar Animal recebe denúncias, realiza resgates "
                                                    "oficiais e encaminha para abrigos, tratamento ou adoção.",
                                                    style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"}),
                                         ]),
                                html.Div(style={"background": "#f8f9fa", "borderRadius": "10px",
                                                "padding": "14px", "borderLeft": f"4px solid {COR_PERIGO}"},
                                         children=[
                                             html.P("📱 Redes sociais e apps", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                             html.P("Grupos de WhatsApp, Facebook e Instagram de protetores locais "
                                                    "funcionam como canais de alerta rápido — mobilizam voluntários em minutos.",
                                                    style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"}),
                                         ]),
                            ],
                        ),
                    ],
                ),

                # ── Gráficos linha 1 ─────────────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                           "gap": "20px", "marginBottom": "20px"},
                    children=[
                        html.Div(id="card-graf-bairros",
                                 style={"background": TEMAS["claro"]["card"], "borderRadius": "12px",
                                        "padding": "18px 20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
                                 children=[
                                     html.H3("Ocorrências por Bairro",
                                             style={"margin": "0 0 10px", "fontSize": "14px"}),
                                     dcc.Graph(id="graf-bairros", config={"displayModeBar": False}),
                                 ]),
                        html.Div(id="card-graf-zonas",
                                 style={"background": TEMAS["claro"]["card"], "borderRadius": "12px",
                                        "padding": "18px 20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
                                 children=[
                                     html.H3("Ocorrências por Zona da Cidade",
                                             style={"margin": "0 0 10px", "fontSize": "14px"}),
                                     dcc.Graph(id="graf-zonas", config={"displayModeBar": False}),
                                 ]),
                    ],
                ),

                # ── Gráficos linha 2 ─────────────────────────
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr",
                           "gap": "20px", "marginBottom": "24px"},
                    children=[
                        html.Div(id="card-graf-especies",
                                 style={"background": TEMAS["claro"]["card"], "borderRadius": "12px",
                                        "padding": "18px 20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
                                 children=[
                                     html.H3("Distribuição por Espécie",
                                             style={"margin": "0 0 10px", "fontSize": "14px"}),
                                     dcc.Graph(id="graf-especies", config={"displayModeBar": False}),
                                 ]),
                        html.Div(id="card-graf-status",
                                 style={"background": TEMAS["claro"]["card"], "borderRadius": "12px",
                                        "padding": "18px 20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
                                 children=[
                                     html.H3("Status dos Animais",
                                             style={"margin": "0 0 10px", "fontSize": "14px"}),
                                     dcc.Graph(id="graf-status", config={"displayModeBar": False}),
                                 ]),
                        html.Div(id="card-graf-situacao",
                                 style={"background": TEMAS["claro"]["card"], "borderRadius": "12px",
                                        "padding": "18px 20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
                                 children=[
                                     html.H3("Tipo de Situação",
                                             style={"margin": "0 0 10px", "fontSize": "14px"}),
                                     dcc.Graph(id="graf-situacao", config={"displayModeBar": False}),
                                 ]),
                    ],
                ),

                # ── Rodapé ───────────────────────────────────
                html.Div(
                    id="rodape",
                    style={"textAlign": "center", "marginTop": "32px",
                           "fontSize": "11px", "color": "#b2bec3"},
                    children=[
                        html.P("Fontes: IBGE API (servicodados.ibge.gov.br) · CNJ — cnj.jus.br · "
                               "Instituto Pet Brasil · G1 Ribeirão Preto / Corpo de Bombeiros · "
                               "Prefeitura de Ribeirão Preto (ribeiraopreto.sp.gov.br)"),
                        html.P("Dashboard desenvolvido com Python + Dash + Plotly"),
                    ],
                ),
            ],
        ),
    ],
)


# -------------------------------------------------------
# Callback 1 — alternar tema claro/escuro
# -------------------------------------------------------
@app.callback(
    Output("pagina-raiz",        "style"),
    Output("btn-tema",           "children"),
    Output("cabecalho",          "style"),
    Output("aviso-fontes",       "style"),
    Output("secao-como",         "style"),
    Output("card-graf-bairros",  "style"),
    Output("card-graf-zonas",    "style"),
    Output("card-graf-especies", "style"),
    Output("card-graf-status",   "style"),
    Output("card-graf-situacao", "style"),
    Output("rodape",             "style"),
    Input("btn-tema", "n_clicks"),
)
def alternar_tema(n):
    """
    Alterna entre modo claro e escuro a cada clique no botão.
    n par = claro, n ímpar = escuro.
    """
    tema = "escuro" if (n or 0) % 2 == 1 else "claro"
    t = TEMAS[tema]

    estilo_pagina = {
        "fontFamily":       "Segoe UI, Arial, sans-serif",
        "minHeight":        "100vh",
        "backgroundColor":  t["fundo"],
    }
    estilo_header = {
        "background":     t["grad_header"],
        "color":          "white",
        "padding":        "22px 32px",
        "marginBottom":   "24px",
        "display":        "flex",
        "justifyContent": "space-between",
        "alignItems":     "center",
    }
    estilo_aviso = {
        "background":    t["fundo_aviso"],
        "border":        f"1px solid {t['borda_aviso']}",
        "borderRadius":  "8px",
        "padding":       "10px 16px",
        "marginBottom":  "20px",
        "fontSize":      "12px",
        "color":         t["cor_aviso"],
    }
    estilo_card_secao = {
        "background":   t["card"],
        "borderRadius": "12px",
        "padding":      "18px 22px",
        "marginBottom": "24px",
        "boxShadow":    "0 2px 8px rgba(0,0,0,0.12)",
    }
    estilo_card_graf = {
        "background":   t["card"],
        "borderRadius": "12px",
        "padding":      "18px 20px",
        "boxShadow":    "0 2px 8px rgba(0,0,0,0.12)",
    }
    estilo_rodape = {
        "textAlign":   "center",
        "marginTop":   "32px",
        "fontSize":    "11px",
        "color":       t["texto_tenue"],
    }

    return (
        estilo_pagina,
        t["btn_label"],
        estilo_header,
        estilo_aviso,
        estilo_card_secao,
        estilo_card_graf,
        estilo_card_graf,
        estilo_card_graf,
        estilo_card_graf,
        estilo_card_graf,
        estilo_rodape,
    )


# -------------------------------------------------------
# Callback 2 — atualizar gráficos e cards com os filtros
# -------------------------------------------------------
@app.callback(
    Output("cards-kpi",     "children"),
    Output("graf-bairros",  "figure"),
    Output("graf-zonas",    "figure"),
    Output("graf-especies", "figure"),
    Output("graf-status",   "figure"),
    Output("graf-situacao", "figure"),
    Input("filtro-zona",    "value"),
    Input("filtro-bairro",  "value"),
    Input("filtro-especie", "value"),
    Input("filtro-status",  "value"),
    Input("btn-tema",       "n_clicks"),   # re-renderiza os gráficos no tema certo
)
def atualizar(zona, bairro, especie, status, n_tema):
    """Aplica filtros e gera todos os gráficos no tema correto."""

    tema = "escuro" if (n_tema or 0) % 2 == 1 else "claro"
    t    = TEMAS[tema]

    # ── Filtros ──────────────────────────────────────────
    df = df_animais.copy()
    if zona    != "Todas": df = df[df["zona"]    == zona]
    if bairro  != "Todos": df = df[df["bairro"]  == bairro]
    if especie != "Todas": df = df[df["especie"] == especie]
    if status  != "Todos": df = df[df["status"]  == status]

    total         = len(df)
    aguardando    = len(df[df["status"] == "Aguardando Resgate"])
    resgatados    = len(df[df["status"] == "Resgatado"])
    em_tratamento = len(df[df["status"] == "Em Tratamento"])
    adotados      = len(df[df["status"] == "Adotado"])

    # ── Cards KPI ────────────────────────────────────────
    cards = [
        card_kpi("📋", "Total de Ocorrências", total,         COR_PRIMARIA, "registros filtrados",       tema),
        card_kpi("🚨", "Aguardando Resgate",   aguardando,    COR_PERIGO,   "necessitam ação imediata",  tema),
        card_kpi("✅", "Resgatados",           resgatados,    COR_SUCESSO,  "animais salvos",            tema),
        card_kpi("🏥", "Em Tratamento",        em_tratamento, COR_ALERTA,   "sob cuidados veterinários", tema),
        card_kpi("🏠", "Adotados",             adotados,      COR_ROXO,     "encontraram lar",           tema),
    ]

    # Cor do texto nos gráficos
    cor_texto_graf = t["texto"]

    # ── Gráfico: ocorrências por bairro ──────────────────
    df_b = (df.groupby("bairro").size()
              .reset_index(name="ocorrencias")
              .sort_values("ocorrencias", ascending=True))

    fig_bairros = px.bar(
        df_b, x="ocorrencias", y="bairro", orientation="h",
        color="ocorrencias", color_continuous_scale="Blues",
        labels={"ocorrencias": "Ocorrências", "bairro": "Bairro"},
    )
    fig_bairros.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        plot_bgcolor=t["plot_bg"], paper_bgcolor=t["plot_bg"],
        height=350,
        font=dict(color=cor_texto_graf),
        xaxis=dict(gridcolor="#333" if tema == "escuro" else "#eee"),
        yaxis=dict(gridcolor="#333" if tema == "escuro" else "#eee"),
    )
    fig_bairros.update_traces(hovertemplate="<b>%{y}</b><br>Ocorrências: %{x}<extra></extra>")

    # ── Gráfico: ocorrências por zona ────────────────────
    df_z = (df.groupby("zona").size()
              .reset_index(name="ocorrencias")
              .sort_values("ocorrencias", ascending=False))

    CORES_ZONA = {
        "Norte": "#e63946", "Sul": "#e9c46a",
        "Leste": "#2c7be5", "Oeste": "#2a9d8f", "Centro": "#6c5ce7",
    }
    fig_zonas = px.bar(
        df_z, x="zona", y="ocorrencias",
        color="zona", color_discrete_map=CORES_ZONA,
        labels={"ocorrencias": "Ocorrências", "zona": "Zona"},
        text="ocorrencias",
    )
    fig_zonas.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor=t["plot_bg"], paper_bgcolor=t["plot_bg"],
        height=350,
        font=dict(color=cor_texto_graf),
        yaxis=dict(gridcolor="#333" if tema == "escuro" else "#eee"),
    )
    fig_zonas.update_traces(
        textposition="outside",
        hovertemplate="<b>Zona %{x}</b><br>Ocorrências: %{y}<extra></extra>",
    )

    # ── Gráfico: espécies (rosca) ────────────────────────
    df_e = df.groupby("especie").size().reset_index(name="total")
    fig_especies = px.pie(
        df_e, names="especie", values="total",
        hole=0.42,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_especies.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=t["plot_bg"], height=300,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(color=cor_texto_graf)),
        font=dict(color=cor_texto_graf),
    )
    fig_especies.update_traces(hovertemplate="<b>%{label}</b><br>%{value} animais (%{percent})<extra></extra>")

    # ── Gráfico: status ──────────────────────────────────
    df_s = (df.groupby("status").size()
              .reset_index(name="total")
              .sort_values("total", ascending=True))

    fig_status = px.bar(
        df_s, x="total", y="status", orientation="h",
        color="status", color_discrete_map=CORES_STATUS,
        labels={"total": "Quantidade", "status": "Status"},
    )
    fig_status.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor=t["plot_bg"], paper_bgcolor=t["plot_bg"],
        height=300,
        font=dict(color=cor_texto_graf),
        xaxis=dict(gridcolor="#333" if tema == "escuro" else "#eee"),
    )
    fig_status.update_traces(hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>")

    # ── Gráfico: situação (rosca) ────────────────────────
    df_sit = df.groupby("situacao").size().reset_index(name="total")
    fig_situacao = px.pie(
        df_sit, names="situacao", values="total",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_situacao.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=t["plot_bg"], height=300,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, font=dict(color=cor_texto_graf)),
        font=dict(color=cor_texto_graf),
    )
    fig_situacao.update_traces(hovertemplate="<b>%{label}</b><br>%{value} casos (%{percent})<extra></extra>")

    return cards, fig_bairros, fig_zonas, fig_especies, fig_status, fig_situacao


# -------------------------------------------------------
# Ponto de entrada
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n🐾 Dashboard Resgate de Pets — Ribeirão Preto iniciando...")
    print("   Acesse: http://127.0.0.1:8050\n")
    app.run(debug=True)

