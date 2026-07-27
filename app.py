import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
 
-# --- CONFIGURAÇÃO DA PÁGINA ---
-st.set_page_config(page_title="Caixas - Portal", page_icon="📦", layout="centered")
+st.set_page_config(page_title="Caixas - Portal", page_icon="📦", layout="wide")
 
-# --- DESIGN ULTRA PREMIUM (CSS HACK) ---
 st.markdown("""
-    <style>
-    /* Esconde elementos padrão do Streamlit */
-    #MainMenu {visibility: hidden;}
-    header {visibility: hidden;}
-    footer {visibility: hidden;}
-    
-    /* Fundo geral mais escuro e limpo */
-    .stApp {
-        background-color: #0a0a0a;
-    }
-    
-    /* =========================================
-       CUSTOMIZAÇÃO DAS ABAS (JANELAS)
-       ========================================= */
-    div[data-baseweb="tab-list"] {
-        gap: 8px; /* Espaço entre as abas */
-        margin-bottom: 20px;
-    }
-    div[data-baseweb="tab"] {
-        background-color: #1A1A1A !important;
-        border-radius: 8px !important;
-        padding: 8px 16px !important;
-        border: 1px solid #333 !important;
-        transition: all 0.3s ease;
-    }
-    div[data-baseweb="tab"]:hover {
-        border-color: #555 !important;
-        background-color: #222 !important;
-    }
-    /* Aba selecionada */
-    div[data-baseweb="tab"][aria-selected="true"] {
-        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
-        border: none !important;
-        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.4) !important;
-    }
-    div[data-baseweb="tab"] p {
-        color: #ffffff !important;
-        font-weight: 700 !important;
-        font-size: 15px !important;
-    }
-    
-    /* =========================================
-       CUSTOMIZAÇÃO DA TELA DE LOGIN
-       ========================================= */
-    .login-container {
-        display: flex;
-        justify-content: center;
-        align-items: center;
-        margin-top: 2rem;
-    }
-    .login-box {
-        background: linear-gradient(145deg, #1c1c1c 0%, #121212 100%);
-        padding: 40px;
-        border-radius: 16px;
-        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
-        border: 1px solid #2a2a2a;
-        width: 100%;
-        max-width: 450px;
-        text-align: center;
-    }
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
-    }
-    
-    .stButton>button {
-        border-radius: 8px !important;
-        font-weight: 700 !important;
-        transition: all 0.3s ease !important;
-        border: 1px solid #333 !important;
-        background-color: #1A1A1A !important;
-        color: white !important;
-    }
-    .stButton>button:hover {
-        transform: translateY(-2px) !important;
-        border-color: #F38020 !important;
-        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.2) !important;
-    }
-    
-    /* Botões Primários (Ação Principal) */
-    .stButton>button[data-testid="baseButton-primary"] {
-        background: linear-gradient(90deg, #F38020 0%, #dc2626 100%) !important;
-        border: none !important;
-        box-shadow: 0 4px 15px rgba(243, 128, 32, 0.3) !important;
-    }
-    .stButton>button[data-testid="baseButton-primary"]:hover {
-        box-shadow: 0 6px 20px rgba(243, 128, 32, 0.6) !important;
-    }
-    
-    /* Títulos Principais */
-    .main-title {
-        text-align: center;
-        font-weight: 900;
-        font-size: 32px;
-        color: #ffffff;
-        margin-bottom: 30px;
-        letter-spacing: 1px;
-    }
-    </style>
-    """, unsafe_allow_html=True)
-
-# --- CONTROLE DE SESSÃO ---
-if "logado" not in st.session_state:
-    st.session_state.logado = False
-if "perfil" not in st.session_state:
-    st.session_state.perfil = ""
-if "dados_carregados" not in st.session_state:
-    st.session_state.dados_carregados = False
+<style>
+#MainMenu, header, footer {visibility:hidden;}
+.stApp{background:radial-gradient(circle at 12% 8%,rgba(243,128,32,.35),transparent 28rem),radial-gradient(circle at 86% 12%,rgba(220,38,38,.22),transparent 26rem),radial-gradient(circle at 50% 90%,rgba(14,165,233,.10),transparent 30rem),linear-gradient(135deg,#050608,#111827 50%,#050608);color:#f8fafc;}
+.block-container{max-width:1180px;padding-top:2rem;padding-bottom:3rem;}
+[data-testid="stSidebar"]{background:linear-gradient(180deg,#0b0d14,#171b28);border-right:1px solid rgba(255,255,255,.12);}
+.hero,.panel,[data-testid="stForm"]{position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(31,36,55,.92),rgba(7,9,16,.96));border:1px solid rgba(255,255,255,.14);border-radius:28px;box-shadow:0 28px 80px rgba(0,0,0,.52),inset 0 1px 0 rgba(255,255,255,.14);padding:26px;margin-bottom:22px;backdrop-filter:blur(18px)}.hero:before,.panel:before,[data-testid="stForm"]:before{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(120deg,rgba(255,255,255,.12),transparent 35%,rgba(243,128,32,.12))}.hero>*{position:relative}.hero{padding:32px}.hero-top{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap}.badge{display:inline-flex;gap:8px;align-items:center;background:rgba(243,128,32,.13);border:1px solid rgba(243,128,32,.42);color:#fed7aa;border-radius:999px;padding:8px 12px;font-weight:900;font-size:12px;letter-spacing:.08em}.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px}.kpi{background:rgba(5,7,12,.48);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:14px 16px;box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}.kpi b{display:block;font-size:24px;color:#fff}.kpi span{color:#9ca3af;font-size:12px;font-weight:800;text-transform:uppercase}.danger-glow{border-left:5px solid #ef4444;background:linear-gradient(90deg,rgba(127,29,29,.8),rgba(31,41,55,.75));border-radius:18px;padding:16px;margin-bottom:18px;color:#fecaca}.login-wrap{min-height:82vh;display:flex;align-items:center}.profile-pill{background:rgba(5,7,12,.54);border:1px solid rgba(255,255,255,.13);border-radius:18px;padding:12px;text-align:center;margin:14px 0;color:#cbd5e1}.profile-pill b{color:#F38020}.window-title{margin:0;font-weight:900}.window-sub{color:#cbd5e1;margin:6px 0 0}.divider-glow{height:1px;background:linear-gradient(90deg,transparent,rgba(243,128,32,.8),transparent);margin:18px 0}.role-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0}.role-card{background:rgba(5,7,12,.48);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:12px;text-align:center}.role-card b{display:block;color:#fff}.role-card span{font-size:12px;color:#9ca3af}.history-card{display:grid;grid-template-columns:1.1fr .8fr 1fr 2fr .7fr;gap:10px;align-items:center;background:linear-gradient(145deg,rgba(24,29,43,.92),rgba(8,10,16,.96));border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:12px 14px;margin-bottom:10px;box-shadow:0 12px 30px rgba(0,0,0,.28)}.history-head{color:#9ca3af;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.history-action{font-weight:900;border-radius:999px;padding:6px 10px;text-align:center}.entrada{background:rgba(16,185,129,.15);color:#86efac;border:1px solid rgba(16,185,129,.35)}.saida{background:rgba(239,68,68,.15);color:#fecaca;border:1px solid rgba(239,68,68,.35)}.qty-badge{font-weight:900;color:#F38020;text-align:center}
+.logo{font-size:34px;font-weight:900;text-align:center;letter-spacing:-1px;margin-bottom:14px;text-shadow:0 10px 30px rgba(0,0,0,.45)}.logo span{background:linear-gradient(90deg,#ffbd77,#F38020,#ef4444);-webkit-background-clip:text;color:transparent}.eyebrow{color:#F38020;font-size:12px;font-weight:900;letter-spacing:.18em;text-transform:uppercase}.title{font-size:clamp(38px,5vw,64px);font-weight:900;line-height:.92;margin:8px 0;letter-spacing:-.05em}.sub{color:#cbd5e1;margin:8px 0 0;max-width:720px}
+div[data-baseweb="tab-list"]{gap:14px;background:linear-gradient(145deg,rgba(3,5,10,.72),rgba(20,24,36,.58));border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:12px;margin-bottom:24px;box-shadow:inset 0 2px 18px rgba(0,0,0,.45),0 18px 45px rgba(0,0,0,.25)}div[data-baseweb="tab"]{min-height:54px;background:linear-gradient(145deg,#2b3145,#0e111a)!important;border:1px solid rgba(255,255,255,.14)!important;border-radius:18px!important;box-shadow:0 8px 0 #050608,0 18px 32px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.12)!important;padding:12px 18px!important;transition:.18s ease!important}div[data-baseweb="tab"]:hover{transform:translateY(-3px);border-color:rgba(243,128,32,.82)!important;filter:brightness(1.12)}div[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(145deg,#ffc078,#F38020 48%,#991b1b)!important;box-shadow:0 8px 0 #7f1d1d,0 22px 42px rgba(243,128,32,.38),inset 0 1px 0 rgba(255,255,255,.28)!important}div[data-baseweb="tab"] p{color:white!important;font-weight:900!important;letter-spacing:.01em}
+.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:15px!important;font-weight:900!important;min-height:45px;background:linear-gradient(145deg,#262b3c,#10131d)!important;color:white!important;border:1px solid rgba(255,255,255,.14)!important;box-shadow:0 7px 0 #050608,0 15px 28px rgba(0,0,0,.35)!important}.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);border-color:#F38020!important}.stButton>button[data-testid="baseButton-primary"],[data-testid="stFormSubmitButton"] button[kind="primary"],.stDownloadButton>button[data-testid="baseButton-primary"]{background:linear-gradient(145deg,#ffb15f,#F38020,#dc2626)!important;box-shadow:0 8px 0 #7f1d1d,0 20px 40px rgba(243,128,32,.32)!important}
+input,textarea,[data-baseweb="select"]>div{background:rgba(5,6,8,.7)!important;border-radius:14px!important;border-color:rgba(255,255,255,.14)!important}.card{background:linear-gradient(145deg,#202638,#0b0d14);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px;text-align:center;box-shadow:0 15px 36px rgba(0,0,0,.38);margin-bottom:12px}.card .label{color:#a7adb8;font-size:12px;font-weight:900;text-transform:uppercase}.card .value{color:#F38020;font-size:34px;font-weight:900}.card .status{color:#d1d5db;font-size:12px}[data-testid="stMetric"]{background:#111827;border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px}
+</style>
+""", unsafe_allow_html=True)
 
-# URL DA PLANILHA GOOGLE
 URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk"
 conn = st.connection("gsheets", type=GSheetsConnection)
 
+for chave, valor in {"logado": False, "perfil": "", "dados_carregados": False}.items():
+    if chave not in st.session_state:
+        st.session_state[chave] = valor
+
+def logo():
+    st.markdown("<div class='logo'>⬢ SETOR <span>CAIXAS</span></div>", unsafe_allow_html=True)
+
 def carregar_dados():
     try:
-        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
-        df_estoque = df_estoque.dropna(subset=["Modelo"])
-        df_estoque["Quantidade"] = pd.to_numeric(df_estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
-    except Exception as e:
+        estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
+        estoque = estoque.dropna(subset=["Modelo"])
+        estoque["Quantidade"] = pd.to_numeric(estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
+    except Exception:
         st.error("⚠️ Falha de comunicação com o Google Drive.")
         st.stop()
-
     try:
-        df_historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=600).copy()
-        df_historico = df_historico.dropna(subset=["ID"])
-    except:
-        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
-    return df_estoque, df_historico
+        historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=600).copy()
+        historico = historico.dropna(subset=["ID"])
+    except Exception:
+        historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
+    return estoque, historico
 
 def salvar_estoque(df):
     conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)
 
 def salvar_historico(df):
     conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)
 
 @st.dialog("Detalhes do Modelo")
 def abrir_janela_modelo(linha, df_linha, total):
-    st.markdown(f"<h3 style='text-align:center; margin-bottom: 0;'>{linha}</h3>", unsafe_allow_html=True)
-    st.markdown(f"<p style='text-align:center; color:#F38020; font-weight:bold; font-size:18px;'>Estoque Total: {total} un.</p>", unsafe_allow_html=True)
+    st.markdown(f"<h3 style='text-align:center'>{linha}</h3>", unsafe_allow_html=True)
+    st.markdown(f"<p style='text-align:center;color:#F38020;font-weight:900'>Estoque Total: {total} un.</p>", unsafe_allow_html=True)
     st.divider()
     for i in range(0, len(df_linha), 2):
         cols = st.columns(2)
         for j in range(2):
             if i + j < len(df_linha):
-                row = df_linha.iloc[i+j]
-                cor = row['Cor']
-                qtd = int(row['Quantidade'])
+                row = df_linha.iloc[i + j]
+                qtd = int(row["Quantidade"])
                 status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
-                card_html = f"""
-                <div style="background-color: #111; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; margin-bottom: 10px;">
-                    <div style="color: #888; font-size: 13px; font-weight: bold; text-transform: uppercase;">{cor}</div>
-                    <div style="color: #F38020; font-size: 28px; font-weight: 900; margin: 5px 0;">{qtd}</div>
-                    <div style="font-size: 11px; color: #AAA;">{status}</div>
-                </div>
-                """
-                cols[j].markdown(card_html, unsafe_allow_html=True)
+                cols[j].markdown(f"<div class='card'><div class='label'>{row['Cor']}</div><div class='value'>{qtd}</div><div class='status'>{status}</div></div>", unsafe_allow_html=True)
 
-def exibir_estoque_premium(df_base, termo_busca=""):
-    df_view = df_base.copy()
+def exibir_estoque(df_base, termo_busca=""):
+    df = df_base.copy()
     if termo_busca:
-        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
-    if df_view.empty:
+        df = df[df["Modelo"].str.contains(termo_busca, case=False, na=False)]
+    if df.empty:
         st.warning("Nenhum modelo encontrado.")
         return
-
-    def extrair_linha(nome): return nome.rsplit(" - ", 1)[0] if " - " in nome else nome
-    def extrair_cor(nome): return nome.rsplit(" - ", 1)[1] if " - " in nome else "Padrão"
-
-    df_view['Linha'] = df_view['Modelo'].apply(extrair_linha)
-    df_view['Cor'] = df_view['Modelo'].apply(extrair_cor)
-    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index().sort_values(by='Quantidade', ascending=False)
-    
-    st.markdown("<p style='color:#888; font-size:14px; text-align:center;'>Selecione um modelo para ver os detalhes:</p>", unsafe_allow_html=True)
-    
-    for i in range(0, len(df_totais), 2):
+    df["Linha"] = df["Modelo"].apply(lambda n: n.rsplit(" - ", 1)[0] if " - " in n else n)
+    df["Cor"] = df["Modelo"].apply(lambda n: n.rsplit(" - ", 1)[1] if " - " in n else "Padrão")
+    totais = df.groupby("Linha")["Quantidade"].sum().reset_index().sort_values("Quantidade", ascending=False)
+    st.markdown("<p style='color:#9ca3af;text-align:center'>Selecione um modelo para ver os detalhes:</p>", unsafe_allow_html=True)
+    for i in range(0, len(totais), 2):
         cols = st.columns(2)
         for j in range(2):
-            if i + j < len(df_totais):
-                row_total = df_totais.iloc[i+j]
-                linha = row_total['Linha']
-                total = int(row_total['Quantidade'])
+            if i + j < len(totais):
+                linha = totais.iloc[i + j]["Linha"]
+                total = int(totais.iloc[i + j]["Quantidade"])
                 icone = "🔴" if total == 0 else ("🟡" if total <= 5 else "📦")
-                
                 if cols[j].button(f"{icone} {linha} ({total})", key=f"btn_{linha}", use_container_width=True):
-                    df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
-                    abrir_janela_modelo(linha, df_linha, total)
+                    abrir_janela_modelo(linha, df[df["Linha"] == linha].sort_values("Cor"), total)
+
 
-# --- LOGO SVG ---
-logo_svg = """
-<div style="display: flex; justify-content: center; margin-bottom: 20px;">
-    <svg width="100%" viewBox="0 0 400 350" xmlns="http://www.w3.org/2000/svg" style="max-width: 220px;">
-        <rect width="400" height="350" fill="transparent" rx="12"/>
-        <path d="M 320 180 L 320 50 L 50 50 L 50 300 L 320 300 L 320 250" fill="none" stroke="#ffffff" stroke-width="12" />
-        <text x="75" y="150" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="70" letter-spacing="2">SETOR</text>
-        <text x="75" y="235" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="60" letter-spacing="1">CAIXAS</text>
-        <line x1="290" y1="260" x2="380" y2="260" stroke="#F38020" stroke-width="12" />
-    </svg>
-</div>
-"""
+def exibir_historico_bonito(df_historico):
+    if df_historico.empty:
+        st.info("Nenhum lançamento no histórico ainda.")
+        return
+    df = df_historico.drop(columns=["ID"], errors="ignore").head(80).copy()
+    st.markdown("""
+    <div class='history-card history-head'>
+        <div>Data</div><div>Ação</div><div>Separador</div><div>Modelo</div><div>Qtd</div>
+    </div>
+    """, unsafe_allow_html=True)
+    for _, row in df.iterrows():
+        acao = str(row.get("Ação", ""))
+        classe = "entrada" if acao == "Entrada" else "saida"
+        icone = "📥" if acao == "Entrada" else "📤"
+        st.markdown(f"""
+        <div class='history-card'>
+            <div>{row.get('Data', '')}</div>
+            <div class='history-action {classe}'>{icone} {acao}</div>
+            <div>{row.get('Separador', '')}</div>
+            <div>{row.get('Modelo', '')}</div>
+            <div class='qty-badge'>{row.get('Quantidade', '')}</div>
+        </div>
+        """, unsafe_allow_html=True)
+
+def registrar_movimento(acao, pessoa, modelo, quantidade, df_estoque, df_historico):
+    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
+    if acao == "Saída" and df_estoque.at[idx, "Quantidade"] < quantidade:
+        st.error(f"⚠️ Saldo insuficiente! Temos {df_estoque.at[idx, 'Quantidade']} un.")
+        return
+    df_estoque.at[idx, "Quantidade"] += quantidade if acao == "Entrada" else -quantidade
+    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": acao, "Separador": pessoa, "Modelo": modelo, "Quantidade": quantidade}])
+    st.session_state.df_estoque = df_estoque
+    st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
+    salvar_estoque(df_estoque)
+    salvar_historico(st.session_state.df_historico)
+    st.success("✅ Movimento registrado com sucesso!")
+    st.rerun()
 
-# ==========================================
-# TELA 1: PORTAL DE ACESSO (LOGIN PREMIUM)
-# ==========================================
 if not st.session_state.logado:
-    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
-    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
-    
-    st.markdown(logo_svg, unsafe_allow_html=True)
-    st.markdown("<h3 style='margin-bottom: 20px; color: #fff;'>Acesso ao Sistema</h3>", unsafe_allow_html=True)
-    
-    opcao = st.selectbox("Identifique seu perfil:", ["", "👀 Equipe (Visualização)", "⚙️ Controle (Marcello)", "👑 Coordenador"])
-    
-    if opcao == "👀 Equipe (Visualização)":
-        if st.button("Acessar Estoque Livre", type="primary", use_container_width=True):
-            st.session_state.logado = True
-            st.session_state.perfil = "equipe"
-            st.rerun()
-            
-    elif opcao == "⚙️ Controle (Marcello)":
-        senha = st.text_input("Senha de Acesso:", type="password")
-        if st.button("Entrar no Painel", type="primary", use_container_width=True):
-            if senha == "marcello123":
-                st.session_state.logado = True
-                st.session_state.perfil = "marcello"
-                st.rerun()
-            else:
-                st.error("❌ Senha incorreta!")
-                
-    elif opcao == "👑 Coordenador":
-        senha = st.text_input("Senha da Coordenação:", type="password")
-        if st.button("Entrar no Painel", type="primary", use_container_width=True):
-            if senha == "coord123":
+    _, centro, _ = st.columns([1, 1.05, 1])
+    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
+    with centro:
+        st.markdown("<div class='panel'>", unsafe_allow_html=True)
+        logo()
+        st.markdown("<div class='badge' style='margin:auto;width:max-content'>ACESSO SEGURO</div><h3 style='text-align:center;margin-top:14px'>Acesso ao Sistema</h3><p class='sub' style='text-align:center'>Escolha seu perfil para abrir a janela correta do estoque.</p><div class='divider-glow'></div>", unsafe_allow_html=True)
+        st.markdown("""
+        <div class='role-grid'>
+            <div class='role-card'><b>👀 Equipe</b><span>consulta rápida</span></div>
+            <div class='role-card'><b>⚙️ Controle</b><span>entradas e saídas</span></div>
+            <div class='role-card'><b>👑 Coord.</b><span>exportação e gestão</span></div>
+        </div>
+        """, unsafe_allow_html=True)
+        opcao = st.selectbox("Identifique seu perfil:", ["", "👀 Equipe (Visualização)", "⚙️ Controle (Marcello)", "👑 Coordenador"])
+        if opcao == "👀 Equipe (Visualização)":
+            if st.button("Acessar Estoque Livre", type="primary", use_container_width=True):
                 st.session_state.logado = True
-                st.session_state.perfil = "coord"
+                st.session_state.perfil = "equipe"
                 st.rerun()
-            else:
-                st.error("❌ Senha incorreta!")
-                
-    st.markdown("</div>", unsafe_allow_html=True)
+        elif opcao == "⚙️ Controle (Marcello)":
+            senha = st.text_input("Senha de Acesso:", type="password")
+            if st.button("Entrar no Painel", type="primary", use_container_width=True):
+                if senha == "marcello123":
+                    st.session_state.logado = True
+                    st.session_state.perfil = "marcello"
+                    st.rerun()
+                else:
+                    st.error("❌ Senha incorreta!")
+        elif opcao == "👑 Coordenador":
+            senha = st.text_input("Senha da Coordenação:", type="password")
+            if st.button("Entrar no Painel", type="primary", use_container_width=True):
+                if senha == "coord123":
+                    st.session_state.logado = True
+                    st.session_state.perfil = "coord"
+                    st.rerun()
+                else:
+                    st.error("❌ Senha incorreta!")
+        st.markdown("</div>", unsafe_allow_html=True)
     st.markdown("</div>", unsafe_allow_html=True)
-
-# ==========================================
-# TELA 2: DENTRO DO SISTEMA (DASHBOARD)
-# ==========================================
 else:
     if not st.session_state.dados_carregados:
         with st.spinner("⏳ Sincronizando com o banco de dados..."):
-            e, h = carregar_dados()
-            st.session_state.df_estoque = e
-            st.session_state.df_historico = h
+            st.session_state.df_estoque, st.session_state.df_historico = carregar_dados()
             st.session_state.dados_carregados = True
 
     df_estoque = st.session_state.df_estoque
     df_historico = st.session_state.df_historico
     separadores = ["Marcello", "Fabiano", "Sérgio"]
-    lista_modelos = sorted(df_estoque["Modelo"].tolist())
-
-    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
-    st.sidebar.markdown("---")
-    st.sidebar.markdown(f"<div style='text-align:center; color:#888;'>LOGADO COMO</div><div style='text-align:center; font-weight:bold; font-size:18px; color:#F38020; margin-bottom:20px;'>{st.session_state.perfil.upper()}</div>", unsafe_allow_html=True)
-    
-    if st.sidebar.button("🔄 Sincronizar Base", use_container_width=True):
-        st.cache_data.clear()
-        st.session_state.dados_carregados = False
-        st.rerun()
-        
-    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
-    if st.sidebar.button("🚪 Sair (Logout)", type="primary", use_container_width=True):
-        st.session_state.logado = False
-        st.session_state.perfil = ""
-        st.session_state.dados_carregados = False
-        st.rerun()
+    modelos = sorted(df_estoque["Modelo"].tolist())
 
-    st.markdown("<div class='main-title'>Painel Operacional</div>", unsafe_allow_html=True)
+    with st.sidebar:
+        logo()
+        st.markdown("---")
+        st.markdown(f"<div class='profile-pill'><span>LOGADO COMO</span><br><b>{st.session_state.perfil.upper()}</b></div>", unsafe_allow_html=True)
+        if st.button("🔄 Sincronizar Base", use_container_width=True):
+            st.session_state.dados_carregados = False
+            st.rerun()
+        st.markdown("<br><br>", unsafe_allow_html=True)
+        if st.button("🚪 Sair (Logout)", type="primary", use_container_width=True):
+            st.session_state.logado = False
+            st.session_state.perfil = ""
+            st.session_state.dados_carregados = False
+            st.rerun()
 
     zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
+    total_pecas = int(df_estoque["Quantidade"].sum())
+    total_modelos = len(df_estoque)
+    st.markdown(f"""
+    <section class='hero'>
+        <div class='hero-top'>
+            <div>
+                <div class='badge'>⬢ OPERAÇÃO PREMIUM</div>
+                <div class='title'>Painel Operacional</div>
+                <p class='sub'>Controle de estoque com janelas independentes, cartões premium, botões 3D e leitura rápida dos indicadores.</p>
+            </div>
+            <div class='badge'>PERFIL {st.session_state.perfil.upper()}</div>
+        </div>
+        <div class='kpis'>
+            <div class='kpi'><span>Peças em estoque</span><b>{total_pecas}</b></div>
+            <div class='kpi'><span>Modelos cadastrados</span><b>{total_modelos}</b></div>
+            <div class='kpi'><span>Itens zerados</span><b>{len(zerados)}</b></div>
+        </div>
+    </section>
+    """, unsafe_allow_html=True)
     if zerados:
-        st.markdown(f"<div style='background-color:#3f0e0e; border-left:5px solid #ef4444; padding:15px; border-radius:8px; margin-bottom:20px; color:#fca5a5;'>🚨 <b>ALERTA:</b> Há {len(zerados)} modelos com estoque totalmente zerado.</div>", unsafe_allow_html=True)
+        st.markdown(f"<div class='danger-glow'>🚨 <b>ALERTA:</b> Há {len(zerados)} modelos com estoque totalmente zerado.</div>", unsafe_allow_html=True)
 
     if st.session_state.perfil == "equipe":
-        st.info("👋 Modo Visualização. Solicite retiradas ao responsável.")
-        busca = st.text_input("🔍 Buscar modelo específico...", key="busca_equipe")
-        st.divider()
-        exibir_estoque_premium(df_estoque, busca)
-
+        st.markdown("<div class='panel'>👋 <b>Modo Visualização.</b> Solicite retiradas ao responsável.</div>", unsafe_allow_html=True)
+        busca = st.text_input("🔍 Buscar modelo específico...")
+        exibir_estoque(df_estoque, busca)
     else:
-        # ABAS MODERNAS (Agora formatadas pelo CSS como botões)
-        abas_nomes = ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico", "👑 Excel"] if st.session_state.perfil == "coord" else ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico"]
-        abas = st.tabs(abas_nomes)
-
-        with abas[0]: 
-            busca = st.text_input("🔍 Pesquisar no estoque...", key="busca_admin")
-            st.divider()
-            exibir_estoque_premium(df_estoque, busca)
+        nomes = ["🗂️ Catálogo", "📤 Saídas", "📥 Entradas", "📊 Gráficos", "🕒 Histórico"]
+        if st.session_state.perfil == "coord":
+            nomes.append("👑 Excel")
+        abas = st.tabs(nomes)
 
-        with abas[1]: 
-            st.markdown("<h3 style='color:#ef4444; margin-bottom:20px;'>📤 Material Pego do Estoque</h3>", unsafe_allow_html=True)
+        with abas[0]:
+            busca = st.text_input("🔍 Pesquisar no estoque...")
+            exibir_estoque(df_estoque, busca)
+        with abas[1]:
+            st.markdown("<div class='panel'><h3 class='window-title'>📤 Janela de Saídas</h3><p class='window-sub'>Registre retiradas com validação automática de saldo.</p></div>", unsafe_allow_html=True)
             with st.form("form_saida", clear_on_submit=True):
-                col1, col2, col3 = st.columns([2, 3, 1])
-                with col1: sep = st.selectbox("Quem retirou?", [""] + separadores)
-                with col2: modelo = st.selectbox("Qual Modelo?", [""] + lista_modelos)
-                with col3: qtd = st.number_input("Qtd", min_value=1, value=1)
-                st.markdown("<br>", unsafe_allow_html=True)
-                submit_saida = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)
-
-            if submit_saida:
-                if not sep or not modelo: st.error("⚠️ Preencha os campos.")
-                else:
-                    idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
-                    if df_estoque.at[idx, "Quantidade"] < qtd:
-                        st.error(f"⚠️ Saldo insuficiente! Temos {df_estoque.at[idx, 'Quantidade']} un.")
-                    else:
-                        df_estoque.at[idx, "Quantidade"] -= qtd
-                        st.session_state.df_estoque = df_estoque
-                        novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Saída", "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
-                        st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
-                        salvar_estoque(df_estoque)
-                        salvar_historico(st.session_state.df_historico)
-                        st.success(f"✅ Saída registrada com sucesso!")
-                        st.rerun()
-
-        with abas[2]: 
-            st.markdown("<h3 style='color:#10b981; margin-bottom:20px;'>📥 Material Feito de Estoque</h3>", unsafe_allow_html=True)
+                c1, c2, c3 = st.columns([2, 3, 1])
+                pessoa = c1.selectbox("Quem retirou?", [""] + separadores)
+                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
+                qtd = c3.number_input("Qtd", min_value=1, value=1)
+                enviar = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)
+            if enviar:
+                registrar_movimento("Saída", pessoa, modelo, qtd, df_estoque, df_historico) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
+        with abas[2]:
+            st.markdown("<div class='panel'><h3 class='window-title'>📥 Janela de Entradas</h3><p class='window-sub'>Lance produção e reposição no estoque conectado.</p></div>", unsafe_allow_html=True)
             with st.form("form_entrada", clear_on_submit=True):
-                col1_in, col2_in, col3_in = st.columns([2, 3, 1])
-                with col1_in: quem_fez = st.selectbox("Quem produziu?", [""] + separadores)
-                with col2_in: modelo_rep = st.selectbox("Qual Modelo?", [""] + lista_modelos)
-                with col3_in: qtd_rep = st.number_input("Qtd", min_value=1, value=1)
-                st.markdown("<br>", unsafe_allow_html=True)
-                submit_entrada = st.form_submit_button("Lançar no Estoque", type="primary", use_container_width=True)
-                
-                if submit_entrada:
-                    if not modelo_rep or not quem_fez: st.error("⚠️ Preencha os campos.")
-                    else:
-                        idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
-                        df_estoque.at[idx, "Quantidade"] += qtd_rep
-                        st.session_state.df_estoque = df_estoque
-                        novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Entrada", "Separador": quem_fez, "Modelo": modelo_rep, "Quantidade": qtd_rep}])
-                        st.session_state.df_historico = pd.concat([novo, df_historico], ignore_index=True)
-                        salvar_estoque(df_estoque)
-                        salvar_historico(st.session_state.df_historico)
-                        st.success("✅ Material lançado no estoque com sucesso!")
-                        st.rerun()
-
-        with abas[3]: 
-            st.header("📊 Resumo Visual")
-            col_m1, col_m2 = st.columns(2)
-            col_m1.metric("📦 Peças no Estoque", int(df_estoque["Quantidade"].sum()))
-            col_m2.metric("⚠️ Modelos Críticos", len(zerados))
-            st.divider()
-            
-            d_inicio, d_fim = st.columns(2)
-            d_in = d_inicio.date_input("De:", datetime.now().replace(day=1))
-            d_out = d_fim.date_input("Até:", datetime.now())
-            
+                c1, c2, c3 = st.columns([2, 3, 1])
+                pessoa = c1.selectbox("Quem produziu?", [""] + separadores)
+                modelo = c2.selectbox("Qual Modelo?", [""] + modelos)
+                qtd = c3.number_input("Qtd", min_value=1, value=1)
+                enviar = st.form_submit_button("Lançar no Estoque", type="primary", use_container_width=True)
+            if enviar:
+                registrar_movimento("Entrada", pessoa, modelo, qtd, df_estoque, df_historico) if pessoa and modelo else st.error("⚠️ Preencha os campos.")
+        with abas[3]:
+            st.markdown("<div class='panel'><h3 class='window-title'>📊 Janela de Indicadores</h3><p class='window-sub'>Acompanhe volume, itens críticos e movimentos por período.</p></div>", unsafe_allow_html=True)
+            m1, m2 = st.columns(2)
+            m1.metric("📦 Peças no Estoque", int(df_estoque["Quantidade"].sum()))
+            m2.metric("⚠️ Modelos Críticos", len(zerados))
+            d1, d2 = st.columns(2)
+            inicio = d1.date_input("De:", datetime.now().replace(day=1))
+            fim = d2.date_input("Até:", datetime.now())
             if not df_historico.empty:
-                df_h = df_historico.copy()
-                df_h['Data_Filtro'] = pd.to_datetime(df_h['Data']).dt.date
-                df_f = df_h[(df_h['Data_Filtro'] >= d_in) & (df_h['Data_Filtro'] <= d_out)]
-                col_g1, col_g2 = st.columns(2)
-                with col_g1:
-                    st.markdown("**Produção (Entradas)**")
-                    st.bar_chart(df_f[df_f["Ação"] == "Entrada"].groupby("Separador")["Quantidade"].sum(), color="#10b981")
-                with col_g2:
-                    st.markdown("**Consumo (Saídas)**")
-                    st.bar_chart(df_f[df_f["Ação"] == "Saída"].groupby("Separador")["Quantidade"].sum(), color="#ef4444")
-
-        with abas[4]: 
-            st.header("🕒 Histórico Recente")
-            st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
-
+                hist = df_historico.copy()
+                hist["Data_Filtro"] = pd.to_datetime(hist["Data"]).dt.date
+                hist = hist[(hist["Data_Filtro"] >= inicio) & (hist["Data_Filtro"] <= fim)]
+                g1, g2 = st.columns(2)
+                g1.bar_chart(hist[hist["Ação"] == "Entrada"].groupby("Separador")["Quantidade"].sum(), color="#10b981")
+                g2.bar_chart(hist[hist["Ação"] == "Saída"].groupby("Separador")["Quantidade"].sum(), color="#ef4444")
+        with abas[4]:
+            st.markdown("<div class='panel'><h3 class='window-title'>🕒 Janela de Histórico</h3><p class='window-sub'>Últimos lançamentos sincronizados com a planilha.</p></div>", unsafe_allow_html=True)
+            exibir_historico_bonito(df_historico)
         if st.session_state.perfil == "coord":
-            with abas[5]: 
-                st.header("👑 Download de Dados")
-                if not df_historico.empty:
-                    csv_convertido = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
-                    st.download_button(label="📥 Baixar Excel (CSV)", data=csv_convertido, file_name=f"Caixas_{datetime.now().strftime('%d-%m')}.csv", mime="text/csv", type="primary", use_container_width=True)
+            with abas[5]:
+                st.markdown("<div class='panel'><h3 class='window-title'>👑 Janela Executiva</h3><p class='window-sub'>Exporte os dados para análise e conferência.</p></div>", unsafe_allow_html=True)
+                csv = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False, sep=";").encode("utf-8-sig")
+                st.download_button("📥 Baixar Excel (CSV)", csv, f"Caixas_{datetime.now().strftime('%d-%m')}.csv", "text/csv", type="primary", use_container_width=True)
