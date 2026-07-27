import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Portal Logística", page_icon="📦", layout="wide")

st.markdown("""
<style>
/* Esconde o menu padrão do Streamlit */
#MainMenu, header, footer {visibility:hidden;}

/* Fundo Geral Premium */
.stApp {
    background: radial-gradient(circle at 12% 8%,rgba(243,128,32,.35),transparent 28rem),
                radial-gradient(circle at 86% 12%,rgba(220,38,38,.22),transparent 26rem),
                radial-gradient(circle at 50% 90%,rgba(14,165,233,.10),transparent 30rem),
                linear-gradient(135deg,#050608,#111827 50%,#050608);
    color: #f8fafc;
}
.block-container {max-width:1180px; padding-top:2rem; padding-bottom:3rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0b0d14,#171b28); border-right:1px solid rgba(255,255,255,.12);}

/* Fonte premium */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&family=Inter:wght@400;600;700&display=swap');

/* =========================================
   NOVO VISUAL DAS ABAS (Glass Premium 2.0)
   ========================================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: linear-gradient(180deg, rgba(20,22,32,.75), rgba(8,9,14,.85));
    padding: 10px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: inset 0 4px 14px rgba(0,0,0,.55), 0 20px 45px rgba(0,0,0,.35);
    backdrop-filter: blur(22px);
    margin-bottom: 28px;
    position: relative;
}

.stTabs button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 12px 22px !important;
    margin: 0 !important;
    transition: all .35s cubic-bezier(.22,1,.36,1) !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
}

.stTabs button[data-baseweb="tab"]:hover {
    background: rgba(255,255,255,.06) !important;
    transform: translateY(-1px);
}

.stTabs button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(145deg, #ffb15f 0%, #F38020 45%, #dc2626 100%) !important;
    box-shadow:
        0 6px 20px rgba(243,128,32,.45),
        0 2px 0 rgba(255,255,255,.25) inset,
        0 -6px 14px rgba(127,29,29,.35) inset !important;
    transform: translateY(-2px) scale(1.03);
    animation: glowPulse 2.6s ease-in-out infinite;
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 6px 20px rgba(243,128,32,.45), 0 2px 0 rgba(255,255,255,.25) inset, 0 -6px 14px rgba(127,29,29,.35) inset; }
    50% { box-shadow: 0 8px 28px rgba(243,128,32,.7), 0 2px 0 rgba(255,255,255,.3) inset, 0 -6px 14px rgba(127,29,29,.4) inset; }
}

.stTabs button[data-baseweb="tab"] p {
    color: #9ca3af !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14.5px !important;
    letter-spacing: .01em;
    margin: 0 !important;
    transition: letter-spacing .3s ease;
}

.stTabs button[data-baseweb="tab"][aria-selected="true"] p {
    color: #ffffff !important;
    font-weight: 900 !important;
    letter-spacing: .03em;
    text-shadow: 0 2px 8px rgba(0,0,0,.35);
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
    background-color: transparent !important;
}

.stTabs button[data-baseweb="tab"]:not(:last-child)::after {
    content: "";
    position: absolute;
    right: -3px;
    top: 25%;
    height: 50%;
    width: 1px;
    background: rgba(255,255,255,.08);
}
.stTabs button[data-baseweb="tab"][aria-selected="true"]::after,
.stTabs button[data-baseweb="tab"][aria-selected="true"] + button::after {
    display: none;
}

/* =========================================
   RESTANTE DO DESIGN
   ========================================= */
.hero, .panel, [data-testid="stForm"] {
    position:relative; overflow:hidden;
    background:linear-gradient(145deg,rgba(31,36,55,.92),rgba(7,9,16,.96));
    border:1px solid rgba(255,255,255,.14);
    border-radius:28px;
    box-shadow:0 28px 80px rgba(0,0,0,.52),inset 0 1px 0 rgba(255,255,255,.14);
    padding:26px; margin-bottom:22px; backdrop-filter:blur(18px)
}
.hero:before, .panel:before, [data-testid="stForm"]:before {
    content:""; position:absolute; inset:0; pointer-events:none;
    background:linear-gradient(120deg,rgba(255,255,255,.12),transparent 35%,rgba(243,128,32,.12))
}
.hero > * {position:relative}
.hero {padding:32px}
.hero-top {display:flex; justify-content:space-between; gap:18px; align-items:flex-start; flex-wrap:wrap}
.badge {display:inline-flex; gap:8px; align-items:center; background:rgba(243,128,32,.13); border:1px solid rgba(243,128,32,.42); color:#fed7aa; border-radius:999px; padding:8px 12px; font-weight:900; font-size:12px; letter-spacing:.08em}
.kpis {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-top:22px}
.kpi {background:rgba(5,7,12,.48); border:1px solid rgba(255,255,255,.12); border-radius:20px; padding:14px 16px; box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}
.kpi b {display:block; font-size:24px; color:#fff}
.kpi span {color:#9ca3af; font-size:12px; font-weight:800; text-transform:uppercase}
.danger-glow {border-left:5px solid #ef4444; background:linear-gradient(90deg,rgba(127,29,29,.8),rgba(31,41,55,.75)); border-radius:18px; padding:16px; margin-bottom:18px; color:#fecaca}
.login-wrap {min-height:88vh; display:flex; align-items:center; justify-content:center}
.login-card {
    position:relative; overflow:hidden;
    max-width:420px; margin:0 auto;
    background:linear-gradient(165deg,rgba(28,32,48,.94),rgba(6,7,12,.97));
    border:1px solid rgba(255,255,255,.10);
    border-radius:28px;
    padding:40px 34px 32px;
    box-shadow:0 30px 90px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.10);
    backdrop-filter:blur(20px);
}
.login-icon {
    width:64px; height:64px; margin:0 auto 14px;
    display:flex; align-items:center; justify-content:center;
    font-size:30px;
    border-radius:20px;
    background:linear-gradient(150deg,#ffb15f,#F38020 55%,#dc2626);
    box-shadow:0 14px 34px rgba(243,128,32,.4), inset 0 1px 0 rgba(255,255,255,.35);
}
.login-eyebrow {
    text-align:center; color:#fdba74; font-size:11px; font-weight:800;
    letter-spacing:.22em; text-transform:uppercase; margin-top:4px;
}
.login-title {
    text-align:center; font-family:'Poppins',sans-serif; font-weight:900;
    font-size:26px; margin:8px 0 4px; letter-spacing:-.02em; color:#fff;
}
.profile-pill {background:rgba(5,7,12,.54); border:1px solid rgba(255,255,255,.13); border-radius:18px; padding:12px; text-align:center; margin:14px 0; color:#cbd5e1}
.profile-pill b {color:#F38020}
.window-title {margin:0; font-weight:900}
.window-sub {color:#cbd5e1; margin:6px 0 0}
.history-card {display:grid; grid-template-columns:1.1fr .8fr 1fr 2fr .7fr; gap:10px; align-items:center; background:linear-gradient(145deg,rgba(24,29,43,.92),rgba(8,10,16,.96)); border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:12px 14px; margin-bottom:10px; box-shadow:0 12px 30px rgba(0,0,0,.28)}
.history-head {color:#9ca3af; font-size:11px; font-weight:900; text-transform:uppercase; letter-spacing:.08em}
.history-action {font-weight:900; border-radius:999px; padding:6px 10px; text-align:center}
.entrada {background:rgba(16,185,129,.15); color:#86efac; border:1px solid rgba(16,185,129,.35)}
.saida {background:rgba(239,68,68,.15); color:#fecaca; border:1px solid rgba(239,68,68,.35)}
.qty-badge {font-weight:900; color:#F38020; text-align:center}
.logo {font-size:34px; font-weight:900; text-align:center; letter-spacing:-1px; margin-bottom:14px; text-shadow:0 10px 30px rgba(0,0,0,.45)}
.logo span {background:linear-gradient(90deg,#ffbd77,#F38020,#ef4444); -webkit-background-clip:text; color:transparent}
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button {
    border-radius:15px !important; font-weight:900 !important; min-height:45px;
    background:linear-gradient(145deg,#262b3c,#10131d) !important; color:white !important;
    border:1px solid rgba(255,255,255,.14) !important; box-shadow:0 7px 0 #050608,0 15px 28px rgba(0,0,0,.35) !important
}
.stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stFormSubmitButton"] button:hover {
    transform:translateY(-2px); border-color:#F38020 !important
}
.stButton>button[data-testid="baseButton-primary"], [data-testid="stFormSubmitButton"] button[kind="primary"], .stDownloadButton>button[data-testid="baseButton-primary"] {
    background:linear-gradient(145deg,#ffb15f,#F38020,#dc2626) !important;
    box-shadow:0 8px 0 #7f1d1d,0 20px 40px rgba(243,128,32,.32) !important
}
input, textarea, [data-baseweb="select"] > div {
    background:rgba(5,6,8,.7) !important; border-radius:14px !important; border-color:rgba(255,255,255,.14) !important
}
.card {
    background:linear-gradient(145deg,#202638,#0b0d14); border:1px solid rgba(255,255,255,.12);
    border-radius:18px; padding:16px; text-align:center; box-shadow:0 15px 36px rgba(0,0,0,.38); margin-bottom:12px
}
.card .label {color:#a7adb8; font-size:12px; font-weight:900; text-transform:uppercase}
.card .value {color:#F38020; font-size:34px; font-weight:900}
.card .status {color:#d1d5db; font-size:12px}
[data-testid="stMetric"] {background:#111827; border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:16px}
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONFIGURAÇÕES E DICIONÁRIOS (CAIXAS E TORRES)
# ==========================================
PLANILHAS = {
    "Caixas": "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk",
    "Torres": "COLE_O_LINK_DAS_TORRES_AQUI"
}

EQUIPES = {
    "Caixas": ["Marcello", "Fabiano", "Sérgio"],
    "Torres": ["Fran", "Henrique", "Leonardo", "Patrick"]
}

SENHAS_CONTROLE = {
    "Caixas": "marcello123",
    "Torres": "fran123"
}

conn = st.connection("gsheets", type=GSheetsConnection)

for chave, valor in {"logado": False, "perfil": "", "setor": "", "dados_carregados": False}.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

def logo(setor_nome="SISTEMA"):
    st.markdown(f"<div class='logo'>⬢ SETOR <span>{setor_nome.upper()}</span></div>", unsafe_allow_html=True)

def carregar_dados(setor):
    url_alvo = PLANILHAS[setor]
    try:
        estoque = conn.read(spreadsheet=url_alvo, worksheet="Estoque", ttl=600).copy()
        estoque = estoque.dropna(subset=["Modelo"])
        estoque["Quantidade"] = pd.to_numeric(estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
    except Exception:
        st.error("⚠️ Falha de comunicação com o Google Drive.")
        st.stop()
    try:
        historico = conn.read(spreadsheet=url_alvo, worksheet="Historico", ttl=600).copy()
        historico = historico.dropna(subset=["ID"])
    except Exception:
        historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
    return estoque, historico

def salvar_estoque(df, setor):
    conn.update(spreadsheet=PLANILHAS[setor], worksheet="Estoque", data=df)

def salvar_historico(df, setor):
    conn.update(spreadsheet=PLANILHAS[setor], worksheet="Historico", data=df)

@st.dialog("Detalhes do Modelo")
def abrir_janela_modelo(linha, df_linha, total):
    st.markdown(f"<h3 style='text-align:center'>{linha}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#F38020;font-weight:900'>Estoque Total: {total} un.</p>", unsafe_allow_html=True)
    st.divider()
    for i in range(0, len(df_linha), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(df_linha):
                row = df_linha.iloc[i + j]
                qtd = int(row["Quantidade"])
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                cols[j].markdown(f"<div class='card'><div class='label'>{row['Cor']}</div><div class='value'>{qtd}</div><div class='status'>{status}</div></div>", unsafe_allow_html=True)

def exibir_estoque(df_base, termo_busca=""):
    df = df_base.copy()
    if termo_busca:
        df = df[df["Modelo"].str.contains(termo_busca, case=False, na=False)]
    if df.empty:
        st.warning("Nenhum modelo encontrado.")
        return
    df["Linha"] = df["Modelo"].apply(lambda n: n.rsplit(" - ", 1)[0] if " - " in n else n)
    df["Cor"] = df["Modelo"].apply(lambda n: n.rsplit(" - ", 1)[1] if " - " in n else "Padrão")
    totais = df.groupby("Linha")["Quantidade"].sum().reset_index().sort_values("Quantidade", ascending=False)
    st.markdown("<p style='color:#9ca3af;text-align:center'>Selecione um modelo para ver os detalhes:</p>", unsafe_allow_html=True)
    for i in range(0, len(totais), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(totais):
                linha = totais.iloc[i + j]["Linha"]
                total = int(totais.iloc[i + j]["Quantidade"])
                icone = "🔴" if total == 0 else ("🟡" if total <= 5 else "📦")
                if cols[j].button(f"{icone} {linha} ({total})", key=f"btn_{linha}", use_container_width=True):
                    abrir_janela_modelo(linha, df[df["Linha"] == linha].sort_values("Cor"), total)

def exibir_historico_bonito(df_historico):
    if df_historico.empty:
        st.info("Nenhum lançamento no histórico ainda.")
        return
    df = df_historico.drop(columns=["ID"], errors="ignore").head(80).copy()
    st.markdown("""
    <div class='history-card history-head'>
        <div>Data</div><div>Ação</div><div>Separador</div><div>Modelo</div><div>Qtd</div>
    </div>
    """, unsafe_allow_html=True)
    for _, row in df.iterrows():
        acao = str(row.get("Ação", ""))
        classe = "entrada" if acao == "Entrada" else "saida"
        icone = "📥" if acao == "Entrada" else "📤"
        st.markdown(f"""
        <div class='history-card'>
            <div>{row.get('Data', '')}</div>
            <div class='history-action {classe}'>{icone} {acao}</div>
            <div>{row.get('Separador', '')}</div>
            <div>{row.get('Modelo', '')}</div>
            <div class='qty-badge'>{row.get('Quantidade', '')}</div>
        </div>
        """, unsafe_allow_html=True)

def registrar_movimento(acao, pessoa, modelo, quantidade, df_estoque, df_historico, setor):
    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
    if acao == "Saída" and df_estoque.at[idx, "Quantidade"] < quantidade:
        st.error(f"⚠️ Saldo insuficiente! Temos {df_estoque.at[idx, 'Quantidade']} un.")
        return
    df_estoque.at[idx, "Quantidade"] += quantidade if acao == "Entrada" else -quantidade
    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": acao, "Separador": pessoa, "Modelo": modelo, "Quantidade": quantidade}])
    st.session_state.df_estoque = df_estoque
    st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
    salvar_estoque(df_estoque, setor)
    salvar_historico(st.session_state.df_historico, setor)
    st.success("✅ Movimento registrado com sucesso!")
    st.rerun()


# ==========================================
# TELA DE LOGIN INTEGRADA
# ==========================================
if not st.session_state.logado:
    _, centro, _ = st.columns([1, 1.15, 1])
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    with centro:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='login-icon'>⬢</div>
        <div class='login-eyebrow'>Acesso Seguro ERP</div>
        <div class='login-title'>Portal Logística</div>
        """, unsafe_allow_html=True)
        
        escolha_setor = st.selectbox("1. Escolha o Setor", ["", "📦 Caixas", "🗼 Torres"])
        escolha_perfil = st.selectbox("2. Escolha o Perfil", ["", "👀 Equipe (Visualização)", "⚙️ Controle", "👑 Coordenador"])
        
        if escolha_setor and escolha_perfil:
            setor_limpo = "Caixas" if "Caixas" in escolha_setor else "Torres"
            
            if escolha_perfil == "👀 Equipe (Visualização)":
                if st.button(f"Acessar Estoque Livre - {setor_limpo}", type="primary", use_container_width=True):
                    st.session_state.logado = True
                    st.session_state.perfil = "equipe"
                    st.session_state.setor = setor_limpo
                    st.rerun()
                    
            elif escolha_perfil == "⚙️ Controle":
                senha = st.text_input("Senha", type="password")
                if st.button(f"Entrar no Painel - {setor_limpo}", type="primary", use_container_width=True):
                    senha_correta = SENHAS_CONTROLE[setor_limpo]
                    if senha == senha_correta:
                        st.session_state.logado = True
                        st.session_state.perfil = "controle"
                        st.session_state.setor = setor_limpo
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta!")
                        
            elif escolha_perfil == "👑 Coordenador":
                senha = st.text_input("Senha Master", type="password")
                if st.button("Entrar no Painel Gerencial", type="primary", use_container_width=True):
                    if senha == "coord123":
                        st.session_state.logado = True
                        st.session_state.perfil = "coord"
                        st.session_state.setor = setor_limpo
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta!")
                        
        st.markdown("<div class='login-footnote'>🔒 Conexão criptografada com o Google Sheets</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAINEL OPERACIONAL (CARREGADO APÓS LOGIN)
# ==========================================
else:
    meu_setor = st.session_state.setor
    
    if not st.session_state.dados_carregados:
        with st.spinner(f"⏳ Sincronizando banco de dados de {meu_setor}..."):
            st.session_state.df_estoque, st.session_state.df_historico = carregar_dados(meu_setor)
            st.session_state.dados_carregados = True

    df_estoque = st.session_state.df_estoque
    df_historico = st.session_state.df_historico
    separadores = EQUIPES[meu_setor]
    modelos = sorted(df_estoque["Modelo"].tolist())

    with st.sidebar:
        logo(meu_setor)
        st.markdown("---")
        st.markdown(f"<div class='profile-pill'><span>PERFIL ATIVO</span><br><b>{st.session_state.perfil.upper()}</b></div>", unsafe_allow_html=True)
        if st.button("🔄 Sincronizar Base", use_container_width=True):
            st.session_state.dados_carregados = False
            st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Sair (Logout)", type="primary", use_container_width=True):
            st.session_state.logado = False
            st.session_state.perfil = ""
            st.session_state.setor = ""
            st.session_state.dados_carregados = False
            st.rerun()

    zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
    total_pecas = int(df_estoque["Quantidade"].sum())
    total_modelos = len(df_estoque)
    
    st.markdown(f"""
    <section class='hero'>
        <div class='hero-top'>
            <div>
                <div class='badge'>⬢ SETOR {meu_setor.upper()}</div>
                <div class='title'>Painel Operacional</div>
                <p class='sub'>Controle unificado de estoque com validação de saldo e histórico em tempo real.</p>
            </div>
            <div class='badge'>ACESSO {st.session_state.perfil.upper()}</div>
        </div>
        <div class='kpis'>
            <div class='kpi'><span>Peças em estoque</span><b>{total_pecas}</b></div>
            <div class='kpi'><span>Modelos cadastrados</span><b>{total_modelos}</b></div>
            <div class='kpi'><span>Itens zerados</span><b>{len(zerados)}</b></div>
        </div>
    </section>
    """, unsafe_allow_html=True)
    
    if zerados:
        st.markdown(f"<div class='danger-glow'>🚨 <b>ALERTA:</b> Há {len(zerados)} modelos com estoque totalmente zerado.</div>", unsafe_allow_html=True)

    if st.session_state.perfil == "equipe":
        st.markdown("<div class='panel'>👋 <b>Modo Visualização.</b> Solicite retiradas ao responsável.</div>", unsafe_allow_html=True)
        busca = st.text_input("🔍 Buscar modelo específico...")
        exibir_estoque(df_estoque, busca)
    else:
        nomes = ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico"]
        if st.session_state.perfil == "coord":
            nomes.append("👑 Excel")
        abas = st.tabs(nomes)

        with abas[0]:
            busca = st.text_input("🔍 Pesquisar no estoque...")
            exibir_estoque(df_estoque, busca)
            
        with abas[1]:
            st.markdown("<div class='panel'><h3 class='window-title'>📤 Janela de Saídas</h3><p class='window-sub'>Registre retiradas com validação automática de saldo.</p></div>", unsafe_allow_html=True)
            with st.form("form_saida", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                pessoa = c1.selectbox("Quem retirou?", [""] + separadores)
                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
                qtd = c3.number_input("Qtd", min_value=1, value=1)
                enviar = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)
            if enviar:
                registrar_movimento("Saída", pessoa, modelo, qtd, df_estoque, df_historico, meu_setor) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
                
        with abas[2]:
            st.markdown("<div class='panel'><h3 class='window-title'>📥 Janela de Entradas</h3><p class='window-sub'>Lance produção e reposição no estoque conectado.</p></div>", unsafe_allow_html=True)
            with st.form("form_entrada", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                pessoa = c1.selectbox("Quem produziu?", [""] + separadores)
                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
                qtd = c3.number_input("Qtd", min_value=1, value=1)
                enviar = st.form_submit_button("Lançar no Estoque", type="primary", use_container_width=True)
            if enviar:
                registrar_movimento("Entrada", pessoa, modelo, qtd, df_estoque, df_historico, meu_setor) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
                
        with abas[3]:
            st.markdown("<div class='panel'><h3 class='window-title'>📊 Janela de Indicadores</h3><p class='window-sub'>Acompanhe volume, itens críticos e movimentos por período.</p></div>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("📦 Total de Peças", int(df_estoque["Quantidade"].sum()))
            m2.metric("⚠️ Críticos (Zerados)", len(zerados))
            d1, d2 = st.columns(2)
            inicio = d1.date_input("De:", datetime.now().replace(day=1))
            fim = d2.date_input("Até:", datetime.now())
            
            if not df_historico.empty:
                hist = df_historico.copy()
                hist["Data_Filtro"] = pd.to_datetime(hist["Data"]).dt.date
                hist = hist[(hist["Data_Filtro"] >= inicio) & (hist["Data_Filtro"] <= fim)]
                g1, g2 = st.columns(2)
                g1.bar_chart(hist[hist["Ação"] == "Entrada"].groupby("Separador")["Quantidade"].sum(), color="#10b981")
                g2.bar_chart(hist[hist["Ação"] == "Saída"].groupby("Separador")["Quantidade"].sum(), color="#ef4444")
                
        with abas[4]:
            st.markdown("<div class='panel'><h3 class='window-title'>🕒 Janela de Histórico</h3><p class='window-sub'>Últimos lançamentos sincronizados com a planilha.</p></div>", unsafe_allow_html=True)
            exibir_historico_bonito(df_historico)
            
        if st.session_state.perfil == "coord":
            with abas[5]:
                st.markdown("<div class='panel'><h3 class='window-title'>👑 Janela Executiva</h3><p class='window-sub'>Exporte os dados para análise e conferência.</p></div>", unsafe_allow_html=True)
                csv = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button("📥 Baixar Excel (CSV)", csv, f"Relatorio_{meu_setor}_{datetime.now().strftime('%d-%m')}.csv", "text/csv", type="primary", use_container_width=True)
