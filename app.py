import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from google import genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import io

load_dotenv()

# --- Função Auxiliar ---
def obter_configuracao(chave):
    if chave in st.secrets:
        return st.secrets[chave]
    return os.getenv(chave)

st.set_page_config(page_title="LinkedIn Analyzer Pro", page_icon="💼", layout="wide")

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #0077B5 0%, #00A0DC 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,119,181,0.3);
    }
    .metric-card h2 { font-size: 2.5rem; margin: 0; font-weight: 700; }
    .metric-card p  { margin: 4px 0 0; font-size: 0.9rem; opacity: 0.9; }

    .checklist-item {
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        font-size: 0.95rem;
    }
    .check-ok  { background: #e8f5e9; color: #2e7d32; }
    .check-no  { background: #fff3e0; color: #e65100; }

    .teaser-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 28px;
        color: white;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .teaser-box h3 { color: #00A0DC; margin-bottom: 6px; }

    .keyword-pill {
        display: inline-block;
        background: #e3f2fd;
        color: #0077B5;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #90caf9;
    }
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0077B5;
        border-bottom: 2px solid #e0f0fb;
        padding-bottom: 6px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- Funções de Extração ---
def extrair_texto_pdf(ficheiro_pdf):
    leitor = PyPDF2.PdfReader(ficheiro_pdf)
    texto = ""
    for pagina in leitor.pages:
        texto += pagina.extract_text() or ""
    return texto

def contar_secoes(texto):
    secoes = {
        "Resumo / Sobre":  ["sobre", "about", "summary", "resumo"],
        "Experiência":     ["experiência", "experience", "cargo", "empresa"],
        "Formação":        ["formação", "education", "graduação", "universidade", "faculdade"],
        "Competências":    ["competências", "skills", "habilidades", "conhecimentos"],
        "Certificações":   ["certificação", "certification", "certificado", "licença"],
        "Idiomas":         ["idioma", "language", "língua", "inglês", "espanhol", "português"],
        "Recomendações":   ["recomendação", "recommendation", "recomendou"],
        "Projetos":        ["projeto", "project"],
    }
    texto_lower = texto.lower()
    return {s: any(p in texto_lower for p in palavras) for s, palavras in secoes.items()}

def extrair_palavras_chave(texto, top_n=20):
    stopwords = set([
        "de","a","o","e","do","da","em","um","para","com","uma","os","no",
        "se","na","por","mais","as","dos","das","ao","aos","que","não","ou",
        "seu","sua","seus","suas","ele","ela","eles","elas","eu","nós","este",
        "esta","isso","aqui","ter","ser","foi","como","mas","pelo","pela",
        "entre","após","sobre","até","desde","quando","também","porque",
        "então","ainda","já","muito","bem","anos","ano","mesmo","todo",
        "toda","minha","meu","contact","page","linkedin","profile",
        "the","of","and","in","to","for","is","are","was","were","have",
        "has","had","with","on","at","by","from","be","been"
    ])
    palavras = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', texto.lower())
    filtradas = [p for p in palavras if p not in stopwords]
    return Counter(filtradas).most_common(top_n)

def gerar_nuvem_palavras(texto):
    stopwords = set([
        "de","a","o","e","do","da","em","um","para","com","uma","os","no",
        "se","na","por","mais","as","dos","das","ao","aos","que","não","ou",
        "seu","sua","seus","suas","ele","ela","eles","elas","eu","nós","este",
        "esta","isso","aqui","ter","ser","foi","como","mas","pelo","pela",
        "entre","após","sobre","até","desde","quando","também","porque",
        "então","ainda","já","muito","bem","anos","ano","mesmo","todo",
        "toda","minha","meu","contact","page","linkedin","profile",
        "the","of","and","in","to","for","is","are","was","were","have",
        "has","had","with","on","at","by","from","be","been"
    ])
    wc = WordCloud(
        width=900, height=420,
        background_color="white",
        colormap="Blues",
        stopwords=stopwords,
        max_words=80,
        prefer_horizontal=0.8,
        collocations=False,
    )
    wc.generate(texto)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    fig.patch.set_facecolor('white')
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def estimar_pontuacao_base(secoes, top_palavras, texto):
    pontos = 0
    pesos = {
        "Resumo / Sobre": 15, "Experiência": 20, "Formação": 10,
        "Competências": 15, "Certificações": 10, "Idiomas": 10,
        "Recomendações": 10, "Projetos": 5,
    }
    for secao, presente in secoes.items():
        if presente:
            pontos += pesos.get(secao, 0)
    if len(top_palavras) >= 15:
        pontos += 5
    return min(pontos, 70)  # Máx 70 visível — a IA revela o resto

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

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

prompt_sistema = obter_configuracao("PROMPT_ANALISE_LINKEDIN")

st.title("💼 LinkedIn Analyzer Pro")
st.markdown("**Descubra em segundos o potencial do seu perfil** — e receba um plano de ação gerado por IA para atrair mais recrutadores.")
st.info("💡 No LinkedIn: clique em **Mais…** → **Guardar como PDF** e faça o upload abaixo.")

ficheiro_upload = st.file_uploader("📎 Upload do seu perfil LinkedIn (PDF)", type=["pdf"])

if ficheiro_upload is not None:
    with st.spinner("📄 A ler o documento..."):
        texto_extraido  = extrair_texto_pdf(ficheiro_upload)
        secoes          = contar_secoes(texto_extraido)
        top_palavras    = extrair_palavras_chave(texto_extraido, top_n=20)
        pontuacao_base  = estimar_pontuacao_base(secoes, top_palavras, texto_extraido)
        secoes_ok       = sum(1 for v in secoes.values() if v)
        total_secoes    = len(secoes)
        palavras_unicas = len(set(re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', texto_extraido.lower())))
        total_chars     = len(texto_extraido)
        densidade       = "Alta" if total_chars > 3000 else ("Média" if total_chars > 1500 else "Baixa")

    st.success("✅ Perfil carregado com sucesso!")
    st.divider()

    # ── PRÉ-ANÁLISE ──────────────────────────────────────────
    st.subheader("🔍 Pré-visualização do Perfil")
    st.caption("Análise instantânea antes de enviar para a IA — veja o que já temos sobre o seu perfil.")

    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{secoes_ok}/{total_secoes}</h2>
            <p>Seções Detectadas</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{palavras_unicas}</h2>
            <p>Palavras Únicas</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(top_palavras)}</h2>
            <p>Termos Relevantes</p>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{densidade}</h2>
            <p>Densidade de Conteúdo</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Checklist + Teaser lado a lado
    col_check, col_teaser = st.columns([1, 1])

    with col_check:
        st.markdown('<p class="section-header">✅ Checklist de Completude</p>', unsafe_allow_html=True)
        for secao, presente in secoes.items():
            icon = "✅" if presente else "⚠️"
            cls  = "check-ok" if presente else "check-no"
            msg  = "Detectado" if presente else "Não encontrado"
            st.markdown(
                f'<div class="checklist-item {cls}">{icon} <b>{secao}</b> — {msg}</div>',
                unsafe_allow_html=True
            )

    with col_teaser:
        st.markdown('<p class="section-header">🎯 Pré-score do Perfil</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="teaser-box">
            <h3>Pontuação Parcial Detectada</h3>
            <p style="font-size:0.85rem; opacity:0.7; margin-bottom:18px;">
                Com base nas seções encontradas no seu PDF
            </p>
            <div style="font-size:4rem; font-weight:900; line-height:1;">
                {pontuacao_base}<span style="font-size:1.8rem; opacity:0.6;">/100</span>
            </div>
            <div style="background:rgba(255,255,255,0.1); border-radius:10px; height:12px; margin:18px 0 8px;">
                <div style="background:linear-gradient(90deg,#00A0DC,#0077B5); width:{pontuacao_base}%; height:12px; border-radius:10px;"></div>
            </div>
            <p style="font-size:0.8rem; opacity:0.6;">
                🔒 Os restantes <b>{100 - pontuacao_base} pontos</b> são avaliados pela IA —<br>
                inclui impacto real no mercado, qualidade do texto e alinhamento com vagas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Nuvem de Palavras
    st.markdown('<p class="section-header">☁️ Nuvem de Palavras do Perfil</p>', unsafe_allow_html=True)
    st.caption("As palavras mais presentes no seu perfil — reflectem como os recrutadores percebem o seu posicionamento.")

    if len(texto_extraido.strip()) > 100:
        with st.spinner("A gerar nuvem de palavras..."):
            img_buf = gerar_nuvem_palavras(texto_extraido)
        st.image(img_buf, use_container_width=True)
    else:
        st.warning("Texto insuficiente para gerar a nuvem de palavras.")

    # Top keywords como pills
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">🏷️ Termos Mais Frequentes</p>', unsafe_allow_html=True)
    st.caption("Estas são as palavras que mais caracterizam o seu perfil actualmente.")
    pills_html = "".join(
        f'<span class="keyword-pill">{palavra} <span style="opacity:0.5">×{freq}</span></span>'
        for palavra, freq in top_palavras[:15]
    )
    st.markdown(f'<div style="line-height:2.4;">{pills_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # CTA para análise IA
    st.markdown("### 🚀 Pronto para a análise completa?")
    st.markdown(
        "A IA vai avaliar o **impacto real** do seu perfil, identificar pontos cegos e "
        "recomendar as melhores vagas para o seu momento de carreira."
    )

    if st.button("✨ Analisar Perfil com IA Agora", type="primary", use_container_width=True):
        with st.spinner("🤖 A analisar com o Gemini 2.0 Flash Lite. Por favor, aguarde..."):
            resultado_analise = analisar_perfil_com_gemini(texto_extraido, prompt_sistema)

        st.divider()
        st.header("📊 Resultados Completos da Análise IA")
        st.markdown(resultado_analise)
