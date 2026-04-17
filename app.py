import streamlit as st
import pandas as pd
import re
import io
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Analista IA - GEIP", page_icon="🏢", layout="wide")

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

# --- CSS PERSONALIZADO (PADRÃO GEIP) ---
st.markdown("""
    <style>
    /* Importando fontes e definindo base */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    
    .stApp {
        background-color: #023440;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }

    /* Card Principal */
    .main-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        max-width: 900px;
        margin: 0 auto;
        color: #333333;
    }

    /* Estilização de Botões */
    .stButton>button {
        background-color: #018DA6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 25px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #279eb3;
        color: white;
        border-color: #279eb3;
    }

    /* Títulos dentro do app */
    h1, h2, h3 {
        color: #018DA6 !important;
    }

    /* Texto de destaque light blue */
    .highlight-text {
        color: #bff9ff;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Ajuste da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #012a33;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO (HEADER) ---
st.markdown("""
    <div style="max-width: 900px; margin: 40px auto 0 auto; background-color: #ffffff; padding: 25px 40px; border-radius: 12px 12px 0 0; display: flex; align-items: center; border-bottom: 5px solid #018DA6;">
        <div style="flex: 1;">
            <h2 style="margin:0; font-size: 24px;">SISTEMA DE ANÁLISE GEIP</h2>
            <p style="margin:0; color: #666; font-size: 14px;">Gestão de Infraestrutura e Projetos - FHEMIG</p>
        </div>
        <div style="text-align: right;">
             <span style="background-color: #018DA6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold;">IA CORPORATIVA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- CORPO DO APLICATIVO ---
with st.container():
    # Abrindo o card principal
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### 📊 Gerador de Relatórios Estratégicos")
    st.write("Selecione o arquivo Excel exportado para que a IA realize a análise técnica.")

    # Input de Dados
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
    arquivo = st.file_uploader("Upload do Excel (Power BI)", type="xlsx")

    if arquivo and api_key:
        if st.button("🚀 INICIAR ANÁLISE DE DADOS"):
            try:
                with st.spinner("Analisando dados e redigindo relatório..."):
                    df = pd.read_excel(arquivo)
                    dados_completos = df.to_csv(index=False)
                    
                    client = genai.Client(api_key=api_key) 
                    prompt = f"Atue como Analista Sênior. Gere um relatório longo e detalhado sem introduções. Dados: {dados_completos}"
                    
                    resposta = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                    pdf_output = criar_pdf_buffer(resposta.text)
                    
                    st.success("Análise Finalizada com Sucesso!")
                    st.download_button(
                        label="📥 BAIXAR RELATÓRIO OFICIAL (PDF)",
                        data=pdf_output,
                        file_name="Relatorio_Executivo_GEIP.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Limite de cota atingido. Tente novamente em 60 segundos.")
                else:
                    st.error(f"Erro inesperado: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True) # Fechando o card principal

# --- RODAPÉ (FOOTER) ---
st.markdown(f"""
    <div style="max-width: 900px; margin: 30px auto; text-align: center;">
        <p class="highlight-text">“Transformando dados em decisões estratégicas para a infraestrutura.”</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">
        <p style="color: #ffffff; font-size: 14px;">Esta é uma ferramenta de uso interno da GEIP.</p>
        <a href="https://fhemigmg.sharepoint.com/sites/GEIP" style="background-color: #006375; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; border: 1px solid #279eb3;">Acessar Portal GEIP</a>
    </div>
    """, unsafe_allow_html=True)
