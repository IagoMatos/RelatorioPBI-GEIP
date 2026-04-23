import streamlit as st
import pandas as pd
import re
import io
import base64
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analista IA - GEIP", 
    page_icon="design/favicon.ico", 
    layout="centered"
)

# --- FUNÇÃO PARA LER IMAGEM LOCAL E CONVERTER PARA BASE64 ---
@st.cache_data
def get_image_base64(caminho_imagem):
    try:
        with open(caminho_imagem, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# Carregamento de Imagens
logo_b64 = get_image_base64("design/logo_GeipIA.png")
if logo_b64:
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 90px; object-fit: contain;">'
else:
    img_html = '<div style="background-color: #018DA6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold;">IA CORPORATIVA</div>'

grafico_b64 = get_image_base64("design/GraficoBarra.png")
if grafico_b64:
    img_grafico_html = f'<img src="data:image/png;base64,{grafico_b64}" style="height: 32px; vertical-align: middle; margin-right: 8px;">'
else:
    img_grafico_html = '📊'

# --- FUNÇÃO DO PDF COM ESTILOS AVANÇADOS ---
def criar_pdf_buffer(texto, titulo_documento="GEIP - Relatório Executivo Gerencial"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Estilos Personalizados
    styles.add(ParagraphStyle(name='CustomNormal', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=8, textColor='#333333'))
    styles.add(ParagraphStyle(name='CustomBullet', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=6, leftIndent=20, textColor='#333333'))
    styles.add(ParagraphStyle(name='CustomHeading', parent=styles['Heading2'], fontSize=14, leading=18, spaceBefore=20, spaceAfter=10, textColor=HexColor('#018DA6')))
    styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Normal'], fontSize=8, textColor='gray', alignment=1, fontName='Helvetica-Oblique'))
    
    story = [Paragraph(f"<b>{titulo_documento}</b>", styles["Heading1"]), Spacer(1, 10)]
    
    # Limpeza de resíduos técnicos
    texto_limpo = texto.replace('{', '').replace('}', '').replace('"', '').replace('json', '').replace('relatorio_executivo:', '')
    texto_tratado = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto_limpo)
    
    for linha in texto_tratado.split('\n'):
        linha = linha.strip()
        if not linha:
            continue
            
        if linha.startswith('#'):
            linha = linha.replace('#', '').strip()
            story.append(Paragraph(f"<b>{linha}</b>", styles["CustomHeading"]))
        elif linha.startswith('* ') or linha.startswith('- '):
            linha = linha[2:].strip()
            story.append(Paragraph(f"&bull; {linha}", styles["CustomBullet"]))
        else:
            story.append(Paragraph(linha, styles["CustomNormal"]))
    
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color="lightgrey"))
    story.append(Paragraph("Este relatório foi gerado por Inteligência Artificial e não substitui a análise humana.", styles["Disclaimer"]))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNÇÃO AUXILIAR DE PROCESSAMENTO ---
def processar_planilha(file, nome_aba):
    df = pd.read_excel(file, sheet_name=nome_aba)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.index = df.index + 2 
    df.index.name = 'Linha_Excel'
    return df.to_csv(index=True)

# --- CSS NATIVO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #017d93 !important;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }
    .block-container, [data-testid="stMainBlockContainer"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 40px 50px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        max-width: 850px !important;
        margin-top: 50px !important;
        margin-bottom: 50px !important;
        zoom: 1.1 !important;
    }
    .header-divider {
        border-bottom: 5px solid #018DA6;
        margin-bottom: 30px;
        padding-bottom: 15px;
    }
    div.stButton > button {
        background-color: #018DA6 !important;
        color: white !important;
        border: none !important;
        padding: 15px !important;
        width: 100% !important;
        border-radius: 8px !important;
        transition: 0.3s;
    }
    div.stButton > button p {
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        margin: 0 !important;
    }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
cabecalho_html = f"""
<div class="header-divider" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h2 style="margin:0; color: #018DA6; font-size: 26px;">SISTEMA DE ANÁLISE GEIP</h2>
        <p style="margin:0; color: #666; font-size: 14px;">Gerência de Infraestrutura Predial - FHEMIG</p>
    </div>
    {img_html}
</div>
<h3 style="color: #018DA6; font-size: 18px; display: flex; align-items: center;">{img_grafico_html} Gerador de Relatórios Estratégicos</h3>
"""
st.markdown(cabecalho_html, unsafe_allow_html=True)

# Configuração de Chave Silenciosa
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ Manutenção: Chave API não encontrada no cofre.")
    api_key = None

