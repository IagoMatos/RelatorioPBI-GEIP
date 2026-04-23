import streamlit as st
import pandas as pd
import re
import io
import base64
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

# --- FUNÇÃO DO PDF (AGORA ACEITA TÍTULOS DINÂMICOS) ---
def criar_pdf_buffer(texto, titulo_documento="GEIP - Relatório Executivo Gerencial"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    if 'Disclaimer' not in styles:
        styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Normal'], fontSize=8, textColor='gray', alignment=1, fontName='Helvetica-Oblique'))
    
    # O título agora muda dependendo do botão clicado
    story = [Paragraph(f"<b>{titulo_documento}</b>", styles["Heading1"]), Spacer(1, 20)]
    
    texto_limpo = texto.replace('{', '').replace('}', '').replace('"', '').replace('json', '').replace('relatorio_executivo:', '')
    texto_tratado = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto_limpo)
    
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

# --- INTERFACE PRINCIPAL ---
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

api_key = st.text_input("🔑 Insira a Nova Chave API aqui:", type="password").strip()
arquivo = st.file_uploader("Faça o upload do Excel exportado para iniciar a redação técnica.", type="xlsx")

# --- FUNÇÃO AUXILIAR DE LIMPEZA ---
# Criamos esta função para não repetir código nos dois botões
def processar_planilha(file):
    df = pd.read_excel(file)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.index = df.index + 2 
    df.index.name = 'Linha_Excel'
    return df.to_csv(index=True)


if arquivo and api_key:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Adicionamos um 'gap' para afastar os botões de forma simétrica
    col1, col2 = st.columns(2, gap="medium")
    
    # ==========================================
    # BOTÃO 1: RELATÓRIO EXECUTIVO DE NEGÓCIOS
    # ==========================================
    with col1:
        # Forçamos o botão a usar 100% do container
        if st.button("📊 RELATÓRIO EXECUTIVO", use_container_width=True):
            try:
                with st.spinner("Analisando o cenário de negócios..."):
                    dados_csv = processar_planilha(arquivo)
                    client = genai.Client(api_key=api_key)
                    
                    prompt_executivo = f"""Atue como um Consultor Estratégico e Analista Sênior da GEIP. 
                    Sua missão é deduzir o contexto de negócio da base e gerar um relatório executivo padronizado.
                    
                    DIRETRIZES:
                    1. Foco exclusivo em métricas, desempenho, finanças, prazos e visão geral de portfólio.
                    2. IGNORE qualquer erro de formatação de dados, células vazias ou tipos de dados errados. Isso não é uma auditoria técnica.
                    3. É EXPRESSAMENTE PROIBIDO o uso de formato JSON ou chaves. Use texto humano.

                    ESTRUTURA OBRIGATÓRIA (Use '#' para títulos):
                    # Visão Geral do Portfólio
                    # Desempenho e Métricas Principais
                    # Matriz de Risco e Alertas Estratégicos

                    BASE DE DADOS:
                    {dados_csv}"""
                    
                    resposta = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt_executivo)
                    
                    # Gera PDF com Título Específico
                    pdf_output = criar_pdf_buffer(resposta.text, titulo_documento="GEIP - Relatório Executivo Gerencial")
                    
                    st.success("Relatório gerado com sucesso!")
                    st.download_button(
                        label="📥 BAIXAR RELATÓRIO EXECUTIVO",
                        data=pdf_output,
                        file_name="Relatorio_Executivo_GEIP.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"⚠️ Erro ao processar relatório: {e}")

    # ==========================================
    # BOTÃO 2: AUDITORIA DE INTEGRIDADE DE DADOS
    # ==========================================
    with col2:
        # Forçamos o botão a usar 100% do container
        if st.button("🔍 AUDITORIA DE DADOS", use_container_width=True):
            try:
                with st.spinner("Auditando as células e formatações..."):
                    dados_csv = processar_planilha(arquivo)
                    client = genai.Client(api_key=api_key)
                    
                    prompt_auditoria = f"""Atue como um Engenheiro de Dados Sênior da GEIP. 
                    Sua missão é realizar uma varredura estritamente técnica na base de dados para garantir a compatibilidade com o sistema Power BI.
                    
                    DIRETRIZES:
                    1. Foco exclusivo em quebras de padrão lógicas: textos em campos numéricos, datas corrompidas, outliers absurdos ou células vazias.
                    2. IGNORE o contexto de negócios, montantes financeiros globais ou visão de portfólio.
                    3. A primeira coluna chama-se 'Linha_Excel'. Use-a para indicar a localização exata de falhas.
                    4. Se a base estiver perfeita, declare explicitamente: "Nenhuma inconsistência técnica detectada."
                    5. É EXPRESSAMENTE PROIBIDO o uso de formato JSON.

                    ESTRUTURA OBRIGATÓRIA (Use '#' para títulos):
                    # Resumo da Qualidade de Dados
                    # Inconsistências Técnicas Encontradas (Aponte Linha_Excel e o problema exato)
                    # Recomendações de Formatação

                    BASE DE DADOS:
                    {dados_csv}"""
                    
                    resposta = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt_auditoria)
                    
                    # Gera PDF com Título Específico para a Auditoria
                    pdf_output = criar_pdf_buffer(resposta.text, titulo_documento="GEIP - Auditoria de Integridade de Dados")
                    
                    st.success("Auditoria concluída com sucesso!")
                    st.download_button(
                        label="📥 BAIXAR RELATÓRIO DE AUDITORIA",
                        data=pdf_output,
                        file_name="Auditoria_Dados_GEIP.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"⚠️ Erro ao auditar dados: {e}")

# --- RODAPÉ ---
st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <hr style="border: 0; border-top: 1px solid #ddd; margin-bottom: 20px;">
        <p style="color: rgba(0,0,0,0.42); font-style: italic ;font-size: 14px;">'Relatórios gerados por IA podem conter erros e não substituem a análise Humana.'</p>
        <a href="https://fhemigmg.sharepoint.com/sites/GEIP" target="_blank" 
           style="background-color: #018DA6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
           Acessar Portal GEIP
        </a>
    </div>
    """, unsafe_allow_html=True)
