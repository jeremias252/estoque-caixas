import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Caixas - Portal", page_icon="📦", layout="wide")

st.markdown("""
<style>
#MainMenu, header, footer {visibility:hidden;}
.stApp{background:radial-gradient(circle at top left,#3b1b08 0,#090b12 34rem),linear-gradient(135deg,#07080d,#121827 55%,#050608);color:#f8fafc;}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:3rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0b0d14,#171b28);border-right:1px solid rgba(255,255,255,.12);}
.hero,.panel,[data-testid="stForm"]{background:linear-gradient(145deg,rgba(30,34,50,.94),rgba(9,11,18,.96));border:1px solid rgba(255,255,255,.13);border-radius:24px;box-shadow:0 24px 70px rgba(0,0,0,.48),inset 0 1px 0 rgba(255,255,255,.12);padding:24px;margin-bottom:20px;}
.logo{font-size:34px;font-weight:900;text-align:center;letter-spacing:-1px;margin-bottom:14px}.logo span{color:#F38020}.eyebrow{color:#F38020;font-size:12px;font-weight:900;letter-spacing:.18em;text-transform:uppercase}.title{font-size:clamp(34px,5vw,58px);font-weight:900;line-height:.95;margin:6px 0}.sub{color:#cbd5e1;margin:8px 0 0}
div[data-baseweb="tab-list"]{gap:10px;background:rgba(5,6,10,.55);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:10px;margin-bottom:20px}div[data-baseweb="tab"]{background:linear-gradient(145deg,#252b3d,#10131d)!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:15px!important;box-shadow:0 7px 0 #050608,0 14px 28px rgba(0,0,0,.35)!important;padding:10px 16px!important}div[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(145deg,#ffad55,#F38020,#b91c1c)!important;box-shadow:0 7px 0 #7f1d1d,0 18px 36px rgba(243,128,32,.32)!important}div[data-baseweb="tab"] p{color:white!important;font-weight:900!important}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:15px!important;font-weight:900!important;min-height:45px;background:linear-gradient(145deg,#262b3c,#10131d)!important;color:white!important;border:1px solid rgba(255,255,255,.14)!important;box-shadow:0 7px 0 #050608,0 15px 28px rgba(0,0,0,.35)!important}.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);border-color:#F38020!important}.stButton>button[data-testid="baseButton-primary"],[data-testid="stFormSubmitButton"] button[kind="primary"],.stDownloadButton>button[data-testid="baseButton-primary"]{background:linear-gradient(145deg,#ffb15f,#F38020,#dc2626)!important;box-shadow:0 8px 0 #7f1d1d,0 20px 40px rgba(243,128,32,.32)!important}
input,textarea,[data-baseweb="select"]>div{background:rgba(5,6,8,.7)!important;border-radius:14px!important;border-color:rgba(255,255,255,.14)!important}.card{background:linear-gradient(145deg,#202638,#0b0d14);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px;text-align:center;box-shadow:0 15px 36px rgba(0,0,0,.38);margin-bottom:12px}.card .label{color:#a7adb8;font-size:12px;font-weight:900;text-transform:uppercase}.card .value{color:#F38020;font-size:34px;font-weight:900}.card .status{color:#d1d5db;font-size:12px}[data-testid="stMetric"]{background:#111827;border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px}
</style>
""", unsafe_allow_html=True)

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk"
conn = st.connection("gsheets", type=GSheetsConnection)

for chave, valor in {"logado": False, "perfil": "", "dados_carregados": False}.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

def logo():
    st.markdown("<div class='logo'>📦 SETOR <span>CAIXAS</span></div>", unsafe_allow_html=True)

def carregar_dados():
    try:
        estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
        estoque = estoque.dropna(subset=["Modelo"])
        estoque["Quantidade"] = pd.to_numeric(estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
    except Exception:
        st.error("⚠️ Falha de comunicação com o Google Drive.")
        st.stop()
    try:
        historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=600).copy()
        historico = historico.dropna(subset=["ID"])
    except Exception:
        historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
    return estoque, historico

def salvar_estoque(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)

def salvar_historico(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)

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

def registrar_movimento(acao, pessoa, modelo, quantidade, df_estoque, df_historico):
    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
    if acao == "Saída" and df_estoque.at[idx, "Quantidade"] < quantidade:
        st.error(f"⚠️ Saldo insuficiente! Temos {df_estoque.at[idx, 'Quantidade']} un.")
        return
    df_estoque.at[idx, "Quantidade"] += quantidade if acao == "Entrada" else -quantidade
    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": acao, "Separador": pessoa, "Modelo": modelo, "Quantidade": quantidade}])
    st.session_state.df_estoque = df_estoque
    st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
    salvar_estoque(df_estoque)
    salvar_historico(st.session_state.df_historico)
    st.success("✅ Movimento registrado com sucesso!")
    st.rerun()