arquivo = st.file_uploader("Faça o upload do Excel exportado para iniciar a redação técnica.", type="xlsx")

aba_selecionada = None
if arquivo:
    xl = pd.ExcelFile(arquivo)
    lista_de_abas = xl.sheet_names
    aba_selecionada = st.selectbox("Selecione a aba (planilha) que contém os dados:", lista_de_abas)

if arquivo and api_key and aba_selecionada:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        if st.button("📊 RELATÓRIO EXECUTIVO", use_container_width=True):
            try:
                with st.spinner("Analisando cenário de negócios..."):
                    dados_csv = processar_planilha(arquivo, aba_selecionada)
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""Atue como um Consultor Estratégico da GEIP. Deduza o contexto e gere um relatório executivo.
                    IGNORE erros técnicos de dados. Foco em métricas e prazos.
                    # Visão Geral do Portfólio
                    # Desempenho e Métricas Principais
                    # Matriz de Risco e Alertas Estratégicos
                    BASE: {dados_csv}"""
                    
                    resposta = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    pdf = criar_pdf_buffer(resposta.text, "GEIP - Relatório Executivo Gerencial")
                    st.success("Relatório pronto!")
                    st.download_button("📥 BAIXAR RELATÓRIO", pdf, "Relatorio_Executivo.pdf", "application/pdf")
            except Exception as e:
                st.error(f"⚠️ Erro: {e}")

    with col2:
        if st.button("🔍 AUDITORIA DE DADOS", use_container_width=True):
            try:
                with st.spinner("Auditando integridade técnica..."):
                    dados_csv = processar_planilha(arquivo, aba_selecionada)
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""Atue como Engenheiro de Dados Sênior da GEIP. 
                    Sua missão é realizar uma varredura técnica rigorosa na base de dados, com foco EXCLUSIVO em garantir a importação perfeita no Power BI.
                    
                    REGRAS DE CLASSIFICAÇÃO DE ERROS E ALERTAS:
                    1. 🚨 ERROS CRÍTICOS (Bloqueantes - Liste 1 a 1): Tudo que trava a tipagem do Power BI. Ex: valores numéricos com pontuação dupla, letras misturadas em colunas financeiras ou de datas, e formatos de data inválidos. Identifique a 'Linha_Excel' exata.
                    
                    2. ⚠️ AVISOS E SUGESTÕES (Não bloqueantes - AGRUPE OS DADOS): 
                       - É EXPRESSAMENTE PROIBIDO listar células vazias linha por linha se elas não forem um erro bloqueante.
                       - Identifique o padrão e agrupe a informação (Ex: "A coluna 'X' possui 45 células vazias, principalmente a partir da linha 200").
                       - INTELIGÊNCIA DE CONTEXTO: Ignore células vazias em linhas que parecem ser "Cabeçalhos de Seção", linhas de "Total/Subtotal", ou colunas que são obviamente opcionais (ex: "Justificativa" ou linhas marcadas como 'NÃO POSSUI').
                    
                    É EXPRESSAMENTE PROIBIDO o uso de formato JSON, chaves ou aspas de código. Use tópicos limpos e seja muito conciso.

                    ESTRUTURA OBRIGATÓRIA (Use '#' para títulos):
                    # Resumo da Qualidade de Dados
                    # 🚨 ERROS CRÍTICOS (Ação Imediata Obrigatória)
                    [Liste individualmente apenas os erros graves, com a respectiva Linha_Excel]
                    # ⚠️ PADRÕES E SUGESTÕES (Resumo Agrupado)
                    [Resuma os problemas menores e os padrões de células vazias não-intencionais em no MÁXIMO 5 tópicos]

                    BASE DE DADOS:
                    {dados_csv}"""
                    
                    resposta = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    pdf = criar_pdf_buffer(resposta.text, "GEIP - Auditoria de Integridade de Dados")
                    st.success("Auditoria pronta!")
                    st.download_button("📥 BAIXAR AUDITORIA", pdf, "Auditoria_Dados.pdf", "application/pdf")
            except Exception as e:
                st.error(f"⚠️ Erro: {e}")

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align: center; margin-top: 40px;">
        <hr style="border: 0; border-top: 1px solid #ddd; margin-bottom: 20px;">
        <p style="color: rgba(0,0,0,0.42); font-style: italic ;font-size: 14px;">'Relatórios gerados por IA podem conter erros e não substituem a análise Humana.'</p>
        <a href="https://fhemigmg.sharepoint.com/sites/GEIP" target="_blank" 
           style="background-color: #018DA6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
           Acessar Portal GEIP
        </a>
    </div>
    """, unsafe_allow_html=True)
