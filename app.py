import streamlit as st
import pandas as pd
import re
import io
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURAÇÃO DA PÁGINA ---
# Usamos 'centered' para o card não esticar muito em telas grandes
st.set_page_config(page_title="Analista IA - GEIP", page_icon="🏢", layout="centered")

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
    
    /* Fundo Azul Escuro da GEIP para toda a tela */
    .stApp {
        background-color: #ffffff;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }

    /* Transforma o container central do Streamlit no nosso Card Branco */
    [data-testid="block-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 40px 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-top: 40px;
        margin-bottom: 40px;
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
        font-weight: bolder !important;
        padding: 15px !important;
        width: 100% !important;
        border-radius: 8px !important;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #279eb3 !important;
    }

    /* Ocultar a barra superior chata do Streamlit */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO DENTRO DO CARD ---
st.markdown("""
    <div class="header-divider" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color: #018DA6; font-size: 26px;">SISTEMA DE ANÁLISE GEIP</h2>
            <p style="margin:0; color: #666; font-size: 14px;">Gerência de Infraestrutura Predial - FHEMIG</p>
        </div>
        <div style="background-color: #018DA6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold;">IA CORPORATIVA</div>
    </div>
    <h3 style="color: #018DA6; font-size: 18px;">📊 Gerador de Relatórios Estratégicos</h3>
    <p style="color: #555; font-size: 14px; margin-bottom: 20px;">Faça o upload do Excel exportado para gerar o relatório.</p>
    """, unsafe_allow_html=True)

# --- WIDGETS NATIVOS (Agora ficarão naturalmente dentro do card branco) ---
api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")
arquivo = st.file_uploader("", type="xlsx", label_visibility="collapsed")

if arquivo and api_key:
    if st.button("🚀 INICIAR ANÁLISE DE DADOS"):
        try:
            with st.spinner("A IA está analisando o dashboard..."):
                df = pd.read_excel(arquivo)
                dados_csv = df.to_csv(index=False)
                
                client = genai.Client(api_key=api_key)
                prompt = f"Atue como Analista Sênior da GEIP. Analise os dados e gere um relatório detalhado sem introduções. Dados: {dados_csv}"
                
                # Voltando para o modelo principal que funcionou para a sua chave
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
            # Tratamento de erro limpo sem vazar código no app
            if "429" in str(e):
                st.error("⚠️ O limite de análises da sua chave foi atingido. Tente novamente mais tarde.")
            else:
                st.error("⚠️ Ocorreu um erro ao processar os dados. Verifique sua chave de API ou a formatação da planilha.")

# --- RODAPÉ ---
st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <hr style="border: 0; border-top: 1px solid #eee; margin-bottom: 20px;">
        <p style="color: #666; font-size: 14px; font-weight: bold;">“Transformando dados em decisões estratégicas para a infraestrutura.”</p>
        <a href="https://fhemigmg.sharepoint.com/sites/GEIP" target="_blank" 
           style="background-color: #018DA6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; display: inline-block; margin-top: 10px;">
           Acessar Portal GEIP
        </a>
    </div>
    """, unsafe_allow_html=True)
