import os
import html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# CONFIGURAÇÃO GERAL
# =========================================================
st.set_page_config(
    page_title="Radar Canarinho",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

VERDE   = "#009C3B"
AMARELO = "#FFDF00"
AZUL    = "#002776"
VERDE2  = "#00B84A"
FUNDO   = "#F0F4F8"
TEXTO   = "#0D1B2A"
CINZA   = "#64748B"

# =========================================================
# CSS GLOBAL
# =========================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;700;900&family=Barlow:wght@400;500;600;700&display=swap');

* {{ box-sizing: border-box; }}

html, body, .stApp {{
    background: {FUNDO} !important;
    font-family: 'Barlow', sans-serif;
    color: {TEXTO} !important;
}}

/* ═══════════════════════════════════════════════════════
   RESET GLOBAL DE COR — desfaz o tema escuro do Streamlit
   no conteúdo principal. Sidebar é sobrescrita separadamente.
   ═══════════════════════════════════════════════════════ */

/* Todos os textos no bloco principal */
.main *:not(
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] *
) {{
    color: {TEXTO};
}}

/* Força especificidade máxima para os elementos mais problemáticos */
.main p,
.main span,
.main label,
.main div,
.main li,
.main a,
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
.block-container p,
.block-container span,
.block-container label,
.block-container div,
.block-container li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stText"] p,
[data-testid="stText"] span {{
    color: {TEXTO} !important;
}}

/* Headings: azul escuro */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    color: {AZUL} !important;
    font-family: 'Barlow Condensed', sans-serif !important;
}}

/* Labels dos widgets (selectbox, multiselect, radio…) */
[data-testid="stWidgetLabel"] *,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
.stSelectbox label,
.stMultiSelect label,
.stRadio label,
.stRadio span,
.stRadio p {{
    color: {TEXTO} !important;
    font-weight: 600 !important;
}}

/* Caption / legenda */
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {{
    color: {CINZA} !important;
}}

/* Opções dentro do radio button */
.stRadio [data-testid="stMarkdownContainer"] p {{
    color: {TEXTO} !important;
}}

/* ─── SIDEBAR: tudo branco ─────────────────────────── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {{
    color: white !important;
}}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {AZUL} 0%, #001550 100%) !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,.25) !important;
}}

/* ─── HEADER ──────────────────────────────────────── */
.header-wrap {{
    background: linear-gradient(135deg, {AZUL} 0%, #001955 60%, {VERDE} 100%);
    border-radius: 0 0 32px 32px;
    padding: 32px 40px 28px 40px;
    margin: -1rem -1rem 28px -1rem;
    position: relative;
    overflow: hidden;
}}
.header-wrap::before {{
    content:"";
    position:absolute; inset:0;
    background: repeating-linear-gradient(45deg, rgba(255,223,0,.04) 0px,
        rgba(255,223,0,.04) 2px, transparent 2px, transparent 20px);
    pointer-events:none;
}}
.header-title {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 52px; font-weight: 900;
    color: {AMARELO} !important;
    letter-spacing: -1px; line-height: 1;
    text-shadow: 0 2px 8px rgba(0,0,0,.3); position: relative;
}}
.header-sub {{
    font-size: 16px; font-weight: 500;
    color: rgba(255,255,255,.9) !important;
    margin-top: 6px; position: relative;
}}
.header-badge {{
    display: inline-block; background: {AMARELO};
    color: {AZUL} !important;
    font-weight: 900; font-size: 13px; padding: 4px 14px;
    border-radius: 999px; text-transform: uppercase;
    letter-spacing: 1px; margin-top: 10px;
}}

/* ─── MÉTRICAS ────────────────────────────────────── */
div[data-testid="stMetric"] {{
    background: white !important; border-radius: 16px; padding: 20px 22px;
    border-top: 5px solid {VERDE}; box-shadow: 0 4px 18px rgba(0,0,0,.07);
}}
div[data-testid="stMetricValue"] > div,
div[data-testid="stMetricValue"] * {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 34px !important; font-weight: 900 !important;
    color: {AZUL} !important;
}}
div[data-testid="stMetricLabel"] > div,
div[data-testid="stMetricLabel"] * {{
    font-size: 12px !important; font-weight: 700 !important;
    color: {CINZA} !important; text-transform: uppercase; letter-spacing: .5px;
}}
div[data-testid="stMetricDelta"] > div,
div[data-testid="stMetricDelta"] * {{
    color: {VERDE} !important; font-weight: 700 !important;
}}

/* ─── TABS ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: white !important; border-radius: 14px; padding: 6px; gap: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,.06);
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important; font-size: 16px !important;
    border-radius: 10px; padding: 10px 22px;
}}
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {{
    color: {CINZA} !important;
}}
.stTabs [aria-selected="true"] {{
    background: {VERDE} !important;
}}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {{
    color: white !important;
}}

/* ─── SECTION TITLES ──────────────────────────────── */
.section-title {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 26px; font-weight: 900;
    color: {AZUL} !important;
    border-left: 5px solid {AMARELO}; padding-left: 14px;
    margin: 24px 0 16px;
}}

/* ─── INSIGHT / NARRATIVE CARDS ───────────────────── */
.insight-card {{
    background: white !important; border-radius: 18px; padding: 22px 26px;
    margin-bottom: 16px; box-shadow: 0 4px 18px rgba(0,0,0,.07);
    border-left: 6px solid {VERDE};
}}
.insight-title {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 20px; font-weight: 900;
    color: {AZUL} !important; margin-bottom: 6px;
}}
.insight-text, .insight-text * {{
    font-size: 15px !important; color: {TEXTO} !important; line-height: 1.55;
}}

