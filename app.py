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
-    /* Esconde elementos padrão do Streamlit */
+    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
+
     #MainMenu {visibility: hidden;}
     header {visibility: hidden;}
     footer {visibility: hidden;}
-    
-    /* Fundo geral mais escuro e limpo */
+
+    :root {
+        --bg: #07080d;
+        --panel: rgba(18, 20, 31, 0.86);
+        --panel-strong: rgba(25, 28, 42, 0.94);
+        --line: rgba(255, 255, 255, 0.12);
+        --muted: #9ca3af;
+        --text: #f8fafc;
+        --orange: #F38020;
+        --red: #dc2626;
+        --green: #10b981;
+        --shadow: 0 24px 80px rgba(0, 0, 0, 0.55);
+    }
+
+    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
+
     .stApp {
-        background-color: #0a0a0a;
+        color: var(--text);
+        background:
+            radial-gradient(circle at top left, rgba(243, 128, 32, 0.24), transparent 34rem),
+            radial-gradient(circle at top right, rgba(220, 38, 38, 0.18), transparent 30rem),
+            linear-gradient(135deg, #07080d 0%, #10131f 48%, #050608 100%);
     }
-    
-    /* =========================================
-       CUSTOMIZAÇÃO DAS ABAS (JANELAS)
-       ========================================= */
-    div[data-baseweb="tab-list"] {
-        gap: 8px; /* Espaço entre as abas */
-        margin-bottom: 20px;
+
+    .block-container {
+        max-width: 1180px;
+        padding-top: 2rem;
+        padding-bottom: 3rem;
     }
-    div[data-baseweb="tab"] {
-        background-color: #1A1A1A !important;
-        border-radius: 8px !important;
-        padding: 8px 16px !important;
-        border: 1px solid #333 !important;
-        transition: all 0.3s ease;
+
+    [data-testid="stSidebar"] {
+        background: linear-gradient(180deg, rgba(12, 14, 22, 0.98), rgba(20, 22, 32, 0.96));
+        border-right: 1px solid var(--line);
+        box-shadow: 16px 0 60px rgba(0,0,0,0.35);
     }
-    div[data-baseweb="tab"]:hover {
-        border-color: #555 !important;
-        background-color: #222 !important;
+
+    .hero-panel, .glass-window, [data-testid="stForm"] {
+        position: relative;
+        overflow: hidden;
+        background: linear-gradient(145deg, rgba(27, 31, 46, 0.92), rgba(10, 12, 18, 0.92));
+        border: 1px solid var(--line);
+        border-radius: 24px;
+        box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.08);
+        backdrop-filter: blur(16px);
     }
-    /* Aba selecionada */
-    div[data-baseweb="tab"][aria-selected="true"] {
-        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
-        border: none !important;
-        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.4) !important;
+
+    .hero-panel {
+        padding: 28px 30px;
+        margin-bottom: 24px;
     }
-    div[data-baseweb="tab"] p {
-        color: #ffffff !important;
-        font-weight: 700 !important;
-        font-size: 15px !important;
+
+    .hero-panel:before, .glass-window:before, [data-testid="stForm"]:before {
+        content: "";
+        position: absolute;
+        inset: 0;
+        pointer-events: none;
+        background: linear-gradient(120deg, rgba(255,255,255,0.10), transparent 34%, rgba(243,128,32,0.10));
     }
-    
-    /* =========================================
-       CUSTOMIZAÇÃO DA TELA DE LOGIN
-       ========================================= */
-    .login-container {
-        display: flex;
-        justify-content: center;
-        align-items: center;
-        margin-top: 2rem;
+
+    .eyebrow {
+        color: var(--orange);
+        font-size: 12px;
+        font-weight: 900;
+        letter-spacing: 0.18em;
+        text-transform: uppercase;
+        margin-bottom: 8px;
+    }
+
+    .main-title {
+        font-weight: 900;
+        font-size: clamp(34px, 5vw, 58px);
+        line-height: 0.95;
+        letter-spacing: -0.06em;
+        margin: 0;
+        color: #ffffff;
+        text-shadow: 0 10px 30px rgba(0,0,0,0.45);
     }
+
+    .subtitle {
+        color: #cbd5e1;
+        margin-top: 12px;
+        margin-bottom: 0;
+        font-size: 16px;
+    }
+
+    div[data-baseweb="tab-list"] {
+        gap: 12px;
+        padding: 10px;
+        margin-bottom: 22px;
+        background: rgba(8, 10, 16, 0.62);
+        border: 1px solid var(--line);
+        border-radius: 22px;
+        box-shadow: inset 0 2px 16px rgba(0,0,0,0.38);
+    }
+    div[data-baseweb="tab"] {
+        min-height: 52px;
+        background: linear-gradient(145deg, #242838, #0d0f17) !important;
+        border-radius: 16px !important;
+        padding: 10px 18px !important;
+        border: 1px solid rgba(255,255,255,0.10) !important;
+        box-shadow: 0 8px 0 #07080d, 0 18px 34px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.12) !important;
+        transition: all 0.18s ease;
+    }
+    div[data-baseweb="tab"]:hover { transform: translateY(-2px); border-color: rgba(243,128,32,0.8) !important; }
+    div[data-baseweb="tab"][aria-selected="true"] {
+        background: linear-gradient(145deg, #ff9d3f 0%, #F38020 45%, #b91c1c 100%) !important;
+        box-shadow: 0 8px 0 #7f1d1d, 0 18px 40px rgba(243, 128, 32, 0.35), inset 0 1px 0 rgba(255,255,255,0.35) !important;
+    }
+    div[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 900 !important; font-size: 15px !important; }
+
+    .login-container { display: flex; justify-content: center; align-items: center; min-height: 88vh; }
     .login-box {
-        background: linear-gradient(145deg, #1c1c1c 0%, #121212 100%);
-        padding: 40px;
-        border-radius: 16px;
-        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
-        border: 1px solid #2a2a2a;
+        background: linear-gradient(145deg, rgba(28,32,47,0.96), rgba(8,10,16,0.96));
+        padding: 42px;
+        border-radius: 30px;
+        box-shadow: 0 35px 100px rgba(0,0,0,0.66), inset 0 1px 0 rgba(255,255,255,0.12);
+        border: 1px solid rgba(255,255,255,0.14);
         width: 100%;
-        max-width: 450px;
+        max-width: 500px;
         text-align: center;
     }
-    
-    /* =========================================
-       CUSTOMIZAÇÃO DE FORMULÁRIOS E BOTÕES
-       ========================================= */
-    [data-testid="stForm"] {
-        background-color: #121212;
-        border: 1px solid #222;
-        border-radius: 12px;
-        padding: 25px;
-        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
+
+    [data-testid="stForm"] { padding: 28px; }
+
+    [data-testid="stMetric"] {
+        background: linear-gradient(145deg, rgba(30,34,49,0.92), rgba(10,12,18,0.94));
+        border: 1px solid var(--line);
+        border-radius: 22px;
+        padding: 18px;
+        box-shadow: 0 16px 44px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08);
     }
-    
-    .stButton>button {
-        border-radius: 8px !important;
-        font-weight: 700 !important;
-        transition: all 0.3s ease !important;
-        border: 1px solid #333 !important;
-        background-color: #1A1A1A !important;
+
+    .stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button {
+        border-radius: 16px !important;
+        font-weight: 900 !important;
+        min-height: 46px;
+        transition: all 0.16s ease !important;
+        border: 1px solid rgba(255,255,255,0.14) !important;
+        background: linear-gradient(145deg, #262b3c, #10131d) !important;
         color: white !important;
+        box-shadow: 0 7px 0 #050608, 0 16px 30px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.14) !important;
     }
-    .stButton>button:hover {
-        transform: translateY(-2px) !important;
-        border-color: #F38020 !important;
-        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.2) !important;
+    .stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stFormSubmitButton"] button:hover {
+        transform: translateY(-3px) !important;
+        border-color: rgba(243,128,32,0.9) !important;
+        box-shadow: 0 10px 0 #050608, 0 22px 38px rgba(243,128,32,0.18), inset 0 1px 0 rgba(255,255,255,0.18) !important;
     }
-    
-    /* Botões Primários (Ação Principal) */
-    .stButton>button[data-testid="baseButton-primary"] {
-        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
-        border: none !important;
-        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.3) !important;
+    .stButton>button:active, .stDownloadButton>button:active, [data-testid="stFormSubmitButton"] button:active { transform: translateY(4px) !important; box-shadow: 0 3px 0 #050608 !important; }
+    .stButton>button[data-testid="baseButton-primary"], [data-testid="stFormSubmitButton"] button[kind="primary"], .stDownloadButton>button[data-testid="baseButton-primary"] {
+        background: linear-gradient(145deg, #ffb15f 0%, #F38020 42%, #dc2626 100%) !important;
+        border: 1px solid rgba(255,255,255,0.18) !important;
+        box-shadow: 0 8px 0 #7f1d1d, 0 20px 42px rgba(243,128,32,0.32), inset 0 1px 0 rgba(255,255,255,0.35) !important;
     }
-    .stButton>button[data-testid="baseButton-primary"]:hover {
-        box-shadow: 0 6px 20px rgba(243, 128, 32, 0.6) !important;
+
+    input, textarea, [data-baseweb="select"] > div {
+        background: rgba(5, 6, 8, 0.68) !important;
+        border-color: rgba(255,255,255,0.12) !important;
+        border-radius: 14px !important;
     }
-    
-    /* Títulos Principais */
-    .main-title {
+
+    .premium-card {
+        background: linear-gradient(145deg, rgba(31,35,50,0.94), rgba(10,12,18,0.96));
+        border: 1px solid rgba(255,255,255,0.12);
+        border-radius: 20px;
+        padding: 16px;
         text-align: center;
-        font-weight: 900;
-        font-size: 32px;
-        color: #ffffff;
-        margin-bottom: 30px;
-        letter-spacing: 1px;
+        box-shadow: 0 16px 42px rgba(0,0,0,0.40), inset 0 1px 0 rgba(255,255,255,0.10);
+        margin-bottom: 12px;
     }
+    .premium-card .label { color: #a7adb8; font-size: 12px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.12em; }
+    .premium-card .value { color: var(--orange); font-size: 34px; font-weight: 900; margin: 4px 0; }
+    .premium-card .status { color: #d1d5db; font-size: 12px; }
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
@@ -143,54 +216,54 @@ def carregar_dados():
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
-                <div style="background-color: #111; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; margin-bottom: 10px;">
-                    <div style="color: #888; font-size: 13px; font-weight: bold; text-transform: uppercase;">{cor}</div>
-                    <div style="color: #F38020; font-size: 28px; font-weight: 900; margin: 5px 0;">{qtd}</div>
-                    <div style="font-size: 11px; color: #AAA;">{status}</div>
+                <div class="premium-card">
+                    <div class="label">{cor}</div>
+                    <div class="value">{qtd}</div>
+                    <div class="status">{status}</div>
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
@@ -267,129 +340,135 @@ else:
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
 
-    st.markdown("<div class='main-title'>Painel Operacional</div>", unsafe_allow_html=True)
+    st.markdown("""
+        <section class='hero-panel'>
+            <div class='eyebrow'>Setor Caixas • Portal Premium</div>
+            <h1 class='main-title'>Painel Operacional</h1>
+            <p class='subtitle'>Controle de estoque com janelas independentes, cartões de leitura rápida e botões 3D.</p>
+        </section>
+        """, unsafe_allow_html=True)
 
     zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
     if zerados:
         st.markdown(f"<div style='background-color:#3f0e0e; border-left:5px solid #ef4444; padding:15px; border-radius:8px; margin-bottom:20px; color:#fca5a5;'>🚨 <b>ALERTA:</b> Há {len(zerados)} modelos com estoque totalmente zerado.</div>", unsafe_allow_html=True)
 
     if st.session_state.perfil == "equipe":
-        st.info("👋 Modo Visualização. Solicite retiradas ao responsável.")
+        st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'>👋 <b>Modo Visualização.</b> Solicite retiradas ao responsável.</div>", unsafe_allow_html=True)
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
-            st.markdown("<h3 style='color:#ef4444; margin-bottom:20px;'>📤 Material Pego do Estoque</h3>", unsafe_allow_html=True)
+            st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'><h3 style='color:#ef4444; margin:0;'>📤 Janela de Saídas</h3><p class='subtitle'>Registre retiradas com validação automática de saldo.</p></div>", unsafe_allow_html=True)
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
-            st.markdown("<h3 style='color:#10b981; margin-bottom:20px;'>📥 Material Feito de Estoque</h3>", unsafe_allow_html=True)
+            st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'><h3 style='color:#10b981; margin:0;'>📥 Janela de Entradas</h3><p class='subtitle'>Lance produção e reposição no estoque conectado.</p></div>", unsafe_allow_html=True)
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
-            st.header("📊 Resumo Visual")
+            st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'><h3 style='margin:0;'>📊 Janela de Indicadores</h3><p class='subtitle'>Acompanhe volume, itens críticos e movimentos por período.</p></div>", unsafe_allow_html=True)
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
-            st.header("🕒 Histórico Recente")
+            st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'><h3 style='margin:0;'>🕒 Janela de Histórico</h3><p class='subtitle'>Últimos lançamentos sincronizados com a planilha.</p></div>", unsafe_allow_html=True)
             st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
 
         if st.session_state.perfil == "coord":
             with abas[5]: 
-                st.header("👑 Download de Dados")
+                st.markdown("<div class='glass-window' style='padding: 22px; margin-bottom: 18px;'><h3 style='margin:0;'>👑 Janela Executiva</h3><p class='subtitle'>Exporte os dados para análise e conferência.</p></div>", unsafe_allow_html=True)
                 if not df_historico.empty:
                     csv_convertido = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
                     st.download_button(label="📥 Baixar Excel (CSV)", data=csv_convertido, file_name=f"Caixas_{datetime.now().strftime('%d-%m')}.csv", mime="text/csv", type="primary", use_container_width=True)
 
EOF
)