if not st.session_state.logado:
    _, centro, _ = st.columns([1, 1.1, 1])
    with centro:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        logo()
        st.markdown("<h3 style='text-align:center'>Acesso ao Sistema</h3>", unsafe_allow_html=True)
        opcao = st.selectbox("Identifique seu perfil:", ["", "👀 Equipe (Visualização)", "⚙️ Controle (Marcello)", "👑 Coordenador"])
        if opcao == "👀 Equipe (Visualização)":
            if st.button("Acessar Estoque Livre", type="primary", use_container_width=True):
                st.session_state.logado = True
                st.session_state.perfil = "equipe"
                st.rerun()
        elif opcao == "⚙️ Controle (Marcello)":
            senha = st.text_input("Senha de Acesso:", type="password")
            if st.button("Entrar no Painel", type="primary", use_container_width=True):
                if senha == "marcello123":
                    st.session_state.logado = True
                    st.session_state.perfil = "marcello"
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        elif opcao == "👑 Coordenador":
            senha = st.text_input("Senha da Coordenação:", type="password")
            if st.button("Entrar no Painel", type="primary", use_container_width=True):
                if senha == "coord123":
                    st.session_state.logado = True
                    st.session_state.perfil = "coord"
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    if not st.session_state.dados_carregados:
        with st.spinner("⏳ Sincronizando com o banco de dados..."):
            st.session_state.df_estoque, st.session_state.df_historico = carregar_dados()
            st.session_state.dados_carregados = True

    df_estoque = st.session_state.df_estoque
    df_historico = st.session_state.df_historico
    separadores = ["Marcello", "Fabiano", "Sérgio"]
    modelos = sorted(df_estoque["Modelo"].tolist())

    with st.sidebar:
        logo()
        st.markdown("---")
        st.markdown(f"<div style='text-align:center;color:#888'>LOGADO COMO</div><div style='text-align:center;font-weight:900;color:#F38020'>{st.session_state.perfil.upper()}</div>", unsafe_allow_html=True)
        if st.button("🔄 Sincronizar Base", use_container_width=True):
            st.session_state.dados_carregados = False
            st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Sair (Logout)", type="primary", use_container_width=True):
            st.session_state.logado = False
            st.session_state.perfil = ""
            st.session_state.dados_carregados = False
            st.rerun()

    st.markdown("<section class='hero'><div class='eyebrow'>Setor Caixas • Portal Premium</div><div class='title'>Painel Operacional</div><p class='sub'>Controle de estoque com janelas independentes, cartões premium e botões 3D.</p></section>", unsafe_allow_html=True)
    zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
    if zerados:
        st.error(f"🚨 ALERTA: Há {len(zerados)} modelos com estoque totalmente zerado.")

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
            st.markdown("<div class='panel'><h3>📤 Janela de Saídas</h3><p class='sub'>Registre retiradas com validação automática de saldo.</p></div>", unsafe_allow_html=True)
            with st.form("form_saida", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                pessoa = c1.selectbox("Quem retirou?", [""] + separadores)
                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
                qtd = c3.number_input("Qtd", min_value=1, value=1)
                enviar = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)
            if enviar:
                registrar_movimento("Saída", pessoa, modelo, qtd, df_estoque, df_historico) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
        with abas[2]:
            st.markdown("<div class='panel'><h3>📥 Janela de Entradas</h3><p class='sub'>Lance produção e reposição no estoque conectado.</p></div>", unsafe_allow_html=True)
            with st.form("form_entrada", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                pessoa = c1.selectbox("Quem produziu?", [""] + separadores)
                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
                qtd = c3.number_input("Qtd", min_value=1, value=1)
                enviar = st.form_submit_button("Lançar no Estoque", type="primary", use_container_width=True)
            if enviar:
                registrar_movimento("Entrada", pessoa, modelo, qtd, df_estoque, df_historico) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
        with abas[3]:
            st.markdown("<div class='panel'><h3>📊 Janela de Indicadores</h3><p class='sub'>Acompanhe volume, itens críticos e movimentos por período.</p></div>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("📦 Peças no Estoque", int(df_estoque["Quantidade"].sum()))
            m2.metric("⚠️ Modelos Críticos", len(zerados))
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
            st.markdown("<div class='panel'><h3>🕒 Janela de Histórico</h3><p class='sub'>Últimos lançamentos sincronizados com a planilha.</p></div>", unsafe_allow_html=True)
            st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
        if st.session_state.perfil == "coord":
            with abas[5]:
                st.markdown("<div class='panel'><h3>👑 Janela Executiva</h3><p class='sub'>Exporte os dados para análise e conferência.</p></div>", unsafe_allow_html=True)
                csv = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button("📥 Baixar Excel (CSV)", csv, f"Caixas_{datetime.now().strftime('%d-%m')}.csv", "text/csv", type="primary", use_container_width=True)
