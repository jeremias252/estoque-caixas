import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caixas - ESTOQUE", page_icon="📦", layout="centered")

# --- DESIGN PREMIUM E MODO ESCURO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.3);
    }
    
    .main-title {
        text-align: center;
        font-weight: 800;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #333333;
    }
    
    .alert-box {
        background-color: #3f0e0e;
        border-left: 5px solid #ef4444;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        color: #fca5a5;
    }
    </style>
    """, unsafe_allow_html=True)

# URL DA PLANILHA GOOGLE (CAIXAS)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/10z1gPJNmHoHO5kj6B4SoXknUNz6MwrQz1NjwkkBatQU/edit?usp=drivesdk"

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    precisa_criar_estoque = False
    try:
        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque", ttl=600).copy()
        if "Quantidade" not in df_estoque.columns or "Modelo" not in df_estoque.columns:
            precisa_criar_estoque = True
        else:
            df_estoque = df_estoque.dropna(subset=["Modelo"])
            if df_estoque.empty:
                precisa_criar_estoque = True
            else:
                df_estoque["Quantidade"] = pd.to_numeric(df_estoque["Quantidade"], errors="coerce").fillna(0).astype(int)
                if "CodigoBarras" not in df_estoque.columns:
                    df_estoque["CodigoBarras"] = ""
                else:
                    df_estoque["CodigoBarras"] = df_estoque["CodigoBarras"].astype(str).str.replace(".0", "", regex=False)
    except:
        precisa_criar_estoque = True

    if precisa_criar_estoque:
        modelos_base = [
            "CXP01T", "CXP01", "CX04S", "CX34ABS", "CX44", "CX23ABS", 
            "CX01S", "CX02S", "CX03S", "CXEP02", "CXEP03", "CP01A", 
            "RE04FN", "RE06FN", "CX02Q", "CX02RN"
        ]
        cores = ["Branco", "Preto", "Cinza"]
        
        itens = [f"{m} - {c}" for m in modelos_base for c in cores]
        itens.append("CX56 - Única")
        
        df_estoque = pd.DataFrame({"Modelo": sorted(itens), "CodigoBarras": "", "Quantidade": 0})
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df_estoque)

    precisa_criar_hist = False
    try:
        df_historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico", ttl=600).copy()
        if "Ação" not in df_historico.columns or "Separador" not in df_historico.columns:
            precisa_criar_hist = True
        else:
            df_historico = df_historico.dropna(subset=["ID"])
    except:
        precisa_criar_hist = True
        
    if precisa_criar_hist:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df_historico)

    return df_estoque, df_historico

def salvar_estoque(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)

def salvar_historico(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)

# ==========================================
# FUNÇÃO LEITOR DE CÓDIGO DE BARRAS
# ==========================================
def ler_codigo_barras(foto):
    if foto is not None:
        from pyzbar.pyzbar import decode
        from PIL import Image
        img = Image.open(foto)
        codigos = decode(img)
        if codigos:
            return codigos[0].data.decode('utf-8')
    return None

# ==========================================
# EXIBIÇÃO DE ESTOQUE (AGORA IDÊNTICO AO DAS TORRES)
# ==========================================
def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    if termo_busca:
        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False) | df_view["CodigoBarras"].str.contains(termo_busca, case=False)]
        
    if df_view.empty:
        st.warning("Nenhum modelo encontrado.")
        return

    # Funções para separar a Família da Cor
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
    
    for _, row_total in df_totais.iterrows():
        linha = row_total['Linha']
        total_linha = int(row_total['Quantidade'])
        icone = "🔴" if total_linha == 0 else ("🟡" if total_linha <= 5 else "📦")
        
        # Cria a aba sanfona (expander)
        with st.expander(f"{icone} {linha} — (Total: {total_linha} un.)"):
            df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
            cols = st.columns(len(df_linha) if len(df_linha) > 0 else 1)
            
            for i, (_, row) in enumerate(df_linha.iterrows()):
                cor = row['Cor']
                qtd = int(row['Quantidade'])
                cod = row['CodigoBarras'] if 'CodigoBarras' in row and str(row['CodigoBarras']).strip() != "" else "S/ Cód."
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                
                # HTML do card com a cor e o código de barras
                card_html = f"""
                <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333333; margin-bottom: 5px;">
                    <div style="color: #888888; font-size: 14px; font-weight: bold; text-transform: uppercase;">{cor}</div>
                    <div style="color: #555555; font-size: 10px; margin-top: -2px;">Ref: {cod}</div>
                    <div style="color: #F38020; font-size: 26px; font-weight: 900; margin: 8px 0;">{qtd}</div>
                    <div style="font-size: 12px; color: #AAAAAA;">{status}</div>
                </div>
                """
                cols[i].markdown(card_html, unsafe_allow_html=True)

# CARREGA OS DADOS
df_estoque, df_historico = carregar_dados()
separadores = ["Marcello", "Henrique", "Leonardo", "Patrick"]
lista_modelos = sorted(df_estoque["Modelo"].tolist())

# --- LOGO SVG E BOTÃO DE ATUALIZAR ---
logo_svg = """
<div style="display: flex; justify-content: center; margin-bottom: 20px;">
    <svg width="100%" viewBox="0 0 400 350" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="350" fill="transparent" rx="12"/>
        <path d="M 320 180 L 320 50 L 50 50 L 50 300 L 320 300 L 320 250" fill="none" stroke="#ffffff" stroke-width="12" />
        <text x="75" y="150" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="70" letter-spacing="2">SETOR</text>
        <text x="75" y="235" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="60" letter-spacing="1">CAIXAS</text>
        <text x="325" y="225" fill="#ffffff" font-family="Arial, sans-serif" font-weight="bold" font-size="28">.COM</text>
        <line x1="290" y1="260" x2="380" y2="260" stroke="#F38020" stroke-width="12" />
    </svg>