/* ─── JOGO CARDS ──────────────────────────────────── */
.jogo-card {{
    background: white !important; border-radius: 18px; padding: 20px 24px;
    margin-bottom: 14px; box-shadow: 0 4px 14px rgba(0,0,0,.07);
    border-left: 6px solid {VERDE};
}}
.jogo-meta, .jogo-meta * {{
    font-size: 13px; color: {CINZA} !important; font-weight: 600;
    margin-bottom: 10px; text-transform: uppercase; letter-spacing: .5px;
}}
.jogo-times {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
.jogo-time, .jogo-time * {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 24px; font-weight: 900; color: {AZUL} !important; flex: 1;
}}
.jogo-placar, .jogo-placar * {{
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 28px; font-weight: 900; color: {VERDE} !important;
    text-align: center; min-width: 80px;
    background: {FUNDO}; border-radius: 10px; padding: 6px 14px;
}}
.jogo-info, .jogo-info * {{
    font-size: 13px; color: {CINZA} !important; margin-top: 10px; font-weight: 500;
}}

/* ─── SELECT / INPUTS ─────────────────────────────── */
div[data-baseweb="select"] > div {{
    background: white !important; border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
}}
div[data-baseweb="select"] span,
div[data-baseweb="select"] p,
div[data-baseweb="select"] div {{
    color: {TEXTO} !important;
}}

/* Dropdown de opções */
ul[data-testid="stSelectboxVirtualDropdown"] li span,
ul[data-testid="stMultiSelectDropdown"] li span {{
    color: {TEXTO} !important;
}}

