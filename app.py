import streamlit as st
import pandas as pd
import re
import io
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuração visual do App
st.set_page_config(page_title="Analista IA - GEIP", page_icon="🏢")

def criar_pdf_buffer(texto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    if 'Disclaimer' not in styles:
        styles.add(ParagraphStyle(
            name='Disclaimer', parent=styles['Normal'], fontSize=8,
            textColor='gray', alignment=1, fontName='Helvetica-Oblique'
        ))

    story = [
        Paragraph("<b>GEIP - Relatório Executivo Gerencial</b>", styles["Heading1"]),
        Spacer(1, 20)
    ]

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

# Interface do Usuário
st.title("📊 Gerador de Relatórios Estratégicos")
st.markdown("""
    <style>
    
    .stApp {
        background-color: #ffffff;
    }
    
    .stButton>button {
        border-radius: 20px;
        background-color: #279eb3;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #018DA6;
        border-color: #018DA6;
    }
    </style>
    """, unsafe_allow_html=True)

# Tenta pegar a chave automaticamente dos segredos do Streamlit
# Se não achar, pede para o usuário (fallback)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

arquivo = st.file_uploader("Upload do Excel (Power BI)", type="xlsx")

if arquivo and api_key:
    if st.button("🚀 Iniciar Análise de Dados"):
        try:
            with st.spinner("Analisando dados e redigindo relatório..."):
                df = pd.read_excel(arquivo)
                dados_completos = df.to_csv(index=False)
                
                client = genai.Client(api_key=api_key) 
                prompt = f"Atue como Analista Sênior. Gere um relatório longo e detalhado sem introduções. Dados: {dados_completos}"
                
                resposta = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                pdf_output = criar_pdf_buffer(resposta.text)
                
                st.success("Relatório Concluído!")
                st.download_button(
                    label="📥 Baixar PDF Oficial",
                    data=pdf_output,
                    file_name="Relatorio_Executivo_GEIP.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ O limite de análises diárias foi atingido. Por favor, tente novamente em alguns instantes ou amanhã.")
            else:
                st.error(f"Ocorreu um erro inesperado: {e}")