</div>
"""
st.sidebar.markdown(logo_svg, unsafe_allow_html=True)

if st.sidebar.button("🔄 Atualizar Planilha Agora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
st.sidebar.divider()

# --- CONTROLE DE ACESSO ---
st.sidebar.title("🔐 Acesso Seguro")
perfil = st.sidebar.radio("Nível de permissão:", ["👀 Visualizador (Equipe)", "⚙️ Controle (Marcello)", "👑 Coordenador"])

acesso_marcello = False
acesso_coord = False

if perfil == "⚙️ Controle (Marcello)":
    senha = st.sidebar.text_input("Senha do Marcello:", type="password")
    if senha == "marcello123": acesso_marcello = True
    elif senha != "": st.sidebar.error("❌ Senha incorreta!")

elif perfil == "👑 Coordenador":
    senha = st.sidebar.text_input("Senha do Coordenador:", type="password")
    if senha == "coord123": acesso_coord = True
    elif senha != "": st.sidebar.error("❌ Senha incorreta!")

# --- TELA PRINCIPAL ---
st.markdown("<h1 class='main-title'>📦 Caixas - ESTOQUE</h1>", unsafe_allow_html=True)

zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
if zerados:
    st.markdown(f"<div class='alert-box'>🚨 <b>ATENÇÃO:</b> Há {len(zerados)} modelos com estoque ZERADO!</div>", unsafe_allow_html=True)

if not (acesso_marcello or acesso_coord):
    st.info("👋 Modo Visualização. Solicite retiradas diretamente ao Marcello.")
    busca = st.text_input("🔍 Buscar modelo ou código...", key="busca_equipe")
    st.divider()
    exibir_estoque_premium(df_estoque, busca)

else:
    abas_nomes = ["📤 Operação", "📋 Estoque", "📊 Dashboard", "🕒 Histórico"] if acesso_coord else ["📤 Operação", "📋 Estoque", "📊 Dashboard"]
    abas = st.tabs(abas_nomes)

    with abas[0]: # OPERAÇÃO
        tipo_op = st.radio("Selecione o tipo de operação:", ["➖ Registrar Saída", "➕ Lançar Entrada"], horizontal=True)
        st.divider()
        
        modelo_detectado = None
        with st.expander("📷 Usar Leitor de Código de Barras", expanded=False):
            st.write("Aponte a câmera para o código da caixa:")
            foto = st.camera_input("Câmera", label_visibility="collapsed")
            if foto:
                codigo = ler_codigo_barras(foto)
                if codigo:
                    match = df_estoque[df_estoque["CodigoBarras"] == codigo]
                    if not match.empty:
                        modelo_detectado = match.iloc[0]["Modelo"]
                        st.success(f"✅ Código {codigo} lido com sucesso!")
                    else:
                        st.error(f"❌ O código {codigo} não está cadastrado na planilha!")
                else:
                    st.warning("⚠️ Não foi possível ler o código. Melhore a iluminação ou aproxime a câmera.")
        
        with st.form("form_operacao", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sep = st.selectbox("1. Colaborador", [""] + separadores)
            with col2:
                index_padrao = 0
                if modelo_detectado and modelo_detectado in lista_modelos:
                    index_padrao = lista_modelos.index(modelo_detectado) + 1
                
                modelo = st.selectbox("2. Modelo", [""] + lista_modelos, index=index_padrao)
            
            qtd = st.number_input("3. Quantidade", min_value=1, value=1)
            btn_cor = "primary" if "Saída" in tipo_op else "secondary"
            submit_op = st.form_submit_button(f"Confirmar {tipo_op.split(' ')[1]}", type=btn_cor, use_container_width=True)

        if submit_op:
            if not sep or not modelo: st.error("⚠️ Preencha Colaborador e Modelo.")
            else:
                idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                estoque_atual = df_estoque.at[idx, "Quantidade"]
                acao_texto = "Saída" if "Saída" in tipo_op else "Entrada"
                
                if acao_texto == "Saída" and estoque_atual < qtd:
                    st.error(f"⚠️ Saldo insuficiente! Temos apenas {estoque_atual} un.")
                else:
                    if acao_texto == "Saída":
                        df_estoque.at[idx, "Quantidade"] -= qtd
                    else:
                        df_estoque.at[idx, "Quantidade"] += qtd
                        
                    salvar_estoque(df_estoque)
                    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": acao_texto, "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
                    df_historico = pd.concat([novo, df_historico], ignore_index=True)
                    salvar_historico(df_historico)
                    st.cache_data.clear()
                    st.success(f"✅ {acao_texto} de {qtd}x '{modelo}' registrada!")
                    st.rerun()

    with abas[1]: # ESTOQUE ATUAL
        st.header("📋 Estoque Atual")
        st.write("💡 Adicione os números dos Códigos de Barras diretamente na coluna 'CodigoBarras' na sua planilha.")
        busca = st.text_input("🔍 Buscar modelo ou código...", key="busca_admin")
        st.divider()
        exibir_estoque_premium(df_estoque, busca)

    with abas[2]: # DASHBOARD
        st.header("📊 Indicadores")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("📦 Total de Peças", int(df_estoque["Quantidade"].sum()))
        col_m2.metric("⚠️ Modelos Zerados/Baixos", len(zerados))
        st.divider()
        
        if not df_historico.empty:
            df_hist_copy = df_historico.copy()
            df_hist_copy['Data_Filtro'] = pd.to_datetime(df_hist_copy['Data']).dt.date
            
            df_saidas = df_hist_copy[df_hist_copy["Ação"] == "Saída"]
            df_entradas = df_hist_copy[df_hist_copy["Ação"] == "Entrada"]
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.subheader("🛠️ Quem Produziu")
                if not df_entradas.empty: st.bar_chart(df_entradas.groupby("Separador")["Quantidade"].sum(), color="#16a34a")
            with col_g2:
                st.subheader("👤 Quem Retirou")
                if not df_saidas.empty: st.bar_chart(df_saidas.groupby("Separador")["Quantidade"].sum(), color="#dc2626")

    if acesso_coord and len(abas) > 3:
        with abas[3]: # HISTÓRICO
            st.header("🕒 Histórico Recente")
            st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
