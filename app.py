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
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import pandas as pd

# Importa dados (reais do IBGE + simulados por bairro de Ribeirão Preto)
from dados import (
    df_animais,
    dados_municipio,
    ESTATISTICAS_REAIS,
    BAIRROS,
    ESPECIES,
    STATUS,
)

# -------------------------------------------------------
# Inicialização do app Dash
# -------------------------------------------------------
app = dash.Dash(
    __name__,
    title="🐾 Resgate de Pets — Ribeirão Preto",
    suppress_callback_exceptions=True,
)

# -------------------------------------------------------
# Paleta de cores
# -------------------------------------------------------
COR_FUNDO    = "#f0f4f8"
COR_CARD     = "#ffffff"
COR_PRIMARIA = "#1a6bbf"
COR_PERIGO   = "#e63946"
COR_SUCESSO  = "#2a9d8f"
COR_ALERTA   = "#e9c46a"
COR_ROXO     = "#6c5ce7"
COR_CINZA    = "#636e72"

ESTILO_CARD = {
    "background":    COR_CARD,
    "borderRadius":  "12px",
    "padding":       "18px 20px",
    "boxShadow":     "0 2px 8px rgba(0,0,0,0.08)",
    "textAlign":     "center",
    "flex":          "1",
    "minWidth":      "150px",
}

CORES_STATUS = {
    "Aguardando Resgate": COR_PERIGO,
    "Resgatado":          COR_SUCESSO,
    "Em Tratamento":      COR_ALERTA,
    "Adotado":            COR_ROXO,
    "Óbito":              COR_CINZA,
}

ZONAS = sorted(df_animais["zona"].unique())


def card_kpi(icone, titulo, valor, cor=COR_PRIMARIA, subtexto=""):
    """Monta um card de indicador (KPI) para o topo do dashboard."""
    return html.Div(style=ESTILO_CARD, children=[
        html.Div(icone, style={"fontSize": "28px", "marginBottom": "4px"}),
        html.P(titulo, style={
            "fontSize": "11px", "color": COR_CINZA,
            "fontWeight": "700", "textTransform": "uppercase",
            "letterSpacing": "0.5px", "margin": "0 0 4px",
        }),
        html.H2(str(valor), style={
            "fontSize": "32px", "fontWeight": "bold",
            "color": cor, "margin": "0",
        }),
        html.P(subtexto, style={
            "fontSize": "11px", "color": "#b2bec3", "margin": "4px 0 0",
        }),
    ])


