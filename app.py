import os
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
import os
import glob
import html
import pycountry
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="BR Radar Canarinho", page_icon="🇧🇷", layout="wide")

VERDE = "#009C3B"
AMARELO = "#FFDF00"
AZUL = "#002776"
AZUL_ESCURO = "#001B5E"
TEXTO = "#102033"

st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(135deg, #f7faf4 0%, #eef5ff 100%); color: {TEXTO}; }}
h1, h2, h3, h4, h5, p, label, span {{ color: {TEXTO} !important; }}
.titulo {{ text-align:center; font-size:46px; font-weight:900; color:{VERDE}!important; margin-top:18px; }}
.subtitulo {{ text-align:center; font-size:20px; color:{AZUL}!important; margin-bottom:32px; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {AZUL_ESCURO}, {AZUL}); }}
section[data-testid="stSidebar"] * {{ color:white!important; }}
div[data-testid="stMetric"] {{ background-color:white; border-left:8px solid {VERDE}; padding:20px; border-radius:20px; box-shadow:0 8px 22px rgba(0,0,0,.08); }}
div[data-testid="stMetricValue"] {{ color:{AZUL}!important; font-size:30px!important; font-weight:800!important; }}
div[data-testid="stMetricLabel"] {{ color:{TEXTO}!important; font-weight:700!important; }}
/* Melhora leitura de selects/filtros */
div[data-baseweb="select"] > div {{ background-color:white!important; color:#102033!important; border:1px solid #CBD5E1!important; }}
div[data-baseweb="select"] span {{ color:#102033!important; }}
</style>
""", unsafe_allow_html=True)


def limpar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def escapar(valor):
    return html.escape(str(valor)) if valor is not None else ""


def formatar_numero(valor):
    try:
        valor = float(valor)
    except Exception:
        return "0"
    if valor >= 1_000_000:
        return f"{valor / 1_000_000:.1f}M".replace(".", ",")
    if valor >= 1_000:
        return f"{valor / 1_000:.1f}K".replace(".", ",")
    return str(int(valor))


def formatar_inteiro(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return "0"


def sigla_clube(clube):
    clube = limpar_texto(clube)
    if not clube:
        return "---"
    partes = clube.split()
    if len(partes) == 1:
        return clube[:3].upper()
    return "".join([p[0] for p in partes[:3]]).upper()




def bandeira_pais(nacionalidade):
    nacionalidade = str(nacionalidade).lower()
    if "brazil" in nacionalidade or "brasil" in nacionalidade:
        return "🇧🇷"
    if "france" in nacionalidade:
        return "🇫🇷"
    if "spain" in nacionalidade:
        return "🇪🇸"
    if "england" in nacionalidade:
        return "🏴"
    if "portugal" in nacionalidade:
        return "🇵🇹"
    if "argentina" in nacionalidade:
        return "🇦🇷"
    if "germany" in nacionalidade:
        return "🇩🇪"
    if "italy" in nacionalidade:
        return "🇮🇹"
    if "netherlands" in nacionalidade:
        return "🇳🇱"
    if "belgium" in nacionalidade:
        return "🇧🇪"
    if "uruguay" in nacionalidade:
        return "🇺🇾"
    if "colombia" in nacionalidade:
        return "🇨🇴"
    return "🌎"


def codigo_para_bandeira(codigo):
    codigo = str(codigo).upper().strip()

    if codigo in ["GB", "UK"]:
        return "🏴"

    if len(codigo) != 2 or not codigo.isalpha():
        return "🌎"

    return "".join(chr(127397 + ord(letra)) for letra in codigo)

def pais_para_codigo(nome_pais):
    nome_pais = str(nome_pais).strip()

    aliases = {
        "South Korea": "KR",
        "Czechia": "CZ",
        "Bosnia-Herzegovina": "BA",
        "United States": "US",
        "England": "GB",
        "Scotland": "GB",
        "Wales": "GB",
        "Curaçao": "CW",
        "Curacao": "CW",
        "Turkey": "TR",
        "Iran": "IR",
        "Ivory Coast": "CI",
        "DR Congo": "CD",
        "Cape Verde": "CV",
    }

    if nome_pais in aliases:
        return aliases[nome_pais]

    try:
        pais = pycountry.countries.lookup(nome_pais)
        return pais.alpha_2
    except:
        return ""    

def extrair_bandeira_e_nome(texto):
    try:
        partes = texto.split(" ", 1)

        # Se vier no formato "MX Mexico"
        if len(partes) > 1 and len(partes[0]) == 2:
            sigla = partes[0].upper()
            nome = partes[1]

            bandeira = ''.join(chr(127397 + ord(c)) for c in sigla)
            return bandeira, nome

        return "", texto

    except:
        return "", texto

def estilizar_grafico(fig, titulo=None):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#102033", size=16),
        title_font=dict(color="#002776", size=24),
        legend=dict(
            font=dict(color="#102033", size=15),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#D0D7DE",
            borderwidth=1
        ),
        xaxis=dict(
            title_font=dict(color="#102033", size=16),
            tickfont=dict(color="#102033", size=14),
            gridcolor="#D9DEE8",
            linecolor="#94A3B8"
        ),
        yaxis=dict(
            title_font=dict(color="#102033", size=16),
            tickfont=dict(color="#102033", size=14),
            gridcolor="#D9DEE8",
            linecolor="#94A3B8"
        ),
        margin=dict(l=40, r=40, t=70, b=50)
    )
    if titulo:
        fig.update_layout(title=titulo)
    return fig

def encontrar_coluna(df, opcoes):
    colunas_lower = {c.lower().strip(): c for c in df.columns}
    for opcao in opcoes:
        if opcao.lower().strip() in colunas_lower:
            return colunas_lower[opcao.lower().strip()]
    return None


def carregar_planilha():
    arquivos_excel = glob.glob("*.xlsx")
    if not arquivos_excel:
        st.error("Nenhum arquivo Excel encontrado na pasta do projeto.")
        st.stop()
    arquivo = "atletas.xlsx" if os.path.exists("atletas.xlsx") else arquivos_excel[0]
    return pd.read_excel(arquivo), arquivo


def thesportsdb_key():
    return st.secrets.get("THESPORTSDB_KEY", "123")


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def buscar_jogador_thesportsdb(nome_jogador):
    nome_jogador = limpar_texto(nome_jogador)
    if not nome_jogador:
        return {}
    url = f"https://www.thesportsdb.com/api/v1/json/{thesportsdb_key()}/searchplayers.php"
    try:
        response = requests.get(url, params={"p": nome_jogador}, timeout=12)
        if response.status_code != 200:
            return {}
        dados = response.json().get("player")
        if not dados:
            return {}
        jogador = dados[0]
        return {
            "foto_jogador": jogador.get("strCutout") or jogador.get("strThumb") or "",
            "time_api": jogador.get("strTeam") or "",
            "posicao_api": jogador.get("strPosition") or "",
            "nacionalidade": jogador.get("strNationality") or "",
        }
    except Exception:
        return {}


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def buscar_time_thesportsdb(nome_time):
    nome_time = limpar_texto(nome_time)
    if not nome_time:
        return {}
    url = f"https://www.thesportsdb.com/api/v1/json/{thesportsdb_key()}/searchteams.php"
    try:
        response = requests.get(url, params={"t": nome_time}, timeout=12)
        if response.status_code != 200:
            return {}
        dados = response.json().get("teams")
        if not dados:
            return {}
        time = dados[0]
        return {
            "escudo_time": time.get("strBadge") or time.get("strLogo") or "",
            "nome_time_api": time.get("strTeam") or "",
            "estadio": time.get("strStadium") or "",
            "pais_time": time.get("strCountry") or "",
        }
    except Exception:
        return {}


def enriquecer_com_imagens(row, col_nome_api, col_time_api, col_foto_url, col_escudo_url):
    atleta = limpar_texto(row.get("Atleta", ""))
    clube = limpar_texto(row.get("Clube", ""))
    nome_busca = limpar_texto(row.get(col_nome_api, "")) if col_nome_api else atleta
    time_busca = limpar_texto(row.get(col_time_api, "")) if col_time_api else clube
    foto_manual = limpar_texto(row.get(col_foto_url, "")) if col_foto_url else ""
    escudo_manual = limpar_texto(row.get(col_escudo_url, "")) if col_escudo_url else ""

    dados_jogador = buscar_jogador_thesportsdb(nome_busca) if not foto_manual else {}
    foto = foto_manual or dados_jogador.get("foto_jogador", "")

    if not time_busca:
        time_busca = dados_jogador.get("time_api", clube)

    dados_time = buscar_time_thesportsdb(time_busca) if not escudo_manual else {}
    escudo = escudo_manual or dados_time.get("escudo_time", "")
    return foto, escudo


@st.cache_data(show_spinner=False, ttl=60 * 30)
def buscar_partidas_copa():
    if "FOOTBALL_DATA_KEY" not in st.secrets:
        return pd.DataFrame(), "A chave FOOTBALL_DATA_KEY não foi encontrada no secrets.toml."

    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {"X-Auth-Token": st.secrets["FOOTBALL_DATA_KEY"]}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return pd.DataFrame(), f"Erro na football-data.org: {response.status_code} - {response.text}"

        dados = response.json().get("matches", [])
        linhas = []
        for jogo in dados:
            placar = jogo.get("score", {}) or {}
            full_time = placar.get("fullTime", {}) or {}
            linhas.append({
                "Data UTC": jogo.get("utcDate"),
                "Status": jogo.get("status"),
                "Fase": jogo.get("stage"),
                "Rodada": jogo.get("matchday"),
                "Grupo": jogo.get("group"),
                "Mandante": jogo.get("homeTeam", {}).get("name"),
                "Visitante": jogo.get("awayTeam", {}).get("name"),
                "Gols Mandante": full_time.get("home"),
                "Gols Visitante": full_time.get("away"),
                "Vencedor": placar.get("winner"),
            })

        df_copa = pd.DataFrame(linhas)
        if not df_copa.empty and "Data UTC" in df_copa.columns:
            data = pd.to_datetime(df_copa["Data UTC"], errors="coerce")
            if data.dt.tz is None:
                data = data.dt.tz_localize("UTC")
            df_copa["Data BR"] = data.dt.tz_convert("America/Sao_Paulo").dt.strftime("%d/%m/%Y %H:%M")
        return df_copa, ""
    except Exception as e:
        return pd.DataFrame(), f"Erro ao consultar football-data.org: {e}"




# =========================================================
# HIGHLIGHTLY - ESTATÍSTICAS REAIS DE JOGADOR
# =========================================================
def highlightly_key():
    try:
        return st.secrets.get("HIGHLIGHTLY_KEY", "")
    except Exception:
        return ""


def highlightly_headers():
    key = highlightly_key()
    if not key:
        return None
    return {
        "x-rapidapi-key": key,
        "x-api-key": key
    }


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def buscar_player_highlightly(nome_jogador):
    nome_jogador = limpar_texto(nome_jogador)
    headers = highlightly_headers()

    if not nome_jogador or not headers:
        return {}, "Chave HIGHLIGHTLY_KEY não encontrada no secrets.toml."

    url = "https://soccer.highlightly.net/players"

    try:
        response = requests.get(
            url,
            headers=headers,
            params={"name": nome_jogador, "limit": 10, "offset": 0},
            timeout=20
        )

        if response.status_code != 200:
            return {}, f"Erro Highlightly /players: {response.status_code} - {response.text}"

        payload = response.json()
        jogadores = payload.get("data", []) if isinstance(payload, dict) else []

        if not jogadores:
            return {}, "Nenhum jogador encontrado na Highlightly com esse nome."

        # Prioriza correspondência mais próxima pelo nome
        nome_lower = nome_jogador.lower()
        escolhido = jogadores[0]
        for j in jogadores:
            nome_api = str(j.get("name", "") or j.get("fullName", "")).lower()
            if nome_lower in nome_api or nome_api in nome_lower:
                escolhido = j
                break

        return escolhido, ""

    except Exception as e:
        return {}, f"Erro ao consultar Highlightly /players: {e}"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def buscar_estatisticas_highlightly(player_id):
    headers = highlightly_headers()

    if not player_id or not headers:
        return pd.DataFrame(), "ID do jogador ou chave Highlightly ausente."

    url = f"https://soccer.highlightly.net/players/{player_id}/statistics"

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return pd.DataFrame(), f"Erro Highlightly /players/{{id}}/statistics: {response.status_code} - {response.text}"

        payload = response.json()
        dados = payload if isinstance(payload, list) else payload.get("data", [])

        linhas = []

        for item in dados:
            nome = item.get("name") or item.get("fullName")
            logo = item.get("logo")

            for bloco_nome in ["perCompetition", "perClub"]:
                registros = item.get(bloco_nome, []) or []
                for stat in registros:
                    linhas.append({
                        "Atleta": nome,
                        "Foto": logo,
                        "Agrupamento": bloco_nome,
                        "Clube": stat.get("club"),
                        "Tipo": stat.get("type"),
                        "Liga": stat.get("league"),
                        "Temporada": stat.get("season"),
                        "Gols": stat.get("goals", 0),
                        "Assistências": stat.get("assists", 0),
                        "Jogos": stat.get("gamesPlayed", stat.get("games", 0)),
                        "Minutos": stat.get("minutesPlayed", stat.get("minutes", 0)),
                        "Amarelos": stat.get("yellowCards", 0),
                        "Vermelhos": stat.get("redCards", 0),
                        "Segundo amarelo": stat.get("secondYellowCards", 0),
                        "Gols contra": stat.get("ownGoals", 0),
                        "Pênaltis marcados": stat.get("penaltiesScored", 0),
                        "Clean sheets": stat.get("cleanSheets", 0),
                        "Gols sofridos": stat.get("goalsConceded", 0),
                        "Substituído entrou": stat.get("substitutedIn", 0),
                        "Substituído saiu": stat.get("substitutedOut", 0),
                    })

        return pd.DataFrame(linhas), ""

    except Exception as e:
        return pd.DataFrame(), f"Erro ao consultar estatísticas Highlightly: {e}"


def soma_coluna_segura(df_base, coluna):
    if df_base.empty or coluna not in df_base.columns:
        return 0
    return pd.to_numeric(df_base[coluna], errors="coerce").fillna(0).sum()

# =========================================================
# BASE
# =========================================================
df, arquivo_usado = carregar_planilha()

for coluna in ["Atleta", "Clube", "Posição"]:
    if coluna not in df.columns:
        st.error(f"A planilha precisa ter a coluna obrigatória: {coluna}")
        st.stop()

col_nome_api = encontrar_coluna(df, ["Nome TheSportsDB", "Nome API", "Nome API Jogador", "TheSportsDB Player"])
col_time_api = encontrar_coluna(df, ["Time TheSportsDB", "Clube TheSportsDB", "Nome Time API", "TheSportsDB Team"])
col_foto_url = encontrar_coluna(df, ["Foto Jogador", "Foto Jogador URL", "URL Foto Jogador", "Player Photo"])
col_escudo_url = encontrar_coluna(df, ["Escudo Clube", "Escudo Clube URL", "Logo Clube", "Team Badge"])

np.random.seed(42)
redes = ["Instagram", "TikTok", "X", "Facebook"]
linhas = []
for _, row in df.iterrows():
    atleta = limpar_texto(row.get("Atleta", "Sem nome"))
    clube = limpar_texto(row.get("Clube", "Sem clube"))
    posicao = limpar_texto(row.get("Posição", "Sem posição"))
    for rede in redes:
        seguidores = np.random.randint(80_000, 35_000_000)
        posts = np.random.randint(20, 900)
        curtidas = int(seguidores * np.random.uniform(0.005, 0.08))
        comentarios = int(curtidas * np.random.uniform(0.01, 0.08))
        compartilhamentos = int(curtidas * np.random.uniform(0.005, 0.05))
        visualizacoes = int(curtidas * np.random.uniform(3, 15))
        linhas.append({
            "Atleta": atleta,
            "Clube": clube,
            "Posição": posicao,
            "Rede": rede,
            "Seguidores": seguidores,
            "Posts": posts,
            "Curtidas": curtidas,
            "Comentários": comentarios,
            "Compartilhamentos": compartilhamentos,
            "Visualizações": visualizacoes,
            "Interações": curtidas + comentarios + compartilhamentos,
        })

df_redes = pd.DataFrame(linhas)

st.markdown('<div class="titulo">🇧🇷 BR Radar Canarinho</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Dashboard dos atletas cotados para a Copa — redes sociais, escalação e calendário</div>', unsafe_allow_html=True)

with st.expander("Configuração da base", expanded=False):
    st.write(f"Arquivo carregado: `{arquivo_usado}`")
    st.write("Colunas encontradas:", list(df.columns))

st.sidebar.title("Filtros")
posicoes = st.sidebar.multiselect("Posição", sorted(df_redes["Posição"].dropna().unique()), default=sorted(df_redes["Posição"].dropna().unique()))
clubes = st.sidebar.multiselect("Clube", sorted(df_redes["Clube"].dropna().unique()), default=sorted(df_redes["Clube"].dropna().unique()))
redes_filtro = st.sidebar.multiselect("Rede social", redes, default=redes)

df_filtrado = df_redes[
    (df_redes["Posição"].isin(posicoes)) &
    (df_redes["Clube"].isin(clubes)) &
    (df_redes["Rede"].isin(redes_filtro))
].copy()

aba1, aba2, aba3, aba4 = st.tabs(["📊 Dashboard geral", "⚽ Escalação 4-3-3", "📈 Estatísticas dos jogadores", "🏆 Partidas da Copa"])

# =========================================================
# ABA 1
# =========================================================
with aba1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Atletas", df_filtrado["Atleta"].nunique())
    col2.metric("Clubes", df_filtrado["Clube"].nunique())
    col3.metric("Seguidores", formatar_inteiro(df_filtrado["Seguidores"].sum()))
    col4.metric("Interações", formatar_inteiro(df_filtrado["Interações"].sum()))

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        dados_posicao = df_filtrado[["Atleta", "Posição"]].drop_duplicates()["Posição"].value_counts().reset_index()
        dados_posicao.columns = ["Posição", "Quantidade"]
        fig_pos = px.bar(
            dados_posicao, x="Posição", y="Quantidade", color="Posição", text="Quantidade",
            title="Jogadores por posição", color_discrete_sequence=[VERDE, AMARELO, AZUL, "#00A859"]
        )
        fig_pos.update_traces(texttemplate="%{text}", textposition="inside", textfont_color="white")
        fig_pos = estilizar_grafico(fig_pos)
        st.plotly_chart(fig_pos, use_container_width=True)

    with col_g2:
        dados_rede = df_filtrado.groupby("Rede", as_index=False)["Seguidores"].sum().sort_values("Seguidores", ascending=False)
        fig_rede = px.bar(
            dados_rede, x="Rede", y="Seguidores", color="Rede", text="Seguidores",
            title="Seguidores simulados por rede social", color_discrete_sequence=[VERDE, AMARELO, AZUL, "#00A859"]
        )
        fig_rede.update_traces(texttemplate="%{text:.2s}", textposition="inside", textfont_color="white")
        fig_rede = estilizar_grafico(fig_rede)
        st.plotly_chart(fig_rede, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        top_atletas = df_filtrado.groupby("Atleta", as_index=False)["Seguidores"].sum().sort_values("Seguidores", ascending=False).head(10)
        fig_top = px.bar(
            top_atletas, x="Seguidores", y="Atleta", orientation="h", text="Seguidores",
            title="Top 10 atletas por seguidores simulados", color="Seguidores", color_continuous_scale=[AMARELO, VERDE, AZUL]
        )
        fig_top.update_traces(texttemplate="%{text:.2s}", textposition="inside", textfont_color="white")
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_top = estilizar_grafico(fig_top)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_g4:
        dados_interacoes = df_filtrado.groupby("Rede", as_index=False)["Interações"].sum().sort_values("Interações", ascending=False)
        fig_int = px.pie(
            dados_interacoes, names="Rede", values="Interações", title="Distribuição das interações por rede",
            color_discrete_sequence=[VERDE, AMARELO, AZUL, "#00A859"]
        )
        fig_int.update_traces(textinfo="percent+label", textfont=dict(color="#102033", size=15))
        fig_int.update_layout(
            paper_bgcolor="white",
            font=dict(color=TEXTO, size=16),
            title_font=dict(color=AZUL, size=24),
            legend=dict(font=dict(color=TEXTO, size=15), bgcolor="rgba(255,255,255,0.92)")
        )
        st.plotly_chart(fig_int, use_container_width=True)

    st.subheader("Base simulada de redes sociais")
    st.dataframe(df_filtrado.sort_values("Seguidores", ascending=False), use_container_width=True)

# =========================================================
# ABA 2
# =========================================================
with aba2:
    st.subheader("⚽ Escalação 4-3-3 por popularidade digital")
    modo_rede = st.radio("Como montar a escalação?", ["Todas as redes somadas", "Instagram", "TikTok", "X", "Facebook"], horizontal=True)

    df_escalacao_base = df_filtrado.copy() if modo_rede == "Todas as redes somadas" else df_filtrado[df_filtrado["Rede"] == modo_rede].copy()
    ranking = df_escalacao_base.groupby(["Atleta", "Clube", "Posição"], as_index=False).agg({"Seguidores": "sum", "Interações": "sum"}).sort_values("Seguidores", ascending=False)

    cols_extra = [c for c in [col_nome_api, col_time_api, col_foto_url, col_escudo_url] if c]
    if cols_extra:
        ranking = ranking.merge(df[["Atleta"] + cols_extra], on="Atleta", how="left")

    def escolher_jogadores(posicao, quantidade):
        return ranking[ranking["Posição"] == posicao].head(quantidade)

    goleiro = escolher_jogadores("Gol", 1)
    defensores = escolher_jogadores("Defesa", 4)
    meias = escolher_jogadores("Meio de Campo", 3)
    atacantes = escolher_jogadores("Ataque", 3)
    escalacao = pd.concat([goleiro, defensores, meias, atacantes], ignore_index=True)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Critério", modo_rede)
    col_b.metric("Jogadores escalados", len(escalacao))
    col_c.metric("Seguidores do time", formatar_inteiro(escalacao["Seguidores"].sum()))

    def calcular_overall(jogador):
        max_seguidores = ranking["Seguidores"].max()
        if max_seguidores == 0:
            return 70
        nota = 70 + (jogador["Seguidores"] / max_seguidores) * 29
        return int(min(99, max(70, nota)))

    def card_fifa(jogador, posicao_curta):
        if jogador is None:
            return f"""
            <div class="card-fifa">
                <div class="topo-card"><div class="overall-card">--</div><div class="posicao-card">{posicao_curta}</div></div>
                <div class="bandeira-card">🌎</div>
                <div class="foto-jogador placeholder">?</div>
                <div class="nome-card">Vaga aberta</div>
                <div class="clube-card">Sem atleta suficiente</div>
                <div class="escudo-time placeholder">---</div>
                <div class="stats-card">Sem dados<br>0 interações</div>
                <div class="seguidores-card">0 seguidores</div>
            </div>
            """
        foto, escudo = enriquecer_com_imagens(jogador, col_nome_api, col_time_api, col_foto_url, col_escudo_url)
        nome_busca = limpar_texto(jogador.get(col_nome_api, "")) if col_nome_api else jogador["Atleta"]
        dados_jogador = buscar_jogador_thesportsdb(nome_busca)
        nacionalidade = dados_jogador.get("nacionalidade", "Brazil")
        posicao_api = dados_jogador.get("posicao_api", posicao_curta)
        overall = calcular_overall(jogador)
        foto_html = f'<img class="foto-jogador-img" src="{escapar(foto)}" />' if foto else '<div class="foto-jogador placeholder">👤</div>'
        escudo_html = f'<img class="escudo-time-img" src="{escapar(escudo)}" />' if escudo else f'<div class="escudo-time placeholder">{escapar(sigla_clube(jogador["Clube"]))}</div>'
        return f"""
        <div class="card-fifa">
            <div class="topo-card"><div class="overall-card">{overall}</div><div class="posicao-card">{posicao_curta}</div></div>
            <div class="bandeira-card">{bandeira_pais(nacionalidade)}</div>
            {foto_html}
            <div class="nome-card">{escapar(jogador["Atleta"])}</div>
            <div class="clube-card">{escapar(jogador["Clube"])}</div>
            {escudo_html}
            <div class="stats-card">{escapar(posicao_api)}<br>{formatar_numero(jogador["Interações"])} interações</div>
            <div class="seguidores-card">{formatar_numero(jogador["Seguidores"])} seguidores</div>
        </div>
        """

    def pegar_linha(df_linha, quantidade):
        jogadores = df_linha.to_dict("records")
        while len(jogadores) < quantidade:
            jogadores.append(None)
        return jogadores

    atacantes_linha = pegar_linha(atacantes, 3)
    meias_linha = pegar_linha(meias, 3)
    defensores_linha = pegar_linha(defensores, 4)
    goleiro_linha = pegar_linha(goleiro, 1)

    html_campo = f"""
    <html><head><style>
    body {{ margin:0; background:transparent; font-family:Arial,sans-serif; }}
    .campo {{ width:1060px; min-height:1320px; margin:20px auto; padding:45px 30px; border-radius:34px; border:7px solid white; background:linear-gradient(rgba(0,145,65,.92), rgba(0,115,50,.95)), repeating-linear-gradient(90deg,#18b95f 0px,#18b95f 120px,#0ea64f 120px,#0ea64f 240px); box-shadow:0 22px 50px rgba(0,0,0,.28); position:relative; overflow:hidden; }}
    .campo::before {{ content:""; position:absolute; inset:26px; border:4px solid rgba(255,255,255,.9); border-radius:22px; pointer-events:none; }}
    .campo::after {{ content:""; position:absolute; left:50%; top:50%; width:240px; height:240px; transform:translate(-50%,-50%); border:4px solid rgba(255,255,255,.9); border-radius:50%; pointer-events:none; }}
    .area-goleiro {{ position:absolute; left:50%; bottom:26px; width:310px; height:120px; transform:translateX(-50%); border:4px solid rgba(255,255,255,.9); border-bottom:none; pointer-events:none; }}
    .meia-lua {{ position:absolute; left:50%; bottom:137px; width:175px; height:88px; transform:translateX(-50%); border:4px solid rgba(255,255,255,.9); border-bottom:none; border-radius:175px 175px 0 0; pointer-events:none; }}
    .linha-formacao {{ position:relative; z-index:2; display:flex; justify-content:center; gap:42px; margin:42px 0; flex-wrap:wrap; }}
    .card-fifa {{ width:165px; min-height:285px; background:linear-gradient(145deg,#f7d774,#fff2a8,#d8aa35); border-radius:24px; padding:12px; text-align:center; color:#1b1b1b; box-shadow:0 12px 28px rgba(0,0,0,.38); border:3px solid #f8e08a; position:relative; }}
    .card-fifa::before {{ content:""; position:absolute; inset:7px; border:1px solid rgba(120,80,0,.35); border-radius:18px; pointer-events:none; }}
    .topo-card {{ display:flex; justify-content:space-between; align-items:center; }}
    .overall-card {{ font-size:27px; font-weight:950; color:#002776; }}
    .posicao-card {{ font-size:18px; font-weight:900; color:#002776; }}
    .bandeira-card {{ font-size:22px; margin-top:-2px; }}
    .foto-jogador-img,.foto-jogador {{ width:96px; height:96px; border-radius:50%; background:#fff; margin:8px auto; display:flex; align-items:center; justify-content:center; font-size:36px; border:3px solid #002776; object-fit:cover; }}
    .placeholder {{ color:#002776; font-weight:900; }}
    .nome-card {{ font-size:15px; font-weight:900; color:#111; min-height:38px; display:flex; align-items:center; justify-content:center; }}
    .clube-card {{ font-size:12px; font-weight:700; color:#333; margin-top:4px; min-height:18px; }}
    .escudo-time-img,.escudo-time {{ width:38px; height:38px; border-radius:50%; background:#002776; color:white; margin:8px auto 4px auto; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:900; border:2px solid white; object-fit:contain; }}
    .stats-card {{ font-size:11px; font-weight:800; color:#1b1b1b; margin-top:6px; line-height:1.35; min-height:30px; }}
    .seguidores-card {{ margin-top:8px; background:#002776; color:white; padding:7px; border-radius:12px; font-size:12px; font-weight:800; }}
    </style></head><body>
        <div class="campo"><div class="area-goleiro"></div><div class="meia-lua"></div>
            <div class="linha-formacao">{card_fifa(atacantes_linha[0], "ATA")}{card_fifa(atacantes_linha[1], "ATA")}{card_fifa(atacantes_linha[2], "ATA")}</div>
            <div class="linha-formacao">{card_fifa(meias_linha[0], "MEI")}{card_fifa(meias_linha[1], "MEI")}{card_fifa(meias_linha[2], "MEI")}</div>
            <div class="linha-formacao">{card_fifa(defensores_linha[0], "DEF")}{card_fifa(defensores_linha[1], "DEF")}{card_fifa(defensores_linha[2], "DEF")}{card_fifa(defensores_linha[3], "DEF")}</div>
            <div class="linha-formacao">{card_fifa(goleiro_linha[0], "GOL")}</div>
        </div>
    </body></html>
    """
    components.html(html_campo, height=1450, scrolling=True)
    st.subheader("Tabela da escalação")
    st.dataframe(escalacao, use_container_width=True)

# =========================================================
# ABA 3
# =========================================================
with aba3:
    st.subheader("📈 Estatísticas dos jogadores")
    st.info("Esta aba combina dados simulados de redes sociais, imagens da TheSportsDB e estatísticas reais da Highlightly quando disponíveis.")

    col_f1, col_f2 = st.columns(2)
    jogadores_opcoes = sorted(df_redes["Atleta"].dropna().unique())
    posicoes_opcoes = sorted(df_redes["Posição"].dropna().unique())

    with col_f1:
        jogadores_selecionados = st.multiselect("Filtrar por jogador", jogadores_opcoes, default=jogadores_opcoes)

    with col_f2:
        posicoes_selecionadas = st.multiselect("Filtrar por posição", posicoes_opcoes, default=posicoes_opcoes)

    df_stats = df_redes[(df_redes["Atleta"].isin(jogadores_selecionados)) & (df_redes["Posição"].isin(posicoes_selecionadas))].copy()

    resumo_jogadores = df_stats.groupby(["Atleta", "Clube", "Posição"], as_index=False).agg({
        "Seguidores": "sum", "Interações": "sum", "Curtidas": "sum", "Comentários": "sum",
        "Compartilhamentos": "sum", "Visualizações": "sum", "Posts": "sum"
    }).sort_values("Seguidores", ascending=False)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jogadores filtrados", resumo_jogadores["Atleta"].nunique())
    col2.metric("Seguidores", formatar_inteiro(resumo_jogadores["Seguidores"].sum()))
    col3.metric("Interações", formatar_inteiro(resumo_jogadores["Interações"].sum()))
    col4.metric("Visualizações", formatar_inteiro(resumo_jogadores["Visualizações"].sum()))

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_seg = px.bar(
            resumo_jogadores.head(10), x="Seguidores", y="Atleta", orientation="h", text="Seguidores",
            title="Top 10 jogadores por seguidores simulados", color="Seguidores", color_continuous_scale=[AMARELO, VERDE, AZUL]
        )
        fig_seg.update_traces(texttemplate="%{text:.2s}", textposition="inside", textfont_color="white")
        fig_seg.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_seg = estilizar_grafico(fig_seg)
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_g2:
        top_interacoes = resumo_jogadores.sort_values("Interações", ascending=False).head(10)
        fig_int_jog = px.bar(
            top_interacoes, x="Interações", y="Atleta", orientation="h", text="Interações",
            title="Top 10 jogadores por interações simuladas", color="Interações", color_continuous_scale=[AMARELO, VERDE, AZUL]
        )
        fig_int_jog.update_traces(texttemplate="%{text:.2s}", textposition="inside", textfont_color="white")
        fig_int_jog.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_int_jog = estilizar_grafico(fig_int_jog)
        st.plotly_chart(fig_int_jog, use_container_width=True)

    st.subheader("Comparação por rede social")
    if not df_stats.empty:
        jogador_unico = st.selectbox("Escolha um jogador para detalhar", sorted(df_stats["Atleta"].dropna().unique()))
        df_jogador = df_stats[df_stats["Atleta"] == jogador_unico]
        fig_rede_jogador = px.bar(
            df_jogador, x="Rede", y=["Seguidores", "Interações"], barmode="group",
            title=f"Desempenho simulado de {jogador_unico} por rede social", color_discrete_sequence=[VERDE, AZUL]
        )
        fig_rede_jogador = estilizar_grafico(fig_rede_jogador)
        st.plotly_chart(fig_rede_jogador, use_container_width=True)

    st.divider()
    st.subheader("Consulta visual e estatísticas reais do jogador")
    st.caption("Fotos e escudos vêm da TheSportsDB. Estatísticas de campo vêm da Highlightly, usando busca por nome e depois player ID.")

    jogador_visual = st.selectbox("Buscar dados de qual jogador?", sorted(df["Atleta"].dropna().unique()), key="jogador_visual")
    linha_jogador = df[df["Atleta"] == jogador_visual].iloc[0]
    nome_busca = limpar_texto(linha_jogador.get(col_nome_api, "")) if col_nome_api else jogador_visual
    time_busca = limpar_texto(linha_jogador.get(col_time_api, "")) if col_time_api else limpar_texto(linha_jogador.get("Clube", ""))

    nome_highlightly = st.text_input("Nome para buscar na Highlightly", value=nome_busca, help="Se não encontrar, tente remover acentos ou usar o nome completo do jogador.")

    if st.button("Buscar perfil e estatísticas reais"):
        dados_jogador_tdb = buscar_jogador_thesportsdb(nome_busca)
        dados_time_tdb = buscar_time_thesportsdb(time_busca or dados_jogador_tdb.get("time_api", ""))
        player_h, erro_player_h = buscar_player_highlightly(nome_highlightly)
        df_highlightly = pd.DataFrame()
        erro_stats_h = ""
        if player_h:
            df_highlightly, erro_stats_h = buscar_estatisticas_highlightly(player_h.get("id"))

        df_jogador_stats = df_redes[df_redes["Atleta"] == jogador_visual]
        col_perfil, col_stats = st.columns([1, 2])
        with col_perfil:
            st.markdown("### Perfil")
            if dados_jogador_tdb.get("foto_jogador"):
                st.image(dados_jogador_tdb["foto_jogador"], width=220)
            if dados_time_tdb.get("escudo_time"):
                st.image(dados_time_tdb["escudo_time"], width=90)
            st.markdown(f"""
            **Nome na planilha:** {jogador_visual}  
            **Nome buscado:** {nome_busca}  
            **Clube:** {linha_jogador.get("Clube", "")}  
            **Posição base:** {linha_jogador.get("Posição", "")}  
            **Posição TheSportsDB:** {dados_jogador_tdb.get("posicao_api", "Não encontrada")}  
            **Nacionalidade:** {bandeira_pais(dados_jogador_tdb.get("nacionalidade", "Brazil"))} {dados_jogador_tdb.get("nacionalidade", "Brazil")}
            """)
            if player_h:
                st.success(f"Highlightly encontrou: {player_h.get('name')} | ID {player_h.get('id')}")
                if player_h.get("logo"):
                    st.image(player_h.get("logo"), width=120)
            elif erro_player_h:
                st.warning(erro_player_h)

        with col_stats:
            st.markdown("### Estatísticas reais de campo — Highlightly")
            if erro_stats_h:
                st.warning(erro_stats_h)
            if not df_highlightly.empty:
                gols = soma_coluna_segura(df_highlightly, "Gols")
                assists = soma_coluna_segura(df_highlightly, "Assistências")
                jogos = soma_coluna_segura(df_highlightly, "Jogos")
                minutos = soma_coluna_segura(df_highlightly, "Minutos")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Gols", formatar_inteiro(gols))
                c2.metric("Assistências", formatar_inteiro(assists))
                c3.metric("Jogos", formatar_inteiro(jogos))
                c4.metric("Minutos", formatar_inteiro(minutos))
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    df_comp = df_highlightly.groupby("Liga", as_index=False)[["Gols", "Assistências"]].sum().sort_values("Gols", ascending=False).head(10)
                    fig_campo = px.bar(df_comp, x="Liga", y=["Gols", "Assistências"], barmode="group", title="Gols e assistências por competição", color_discrete_sequence=[VERDE, AZUL])
                    fig_campo = estilizar_grafico(fig_campo)
                    st.plotly_chart(fig_campo, use_container_width=True)
                with col_chart2:
                    df_jogos = df_highlightly.groupby("Liga", as_index=False)[["Jogos", "Minutos"]].sum().sort_values("Jogos", ascending=False).head(10)
                    fig_jogos = px.bar(df_jogos, x="Liga", y=["Jogos", "Minutos"], barmode="group", title="Jogos e minutos por competição", color_discrete_sequence=[AMARELO, VERDE])
                    fig_jogos = estilizar_grafico(fig_jogos)
                    st.plotly_chart(fig_jogos, use_container_width=True)
                st.markdown("#### Tabela completa — estatísticas de campo")
                st.dataframe(df_highlightly, use_container_width=True)
            else:
                st.info("Nenhuma estatística real retornada pela Highlightly para esse jogador.")
            st.markdown("### Estatísticas digitais simuladas")
            c1, c2, c3 = st.columns(3)
            c1.metric("Seguidores", formatar_inteiro(df_jogador_stats["Seguidores"].sum()))
            c2.metric("Interações", formatar_inteiro(df_jogador_stats["Interações"].sum()))
            c3.metric("Visualizações", formatar_inteiro(df_jogador_stats["Visualizações"].sum()))

    st.subheader("Tabela geral dos jogadores — redes simuladas")
    st.dataframe(resumo_jogadores, use_container_width=True)

# =========================================================
# ABA 4
# =========================================================
with aba4:
    st.subheader("🏆 Partidas da Copa do Mundo")
    st.caption("Dados via football-data.org. A disponibilidade depende do plano e da liberação da competição na API.")

    if st.button("Atualizar partidas da Copa"):
        st.cache_data.clear()

    df_copa, erro_copa = buscar_partidas_copa()
    if erro_copa:
        st.warning(erro_copa)

    if df_copa.empty:
        st.info("Nenhuma partida encontrada no momento.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Partidas", len(df_copa))
        col2.metric("Fases", df_copa["Fase"].nunique())
        col3.metric("Status diferentes", df_copa["Status"].nunique())

        col_fase, col_status = st.columns(2)
        with col_fase:
            fase = st.selectbox("Filtrar por fase", ["Todas"] + sorted(df_copa["Fase"].dropna().unique().tolist()))
        with col_status:
            status = st.selectbox("Filtrar por status", ["Todos"] + sorted(df_copa["Status"].dropna().unique().tolist()))

        df_copa_filtrado = df_copa.copy()
        if fase != "Todas":
            df_copa_filtrado = df_copa_filtrado[df_copa_filtrado["Fase"] == fase]
        if status != "Todos":
            df_copa_filtrado = df_copa_filtrado[df_copa_filtrado["Status"] == status]

        st.markdown("""
        <style>
        .card-jogo { background:#ffffff; border-radius:22px; padding:20px; margin-bottom:18px; box-shadow:0 8px 22px rgba(0,0,0,0.10); border-left:8px solid #009C3B; }
        .data-jogo { font-size:15px; color:#002776; font-weight:800; margin-bottom:12px; }
        .times-jogo { display:flex; align-items:center; justify-content:space-between; gap:18px; }
        .time-jogo { width:40%; font-size:21px; font-weight:900; color:#102033; }
        .placar-jogo { width:20%; text-align:center; font-size:26px; font-weight:950; color:#002776; }
        .info-jogo { margin-top:12px; font-size:14px; color:#4b5563; font-weight:700; }
        </style>
        """, unsafe_allow_html=True)

        for _, jogo in df_copa_filtrado.iterrows():
            mandante = jogo.get("Mandante", "")
            visitante = jogo.get("Visitante", "")

            bandeira_mandante, mandante_nome = extrair_bandeira_e_nome(mandante)
            bandeira_visitante, visitante_nome = extrair_bandeira_e_nome(visitante)

            gols_m = jogo.get("Gols Mandante")
            gols_v = jogo.get("Gols Visitante")

            placar = "x"
            if pd.notna(gols_m) and pd.notna(gols_v):
                placar = f"{int(gols_m)} x {int(gols_v)}"

            html_card = (
                '<div class="card-jogo">'
                f'<div class="data-jogo">{jogo.get("Data BR", "")} • {jogo.get("Status", "")}</div>'
                '<div class="times-jogo">'
                f'<div class="time-jogo">{bandeira_mandante} {mandante_nome}</div>'
                f'<div class="placar-jogo">{placar}</div>'
                f'<div class="time-jogo" style="text-align:right;">{visitante_nome} {bandeira_visitante}</div>'
                '</div>'
                f'<div class="info-jogo">Fase: {jogo.get("Fase", "")} • Grupo: {jogo.get("Grupo", "")} • Rodada: {jogo.get("Rodada", "")}</div>'
                '</div>'
            )

            st.markdown(html_card, unsafe_allow_html=True)

