# 💼 LinkedIn Analyzer Pro

Um analisador inteligente de perfis do LinkedIn construído com **Python, Streamlit e Google Gemini 1.5 Pro**. Esta aplicação permite que os utilizadores façam o upload do seu perfil do LinkedIn em formato PDF e recebam uma análise detalhada gerada por Inteligência Artificial, atuando como um Tech Recruiter Sénior.

O objetivo do projeto é ajudar profissionais a otimizarem os seus perfis para conseguirem melhores colocações no mercado, recebendo feedback sobre pontos fortes, pontos de melhoria e recomendações de vagas ideais.

## ✨ Funcionalidades

* **Extração de Texto Offline:** Leitura do perfil exportado em PDF do LinkedIn, contornando bloqueios de scraping e captchas de forma legal e gratuita.
* **Análise com IA Avançada:** Integração com a API do Google Gemini 1.5 Pro para processamento de linguagem natural e geração de insights estruturados.
* **Segurança e Autenticação:** Sistema de login protegido por criptografia de hash **SHA-256**, garantindo que apenas utilizadores autorizados acedam à ferramenta.
* **Proteção de Prompts:** Arquitetura que isola o prompt do sistema e as chaves de API em variáveis de ambiente (`.env`), seguindo as melhores práticas de cibersegurança e desenvolvimento.
* **Interface Interativa:** UI limpa e responsiva construída com Streamlit.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface:** Streamlit
* **IA e LLM:** `google-generativeai` (Gemini 1.5 Pro)
* **Processamento de PDF:** `PyPDF2`
* **Segurança & Configuração:** `hashlib` (SHA-256) e `python-dotenv`

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o repositório
```bash
git clone [https://github.com/adalbertobrant/nome-do-seu-repositorio.git](https://github.com/adalbertobrant/nome-do-seu-repositorio.git)
cd nome-do-seu-repositorio

```

### 2. Criar e ativar um ambiente virtual (Recomendado)

```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt

```

### 4. Configurar as Variáveis de Ambiente

Crie um ficheiro chamado `.env` na raiz do projeto. **Não faça commit deste ficheiro** (certifique-se de que ele está no seu `.gitignore`). Adicione as seguintes chaves:

```env
SENHA_HASH_SHA256=adicione_o_seu_hash_sha256_aqui
PROMPT_ANALISE_LINKEDIN="Atue como um Tech Recruiter Sénior. Analise as informações do perfil a seguir e forneça: 1. Uma nota de 0 a 100 para a força do perfil. 2. Três pontos fortes. 3. Três pontos de melhoria. 4. Três vagas ideais para o perfil. Retorne os dados formatados em Markdown para fácil leitura."
GEMINI_API_KEY=sua_chave_api_do_google_aqui

```

*Dica: Para gerar o hash SHA-256 da sua senha, pode rodar o seguinte comando em Python:*
`import hashlib; print(hashlib.sha256("sua_senha".encode()).hexdigest())`

### 5. Executar a aplicação

```bash
streamlit run app.py

```

*(Substitua `app.py` pelo nome do ficheiro principal do seu código).*

## 💡 Como Usar

1. Aceda à aplicação no seu navegador (geralmente em `http://localhost:8501`).
2. Digite a palavra-passe de acesso.
3. Vá ao seu perfil do LinkedIn, clique em **Mais...** e depois em **Guardar como PDF**.
4. Faça o upload desse PDF na aplicação.
5. Clique em "Analisar Perfil com IA" e aguarde os resultados!

---

**Desenvolvido por [Adalberto Caldeira Brant Filho**](https://github.com/adalbertobrant) 🌐 Visite o meu site: [ilhadev.com.br](https://ilhadev.com.br/)

