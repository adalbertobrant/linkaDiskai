import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from google import genai

load_dotenv()

# --- Função Auxiliar (Mantida para ler a API Key e o Prompt com segurança) ---
def obter_configuracao(chave):
    if chave in st.secrets:
        return st.secrets[chave]
    return os.getenv(chave)

st.set_page_config(page_title="LinkedIn Analyzer Pro", page_icon="💼", layout="wide")

# Função para extrair texto do PDF
def extrair_texto_pdf(ficheiro_pdf):
    leitor = PyPDF2.PdfReader(ficheiro_pdf)
    texto = ""
    for pagina in leitor.pages:
        texto += pagina.extract_text()
    return texto

# Função para chamar o Gemini 2.0 Flash Lite
def analisar_perfil_com_gemini(texto_perfil, prompt_sistema):
    try:
        api_key = obter_configuracao("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        conteudo_completo = f"{prompt_sistema}\n\nPERFIL PARA ANÁLISE:\n{texto_perfil}"
        
        resposta = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=conteudo_completo
        )
        return resposta.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com a API: {e}"

# --- Lógica Principal da Aplicação (Acesso Direto) ---

# Puxa o prompt das configurações (Secrets ou .env)
prompt_sistema = obter_configuracao("PROMPT_ANALISE_LINKEDIN")

st.title("💼 Analisador de Força do LinkedIn")
st.markdown("Descubra o quão atrativo está o seu perfil para os recrutadores e receba recomendações de melhoria.")

st.info("💡 Vá ao seu perfil do LinkedIn, clique em 'Mais' -> 'Guardar como PDF' e faça o upload abaixo.")

ficheiro_upload = st.file_uploader("Faça o upload do seu perfil (PDF)", type=["pdf"])

if ficheiro_upload is not None:
    with st.spinner("A extrair dados do documento..."):
        texto_extraido = extrair_texto_pdf(ficheiro_upload)
        
    st.success("Documento lido com sucesso!")
    
    if st.button("Analisar Perfil com IA", type="primary"):
        with st.spinner("A analisar o perfil com o Gemini 1.5 Pro. Por favor, aguarde..."):
            resultado_analise = analisar_perfil_com_gemini(texto_extraido, prompt_sistema)
            
            st.divider()
            st.header("📊 Resultados da Análise")
            
            st.markdown(resultado_analise)
