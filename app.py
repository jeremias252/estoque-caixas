import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caixas - Portal", page_icon="📦", layout="centered")

# --- DESIGN PREMIUM E MODO ESCURO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #333;
        background-color: #1A1A1A;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.3);
        border-color: #F38020;
    }
    
    .main-title {
        text-align: center;
        font-weight: 800;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #333333;
    }
    
    .login-box {
        background-color: #1A1A1A;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-top: 20px;
    }
    
    .alert-box {
        background-color: #3f0e0e;
        border-left: 5px solid #ef4444;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        color: #fca5a5;
    }
    
    /* Novos Banners Premium para as Janelas */
    .banner-saida {
        background: linear-gradient(90deg, #2b1111 0%, #1A1A1A 100%);
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #ef4444;
        margin-bottom: 20px;
        border-top: 1px solid #333;
        border-right: 1px solid #333;
        border-bottom: 1px solid #333;
    }
    
    .banner-entrada {
        background: linear-gradient(90deg, #0f2b18 0%, #1A1A1A 100%);
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #10b981;
        margin-bottom: 20px;
        border-top: 1px solid #333;
        border-right: 1px solid #333;
        border-bottom: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE SESSÃO (LOGIN) ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""

# URL DA PLANILHA GOOGLE (CAIXAS)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk"

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
        df_estoque = df_estoque.dropna(subset=["Modelo"])
        df_estoque["Quantidade"] = pd.to_numeric(df_estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
    except Exception as e:
        st.error("⚠️ Falha de comunicação com o Google Drive. A internet pode ter oscilado. Tente atualizar a página.")
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

# ==========================================
# JANELA FLUTUANTE (NOVA TELA DE DETALHES)
# ==========================================
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
                <div style="background-color: #0E1117; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333333; margin-bottom: 10px;">
                    <div style="color: #888888; font-size: 13px; font-weight: bold; text-transform: uppercase;">{cor}</div>
                    <div style="color: #F38020; font-size: 28px; font-weight: 900; margin: 5px 0;">{qtd}</div>
                    <div style="font-size: 11px; color: #AAAAAA;">{status}</div>
                </div>
                """
                cols[j].markdown(card_html, unsafe_allow_html=True)

# ==========================================
# CATÁLOGO DE ESTOQUE (TELA PRINCIPAL)
# ==========================================
def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    if termo_busca:
        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
        
    if df_view.empty:
        st.warning("Nenhum modelo encontrado.")
        return

    def extrair_linha(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[0]
        return nome
        
    def extrair_cor(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[1]
        return "Padrão"

    df_view['Linha'] = df_view['Modelo'].apply(extrair_linha)
    df_view['Cor'] = df_view['Modelo'].apply(extrair_cor)
    
    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index()
    df_totais = df_totais.sort_values(by='Quantidade', ascending=False)
    
    st.markdown("<p style='color:#888; font-size:14px;'>Toque em um modelo para ver as cores e o estoque:</p>", unsafe_allow_html=True)
    
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
<div style="display: flex; justify-content: center; margin-bottom: 10px;">
    <svg width="100%" viewBox="0 0 400 350" xmlns="http://www.w3.org/2000/svg" style="max-width: 250px;">
        <rect width="400" height="350" fill="transparent" rx="12"/>
        <path d="M 320 180 L 320 50 L 50 50 L 50 300 L 320 300 L 320 250" fill="none" stroke="#ffffff" stroke-width="12" />
        <text x="75" y="150" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="70" letter-spacing="2">SETOR</text>
        <text x="75" y="235" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="60" letter-spacing="1">CAIXAS</text>
        <text x="325" y="225" fill="#ffffff" font-family="Arial, sans-serif" font-weight="bold" font-size="28">.COM</text>
        <line x1="290" y1="260" x2="380" y2="260" stroke="#F38020" stroke-width="12" />
    </svg>
</div>
"""

# ==========================================
# TELA 1: PORTAL DE ACESSO (LOGIN)
# ==========================================
if not st.session_state.logado:
    st.markdown(logo_svg, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Portal de Acesso</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Identifique-se para entrar no sistema corporativo.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    opcao = st.selectbox("Quem está acessando?", ["", "👀 Visualizador (Equipe)", "⚙️ Controle (Marcello)", "👑 Coordenador"])
    
    if opcao == "👀 Visualizador (Equipe)":
        if st.button("Acessar Estoque", type="primary", use_container_width=True):
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

# ==========================================
# TELA 2: DENTRO DO SISTEMA (DASHBOARD)
# ==========================================
else:
    df_estoque, df_historico = carregar_dados()
    separadores = ["Marcello", "Fabiano", "Sérgio"]
    lista_modelos = sorted(df_estoque["Modelo"].tolist())

    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**👤 Logado como:**<br>{st.session_state.perfil.upper()}", unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sair do Sistema (Logout)", type="primary", use_container_width=True):
        st.session_state.logado = False
        st.session_state.perfil = ""
        st.rerun()

    st.markdown("<h1 class='main-title'>📦 Painel de Controle - CAIXAS</h1>", unsafe_allow_html=True)

    zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
    if zerados:
        st.markdown(f"<div class='alert-box'>🚨 <b>ATENÇÃO CRÍTICA:</b> Há {len(zerados)} modelos com estoque ZERADO!</div>", unsafe_allow_html=True)

    if st.session_state.perfil == "equipe":
        st.info("👋 Você está no Modo Visualização.")
        busca = st.text_input("🔍 Buscar modelo específico...", key="busca_equipe")
        st.divider()
        exibir_estoque_premium(df_estoque, busca)

    else:
        # ABAS COM NOMES ATUALIZADOS
        abas_nomes = ["🗂️ Catálogo", "📤 Pego do Estoque", "📥 Feito de Estoque", "📊 Dashboard", "🕒 Histórico", "👑 Fechamento"] if st.session_state.perfil == "coord" else ["🗂️ Catálogo", "📤 Pego do Estoque", "📥 Feito de Estoque", "📊 Dashboard", "🕒 Histórico"]
        abas = st.tabs(abas_nomes)

        with abas[0]: # ABA 1: SÓ CATÁLOGO
            st.header("🗂️ Catálogo de Estoque")
            busca = st.text_input("🔍 Buscar modelo...", key="busca_admin")
            st.divider()
            exibir_estoque_premium(df_estoque, busca)

        with abas[1]: # ABA 2: PEGO DO ESTOQUE
            # Banner Customizado Premium
            st.markdown("""
                <div class="banner-saida">
                    <h3 style="margin:0; color:#ffffff;">📤 Material que foi pego do estoque</h3>
                    <p style="margin:5px 0 0 0; font-size:14px; color:#aaaaaa;">Registre aqui as peças que estão sendo retiradas da prateleira para uso ou expedição.</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_saida", clear_on_submit=True):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1: sep = st.selectbox("1. Colaborador", [""] + separadores)
                with col2: modelo = st.selectbox("2. Modelo", [""] + lista_modelos)
                with col3: qtd = st.number_input("3. Qtd", min_value=1, value=1)
                submit_saida = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)

            if submit_saida:
                if not sep or not modelo: st.error("⚠️ Preencha os campos.")
                else:
                    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                    estoque_atual = df_estoque.at[idx, "Quantidade"]
                    if estoque_atual < qtd:
                        st.error(f"⚠️ Saldo insuficiente! Temos apenas {estoque_atual} un. deste modelo.")
                    else:
                        with st.spinner("Registrando saída..."):
                            df_estoque.at[idx, "Quantidade"] -= qtd
                            salvar_estoque(df_estoque)
                            novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Saída", "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
                            df_historico = pd.concat([novo, df_historico], ignore_index=True)
                            salvar_historico(df_historico)
                            st.cache_data.clear()
                        st.success(f"✅ Material pego do estoque registrado com sucesso!")
                        st.rerun()

        with abas[2]: # ABA 3: FEITO DE ESTOQUE
            # Banner Customizado Premium
            st.markdown("""
                <div class="banner-entrada">
                    <h3 style="margin:0; color:#ffffff;">📥 Material que foi feito de estoque</h3>
                    <p style="margin:5px 0 0 0; font-size:14px; color:#aaaaaa;">Adicione ao sistema as peças novas que foram produzidas e colocadas na prateleira.</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_entrada", clear_on_submit=True):
                col1_in, col2_in, col3_in = st.columns([2, 3, 1])
                with col1_in: quem_fez = st.selectbox("1. Quem produziu?", [""] + separadores)
                with col2_in: modelo_rep = st.selectbox("2. Modelo", [""] + lista_modelos)
                with col3_in: qtd_rep = st.number_input("3. Qtd", min_value=1, value=1)
                submit_entrada = st.form_submit_button("Lançar no Estoque", use_container_width=True)
                
                if submit_entrada:
                    if not modelo_rep or not quem_fez: st.error("⚠️ Preencha os campos.")
                    else:
                        with st.spinner("Registrando entrada..."):
                            idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                            df_estoque.at[idx, "Quantidade"] += qtd_rep
                            salvar_estoque(df_estoque)
                            novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Entrada", "Separador": quem_fez, "Modelo": modelo_rep, "Quantidade": qtd_rep}])
                            df_historico = pd.concat([novo, df_historico], ignore_index=True)
                            salvar_historico(df_historico)
                            st.cache_data.clear()
                        st.success("✅ Material feito de estoque lançado com sucesso!")
                        st.rerun()

        with abas[3]: # ABA 4: DASHBOARD
            st.header("📊 Indicadores de Estoque")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📦 Total de Peças", int(df_estoque["Quantidade"].sum()))
            col_m2.metric("⚠️ Modelos Zerados/Baixos", len(zerados))
            
            st.divider()
            st.subheader("📅 Filtrar Gráficos por Período")
            col_d1, col_d2 = st.columns(2)
            d_inicio = col_d1.date_input("Data Inicial", datetime.now().replace(day=1))
            d_fim = col_d2.date_input("Data Final", datetime.now())
            
            if not df_historico.empty:
                df_hist_copy = df_historico.copy()
                df_hist_copy['Data_Filtro'] = pd.to_datetime(df_hist_copy['Data']).dt.date
                df_filtrado = df_hist_copy[(df_hist_copy['Data_Filtro'] >= d_inicio) & (df_hist_copy['Data_Filtro'] <= d_fim)]
                
                df_saidas = df_filtrado[df_filtrado["Ação"] == "Saída"]
                df_entradas = df_filtrado[df_filtrado["Ação"] == "Entrada"]
                
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.subheader("🛠️ Quem mais Produziu?")
                    if not df_entradas.empty: st.bar_chart(df_entradas.groupby("Separador")["Quantidade"].sum(), color="#16a34a")
                with col_g2:
                    st.subheader("👤 Quem mais Retirou?")
                    if not df_saidas.empty: st.bar_chart(df_saidas.groupby("Separador")["Quantidade"].sum(), color="#dc2626")

        with abas[4]: # ABA 5: HISTÓRICO
            st.header("🕒 Histórico Recente")
            st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)

        if st.session_state.perfil == "coord":
            with abas[5]: # ABA 6: FECHAMENTO
                st.header("👑 Fechamento e Exportação")
                st.write("Baixe a planilha completa do histórico de movimentações.")
                
                if not df_historico.empty:
                    df_export = df_historico.drop(columns=["ID"], errors="ignore")
                    csv_convertido = df_export.to_csv(index=False, sep=";").encode("utf-8-sig")
                    
                    st.download_button(
                        label="📥 Baixar Relatório (Excel / CSV)",
                        data=csv_convertido,
                        file_name=f"Historico_Caixas_{datetime.now().strftime('%d-%m-%Y')}.csv",
                        mime="text/csv",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.info("Ainda não há histórico para baixar.")
