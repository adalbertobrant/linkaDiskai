import streamlit as st
import hashlib
import os
from dotenv import load_dotenv
import PyPDF2
import google.generativeai as genai

# Carrega as variáveis de segurança e configuração do ficheiro .env
load_dotenv()

# Configuração da API do Gemini usando a chave do .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="LinkedIn Analyzer Pro", page_icon="💼", layout="wide")

# Função para extrair texto do PDF
def extrair_texto_pdf(ficheiro_pdf):
    leitor = PyPDF2.PdfReader(ficheiro_pdf)
    texto = ""
    for pagina in leitor.pages:
        texto += pagina.extract_text()
    return texto

# Função para chamar o Gemini 1.5 Pro
def analisar_perfil_com_gemini(texto_perfil, prompt_sistema):
    try:
        # Instancia o modelo 1.5 Pro
        modelo = genai.GenerativeModel('gemini-1.5-pro')
        
        # Junta o prompt de sistema com o conteúdo do currículo/perfil
        conteudo_completo = f"{prompt_sistema}\n\nPERFIL PARA ANÁLISE:\n{texto_perfil}"
        
        # Faz a chamada à API
        resposta = modelo.generate_content(conteudo_completo)
        return resposta.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com a API: {e}"

# --- Sistema de Autenticação ---
def verificar_senha():
    def checar_senha():
        senha_digitada = st.session_state["senha_input"]
        hash_digitado = hashlib.sha256(senha_digitada.encode()).hexdigest()
        
        if hash_digitado == os.getenv("SENHA_HASH_SHA256"):
            st.session_state["autenticado"] = True
            del st.session_state["senha_input"] 
        else:
            st.session_state["autenticado"] = False

    if st.session_state.get("autenticado", False):
        return True

    st.title("🔒 Acesso Restrito")
    st.text_input("Digite a palavra-passe para utilizar o Analisador:", type="password", on_change=checar_senha, key="senha_input")
    
    if "autenticado" in st.session_state and not st.session_state["autenticado"]:
        st.error("Acesso negado. Palavra-passe incorreta.")
    return False

# --- Lógica Principal da Aplicação ---
if verificar_senha():
    
    # Puxamos o prompt do .env
    prompt_sistema = os.getenv("PROMPT_ANALISE_LINKEDIN")
    
    st.title("💼 Analisador de Força do LinkedIn")
    st.markdown("Descubra o quão atrativo está o seu perfil para os recrutadores e receba recomendações.")

    st.info("💡 Vá ao seu perfil do LinkedIn, clique em 'Mais' -> 'Guardar como PDF' e faça o upload abaixo.")

    ficheiro_upload = st.file_uploader("Faça o upload do seu perfil", type=["pdf"])

    if ficheiro_upload is not None:
        with st.spinner("A extrair dados do PDF..."):
            texto_extraido = extrair_texto_pdf(ficheiro_upload)
            
        st.success("Documento lido com sucesso!")
        
        if st.button("Analisar Perfil com IA", type="primary"):
            with st.spinner("A analisar o perfil com o Gemini 1.5 Pro. Por favor, aguarde..."):
                resultado_analise = analisar_perfil_com_gemini(texto_extraido, prompt_sistema)
                
                st.divider()
                st.header("📊 Resultados da Análise")
                
                # Como pedimos ao Gemini para retornar em Markdown no prompt, 
                # podemos renderizar a resposta diretamente no Streamlit
                st.markdown(resultado_analise)
