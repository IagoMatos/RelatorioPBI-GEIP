import streamlit as st
import pandas as pd
import re
import io
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURAÇÃO DA PÁGINA ---
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

# --- CSS NATIVO STREAMLIT (CORRIGIDO PARA O CARD BRANCO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    
    /* 1. Fundo Azul Escuro para toda a tela, incluindo a margem lateral */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #023440 !important;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }

    /* 2. O Card Branco Central (Forçando em todas as versões do Streamlit) */
    .block-container, [data-testid="stMainBlockContainer"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 40px 50px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        max-width: 850px !important;
        margin-top: 50px !important;
        margin-bottom: 50px !important;
    }

    /* Linha divisória do cabeçalho */
    .header-divider {
        border-bottom: 5px solid #018DA6;
        margin-bottom
