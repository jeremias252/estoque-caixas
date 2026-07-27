import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caixas - Portal", page_icon="📦", layout="centered")

# --- DESIGN ULTRA PREMIUM (CSS HACK) ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fundo geral mais escuro e limpo */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* =========================================
       CUSTOMIZAÇÃO DAS ABAS (JANELAS)
       ========================================= */
    div[data-baseweb="tab-list"] {
        gap: 8px; /* Espaço entre as abas */
        margin-bottom: 20px;
    }
    div[data-baseweb="tab"] {
        background-color: #1A1A1A !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: 1px solid #333 !important;
        transition: all 0.3s ease;
    }
    div[data-baseweb="tab"]:hover {
        border-color: #555 !important;
        background-color: #222 !important;
    }
    /* Aba selecionada */
    div[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.4) !important;
    }
    div[data-baseweb="tab"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    
    /* =========================================
       CUSTOMIZAÇÃO DA TELA DE LOGIN
       ========================================= */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 2rem;
    }
    .login-box {
        background: linear-gradient(145deg, #1c1c1c 0%, #121212 100%);
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        border: 1px solid #2a2a2a;
        width: 100%;
        max-width: 450px;
        text-align: center;
    }
    
    /* =========================================
       CUSTOMIZAÇÃO DE FORMULÁRIOS E BOTÕES
       ========================================= */
    [data-testid="stForm"] {
        background-color: #121212;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        border: 1px solid #333 !important;
        background-color: #1A1A1A !important;
        color: white !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        border-color: #F38020 !important;
        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.2) !important;
    }
    
    /* Botões Primários (Ação Principal) */
    .stButton>button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.3) !important;
    }
    .stButton>button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 6px 20px rgba(243, 128, 32, 0.6) !important;
    }
    
    /* Títulos Principais */
    .main-title {
        text-align: center;
        font-weight: 900;
        font-size: 32px;
        color: #ffffff;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
if "dados_carregados" not in st.session_state:
    st.session_state.dados_carregados = False

# URL DA PLANILHA GOOGLE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk"
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
        df_estoque = df_estoque.dropna(subset=["Modelo"])
        df_estoque["Quantidade"] = pd.to_numeric(df_estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
    except Exception as e:
        st.error("⚠️ Falha de comunicação com o Google Drive.")
        st.stop()

    try:
        df_historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=600).copy()
        df_historico = df_historico.dropna(subset=["ID"])
    except:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
    return df_estoque, df_historico

def salvar_estoque(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)

def salvar_historico(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)

@st.dialog("Detalhes do Modelo")
def abrir_janela_modelo(linha, df_linha, total):
    st.markdown(f"<h3 style='text-align:center; margin-bottom: 0;'>{linha}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#F38020; font-weight:bold; font-size:18px;'>Estoque Total: {total} un.</p>", unsafe_allow_html=True)
    st.divider()
    for i in range(0, len(df_linha), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(df_linha):
                row = df_linha.iloc[i+j]
                cor = row['Cor']
                qtd = int(row['Quantidade'])
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                card_html = f"""
                <div style="background-color: #111; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; margin-bottom: 10px;">
                    <div style="color: #888; font-size: 13px; font-weight: bold; text-transform: uppercase;">{cor}</div>
                    <div style="color: #F38020; font-size: 28px; font-weight: 900; margin: 5px 0;">{qtd}</div>
                    <div style="font-size: 11px; color: #AAA;">{status}</div>
                </div>
                """
                cols[j].markdown(card_html, unsafe_allow_html=True)

def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    if termo_busca:
        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
    if df_view.empty:
        st.warning("Nenhum modelo encontrado.")
        return

    def extrair_linha(nome): return nome.rsplit(" - ", 1)[0] if " - " in nome else nome
    def extrair_cor(nome): return nome.rsplit(" - ", 1)[1] if " - " in nome else "Padrão"

    df_view['Linha'] = df_view['Modelo'].apply(extrair_linha)
    df_view['Cor'] = df_view['Modelo'].apply(extrair_cor)
    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index().sort_values(by='Quantidade', ascending=False)
    
    st.markdown("<p style='color:#888; font-size:14px; text-align:center;'>Selecione um modelo para ver os detalhes:</p>", unsafe_allow_html=True)
    
    for i in range(0, len(df_totais), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(df_totais):
                row_total = df_totais.iloc[i+j]
                linha = row_total['Linha']
                total = int(row_total['Quantidade'])
                icone = "🔴" if total == 0 else ("🟡" if total <= 5 else "📦")
                
                if cols[j].button(f"{icone} {linha} ({total})", key=f"btn_{linha}", use_container_width=True):
                    df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
                    abrir_janela_modelo(linha, df_linha, total)

# --- LOGO SVG ---
logo_svg = """
<div style="display: flex; justify-content: center; margin-bottom: 20px;">
    <svg width="100%" viewBox="0 0 400 350" xmlns="http://www.w3.org/2000/svg" style="max-width: 220px;">
        <rect width="400" height="350" fill="transparent" rx="12"/>
        <path d="M 320 180 L 320 50 L 50 50 L 50 300 L 320 300 L 320 250" fill="none" stroke="#ffffff" stroke-width="12" />
        <text x="75" y="150" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="70" letter-spacing="2">SETOR</text>
        <text x="75" y="235" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="60" letter-spacing="1">CAIXAS</text>
        <line x1="290" y1="260" x2="380" y2="260" stroke="#F38020" stroke-width="12" />
    </svg>
</div>
"""

# ==========================================
# TELA 1: PORTAL DE ACESSO (LOGIN PREMIUM)
# ==========================================
if not st.session_state.logado:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    st.markdown(logo_svg, unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 20px; color: #fff;'>Acesso ao Sistema</h3>", unsafe_allow_html=True)
    
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
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TELA 2: DENTRO DO SISTEMA (DASHBOARD)
# ==========================================
else:
    if not st.session_state.dados_carregados:
        with st.spinner("⏳ Sincronizando com o banco de dados..."):
            e, h = carregar_dados()
            st.session_state.df_estoque = e
            st.session_state.df_historico = h
            st.session_state.dados_carregados = True

    df_estoque = st.session_state.df_estoque
    df_historico = st.session_state.df_historico
    separadores = ["Marcello", "Fabiano", "Sérgio"]
    lista_modelos = sorted(df_estoque["Modelo"].tolist())

    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"<div style='text-align:center; color:#888;'>LOGADO COMO</div><div style='text-align:center; font-weight:bold; font-size:18px; color:#F38020; margin-bottom:20px;'>{st.session_state.perfil.upper()}</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 Sincronizar Base", use_container_width=True):
        st.cache_data.clear()
        st.session_state.dados_carregados = False
        st.rerun()
        
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sair (Logout)", type="primary", use_container_width=True):
        st.session_state.logado = False
        st.session_state.perfil = ""
        st.session_state.dados_carregados = False
        st.rerun()

    st.markdown("<div class='main-title'>Painel Operacional</div>", unsafe_allow_html=True)

    zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
    if zerados:
        st.markdown(f"<div style='background-color:#3f0e0e; border-left:5px solid #ef4444; padding:15px; border-radius:8px; margin-bottom:20px; color:#fca5a5;'>🚨 <b>ALERTA:</b> Há {len(zerados)} modelos com estoque totalmente zerado.</div>", unsafe_allow_html=True)

    if st.session_state.perfil == "equipe":
        st.info("👋 Modo Visualização. Solicite retiradas ao responsável.")
        busca = st.text_input("🔍 Buscar modelo específico...", key="busca_equipe")
        st.divider()
        exibir_estoque_premium(df_estoque, busca)

    else:
        # ABAS MODERNAS (Agora formatadas pelo CSS como botões)
        abas_nomes = ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico", "👑 Excel"] if st.session_state.perfil == "coord" else ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico"]
        abas = st.tabs(abas_nomes)

        with abas[0]: 
            busca = st.text_input("🔍 Pesquisar no estoque...", key="busca_admin")
            st.divider()
            exibir_estoque_premium(df_estoque, busca)

        with abas[1]: 
            st.markdown("<h3 style='color:#ef4444; margin-bottom:20px;'>📤 Material Pego do Estoque</h3>", unsafe_allow_html=True)
            with st.form("form_saida", clear_on_submit=True):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1: sep = st.selectbox("Quem retirou?", [""] + separadores)
                with col2: modelo = st.selectbox("Qual Modelo?", [""] + lista_modelos)
                with col3: qtd = st.number_input("Qtd", min_value=1, value=1)
                st.markdown("<br>", unsafe_allow_html=True)
                submit_saida = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)

            if submit_saida:
                if not sep or not modelo: st.error("⚠️ Preencha os campos.")
                else:
                    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                    if df_estoque.at[idx, "Quantidade"] < qtd:
                        st.error(f"⚠️ Saldo insuficiente! Temos {df_estoque.at[idx, 'Quantidade']} un.")
                    else:
                        df_estoque.at[idx, "Quantidade"] -= qtd
                        st.session_state.df_estoque = df_estoque
                        novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Saída", "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
                        st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
                        salvar_estoque(df_estoque)
                        salvar_historico(st.session_state.df_historico)
                        st.success(f"✅ Saída registrada com sucesso!")
                        st.rerun()

        with abas[2]: 
            st.markdown("<h3 style='color:#10b981; margin-bottom:20px;'>📥 Material Feito de Estoque</h3>", unsafe_allow_html=True)
            with st.form("form_entrada", clear_on_submit=True):
                col1_in, col2_in, col3_in = st.columns([2, 3, 1])
                with col1_in: quem_fez = st.selectbox("Quem produziu?", [""] + separadores)
                with col2_in: modelo_rep = st.selectbox("Qual Modelo?", [""] + lista_modelos)
                with col3_in: qtd_rep = st.number_input("Qtd", min_value=1, value=1)
                st.markdown("<br>", unsafe_allow_html=True)
                submit_entrada = st.form_submit_button("Lançar no Estoque", type="primary", use_container_width=True)
                
                if submit_entrada:
                    if not modelo_rep or not quem_fez: st.error("⚠️ Preencha os campos.")
                    else:
                        idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                        df_estoque.at[idx, "Quantidade"] += qtd_rep
                        st.session_state.df_estoque = df_estoque
                        novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Entrada", "Separador": quem_fez, "Modelo": modelo_rep, "Quantidade": qtd_rep}])
                        st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
                        salvar_estoque(df_estoque)
                        salvar_historico(st.session_state.df_historico)
                        st.success("✅ Material lançado no estoque com sucesso!")
                        st.rerun()

        with abas[3]: 
            st.header("📊 Resumo Visual")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📦 Peças no Estoque", int(df_estoque["Quantidade"].sum()))
            col_m2.metric("⚠️ Modelos Críticos", len(zerados))
            st.divider()
            
            d_inicio, d_fim = st.columns(2)
            d_in = d_inicio.date_input("De:", datetime.now().replace(day=1))
            d_out = d_fim.date_input("Até:", datetime.now())
            
            if not df_historico.empty:
                df_h = df_historico.copy()
                df_h['Data_Filtro'] = pd.to_datetime(df_h['Data']).dt.date
                df_f = df_h[(df_h['Data_Filtro'] >= d_in) & (df_h['Data_Filtro'] <= d_out)]
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("**Produção (Entradas)**")
                    st.bar_chart(df_f[df_f["Ação"] == "Entrada"].groupby("Separador")["Quantidade"].sum(), color="#10b981")
                with col_g2:
                    st.markdown("**Consumo (Saídas)**")
                    st.bar_chart(df_f[df_f["Ação"] == "Saída"].groupby("Separador")["Quantidade"].sum(), color="#ef4444")

        with abas[4]: 
            st.header("🕒 Histórico Recente")
            st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)

        if st.session_state.perfil == "coord":
            with abas[5]: 
                st.header("👑 Download de Dados")
                if not df_historico.empty:
                    csv_convertido = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
                    st.download_button(label="📥 Baixar Excel (CSV)", data=csv_convertido, file_name=f"Caixas_{datetime.now().strftime('%d-%m')}.csv", mime="text/csv", type="primary", use_container_width=True)
