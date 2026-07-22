import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from PIL import Image
from pyzbar.pyzbar import decode

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caixas - ESTOQUE", page_icon="📦", layout="centered")

# --- DESIGN PREMIUM E MODO ESCURO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button { border-radius: 8px; font-weight: 600; border: none; }
    .main-title { text-align: center; font-weight: 800; padding-bottom: 1rem; border-bottom: 2px solid #333333; }
    .alert-box { background-color: #3f0e0e; border-left: 5px solid #ef4444; padding: 12px; border-radius: 6px; margin-bottom: 15px; color: #fca5a5; }
    </style>
    """, unsafe_allow_html=True)

# COLOQUE AQUI O LINK DA SUA PLANILHA "Caixas - Estoque" DO GOOGLE DRIVE
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_CAIXAS"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque")
    except:
        modelos_com_cor = ["CXP01T", "CXP01", "CX04S", "CX34ABS", "CX44", "CX23ABS", "CX01S", "CX02S", "CX03S", "CXEP02", "CXEP03", "CP01A", "RE04FN", "RE06FN", "CX02Q", "CX02RN"]
        cores = ["Branco", "Preto", "Cinza"]
        itens = [f"{modelo} - {cor}" for modelo in modelos_com_cor for cor in cores]
        itens.append("CX56")
        df_estoque = pd.DataFrame({"Modelo": itens, "Quantidade": 0})
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df_estoque)

    try:
        df_historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico")
    except:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df_historico)

    return df_estoque, df_historico

def salvar_estoque(df): conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)
def salvar_historico(df): conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)

def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    if termo_busca: df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
    if df_view.empty:
        st.warning("Nenhum modelo encontrado.")
        return

    df_view['Linha'] = df_view['Modelo'].apply(lambda x: x.rsplit(" - ", 1)[0] if " - " in x else x)
    df_view['Cor'] = df_view['Modelo'].apply(lambda x: x.rsplit(" - ", 1)[1] if " - " in x else "Padrão")
    
    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index().sort_values(by='Quantidade', ascending=False)
    
    for _, row_total in df_totais.iterrows():
        linha = row_total['Linha']
        total_linha = int(row_total['Quantidade'])
        icone = "🔴" if total_linha == 0 else ("🟡" if total_linha <= 5 else "📦")
        
        with st.expander(f"{icone} {linha} — (Total: {total_linha} un.)"):
            df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
            cols = st.columns(len(df_linha) if len(df_linha) > 0 else 1)
            
            for i, (_, row) in enumerate(df_linha.iterrows()):
                cor = row['Cor']
                qtd = int(row['Quantidade'])
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                card_html = f"""
                <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333333;">
                    <div style="color: #888888; font-size: 14px; font-weight: bold;">{cor}</div>
                    <div style="color: #F38020; font-size: 26px; font-weight: 900;">{qtd}</div>
                    <div style="font-size: 12px; color: #AAAAAA;">{status}</div>
                </div>
                """
                cols[i].markdown(card_html, unsafe_allow_html=True)

df_estoque, df_historico = carregar_dados()
separadores = ["Fabiano", "Marcello", "Sérgio", "Renan"]

# --- CONTROLE DE ACESSO ---
st.sidebar.title("🔐 Acesso Seguro")
perfil = st.sidebar.radio("Permissão:", ["👀 Visualizador", "⚙️ Controle (Marcello)", "👑 Coordenador"])

acesso_marcello = (perfil == "⚙️ Controle (Marcello)" and st.sidebar.text_input("Senha Marcello:", type="password") == "marcello123")
acesso_coord = (perfil == "👑 Coordenador" and st.sidebar.text_input("Senha Coordenador:", type="password") == "coord123")

st.markdown("<h1 class='main-title'>📦 Caixas - ESTOQUE</h1>", unsafe_allow_html=True)

zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
if zerados:
    st.markdown(f"<div class='alert-box'>🚨 <b>ATENÇÃO:</b> {len(zerados)} caixas estão com estoque ZERADO!</div>", unsafe_allow_html=True)

if not (acesso_marcello or acesso_coord):
    st.info("Modo Visualização.")
    busca = st.text_input("🔍 Buscar...", key="busca_equipe")
    exibir_estoque_premium(df_estoque, busca)
else:
    abas_nomes = ["📦 Operação", "📷 Leitor Barcode", "📊 Dashboard", "🕒 Histórico"]
    abas = st.tabs(abas_nomes)

    with abas[0]: # OPERAÇÃO
        st.header("📤 Registrar Saída")
        with st.form("form_saida", clear_on_submit=True):
            sep = st.selectbox("1. Colaborador", [""] + separadores)
            modelo = st.selectbox("2. Modelo", [""] + sorted(df_estoque["Modelo"].tolist()))
            qtd = st.number_input("3. Qtd", min_value=1, value=1)
            if st.form_submit_button("Confirmar Saída", type="primary"):
                idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                if df_estoque.at[idx, "Quantidade"] >= qtd:
                    df_estoque.at[idx, "Quantidade"] -= qtd
                    salvar_estoque(df_estoque)
                    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Saída", "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
                    df_historico = pd.concat([novo, df_historico], ignore_index=True)
                    salvar_historico(df_historico)
                    st.success("✅ Registrado!")
                    st.rerun()

    with abas[1]: # LEITOR DE CÓDIGO DE BARRAS / QR CODE
        st.header("📷 Leitor de Código de Barras")
        st.caption("Aponte a câmera do celular ou tablet para a etiqueta da caixa:")
        foto = st.camera_input("Tirar foto do Código de Barras")
        
        if foto is not None:
            img = Image.open(foto)
            codigos = decode(img)
            if codigos:
                codigo_lido = codigos[0].data.decode('utf-8')
                st.success(f"🎯 Código Identificado: **{codigo_lido}**")
                # Filtra automaticamente o modelo encontrado
                exibir_estoque_premium(df_estoque, codigo_lido)
            else:
                st.warning("Nenhum código de barras legível foi encontrado na imagem. Tente aproxima a câmera.")

    with abas[2]: # DASHBOARD COM FILTRO DE DATA
        st.header("📊 Indicadores")
        d_inicio = st.date_input("Data Inicial", datetime.now().replace(day=1))
        d_fim = st.date_input("Data Final", datetime.now())
        
        if not df_historico.empty:
            df_hist_copy = df_historico.copy()
            df_hist_copy['Data_Filtro'] = pd.to_datetime(df_hist_copy['Data']).dt.date
            df_filtrado = df_hist_copy[(df_hist_copy['Data_Filtro'] >= d_inicio) & (df_hist_copy['Data_Filtro'] <= d_fim)]
            st.bar_chart(df_filtrado.groupby("Separador")["Quantidade"].sum())

    with abas[3]: # HISTÓRICO
        st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
