import streamlit as st
import pandas as pd
import re
import io
import base64 # <-- NOVA BIBLIOTECA ADICIONADA AQUI
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analista IA - GEIP", 
    page_icon="favicon.ico", 
    layout="centered"
)

# --- FUNÇÃO PARA LER IMAGEM LOCAL E CONVERTER PARA BASE64 ---
@st.cache_data
def get_image_base64(caminho_imagem):
    with open(caminho_imagem, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 1. Carrega a Logo Principal
try:
    logo_b64 = get_image_base64("logo_GeipIA.png")
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 90px; object-fit: contain;">'
except Exception:
    img_html = '<div style="background-color: #018DA6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold;">IA CORPORATIVA</div>'

# 2. Carrega o Ícone de Gráfico (Substitui o Emoji)
try:
    grafico_b64 = get_image_base64("GraficoBarra.png")
    # A altura (height) foi ajustada para 24px para alinhar perfeitamente com o tamanho da fonte do título
    img_grafico_html = f'<img src="data:image/png;base64,{grafico_b64}" style="height: 32px; vertical-align: middle; margin-right: 8px;">'
except Exception:
    img_grafico_html = '📊' # Se o arquivo não for encontrado, ele volta para o emoji como plano B


def criar_pdf_buffer(texto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    if 'Disclaimer' not in styles:
        styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Normal'], fontSize=8, textColor='gray', alignment=1, fontName='Helvetica-Oblique'))
    story = [Paragraph("<b>GEIP - Relatório Executivo Gerencial</b>", styles["Heading1"]), Spacer(1, 20)]
    texto_tratado = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    for linha in texto_tratado.split('\n'):
        linha = linha.strip()
        if not linha:
            story.append(Spacer(1, 10))
            continue
        estilo = styles["Heading2"] if linha.startswith('#') else styles["Normal"]
        linha = linha.replace('#', '').strip()
        story.append(Paragraph(linha, estilo))
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color="lightgrey"))
    story.append(Paragraph("Este relatório foi gerado por Inteligência Artificial e não substitui a análise humana.", styles["Disclaimer"]))
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS NATIVO STREAMLIT ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    
    /* 1. Fundo Azul Escuro para toda a tela, incluindo a margem lateral */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #017d93 !important;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }

    /* 2. O Card Branco Central */
    .block-container, [data-testid="stMainBlockContainer"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 40px 50px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        max-width: 850px !important;
        margin-top: 50px !important;
        margin-bottom: 50px !important;
        zoom: 1.2 !important;
    }

    /* Linha divisória do cabeçalho */
    .header-divider {
        border-bottom: 5px solid #018DA6;
        margin-bottom: 30px;
        padding-bottom: 15px;
    }

    /* Botões Padrão GEIP */
    div.stButton > button {
        background-color: #018DA6 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 15px !important;
        width: 100% !important;
        border-radius: 8px !important;
        transition: 0.3s;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif !important;
    }
    
    div.stButton > button:hover {
        background-color: #279eb3 !important;
    }

    /* Cor do texto do seletor de arquivo */
    .st-emotion-cache-1wivap2 {
        color: #333333 !important;
    }

    /* Ocultar a barra superior do Streamlit */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO DENTRO DO CARD ---

# A tag <h3> agora usa flexbox para alinhar a imagem e o texto na mesma linha de forma elegante
cabecalho_html = f"""
<div class="header-divider" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h2 style="margin:0; color: #018DA6; font-size: 26px;">SISTEMA DE ANÁLISE GEIP</h2>
        <p style="margin:0; color: #666; font-size: 14px;">Gerência de Infraestrutura Predial - FHEMIG</p>
    </div>
    {img_html}
</div>
<h3 style="color: #018DA6; font-size: 18px; display: flex; align-items: center;">{img_grafico_html} Gerador de Relatórios Estratégicos</h3>
<p style="color: #555; font-size: 14px; margin-bottom: 20px;">Faça o upload do Excel exportado para iniciar a redação técnica.</p>
"""

st.markdown(cabecalho_html, unsafe_allow_html=True)

# --- WIDGETS NATIVOS ---
api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")
arquivo = st.file_uploader("", type="xlsx", label_visibility="collapsed")

if arquivo and api_key:
    if st.button("🚀 INICIAR ANÁLISE DE DADOS"):
        try:
            with st.spinner("A IA está a analisar o dashboard..."):
                df = pd.read_excel(arquivo)
                dados_csv = df.to_csv(index=False)
                
                client = genai.Client(api_key=api_key)
                prompt = f"Atue como Analista Sênior da GEIP. Analise os dados e gere um relatório detalhado sem introduções. Dados: {dados_csv}"
                
                resposta = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                
                pdf_output = criar_pdf_buffer(resposta.text)
                
                st.success("Relatório concluído com sucesso!")
                st.download_button(
                    label="📥 BAIXAR RELATÓRIO OFICIAL (PDF)",
                    data=pdf_output,
                    file_name="Relatorio_Executivo_GEIP.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ O limite de análises da sua chave foi atingido. Tente novamente mais tarde.")
            else:
                st.error("⚠️ Ocorreu um erro ao processar os dados. Verifique a sua chave de API ou a formatação da folha de cálculo.")

# --- RODAPÉ ---
st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <hr style="border: 0; border-top: 1px solid #ddd; margin-bottom: 20px;">
        <p style="color: rgba(0,0,0,0.42); font-style: italic ;font-size: 14px; font-weight: 500;">'Relatórios gerados por IA podem conter erros e não substiuem a análise Humana.'</p>
        <a href="https://fhemigmg.sharepoint.com/sites/GEIP" target="_blank" 
           style="background-color: #018DA6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; display: inline-block; margin-top: 10px;">
           Acessar Portal GEIP
        </a>
    </div>
    """, unsafe_allow_html=True)