# -------------------------------------------------------
# Layout
# -------------------------------------------------------
app.layout = html.Div(
    style={"backgroundColor": COR_FUNDO, "fontFamily": "Segoe UI, Arial, sans-serif", "minHeight": "100vh"},
    children=[

        # ── Cabeçalho ──────────────────────────────────────────────────
        html.Div(
            style={
                "background":    "linear-gradient(135deg, #1a6bbf, #0d3d7a)",
                "color":         "white",
                "padding":       "22px 32px",
                "marginBottom":  "24px",
            },
            children=[
                html.H1("🐾 Dashboard de Resgate de Pets — Ribeirão Preto / SP",
                        style={"margin": "0", "fontSize": "24px"}),
                html.P(
                    f"Município: {dados_municipio['nome']} · "
                    f"Código IBGE: {dados_municipio['id']} · "
                    f"Microrregião: {dados_municipio['microrregiao']} · "
                    "Dados municipais carregados via API pública do IBGE",
                    style={"margin": "6px 0 0", "opacity": "0.80", "fontSize": "12px"},
                ),
            ],
        ),

        # ── Corpo ───────────────────────────────────────────────────────
        html.Div(
            style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px 48px"},
            children=[

                # Aviso sobre as fontes
                html.Div(
                    style={
                        "background":    "#fff3cd",
                        "border":        "1px solid #ffc107",
                        "borderRadius":  "8px",
                        "padding":       "10px 16px",
                        "marginBottom":  "20px",
                        "fontSize":      "12px",
                        "color":         "#856404",
                    },
                    children=[
                        html.Strong("📌 Fontes: "),
                        "Dados do município carregados via API pública do IBGE (servicodados.ibge.gov.br). "
                        "Estatísticas de resgate baseadas em dados reais do CNJ, Corpo de Bombeiros de Ribeirão Preto "
                        "e Instituto Pet Brasil. Ocorrências por bairro são simuladas com base nos percentuais reais "
                        "(nenhuma prefeitura disponibiliza esse dado em API aberta).",
                    ],
                ),

                # ── Filtros ─────────────────────────────────────────────
                html.Div(
                    style={
                        "display": "flex", "gap": "16px",
                        "flexWrap": "wrap", "marginBottom": "20px",
                    },
                    children=[
                        html.Div([
                            html.Label("Zona", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-zona",
                                options=[{"label": "Todas as Zonas", "value": "Todas"}] +
                                        [{"label": f"Zona {z}", "value": z} for z in ZONAS],
                                value="Todas", clearable=False,
                                style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Bairro", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-bairro",
                                options=[{"label": "Todos os Bairros", "value": "Todos"}] +
                                        [{"label": b, "value": b} for b in sorted(BAIRROS)],
                                value="Todos", clearable=False,
                                style={"width": "230px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Espécie", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-especie",
                                options=[{"label": "Todas", "value": "Todas"}] +
                                        [{"label": e, "value": e} for e in ESPECIES],
                                value="Todas", clearable=False,
                                style={"width": "200px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Status", style={"fontSize": "11px", "fontWeight": "700", "color": COR_CINZA}),
                            dcc.Dropdown(
                                id="filtro-status",
                                options=[{"label": "Todos", "value": "Todos"}] +
                                        [{"label": s, "value": s} for s in STATUS],
                                value="Todos", clearable=False,
                                style={"width": "220px"},
                            ),
                        ]),
                    ],
                ),

                # ── Cards KPI ────────────────────────────────────────────
                html.Div(id="cards-kpi",
                         style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "24px"}),

                # ── Como os animais são encontrados ──────────────────────
                html.Div(
                    style={
                        "background":   COR_CARD,
                        "borderRadius": "12px",
                        "padding":      "18px 22px",
                        "marginBottom": "24px",
                        "boxShadow":    "0 2px 8px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.H3("🔍 Como os animais em situação precária são identificados?",
                                style={"margin": "0 0 14px", "fontSize": "15px", "color": "#2d3436"}),
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "16px"},
                            children=[
                                # Civis
                                html.Div(
                                    style={"background": "#f8f9fa", "borderRadius": "10px", "padding": "14px", "borderLeft": f"4px solid {COR_PRIMARIA}"},
                                    children=[
                                        html.P("👥 Civis e moradores", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                        html.P(
                                            "Qualquer pessoa pode denunciar um animal em situação de risco "
                                            "pelo WhatsApp da DBEA: (16) 99170-8198 ou pelo telefone 0800-772-1789.",
                                            style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"},
                                        ),
                                    ],
                                ),
                                # ONGs e protetores
                                html.Div(
                                    style={"background": "#f8f9fa", "borderRadius": "10px", "padding": "14px", "borderLeft": f"4px solid {COR_SUCESSO}"},
                                    children=[
                                        html.P("🏠 ONGs e protetores independentes", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                        html.P(
                                            "Organizações como ONGs locais e protetores voluntários realizam "
                                            "rondas, monitoram redes sociais e respondem a chamados da comunidade. "
                                            "No Brasil, há mais de 184 mil animais sob tutela dessas redes "
                                            "(Instituto Pet Brasil, 2022).",
                                            style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"},
                                        ),
                                    ],
                                ),
                                # Bombeiros
                                html.Div(
                                    style={"background": "#f8f9fa", "borderRadius": "10px", "padding": "14px", "borderLeft": f"4px solid {COR_ALERTA}"},
                                    children=[
                                        html.P("🚒 Corpo de Bombeiros", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                        html.P(
                                            "Em Ribeirão Preto, resgate de animais é o 2º tipo de ocorrência "
                                            "mais atendido pelos Bombeiros — 70% são animais silvestres "
                                            "encontrados em vias públicas ou áreas urbanas "
                                            "(G1 / Bombeiros RP, abr/2024).",
                                            style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"},
                                        ),
                                    ],
                                ),
                                # Prefeitura / DBEA
                                html.Div(
                                    style={"background": "#f8f9fa", "borderRadius": "10px", "padding": "14px", "borderLeft": f"4px solid {COR_ROXO}"},
                                    children=[
                                        html.P("🏛️ Prefeitura — DBEA", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                        html.P(
                                            "A Divisão de Bem-Estar Animal da Prefeitura de Ribeirão Preto "
                                            "recebe denúncias, realiza resgates oficiais e encaminha os animais "
                                            "para abrigos, tratamento veterinário ou adoção.",
                                            style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"},
                                        ),
                                    ],
                                ),
                                # Redes sociais
                                html.Div(
                                    style={"background": "#f8f9fa", "borderRadius": "10px", "padding": "14px", "borderLeft": f"4px solid {COR_PERIGO}"},
                                    children=[
                                        html.P("📱 Redes sociais e apps", style={"fontWeight": "700", "margin": "0 0 6px", "fontSize": "13px"}),
                                        html.P(
                                            "Grupos no WhatsApp, Facebook e Instagram de protetores locais "
                                            "funcionam como canais de alerta rápido. Fotos e localizações "
                                            "compartilhadas mobilizam voluntários em minutos.",
                                            style={"fontSize": "12px", "color": COR_CINZA, "margin": "0"},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                # ── Gráficos — linha 1 ───────────────────────────────────
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "20px",
                        "marginBottom": "20px",
                    },
                    children=[
                        html.Div(
                            style={**ESTILO_CARD, "textAlign": "left"},
                            children=[
                                html.H3("Ocorrências por Bairro",
                                        style={"margin": "0 0 10px", "fontSize": "14px"}),
                                dcc.Graph(id="graf-bairros", config={"displayModeBar": False}),
                            ],
                        ),
                        html.Div(
                            style={**ESTILO_CARD, "textAlign": "left"},
                            children=[
                                html.H3("Ocorrências por Zona da Cidade",
                                        style={"margin": "0 0 10px", "fontSize": "14px"}),
                                dcc.Graph(id="graf-zonas", config={"displayModeBar": False}),
                            ],
                        ),
                    ],
                ),

                # ── Gráficos — linha 2 ───────────────────────────────────
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr 1fr",
                        "gap": "20px",
                        "marginBottom": "24px",
                    },
                    children=[
                        html.Div(
                            style={**ESTILO_CARD, "textAlign": "left"},
                            children=[
                                html.H3("Distribuição por Espécie",
                                        style={"margin": "0 0 10px", "fontSize": "14px"}),
                                dcc.Graph(id="graf-especies", config={"displayModeBar": False}),
                            ],
                        ),
                        html.Div(
                            style={**ESTILO_CARD, "textAlign": "left"},
                            children=[
                                html.H3("Status dos Animais",
                                        style={"margin": "0 0 10px", "fontSize": "14px"}),
                                dcc.Graph(id="graf-status", config={"displayModeBar": False}),
                            ],
                        ),
                        html.Div(
                            style={**ESTILO_CARD, "textAlign": "left"},
                            children=[
                                html.H3("Tipo de Situação",
                                        style={"margin": "0 0 10px", "fontSize": "14px"}),
                                dcc.Graph(id="graf-situacao", config={"displayModeBar": False}),
                            ],
                        ),
                    ],
                ),

                # ── Rodapé ───────────────────────────────────────────────
                html.Div(
                    style={"textAlign": "center", "marginTop": "32px",
                           "fontSize": "11px", "color": "#b2bec3"},
                    children=[
                        html.P(
                            "Fontes: IBGE API (servicodados.ibge.gov.br) · "
                            "CNJ — cnj.jus.br · Instituto Pet Brasil · "
                            "G1 Ribeirão Preto / Corpo de Bombeiros · "
                            "Prefeitura de Ribeirão Preto (ribeiraopreto.sp.gov.br)"
                        ),
                        html.P("Dashboard desenvolvido com Python + Dash + Plotly"),
                    ],
                ),
            ],
        ),
    ],
)


# -------------------------------------------------------
# Callbacks — atualizam tudo ao mudar qualquer filtro
# -------------------------------------------------------

@app.callback(
    Output("cards-kpi",      "children"),
    Output("graf-bairros",   "figure"),
    Output("graf-zonas",     "figure"),
    Output("graf-especies",  "figure"),
    Output("graf-status",    "figure"),
    Output("graf-situacao",  "figure"),
    Input("filtro-zona",     "value"),
    Input("filtro-bairro",   "value"),
    Input("filtro-especie",  "value"),
    Input("filtro-status",   "value"),
)
def atualizar(zona, bairro, especie, status):
    """
    Callback principal: aplica os filtros e regenera todos os
    componentes visuais do dashboard.
    """
    # ── Aplicar filtros ──────────────────────────────────────
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

    # ── Cards KPI ────────────────────────────────────────────
    cards = [
        card_kpi("📋", "Total de Ocorrências", total,         COR_PRIMARIA, "registros filtrados"),
        card_kpi("🚨", "Aguardando Resgate",   aguardando,    COR_PERIGO,   "necessitam ação imediata"),
        card_kpi("✅", "Resgatados",           resgatados,    COR_SUCESSO,  "animais salvos"),
        card_kpi("🏥", "Em Tratamento",        em_tratamento, COR_ALERTA,   "sob cuidados veterinários"),
        card_kpi("🏠", "Adotados",             adotados,      COR_ROXO,     "encontraram lar"),
    ]

    # ── Gráfico: ocorrências por bairro (barra horizontal) ───
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
        plot_bgcolor="white", paper_bgcolor="white",
        height=350,
    )
    fig_bairros.update_traces(
        hovertemplate="<b>%{y}</b><br>Ocorrências: %{x}<extra></extra>"
    )

    # ── Gráfico: ocorrências por zona (barra) ────────────────
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
        plot_bgcolor="white", paper_bgcolor="white",
        height=350,
    )
    fig_zonas.update_traces(
        textposition="outside",
        hovertemplate="<b>Zona %{x}</b><br>Ocorrências: %{y}<extra></extra>",
    )

    # ── Gráfico: distribuição por espécie (rosca) ────────────
    df_e = df.groupby("especie").size().reset_index(name="total")
    fig_especies = px.pie(
        df_e, names="especie", values="total",
        hole=0.42,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_especies.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", height=300,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    )
    fig_especies.update_traces(
        hovertemplate="<b>%{label}</b><br>%{value} animais (%{percent})<extra></extra>"
    )

    # ── Gráfico: status (barra horizontal colorida) ──────────
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
        plot_bgcolor="white", paper_bgcolor="white",
        height=300,
    )
    fig_status.update_traces(
        hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
    )

    # ── Gráfico: tipo de situação (rosca) ────────────────────
    df_sit = df.groupby("situacao").size().reset_index(name="total")
    fig_situacao = px.pie(
        df_sit, names="situacao", values="total",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_situacao.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", height=300,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
    )
    fig_situacao.update_traces(
        hovertemplate="<b>%{label}</b><br>%{value} casos (%{percent})<extra></extra>"
    )

    # ── Dados para a tabela ──────────────────────────────────
    tabela = df.drop(columns=["descricao"], errors="ignore").to_dict("records")

    return cards, fig_bairros, fig_zonas, fig_especies, fig_status, fig_situacao, tabela


# -------------------------------------------------------
# Ponto de entrada
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n🐾 Dashboard Resgate de Pets — Ribeirão Preto iniciando...")
    print("   Acesse: http://127.0.0.1:8050\n")
    app.run(debug=True)

