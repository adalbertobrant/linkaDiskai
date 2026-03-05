import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from google import genai

# Mantemos o load_dotenv para quando você for rodar e testar na sua máquina local
load_dotenv()

# --- Função Auxiliar de Segurança ---
def obter_configuracao(chave):
    """Tenta buscar a variável no Streamlit Cloud (st.secrets). 
       Se falhar, busca no ambiente local (os.getenv)."""
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

# Função para chamar o Gemini 1.5 Pro
def analisar_perfil_com_gemini(texto_perfil, prompt_sistema):
    try:
        # Puxa a chave da API usando a nossa nova função robusta
        api_key = obter_configuracao("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        conteudo_completo = f"{prompt_sistema}\n\nPERFIL PARA ANÁLISE:\n{texto_perfil}"
        
        resposta = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=conteudo_completo
        )
        return resposta.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com a API: {e}"

# --- Sistema de Autenticação ---
def verificar_senha():
    def checar_senha():
        senha_digitada = st.session_state["senha_input"]
        senha_correta = obter_configuracao("SENHA_ACESSO")
        
        if senha_digitada == senha_correta:
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
    
    # Puxa o prompt usando a nova função
    prompt_sistema = obter_configuracao("PROMPT_ANALISE_LINKEDIN")
    
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
                
                st.markdown(resultado_analise)
