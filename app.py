import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from google import genai

load_dotenv()

# --- Função Auxiliar de Segurança com DEBUG ---
def obter_configuracao(chave):
    print(f"[DEBUG] A tentar obter a chave: '{chave}'")
    
    # 1. Tenta pegar do painel Secrets do Streamlit Cloud
    try:
        if chave in st.secrets:
            valor = st.secrets[chave]
            print(f"[DEBUG] Sucesso! A chave '{chave}' foi encontrada no st.secrets.")
            return valor
        else:
            print(f"[DEBUG] A chave '{chave}' NÃO está no st.secrets.")
    except Exception as e:
        print(f"[DEBUG] Erro ao aceder ao st.secrets: {e}")

    # 2. Tenta pegar do ficheiro .env (ambiente local)
    valor_env = os.getenv(chave)
    if valor_env:
        print(f"[DEBUG] Sucesso! A chave '{chave}' foi encontrada no os.getenv().")
        return valor_env
        
    print(f"[DEBUG] ALERTA CRÍTICO: A chave '{chave}' não foi encontrada em lado nenhum!")
    return None

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

# --- Sistema de Autenticação com DEBUG ---
def verificar_senha():
    def checar_senha():
        print("\n=== INICIANDO TENTATIVA DE LOGIN ===")
        
        # Pega a senha que o utilizador digitou no input
        senha_digitada = st.session_state.get("senha_input", "")
        # Puxa a senha do sistema (Secrets ou .env)
        senha_correta = obter_configuracao("SENHA_ACESSO")
        
        # O repr() vai mostrar se há espaços invisíveis, ex: 'hello_world_2026 '
        print(f"[DEBUG] Senha digitada na tela: {repr(senha_digitada)}")
        print(f"[DEBUG] Senha guardada no sistema: {repr(senha_correta)}")
        
        if senha_digitada == senha_correta:
            print("[DEBUG] RESULTADO: As senhas coincidem! Acesso liberado.")
            st.session_state["autenticado"] = True
        else:
            print("[DEBUG] RESULTADO: As senhas são DIFERENTES! Acesso negado.")
            st.session_state["autenticado"] = False
        
        print("======================================\n")

    if st.session_state.get("autenticado", False):
        return True

    st.title("🔒 Acesso Restrito")
    st.text_input("Digite a palavra-passe para utilizar o Analisador:", type="password", on_change=checar_senha, key="senha_input")
    
    if "autenticado" in st.session_state and not st.session_state["autenticado"]:
        st.error("Acesso negado. Palavra-passe incorreta.")
    return False

# --- Lógica Principal da Aplicação ---
if verificar_senha():
    
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
