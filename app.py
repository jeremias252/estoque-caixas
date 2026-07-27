import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="Portal Logística", page_icon="📦", layout="wide")

# ==========================================
# CONFIGURAÇÕES E DICIONÁRIOS
# ==========================================
PLANILHAS = {
    "Caixas": "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk",
    "Torres": "https://docs.google.com/spreadsheets/d/10h0iFxX_FEvQljPyLHD6IdeOaSYsnvHfkYzK7PcHe1U/edit?usp=sharing"
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

# --- GERENCIAMENTO DE ESTADO ---
for chave in ["logado", "perfil", "setor", "dados_carregados", "login_setor", "login_perfil"]:
    if chave not in st.session_state:
        st.session_state[chave] = ""
if "logado" not in st.session_state or st.session_state.logado == "":
    st.session_state.logado = False
if "dados_carregados" not in st.session_state or st.session_state.dados_carregados == "":
    st.session_state.dados_carregados = False

# ==========================================
# TEMATIZAÇÃO DINÂMICA (O EFEITO UAU)
# ==========================================
# Descobre em qual setor o usuário está no momento
setor_ativo = st.session_state.login_setor if not st.session_state.logado else st.session_state.setor

if setor_ativo == "Torres":
    # TEMA AZUL/CIANO ELEGANTE
    c_prim = "#0ea5e9"
    c_sec = "#3b82f6"
    c_glow1 = "rgba(14,165,233,0.3)"
    c_glow2 = "rgba(59,130,246,0.15)"
    grad_logo = "linear-gradient(90deg, #7dd3fc, #0ea5e9, #2563eb)"
    grad_btn = "linear-gradient(145deg, #38bdf8, #0ea5e9, #2563eb)"
else:
    # TEMA LARANJA/VERMELHO (Padrão/Caixas)
    c_prim = "#F38020"
    c_sec = "#dc2626"
    c_glow1 = "rgba(243,128,32,0.3)"
    c_glow2 = "rgba(220,38,38,0.15)"
    grad_logo = "linear-gradient(90deg, #ffbd77, #F38020, #ef4444)"
    grad_btn = "linear-gradient(145deg, #ffb15f, #F38020, #dc2626)"

# INJEÇÃO DO CSS PREMIUM COM VARIÁVEIS
st.markdown(f"""
<style>
:root {{
    --prim: {c_prim};
    --sec: {c_sec};
    --glow1: {c_glow1};
    --glow2: {c_glow2};
    --grad-btn: {grad_btn};
    --grad-logo: {grad_logo};
}}

/* Esconde o menu padrão */
#MainMenu, header, footer {{visibility:hidden;}}

/* Fundo Geral Premium */
.stApp {{
    background: radial-gradient(circle at 12% 8%, var(--glow1), transparent 30rem),
                radial-gradient(circle at 86% 12%, var(--glow2), transparent 28rem),
                linear-gradient(135deg,#050608,#111827 50%,#050608);
    color: #f8fafc;
    transition: background 0.8s ease;
}}
.block-container {{max-width:1180px; padding-top:1rem; padding-bottom:2rem;}}

/* Sidebar de Vidro 100% Translúcida */
[data-testid="stSidebar"] {{
    background: rgba(10, 12, 18, 0.2) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}}

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap');

/* ANIMAÇÕES FADE & SLIDE UP */
@keyframes fadeSlideUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.hero, .panel, [data-testid="stForm"], .card, div[data-baseweb="tab-list"], .history-card, .login-card {{
    animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}}

/* =========================================
   VISUAL DAS ABAS
   ========================================= */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px; background: linear-gradient(180deg, rgba(20,22,32,.75), rgba(8,9,14,.85));
    padding: 10px; border-radius: 22px; border: 1px solid rgba(255,255,255,.08);
    box-shadow: inset 0 4px 14px rgba(0,0,0,.55), 0 20px 45px rgba(0,0,0,.35);
    backdrop-filter: blur(22px); margin-bottom: 28px;
}}
.stTabs button[data-baseweb="tab"] {{
    background: transparent !important; border: none !important; border-radius: 16px !important;
    padding: 12px 22px !important; margin: 0 !important; transition: all .35s ease !important;
}}
.stTabs button[data-baseweb="tab"]:hover {{background: rgba(255,255,255,.06) !important;}}
.stTabs button[data-baseweb="tab"][aria-selected="true"] {{
    background: var(--grad-btn) !important;
    box-shadow: 0 6px 20px var(--glow1) !important;
}}
.stTabs button[data-baseweb="tab"] p {{
    color: #9ca3af !important; font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important; font-size: 14.5px !important; margin: 0 !important;
}}
.stTabs button[data-baseweb="tab"][aria-selected="true"] p {{color: #ffffff !important; font-weight: 900 !important;}}
.stTabs [data-baseweb="tab-highlight"] {{display: none !important;}}

/* =========================================
   NOVA TELA DE LOGIN 
   ========================================= */
.login-wrap {{
    min-height: 50vh; display: flex; align-items: center; justify-content: center;
    position: relative; z-index: 1; margin-top: 15px;
}}
.login-wrap::before {{
    content: ""; position: absolute; width: 380px; height: 380px;
    background: radial-gradient(circle, var(--glow1) 0%, transparent 65%);
    top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: -1; filter: blur(35px); transition: all 0.8s ease;
}}
.login-card {{
    width: 100%; max-width: 440px; margin: 0 auto;
    background: rgba(15, 17, 24, 0.65);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px; padding: 30px 28px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    backdrop-filter: blur(28px);
}}
.login-icon {{
    width: 60px; height: 60px; margin: 0 auto 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; border-radius: 20px;
    background: var(--grad-btn);
    box-shadow: 0 12px 28px var(--glow1), inset 0 2px 0 rgba(255,255,255,.3);
    transition: all 0.8s ease;
}}
.login-title {{
    text-align: center; font-family: 'Poppins', sans-serif; font-weight: 900;
    font-size: 26px; margin: 0 0 4px; color: #fff; letter-spacing: -0.5px;
}}
.login-sub {{
    text-align: center; color: #9ca3af; font-size: 13.5px; margin: 0 0 22px; font-weight: 400;
}}
.login-step-title {{
    text-align: center; font-family: 'Poppins', sans-serif; color: #cbd5e1;
    font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;
}}

/* =========================================
   RESTANTE DO DESIGN E INPUT GLOW
   ========================================= */
.hero, .panel, [data-testid="stForm"] {{
    position:relative; overflow:hidden; background:linear-gradient(145deg,rgba(31,36,55,.92),rgba(7,9,16,.96));
    border:1px solid rgba(255,255,255,.14); border-radius:28px; padding:26px; margin-bottom:22px;
}}
.hero-top {{display:flex; justify-content:space-between; gap:18px; align-items:flex-start; flex-wrap:wrap}}
.badge {{display:inline-flex; gap:8px; align-items:center; background:var(--glow2); border:1px solid var(--glow1); color:#fff; border-radius:999px; padding:8px 12px; font-weight:900; font-size:12px; letter-spacing:.08em}}
.kpis {{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-top:22px}}
.kpi {{background:rgba(5,7,12,.48); border:1px solid rgba(255,255,255,.12); border-radius:20px; padding:14px 16px;}}
.kpi b {{display:block; font-size:24px; color:#fff}}
.kpi span {{color:#9ca3af; font-size:12px; font-weight:800; text-transform:uppercase}}
.danger-glow {{border-left:5px solid #ef4444; background:linear-gradient(90deg,rgba(127,29,29,.8),rgba(31,41,55,.75)); border-radius:18px; padding:16px; margin-bottom:18px; color:#fecaca}}
.profile-pill {{background:rgba(5,7,12,.54); border:1px solid rgba(255,255,255,.13); border-radius:18px; padding:12px; text-align:center; margin:14px 0; color:#cbd5e1}}
.profile-pill b {{color: var(--prim); transition: color 0.5s ease;}}
.history-card {{display:grid; grid-template-columns:1.1fr .8fr 1fr 2fr .7fr; gap:10px; align-items:center; background:linear-gradient(145deg,rgba(24,29,43,.92),rgba(8,10,16,.96)); border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:12px 14px; margin-bottom:10px;}}
.history-head {{color:#9ca3af; font-size:11px; font-weight:900; text-transform:uppercase; letter-spacing:.08em}}
.history-action {{font-weight:900; border-radius:999px; padding:6px 10px; text-align:center}}
.entrada {{background:rgba(16,185,129,.15); color:#86efac; border:1px solid rgba(16,185,129,.35)}}
.saida {{background:rgba(239,68,68,.15); color:#fecaca; border:1px solid rgba(239,68,68,.35)}}
.qty-badge {{font-weight:900; color:var(--prim); text-align:center}}
.logo {{font-size:34px; font-weight:900; text-align:center; letter-spacing:-1px; margin-bottom:14px; font-family:'Poppins',sans-serif;}}
.logo span {{background:var(--grad-logo); -webkit-background-clip:text; color:transparent; transition: all 0.5s ease;}}
.title {{font-size:clamp(38px,5vw,64px); font-weight:900; line-height:.92; margin:8px 0; letter-spacing:-.05em}}

/* Botoes Padrão */
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button {{
    border-radius:18px !important; font-family:'Poppins',sans-serif !important; font-weight:700 !important; min-height:50px;
    background:linear-gradient(145deg,#262b3c,#10131d) !important; color:white !important;
    border:1px solid rgba(255,255,255,.08) !important; box-shadow:0 8px 20px rgba(0,0,0,.3) !important;
    font-size: 15px !important; transition: all 0.2s ease !important;
}}
.stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stFormSubmitButton"] button:hover {{
    transform:translateY(-3px); border-color:var(--glow1) !important; background:linear-gradient(145deg,#2a2f42,#141724) !important;
}}

/* Botão Primário */
.stButton>button[data-testid="baseButton-primary"], [data-testid="stFormSubmitButton"] button[kind="primary"], .stDownloadButton>button[data-testid="baseButton-primary"] {{
    background:var(--grad-btn) !important;
    box-shadow:0 8px 20px var(--glow1) !important; border:none !important;
}}

/* Inputs com GLOW Effect Focus */
input, textarea, [data-baseweb="select"] > div {{
    background:rgba(5,6,8,.7) !important; border-radius:14px !important; border-color:rgba(255,255,255,.14) !important;
    min-height: 48px; font-size: 15px !important; transition: all 0.3s ease !important;
}}
[data-baseweb="input"]:focus-within > div, [data-baseweb="select"]:focus-within > div {{
    border-color: var(--prim) !important;
    box-shadow: 0 0 0 2px var(--glow1) !important;
}}

/* Cards de Estoque */
.card {{
    background:linear-gradient(145deg,#202638,#0b0d14); border:1px solid rgba(255,255,255,.12);
    border-radius:18px; padding:16px; text-align:center; box-shadow:0 15px 36px rgba(0,0,0,.38); margin-bottom:12px;
}}
.card .label {{color:#a7adb8; font-size:12px; font-weight:900; text-transform:uppercase}}
.card .value {{color:var(--prim); font-size:34px; font-weight:900}}
.card .status {{color:#d1d5db; font-size:12px}}
</style>
""", unsafe_allow_html=True)


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
    st.markdown(f"<p style='text-align:center;color:{c_prim};font-weight:900'>Estoque Total: {total} un.</p>", unsafe_allow_html=True)
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
    
    # NOTIFICAÇÃO TOAST 
    st.toast(f"✅ {acao} de {quantidade}x {modelo} registrada com sucesso!", icon="✅")
    time.sleep(0.5)
    st.rerun()

# ==========================================
# WIZARD DE LOGIN
# ==========================================
if not st.session_state.logado:
    _, centro, _ = st.columns([1, 1.2, 1])
    
    with centro:
        st.markdown("<div class='login-wrap'><div class='login-card'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='login-icon'>⬢</div>
        <div class='login-title'>Portal Logística</div>
        <div class='login-sub'>Sistema Integrado de Gestão de Estoque</div>
        """, unsafe_allow_html=True)
        
        # PASSO 1: ESCOLHER SETOR
        if not st.session_state.login_setor:
            st.markdown("<div class='login-step-title'>PASSO 1: SELECIONE O SETOR</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("📦 CAIXAS", use_container_width=True):
                st.session_state.login_setor = "Caixas"
                st.rerun()
            if c2.button("🗼 TORRES", use_container_width=True):
                st.session_state.login_setor = "Torres"
                st.rerun()
                
        # PASSO 2: ESCOLHER PERFIL
        elif not st.session_state.login_perfil:
            st.markdown(f"<div class='login-step-title'>SETOR {st.session_state.login_setor.upper()} • SEU PERFIL</div>", unsafe_allow_html=True)
            
            if st.button("👀 Equipe (Apenas Visualização)", use_container_width=True):
                st.session_state.logado = True
                st.session_state.perfil = "equipe"
                st.session_state.setor = st.session_state.login_setor
                st.rerun()
                
            if st.button("⚙️ Controle Operacional", use_container_width=True):
                st.session_state.login_perfil = "controle"
                st.rerun()
                
            if st.button("👑 Coordenação (Master)", use_container_width=True):
                st.session_state.login_perfil = "coord"
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⬅️ Voltar aos Setores", use_container_width=True):
                st.session_state.login_setor = ""
                st.rerun()

        # PASSO 3: DIGITAR SENHA
        else:
            st.markdown(f"<div class='login-step-title'>ACESSO RESTRITO • {st.session_state.login_perfil.upper()}</div>", unsafe_allow_html=True)
            
            senha = st.text_input("Digite sua Senha de Acesso:", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1.5])
            if c1.button("⬅️ Voltar", use_container_width=True):
                st.session_state.login_perfil = ""
                st.rerun()
                
            if c2.button("Entrar no Sistema", type="primary", use_container_width=True):
                setor_atual = st.session_state.login_setor
                perfil_atual = st.session_state.login_perfil
                senha_correta = "coord123" if perfil_atual == "coord" else SENHAS_CONTROLE[setor_atual]
                
                if senha == senha_correta:
                    st.session_state.logado = True
                    st.session_state.perfil = perfil_atual
                    st.session_state.setor = setor_atual
                    st.toast(f"Bem-vindo(a) ao setor de {setor_atual}!", icon="👋")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
                    
        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# PAINEL OPERACIONAL
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
            st.session_state.login_setor = ""
            st.session_state.login_perfil = ""
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