/* Tags selecionadas no multiselect */
[data-baseweb="tag"] span {{
    color: white !important;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# UTILITÁRIOS
# =========================================================
def limpar(v):
    return "" if pd.isna(v) else str(v).strip()

def esc(v):
    return html.escape(str(v)) if v else ""

def fmt(v):
    try:
        v = float(v)
    except Exception:
        return "0"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return str(int(v))

def fmt_int(v):
    try:
        return f"{int(float(v)):,}".replace(",", ".")
    except Exception:
        return "0"

def grupo_posicao(p):
    p = limpar(p).lower()
    if any(x in p for x in ["gol", "keeper", "goalkeeper", "gk"]):
        return "Goleiro"
    if any(x in p for x in ["defesa", "zagueiro", "lateral", "defender", "back"]):
        return "Defesa"
    if any(x in p for x in ["meio", "volante", "meia", "midfield"]):
        return "Meio-campo"
    if any(x in p for x in ["ataque", "atacante", "ponta", "centroavante", "forward", "striker", "wing"]):
        return "Ataque"
    return "Outros"

def estilo_fig(fig, titulo=None):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Barlow, sans-serif", color=TEXTO, size=14),
        title_font=dict(family="Barlow Condensed, sans-serif", color=AZUL, size=20),
        legend=dict(font=dict(size=13), bgcolor="rgba(255,255,255,.9)"),
        xaxis=dict(gridcolor="#EEF2F7", tickfont=dict(size=13)),
        yaxis=dict(gridcolor="#EEF2F7", tickfont=dict(size=13)),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    if titulo:
        fig.update_layout(title=titulo)
    return fig

# =========================================================
# CARREGAMENTO
# =========================================================
@st.cache_data(show_spinner=False)
def carregar():
    # Tenta vários nomes de arquivo
    candidatos = [
        "atletas_prelista_55_ficticio_realista.xlsx",
        "atletas_prelista_55_ficticio_realista__1_.xlsx",
        "atletas.xlsx",
    ]
    # Também busca na pasta uploads (ambiente de desenvolvimento)
    for prefix in ["", "/mnt/user-data/uploads/"]:
        for nome in candidatos:
            path = prefix + nome
            if os.path.exists(path):
                xl = pd.ExcelFile(path)
                
                # base_produtocopa pode estar vazia — tenta ler de qualquer jeito
                try:
                    base = pd.read_excel(path, sheet_name="base_produtocopa")
                except Exception:
                    base = pd.DataFrame()

                if "redes_ficticias" in xl.sheet_names:
                    redes = pd.read_excel(path, sheet_name="redes_ficticias")
                else:
                    redes = pd.DataFrame()

                return base, redes

    st.error("Arquivo Excel não encontrado. Coloque o arquivo .xlsx na mesma pasta do app.py.")
    st.stop()

base_raw, redes_raw = carregar()

# =========================================================
# PREPARAÇÃO
# =========================================================
redes = redes_raw.copy()

# Renomeia colunas com nomes estimados
rename_map = {
    "Curtidas estimadas": "Curtidas",
    "Comentários estimados": "Comentários",
    "Compartilhamentos estimados": "Compartilhamentos",
    "Visualizações estimadas": "Visualizações",
    "Interações estimadas": "Interações",
    "Posts estimados": "Posts",
}
redes = redes.rename(columns={k: v for k, v in rename_map.items() if k in redes.columns})

# Garante colunas numéricas
for col in ["Seguidores", "Crescimento 30d", "Interações", "Curtidas",
            "Comentários", "Compartilhamentos", "Visualizações", "Posts"]:
    if col not in redes.columns:
        redes[col] = 0
    redes[col] = pd.to_numeric(redes[col], errors="coerce").fillna(0)

# Normaliza posição
if "Posição" not in redes.columns and "Posicao" in redes.columns:
    redes.rename(columns={"Posicao": "Posição"}, inplace=True)
if "Posição" not in redes.columns:
    redes["Posição"] = ""

redes["Grupo Posição"] = redes["Posição"].apply(grupo_posicao)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="header-wrap">
    <div class="header-title">🇧🇷 RADAR CANARINHO</div>
    <div class="header-sub">Inteligência digital da Seleção Brasileira · Pré-lista para a Copa</div>
    <span class="header-badge">55 Pré-convocados · Dados fictícios realistas</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR — FILTROS
# =========================================================
with st.sidebar:
    st.markdown("### 🎯 Filtros")
    st.divider()

    grupos = sorted(redes["Grupo Posição"].dropna().unique())
    clubes = sorted(redes["Clube"].dropna().unique())
    redes_list = sorted(redes["Rede"].dropna().unique())

    f_grupos = st.multiselect("Posição", grupos, default=grupos)
    f_clubes = st.multiselect("Clube", clubes, default=clubes)
    f_redes = st.multiselect("Rede social", redes_list, default=redes_list)

    st.divider()
    st.caption("Dados fictícios realistas para prototipação. Futuramente via Supermetrics.")

# =========================================================
# DADOS FILTRADOS
# =========================================================
df = redes[
    redes["Grupo Posição"].isin(f_grupos) &
    redes["Clube"].isin(f_clubes) &
    redes["Rede"].isin(f_redes)
].copy()

# Resumo por jogador
resumo = (
    df.groupby(["Atleta", "Clube", "Grupo Posição"], as_index=False)
    .agg(
        Seguidores=("Seguidores", "sum"),
        Crescimento=("Crescimento 30d", "sum"),
        Interações=("Interações", "sum"),
        Curtidas=("Curtidas", "sum"),
        Comentários=("Comentários", "sum"),
        Visualizações=("Visualizações", "sum"),
    )
    .sort_values("Seguidores", ascending=False)
)

# =========================================================
# ABAS
# =========================================================
aba_exec, aba_geral, aba_redes_tab, aba_esc, aba_comp, aba_copa = st.tabs([
    "📌 Resumo Executivo",
    "📊 Dashboard Geral",
    "📱 Redes Sociais",
    "⚽ Escalação Digital",
    "🔍 Comparador",
    "🏆 Partidas da Copa",
])

# =========================================================
# ABA 1 — RESUMO EXECUTIVO
# =========================================================
with aba_exec:
    if resumo.empty:
        st.warning("Sem dados com os filtros atuais.")
    else:
        lider = resumo.iloc[0]
        lider_cresc = resumo.sort_values("Crescimento", ascending=False).iloc[0]
        lider_inter = resumo.sort_values("Interações", ascending=False).iloc[0]
        rede_dom = df.groupby("Rede")["Seguidores"].sum().idxmax()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🥇 Líder de Seguidores", lider["Atleta"], fmt(lider["Seguidores"]))
        c2.metric("📈 Maior Crescimento 30d", lider_cresc["Atleta"], f"+{fmt(lider_cresc['Crescimento'])}")
        c3.metric("🔥 Maior Engajamento", lider_inter["Atleta"], fmt(lider_inter["Interações"]) + " interações")
        c4.metric("📱 Rede Dominante", rede_dom, "maior base")

        st.markdown('<div class="section-title">Narrativas Automáticas</div>', unsafe_allow_html=True)

        pos_top = resumo.groupby("Grupo Posição")["Interações"].sum().idxmax()
        rede_cresc = df.groupby("Rede")["Crescimento 30d"].sum().idxmax()

        narrativas = [
            ("🔥 Liderança Digital",
             f"<strong>{esc(lider['Atleta'])}</strong> lidera em seguidores somados nas redes monitoradas, "
             f"com <strong>{fmt_int(lider['Seguidores'])}</strong> seguidores no recorte atual."),
            ("📈 Momento de Crescimento",
             f"<strong>{esc(lider_cresc['Atleta'])}</strong> é o maior nome em crescimento no período, "
             f"com alta estimada de <strong>{fmt_int(lider_cresc['Crescimento'])}</strong> novos seguidores em 30 dias."),
            ("⚽ Força por Posição",
             f"O grupo de <strong>{esc(pos_top)}</strong> concentra o maior volume de interações digitais, "
             f"indicando maior tração de audiência nesse setor da pré-lista."),
            ("📱 Rede Dominante",
             f"<strong>{esc(rede_dom)}</strong> concentra a maior base de seguidores no recorte atual. "
             f"Em crescimento recente, o destaque vai para <strong>{esc(rede_cresc)}</strong>."),
            ("📰 Pauta Sugerida",
             f"Uma pauta possível é comparar a força consolidada de <strong>{esc(lider['Atleta'])}</strong> "
             f"com o momentum recente de <strong>{esc(lider_cresc['Atleta'])}</strong> — alcance estabelecido vs. ascensão em curso."),
        ]

        col_n1, col_n2 = st.columns(2)
        for i, (titulo, texto) in enumerate(narrativas):
            col = col_n1 if i % 2 == 0 else col_n2
            with col:
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">{titulo}</div>
                    <div class="insight-text">{texto}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🌡️ Termômetro Digital</div>', unsafe_allow_html=True)

        def termometro(row):
            if row["Crescimento"] > 100_000:
                return "🔥 Em Alta"
            elif row["Crescimento"] < 0:
                return "📉 Em Queda"
            elif row["Interações"] > 500_000:
                return "👀 Em Observação"
            return "🟡 Estável"

        termo = resumo.copy()
        termo["Status"] = termo.apply(termometro, axis=1)

        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            dist = termo["Status"].value_counts().reset_index()
            dist.columns = ["Status", "Qtd"]
            fig_t = px.pie(dist, names="Status", values="Qtd",
                           color_discrete_sequence=[VERDE, AMARELO, AZUL, "#EF4444"],
                           hole=0.45)
            fig_t = estilo_fig(fig_t, "Status dos atletas")
            fig_t.update_traces(textfont_size=14, textfont_family="Barlow Condensed")
            st.plotly_chart(fig_t, use_container_width=True)

        with col_t2:
            st.dataframe(
                termo[["Atleta", "Clube", "Grupo Posição", "Status", "Seguidores", "Crescimento"]]
                .sort_values("Seguidores", ascending=False)
                .reset_index(drop=True),
                use_container_width=True, height=380
            )

        st.markdown('<div class="section-title">🏅 Ranking de Impacto Digital</div>', unsafe_allow_html=True)
        top12 = resumo.head(12).copy()
        top12["Impacto"] = (
            top12["Seguidores"] * 0.4 +
            top12["Interações"] * 0.35 +
            top12["Crescimento"] * 0.25
        )
        top12 = top12.sort_values("Impacto", ascending=True)
        fig_rank = px.bar(
            top12, x="Impacto", y="Atleta", orientation="h",
            text="Atleta",
            color="Impacto",
            color_continuous_scale=[AMARELO, VERDE, AZUL]
        )
        fig_rank.update_traces(
            textposition="inside", textfont_color="white",
            textfont_size=14, textfont_family="Barlow Condensed"
        )
        fig_rank.update_layout(yaxis={"visible": False}, showlegend=False,
                                coloraxis_showscale=False)
        fig_rank = estilo_fig(fig_rank, "Top 12 — Impacto Digital Agregado")
        st.plotly_chart(fig_rank, use_container_width=True)

# =========================================================
# ABA 2 — DASHBOARD GERAL
# =========================================================
with aba_geral:
    st.markdown('<div class="section-title">Visão Geral da Pré-lista</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Atletas", df["Atleta"].nunique())
    c2.metric("Clubes", df["Clube"].nunique())
    c3.metric("Seguidores Totais", fmt(df["Seguidores"].sum()))
    c4.metric("Interações Totais", fmt(df["Interações"].sum()))

    col1, col2 = st.columns(2)

    with col1:
        pos_data = (
            df[["Atleta", "Grupo Posição"]].drop_duplicates()
            ["Grupo Posição"].value_counts().reset_index()
        )
        pos_data.columns = ["Posição", "Qtd"]
        fig_pos = px.bar(pos_data, x="Posição", y="Qtd",
                         color="Posição", text="Qtd",
                         color_discrete_sequence=[VERDE, AMARELO, AZUL, VERDE2],
                         title="Jogadores por Posição")
        fig_pos.update_traces(textposition="inside", textfont_color="white",
                              textfont_family="Barlow Condensed", textfont_size=16)
        fig_pos = estilo_fig(fig_pos)
        st.plotly_chart(fig_pos, use_container_width=True)

    with col2:
        rede_data = df.groupby("Rede")["Seguidores"].sum().reset_index().sort_values("Seguidores", ascending=False)
        fig_rede = px.bar(rede_data, x="Rede", y="Seguidores",
                          color="Rede", text="Seguidores",
                          color_discrete_sequence=[VERDE, AMARELO, AZUL, VERDE2],
                          title="Seguidores por Rede Social")
        fig_rede.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                               textfont_color="white", textfont_family="Barlow Condensed")
        fig_rede = estilo_fig(fig_rede)
        st.plotly_chart(fig_rede, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        top_seg = resumo.sort_values("Seguidores", ascending=False).head(12)
        fig_ts = px.bar(top_seg, x="Seguidores", y="Atleta", orientation="h",
                        text="Seguidores",
                        color="Seguidores", color_continuous_scale=[AMARELO, VERDE, AZUL],
                        title="Top 12 por Seguidores")
        fig_ts.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                             textfont_color="white", textfont_family="Barlow Condensed")
        fig_ts.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        fig_ts = estilo_fig(fig_ts)
        st.plotly_chart(fig_ts, use_container_width=True)

    with col4:
        top_cresc = resumo.sort_values("Crescimento", ascending=False).head(12)
        fig_tc = px.bar(top_cresc, x="Crescimento", y="Atleta", orientation="h",
                        text="Crescimento",
                        color="Crescimento", color_continuous_scale=[AMARELO, VERDE, AZUL],
                        title="Top 12 por Crescimento 30d")
        fig_tc.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                             textfont_color="white", textfont_family="Barlow Condensed")
        fig_tc.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        fig_tc = estilo_fig(fig_tc)
        st.plotly_chart(fig_tc, use_container_width=True)

    st.markdown('<div class="section-title">Mapa: Seguidores × Crescimento</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(
        resumo, x="Seguidores", y="Crescimento",
        size="Interações", color="Grupo Posição",
        hover_name="Atleta",
        hover_data={"Clube": True, "Seguidores": True, "Crescimento": True},
        color_discrete_sequence=[VERDE, AMARELO, AZUL, VERDE2],
        title="Mapa de posicionamento digital — tamanho = interações",
        size_max=50,
        labels={"Seguidores": "Seguidores totais", "Crescimento": "Crescimento 30d"}
    )
    fig_sc = estilo_fig(fig_sc)
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<div class="section-title">Tabela Geral</div>', unsafe_allow_html=True)
    st.dataframe(resumo.reset_index(drop=True), use_container_width=True)

# =========================================================
# ABA 3 — REDES SOCIAIS
# =========================================================
with aba_redes_tab:
    redes_disp = [r for r in ["Instagram", "TikTok", "X", "Facebook"] if r in df["Rede"].unique()]
    sub_abas = st.tabs(redes_disp)

    for sub_aba, rede in zip(sub_abas, redes_disp):
        with sub_aba:
            dr = df[df["Rede"] == rede].copy()
            res_r = (
                dr.groupby(["Atleta", "Clube", "Grupo Posição"], as_index=False)
                .agg(Seguidores=("Seguidores", "sum"),
                     Crescimento=("Crescimento 30d", "sum"),
                     Interações=("Interações", "sum"),
                     Visualizações=("Visualizações", "sum"))
                .sort_values("Seguidores", ascending=False)
            )

            if res_r.empty:
                st.warning(f"Sem dados para {rede}.")
                continue

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Atletas", res_r["Atleta"].nunique())
            c2.metric("Seguidores", fmt(res_r["Seguidores"].sum()))
            c3.metric("Crescimento 30d", f"+{fmt(res_r['Crescimento'].sum())}")
            c4.metric("Interações", fmt(res_r["Interações"].sum()))

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                t10 = res_r.head(10).sort_values("Seguidores")
                fig_r1 = px.bar(t10, x="Seguidores", y="Atleta", orientation="h",
                                text="Seguidores", color="Seguidores",
                                color_continuous_scale=[AMARELO, VERDE, AZUL],
                                title=f"Top 10 no {rede} — Seguidores")
                fig_r1.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                                     textfont_color="white", textfont_family="Barlow Condensed")
                fig_r1.update_layout(coloraxis_showscale=False)
                fig_r1 = estilo_fig(fig_r1)
                st.plotly_chart(fig_r1, use_container_width=True)

            with col_r2:
                t10c = res_r.sort_values("Crescimento", ascending=False).head(10).sort_values("Crescimento")
                fig_r2 = px.bar(t10c, x="Crescimento", y="Atleta", orientation="h",
                                text="Crescimento", color="Crescimento",
                                color_continuous_scale=[AMARELO, VERDE, AZUL],
                                title=f"Top 10 no {rede} — Crescimento 30d")
                fig_r2.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                                     textfont_color="white", textfont_family="Barlow Condensed")
                fig_r2.update_layout(coloraxis_showscale=False)
                fig_r2 = estilo_fig(fig_r2)
                st.plotly_chart(fig_r2, use_container_width=True)

            lider_r = res_r.iloc[0]
            alta_r = res_r.sort_values("Crescimento", ascending=False).iloc[0]
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">📊 Leitura editorial — {esc(rede)}</div>
                <div class="insight-text">
                    No <strong>{esc(rede)}</strong>, <strong>{esc(lider_r['Atleta'])}</strong> lidera em seguidores
                    com <strong>{fmt_int(lider_r['Seguidores'])}</strong> perfis acompanhando.
                    O maior crescimento recente no {esc(rede)} é de <strong>{esc(alta_r['Atleta'])}</strong>,
                    que ganhou <strong>{fmt_int(alta_r['Crescimento'])}</strong> novos seguidores em 30 dias.
                </div>
            </div>""", unsafe_allow_html=True)

            st.dataframe(res_r.reset_index(drop=True), use_container_width=True)

# =========================================================
# ABA 4 — ESCALAÇÃO DIGITAL
# =========================================================
with aba_esc:
    st.markdown('<div class="section-title">Escalação Digital 4-3-3</div>', unsafe_allow_html=True)

    modo = st.radio("Critério da escalação", ["Todas as redes"] + redes_disp, horizontal=True)

    df_e = df if modo == "Todas as redes" else df[df["Rede"] == modo]

    rank_e = (
        df_e.groupby(["Atleta", "Clube", "Grupo Posição"], as_index=False)
        .agg(Seguidores=("Seguidores", "sum"), Interações=("Interações", "sum"))
        .sort_values("Seguidores", ascending=False)
        .reset_index(drop=True)
    )

    # ── Mapa de escudos por clube (SVG flags via Sofascore / imagens públicas estáveis)
    # Usamos a API da TheSportsDB somente para os clubes necessários, com cache agressivo
    @st.cache_data(show_spinner=False, ttl=86400 * 7)
    def buscar_escudo_clube(clube):
        """Busca escudo do clube via TheSportsDB. Retorna URL ou string vazia."""
        if not clube or clube.strip() == "":
            return ""
        try:
            r = requests.get(
                "https://www.thesportsdb.com/api/v1/json/123/searchteams.php",
                params={"t": clube}, timeout=8
            )
            if r.status_code == 200:
                times = r.json().get("teams") or []
                if times:
                    return times[0].get("strBadge") or times[0].get("strLogo") or ""
        except Exception:
            pass
        return ""

    # Busca escudos apenas para os clubes na escalação (evita chamar para todos)
    clubes_esc = rank_e["Clube"].unique()
    escudos_map = {}
    for clube in clubes_esc:
        escudos_map[clube] = buscar_escudo_clube(clube)

    rank_e["Escudo Time URL"] = rank_e["Clube"].map(escudos_map).fillna("")

    # Foto do jogador: TheSportsDB por nome
    @st.cache_data(show_spinner=False, ttl=86400 * 7)
    def buscar_foto_jogador(nome):
        """Busca foto do jogador via TheSportsDB. Retorna URL ou string vazia."""
        if not nome or nome.strip() == "":
            return ""
        try:
            r = requests.get(
                "https://www.thesportsdb.com/api/v1/json/123/searchplayers.php",
                params={"p": nome}, timeout=8
            )
            if r.status_code == 200:
                jogadores = r.json().get("player") or []
                if jogadores:
                    p = jogadores[0]
                    return p.get("strCutout") or p.get("strThumb") or ""
        except Exception:
            pass
        return ""

    # Busca fotos apenas dos jogadores que vão para a escalação (top por posição)
    def pegar(grupo, qtd):
        sub = rank_e[rank_e["Grupo Posição"] == grupo].head(qtd).to_dict("records")
        while len(sub) < qtd:
            sub.append(None)
        return sub

    gol  = pegar("Goleiro", 1)
    def_ = pegar("Defesa", 4)
    mei  = pegar("Meio-campo", 3)
    ata  = pegar("Ataque", 3)

    todos_esc_jogadores = [j for grupo in [gol, def_, mei, ata] for j in grupo if j is not None]
    fotos_map = {}
    for j in todos_esc_jogadores:
        nome = j["Atleta"]
        fotos_map[nome] = buscar_foto_jogador(nome)

    max_seg = rank_e["Seguidores"].max() or 1

    def card(j, pos):
        if j is None:
            return f"""<div class="card-fifa">
            <div class="topo-f"><span class="pos-f">{pos}</span><span class="ovr-f">--</span></div>
            <div class="foto-wrap"><div class="foto-vazia">👤</div></div>
            <div class="nome-f">Vaga</div>
            <div class="clube-row"><span class="clube-f">—</span></div>
            <div class="stat-f">—</div></div>"""

        ovr = int(70 + (j["Seguidores"] / max_seg) * 29)
        foto = fotos_map.get(j["Atleta"], "")
        escudo = j.get("Escudo Time URL", "") or ""

        if foto:
            foto_html = f'<img class="foto-f" src="{esc(foto)}" onerror="this.parentElement.innerHTML=\'<div class=foto-vazia>👤</div>\'"/>'
        else:
            foto_html = '<div class="foto-vazia">👤</div>'

        if escudo:
            escudo_html = f'<img class="escudo-f" src="{esc(escudo)}" onerror="this.outerHTML=\'<span class=escudo-txt>{esc(j["Clube"][:3].upper())}</span>\'"/>'
        else:
            escudo_html = f'<span class="escudo-txt">{esc(j["Clube"][:3].upper())}</span>'

        return f"""
        <div class="card-fifa">
            <div class="topo-f">
                <span class="pos-f">{esc(pos)}</span>
                <span class="ovr-f">{ovr}</span>
            </div>
            <div class="foto-wrap">{foto_html}</div>
            <div class="nome-f">{esc(j['Atleta'])}</div>
            <div class="clube-row">
                {escudo_html}
                <span class="clube-f">{esc(j['Clube'])}</span>
            </div>
            <div class="stat-f">{fmt(j['Seguidores'])} seg.<br>{fmt(j['Interações'])} inter.</div>
        </div>"""

    def linha_html(jogadores, posicoes):
        cards = "".join(card(j, p) for j, p in zip(jogadores, posicoes))
        return f'<div class="linha-campo">{cards}</div>'

    html_esc = f"""
    <html><head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&family=Barlow:wght@600&display=swap');
    body{{margin:0;background:transparent;font-family:'Barlow',sans-serif;}}
    .campo{{
        width:100%;max-width:1100px;margin:0 auto;
        background: linear-gradient(180deg,#0a7c37 0%,#0d9440 25%,#0a7c37 50%,#0d9440 75%,#0a7c37 100%);
        border-radius:28px;padding:32px 24px;
        border:6px solid rgba(255,255,255,.7);
        box-shadow:0 20px 50px rgba(0,0,0,.35);
        position:relative;overflow:hidden;
    }}
    .campo::before{{
        content:"";position:absolute;inset:16px;
        border:3px solid rgba(255,255,255,.5);border-radius:16px;pointer-events:none;
    }}
    .linha-campo{{display:flex;justify-content:center;gap:18px;margin:20px 0;position:relative;z-index:1;flex-wrap:wrap;}}
    .card-fifa{{
        width:148px;
        background:linear-gradient(145deg,#f7d060,#fff8d0,#e8b830);
        border-radius:20px;padding:12px 10px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,.35);
        border:3px solid rgba(240,200,60,.8);
        position:relative;
    }}
    .card-fifa::before{{
        content:"";position:absolute;inset:5px;
        border:1px solid rgba(160,100,0,.25);border-radius:14px;pointer-events:none;
    }}
    .topo-f{{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}}
    .pos-f{{font-family:'Barlow Condensed';font-size:17px;font-weight:900;color:#002776;}}
    .ovr-f{{font-family:'Barlow Condensed';font-size:26px;font-weight:900;color:#002776;}}
    .foto-wrap{{width:80px;height:80px;border-radius:50%;margin:4px auto;
        border:3px solid #002776;overflow:hidden;
        display:flex;align-items:center;justify-content:center;background:#fff;}}
    .foto-f{{width:80px;height:80px;object-fit:cover;display:block;border-radius:50%;}}
    .foto-vazia{{font-size:32px;line-height:1;}}
    .nome-f{{
        font-family:'Barlow Condensed';font-size:13px;font-weight:900;
        color:#0d1b2a;margin-top:6px;min-height:34px;
        display:flex;align-items:center;justify-content:center;
        word-break:break-word;line-height:1.2;
    }}
    .clube-row{{display:flex;align-items:center;justify-content:center;gap:5px;margin-top:4px;}}
    .escudo-f{{width:20px;height:20px;object-fit:contain;flex-shrink:0;}}
    .escudo-txt{{background:#002776;color:white;font-size:8px;font-weight:900;
        padding:2px 4px;border-radius:4px;}}
    .clube-f{{font-size:11px;font-weight:700;color:#555;}}
    .stat-f{{font-family:'Barlow Condensed';font-size:11px;font-weight:800;
        color:#002776;margin-top:7px;line-height:1.5;}}
    </style>
    </head><body>
    <div class="campo">
        {linha_html(ata, ["ATA","ATA","ATA"])}
        {linha_html(mei, ["MEI","MEI","MEI"])}
        {linha_html(def_, ["DEF","DEF","DEF","DEF"])}
        {linha_html(gol, ["GOL"])}
    </div>
    </body></html>"""

    components.html(html_esc, height=1200, scrolling=True)

    _linhas_esc = [j for grupo in [gol, def_, mei, ata] for j in grupo if j is not None]
    if _linhas_esc:
        todos_esc = pd.DataFrame(_linhas_esc)
        _show_cols = [c for c in ["Atleta","Clube","Grupo Posição","Seguidores","Interações"] if c in todos_esc.columns]
        st.markdown('<div class="section-title">Tabela da Escalação</div>', unsafe_allow_html=True)
        st.dataframe(todos_esc[_show_cols].reset_index(drop=True), use_container_width=True)

# =========================================================
# ABA 5 — COMPARADOR
# =========================================================
with aba_comp:
    st.markdown('<div class="section-title">Comparador de Jogadores</div>', unsafe_allow_html=True)

    if resumo.empty:
        st.warning("Sem dados.")
    else:
        nomes = sorted(resumo["Atleta"].unique())
        col_a, col_b = st.columns(2)
        with col_a:
            j1 = st.selectbox("🔵 Jogador A", nomes, index=0)
        with col_b:
            j2 = st.selectbox("🟡 Jogador B", nomes, index=min(1, len(nomes)-1))

        a = resumo[resumo["Atleta"] == j1].iloc[0] if j1 in resumo["Atleta"].values else None
        b = resumo[resumo["Atleta"] == j2].iloc[0] if j2 in resumo["Atleta"].values else None

        if a is not None and b is not None:
            col_c1, col_cc, col_c2 = st.columns([5, 1, 5])

            metricas = [(label, key) for label, key in [
                ("Seguidores", "Seguidores"),
                ("Crescimento 30d", "Crescimento"),
                ("Interações", "Interações"),
                ("Visualizações", "Visualizações"),
            ] if key in a.index]

            def barra_comp(val_a, val_b, label):
                total = val_a + val_b if (val_a + val_b) > 0 else 1
                pct_a = int(val_a / total * 100)
                pct_b = 100 - pct_a
                return (
                    f'<div class="bar-row">'
                    f'<div class="bar-label">{label}</div>'
                    f'<div class="bar-line">'
                    f'<span class="bar-val bar-val-r">{fmt(val_a)}</span>'
                    f'<div class="bar-track">'
                    f'<div class="bar-a" style="width:{pct_a}%"></div>'
                    f'<div class="bar-b" style="width:{pct_b}%"></div>'
                    f'</div>'
                    f'<span class="bar-val">{fmt(val_b)}</span>'
                    f'</div></div>'
                )

            with col_c1:
                st.markdown(f"""
                <div style="background:white;border-radius:18px;padding:24px;box-shadow:0 4px 18px rgba(0,0,0,.07);border-top:5px solid {VERDE};">
                    <div style="font-family:'Barlow Condensed';font-size:26px;font-weight:900;color:{AZUL};">🔵 {esc(j1)}</div>
                    <div style="font-size:14px;color:{CINZA};font-weight:600;">{esc(a['Clube'])} · {esc(a['Grupo Posição'])}</div>
                    <div style="margin-top:16px;font-family:'Barlow Condensed';font-size:40px;font-weight:900;color:{VERDE};">{fmt(a['Seguidores'])}</div>
                    <div style="font-size:12px;color:{CINZA};text-transform:uppercase;">seguidores totais</div>
                </div>""", unsafe_allow_html=True)

            with col_cc:
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:center;height:100%;
                    font-family:'Barlow Condensed';font-size:28px;font-weight:900;color:{CINZA};">VS</div>
                """, unsafe_allow_html=True)

            with col_c2:
                st.markdown(f"""
                <div style="background:white;border-radius:18px;padding:24px;box-shadow:0 4px 18px rgba(0,0,0,.07);border-top:5px solid {AMARELO};">
                    <div style="font-family:'Barlow Condensed';font-size:26px;font-weight:900;color:{AZUL};">🟡 {esc(j2)}</div>
                    <div style="font-size:14px;color:{CINZA};font-weight:600;">{esc(b['Clube'])} · {esc(b['Grupo Posição'])}</div>
                    <div style="margin-top:16px;font-family:'Barlow Condensed';font-size:40px;font-weight:900;color:{AMARELO};">{fmt(b['Seguidores'])}</div>
                    <div style="font-size:12px;color:{CINZA};text-transform:uppercase;">seguidores totais</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            bhtml_items = "".join(
                barra_comp(float(a[met]), float(b[met]), label)
                for label, met in metricas
            )
            comp_widget = f"""
            <html><head>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&family=Barlow:wght@600&display=swap');
            body{{margin:0;padding:0;background:transparent;font-family:'Barlow',sans-serif;}}
            .comp-wrap{{background:white;border-radius:18px;padding:24px 28px;box-shadow:0 4px 18px rgba(0,0,0,.07);}}
            .comp-title{{font-family:'Barlow Condensed';font-size:22px;font-weight:900;color:#002776;margin-bottom:16px;}}
            .bar-row{{margin:12px 0;}}
            .bar-label{{font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px;}}
            .bar-line{{display:flex;gap:6px;align-items:center;}}
            .bar-val{{font-family:'Barlow Condensed';font-size:16px;font-weight:900;color:#002776;min-width:56px;}}
            .bar-val-r{{text-align:right;}}
            .bar-track{{flex:1;display:flex;height:24px;border-radius:12px;overflow:hidden;}}
            .bar-a{{background:#009C3B;}}
            .bar-b{{background:#FFDF00;}}
            </style></head><body>
            <div class="comp-wrap">
                <div class="comp-title">🔵 {esc(j1)} <span style="color:#64748B;font-size:16px">vs</span> {esc(j2)} 🟡</div>
                {bhtml_items}
            </div></body></html>"""
            components.html(comp_widget, height=60 + len(metricas)*70, scrolling=False)

            st.markdown('<div class="section-title">Seguidores por Rede</div>', unsafe_allow_html=True)
            comp_long = df[df["Atleta"].isin([j1, j2])].copy()
            fig_cr = px.bar(comp_long, x="Rede", y="Seguidores", color="Atleta",
                            barmode="group", text="Seguidores",
                            color_discrete_sequence=[VERDE, AMARELO],
                            title="Comparação por rede social")
            fig_cr.update_traces(texttemplate="%{text:.2s}", textposition="inside",
                                 textfont_color="white", textfont_family="Barlow Condensed")
            fig_cr = estilo_fig(fig_cr)
            st.plotly_chart(fig_cr, use_container_width=True)

            venc = j1 if a["Seguidores"] > b["Seguidores"] else j2
            outro = j2 if venc == j1 else j1
            cresc_venc = j1 if a["Crescimento"] > b["Crescimento"] else j2
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Leitura Comparativa</div>
                <div class="insight-text">
                    Em seguidores totais, <strong>{esc(venc)}</strong> aparece à frente de <strong>{esc(outro)}</strong>
                    no recorte selecionado. Já em crescimento recente,
                    <strong>{esc(cresc_venc)}</strong> tem o maior momentum dos dois.
                </div>
            </div>""", unsafe_allow_html=True)

# =========================================================
# ABA 6 — COPA
# =========================================================
@st.cache_data(show_spinner=False, ttl=1800)
def buscar_copa():
    try:
        key = st.secrets["FOOTBALL_DATA_KEY"]
    except Exception:
        return pd.DataFrame(), "Chave FOOTBALL_DATA_KEY não configurada nos secrets."

    try:
        r = requests.get(
            "https://api.football-data.org/v4/competitions/WC/matches",
            headers={"X-Auth-Token": key}, timeout=15
        )
        if r.status_code != 200:
            return pd.DataFrame(), f"Erro {r.status_code}: {r.text}"

        linhas = []
        for j in r.json().get("matches", []):
            ft = (j.get("score") or {}).get("fullTime") or {}
            linhas.append({
                "Data UTC": j.get("utcDate"),
                "Status": j.get("status"),
                "Fase": j.get("stage"),
                "Rodada": j.get("matchday"),
                "Grupo": j.get("group"),
                "Mandante": (j.get("homeTeam") or {}).get("name"),
                "Visitante": (j.get("awayTeam") or {}).get("name"),
                "Gols M": ft.get("home"),
                "Gols V": ft.get("away"),
            })

        df_c = pd.DataFrame(linhas)
        if not df_c.empty and "Data UTC" in df_c.columns:
            dt = pd.to_datetime(df_c["Data UTC"], errors="coerce", utc=True)
            df_c["Data BR"] = dt.dt.tz_convert("America/Sao_Paulo").dt.strftime("%d/%m/%Y %H:%M")
        return df_c, ""
    except Exception as e:
        return pd.DataFrame(), f"Erro: {e}"

with aba_copa:
    st.markdown('<div class="section-title">Partidas da Copa do Mundo</div>', unsafe_allow_html=True)
    st.caption("Dados via football-data.org. Requer chave configurada nos secrets.")

    if st.button("🔄 Atualizar partidas"):
        st.cache_data.clear()

    df_c, err_c = buscar_copa()

    if err_c:
        st.warning(err_c)
        st.info("Configure `FOOTBALL_DATA_KEY` nos secrets do Streamlit para ver as partidas.")

    if not df_c.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Partidas", len(df_c))
        c2.metric("Fases", df_c["Fase"].nunique())
        c3.metric("Status", df_c["Status"].nunique())

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fase_sel = st.selectbox("Fase", ["Todas"] + sorted(df_c["Fase"].dropna().unique().tolist()))
        with col_f2:
            status_sel = st.selectbox("Status", ["Todos"] + sorted(df_c["Status"].dropna().unique().tolist()))

        df_cf = df_c.copy()
        if fase_sel != "Todas":
            df_cf = df_cf[df_cf["Fase"] == fase_sel]
        if status_sel != "Todos":
            df_cf = df_cf[df_cf["Status"] == status_sel]

        for _, j in df_cf.iterrows():
            gm, gv = j.get("Gols M"), j.get("Gols V")
            placar = f"{int(gm)} × {int(gv)}" if pd.notna(gm) and pd.notna(gv) else "× "
            st.markdown(f"""
            <div class="jogo-card">
                <div class="jogo-meta">{limpar(j.get("Data BR",""))} · {limpar(j.get("Status",""))}</div>
                <div class="jogo-times">
                    <div class="jogo-time">{esc(j.get("Mandante",""))}</div>
                    <div class="jogo-placar">{placar}</div>
                    <div class="jogo-time" style="text-align:right">{esc(j.get("Visitante",""))}</div>
                </div>
                <div class="jogo-info">📍 Fase: {limpar(j.get("Fase",""))} · Grupo: {limpar(j.get("Grupo",""))} · Rodada: {limpar(j.get("Rodada",""))}</div>
            </div>""", unsafe_allow_html=True)
    else:
        if not err_c:
            st.info("Nenhuma partida encontrada no momento.")
