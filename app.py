import streamlit as st
from groq import Groq
import sqlite3
import hashlib
import json
import urllib.request
import urllib.parse
import re

# ==========================================
# 1. CONFIGURAÇÃO VISUAL E BANCO DE DADOS
# ==========================================
st.set_page_config(page_title="SmartUltra SU20", page_icon="⚡", layout="centered")

def iniciar_banco():
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, titulo TEXT, mensagens TEXT)")
    conn.commit()
    conn.close()

iniciar_banco()

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(usuario, senha):
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (usuario, criptografar_senha(senha)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_usuario(usuario, senha):
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (usuario, criptografar_senha(senha)))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def carregar_conversas_usuario(username):
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo FROM historico WHERE username = ? ORDER BY id DESC", (username,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def carregar_mensagens_chat(chat_id):
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT mensagens FROM historico WHERE id = ?", (chat_id,))
    dados = cursor.fetchone()
    conn.close()
    return json.loads(dados) if dados else None

def salvar_ou_atualizar_chat(username, chat_id, titulo, mensagens):
    conn = sqlite3.connect("smartultra.db")
    cursor = conn.cursor()
    mensagens_json = json.dumps(mensagens)
    if chat_id is None:
        cursor.execute("INSERT INTO historico (username, titulo, mensagens) VALUES (?, ?, ?)", (username, titulo, mensagens_json))
        chat_id = cursor.lastrowid
    else:
        cursor.execute("UPDATE historico SET mensagens = ? WHERE id = ?", (mensagens_json, chat_id))
    conn.commit()
    conn.close()
    return chat_id

# ==========================================
# 2. MOTOR DE BUSCA EM TEMPO REAL
# ==========================================
def buscar_noticias_tempo_real(termo_busca):
    try:
        url_busca = f"https://duckduckgo.com{urllib.parse.quote(termo_busca)}"
        req = urllib.request.Request(url_busca, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            contexto = "\n".join([re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:3]])
            return contexto if contexto else "Nenhuma notícia recente encontrada."
    except Exception:
        return "Não foi possível acessar os servidores de notícias no momento."

# ==========================================
# 3. INTERFACE DE LOGIN / CADASTRO
# ==========================================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_atual = ""
    st.session_state.chat_atual_id = None

if not st.session_state.logado:
    st.markdown("<h1 style='text-align: center;'>⚡ SmartUltra <span style='font-size: 1.2rem; color: #88;'>SU20</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Crie sua conta ou faça login para começar.</p>", unsafe_allow_html=True)
    
    aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    
    with aba_login:
        user_login = st.text_input("Usuário", key="main_login_user")
        pass_login = st.text_input("Senha", type="password", key="main_login_pass")
        if st.button("Acessar SmartUltra", key="btn_acessar_su"):
            if verificar_usuario(user_login, pass_login):
                st.session_state.logado = True
                st.session_state.usuario_atual = user_login
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
                
    with aba_cadastro:
        user_cad = st.text_input("Escolha um Nome de Usuário", key="main_cad_user")
        pass_cad = st.text_input("Escolha uma Senha", type="password", key="main_cad_pass")
        if st.button("Cadastrar", key="btn_cadastrar_su"):
            if user_cad and pass_cad:
                if cadastrar_usuario(user_cad, pass_cad):
                    st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                else:
                    st.error("Este nome de usuário já está em uso.")
            else:
                st.warning("Preencha todos os campos.")

# ==========================================
# 4. AMBIENTE DO CHAT (APÓS LOGIN)
# ==========================================
else:
    # Token configurado diretamente para inicialização limpa
    client = Groq(api_key="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")
    MODELO_CHAT = "llama-3.3-70b-versatile"

    # BARRA LATERAL
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.usuario_atual}!")
        if st.button("➕ Nova Conversa", use_container_width=True, key="btn_nova_conversa"):
            st.session_state.chat_atual_id = None
            if "messages" in st.session_state:
                del st.session_state["messages"]
            st.rerun()
            
        st.markdown("---")
        st.markdown("📂 **Seus Chats Salvos:**")
        lista_chats = carregar_conversas_usuario(st.session_state.usuario_atual)
        for cid, tit in lista_chats:
            if st.button(f"💬 {tit}", key=f"chat_item_{cid}", use_container_width=True):
                st.session_state.chat_atual_id = cid
                st.session_state.messages = carregar_mensagens_chat(cid)
                st.rerun()
                
        st.markdown("---")
        if st.button("🚪 Sair da Conta", use_container_width=True, key="btn_logout"):
            st.session_state.logado = False
            st.session_state.usuario_atual = ""
            st.session_state.chat_atual_id = None
            if "messages" in st.session_state:
                del st.session_state["messages"]
            st.rerun()

    # Memória do Chat
    if "messages" not in st.session_state or st.session_state.messages is None:
        st.session_state.messages = [
            {
                "role": "system", 
                "content": (
                    f"Seu nome é SmartUltra, versão oficial SU20. Você é um assistente virtual ultra-avançado. "
                    f"Você foi criado por Marko Luna Almeida e Silva no dia 27/09/2026. "
                    f"DIRETRIZ DE IDENTIDADE: Você está conversando com o usuário chamado '{st.session_state.usuario_atual}'. "
                    f"Sempre que apropriado, trate-o pelo nome de forma educada. "
                    f"A ÚNICA OCASIÃO em que você está autorizado a citar o nome do seu criador (Marko Luna) é se alguém perguntar "
                    f"explicitamente sobre a sua criação, origem ou quem fez você. Nessa única ocasião, responda estritamente: "
                    f"'Fui criado por Marko Luna Almeida e Silva no dia 27/09/2026.' De resto, foque em servir ao usuário atual."
                )
            }
        ]

    st.markdown(f"<h1 style='text-align: center;'>⚡ SmartUltra <span style='font-size: 1.2rem; color: #88;'>SU20</span></h1>", unsafe_allow_html=True)

    # Renderiza histórico na tela
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            avatar_icone = "👤" if msg["role"] == "user" else "⚡"
            with st.chat_message(msg["role"], avatar=avatar_icone):
                st.write(msg["content"])

    # Caixa de Entrada do Chat
    if prompt := st.chat_input("Em que posso servir você agora?"):
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
            
        palavras_chave_tempo_real = ["hoje", "notícia", "recente", "tempo real", "quem ganhou", "atual", "2026"]
        contexto_web = ""
        if any(p in prompt.lower() for p in palavras_chave_tempo_real):
            with st.spinner("Buscando informações em tempo real..."):
                contexto_web = buscar_noticias_tempo_real(prompt)

        historico_envio = list(st.session_state.messages)
        if contexto_web:
            historico_envio.append({"role": "system", "content": f"INFORMAÇÃO EM TEMPO REAL: {contexto_web}"})
            
        historico_envio.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Processando ordens..."):
                try:
                    response = client.chat.completions.create(model=MODELO_CHAT, messages=historico_envio)
                    resposta_texto = response.choices.message.content
                    st.write(resposta_texto)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                    
                    tit_chat = prompt[:20] + "..." if len(prompt) > 20 else prompt
