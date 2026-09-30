import streamlit as st
from groq import Groq

# 1. Configuração visual do site (Título e Ícone na aba do navegador)
st.set_page_config(page_title="SmartUltra SU20", page_icon="⚡", layout="centered")

# Cabeçalho estilizado na página web com a versão oficial SU20
st.markdown("<h1 style='text-align: center;'>⚡ SmartUltra <span style='font-size: 1.2rem; color: #888;'>SU20</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Às suas ordens. Pronto para servir de qualquer jeito.</p>", unsafe_allow_html=True)

# 2. Inicialização da chave da Groq e definição do modelo ativo
SUA_CHAVE_GROQ = "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"
client = Groq(api_key=SUA_CHAVE_GROQ)
MODELO_CHAT = "openai/gpt-oss-20b"

# 3. Configuração do Perfil do Usuário na Barra Lateral (Sidebar)
with st.sidebar:
    st.markdown("## 👤 Perfil do Usuário")
    
    # Campo para o usuário configurar o próprio nome
    nome_usuario = st.text_input("Qual é o seu nome?", value="Usuário", placeholder="Digite seu nome aqui...")
    
    st.markdown("---")
    st.markdown("### Configurações do Chat")
    # Botão de limpar conversa adaptado
    if st.button("Limpar Conversa"):
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

# 4. Personalidade Dinâmica (Injeta o nome configurado diretamente no sistema da IA)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                f"Seu nome é SmartUltra, versão oficial SU20. Você é um assistente virtual ultra-avançado. "
                f"Você foi criado por Marko Luna Almeida e Silva no dia 27/09/2026. "
                f"DIRETRIZ DE IDENTIDADE: Você está conversando com o usuário chamado '{nome_usuario}'. "
                f"Sempre que apropriado, trate-o pelo nome '{nome_usuario}' de forma educada e prestativa (Ex: 'Olá, {nome_usuario}!', 'Como posso ajudar, {nome_usuario}?'). "
                f"A ÚNICA OCASIÃO em que você está autorizado a citar o nome do seu criador (Marko Luna) é se alguém perguntar "
                f"explicitamente sobre a sua criação, origem ou quem fez você. De resto, foque em servir ao '{nome_usuario}'."
            )
        }
    ]
else:
    # Atualiza dinamicamente o nome do usuário no sistema caso ele mude o texto na barra lateral no meio do chat
    st.session_state.messages[0]["content"] = (
        f"Seu nome é SmartUltra, versão oficial SU20. Você é um assistente virtual ultra-avançado. "
        f"Você foi criado por Marko Luna Almeida e Silva no dia 27/09/2026. "
        f"DIRETRIZ DE IDENTIDADE: Você está conversando com o usuário chamado '{nome_usuario}'. "
        f"Sempre que apropriado, trate-o pelo nome '{nome_usuario}' de forma educada e prestativa. "
        f"A ÚNICA OCASIÃO em que você está autorizado a citar o nome do seu criador (Marko Luna) é se alguém perguntar "
        f"explicitamente sobre a sua criação, origem ou quem fez você."
    )

# Exibe o histórico de mensagens antigas na tela do site
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar_icone = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar_icone):
            st.write(msg["content"])

# 5. Caixa de digitação limpa e interativa
if prompt := st.chat_input("Em que posso servir você agora?"):
    
    # Mostra a mensagem do usuário na tela imediatamente
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Busca a resposta do SmartUltra com animação de carregamento
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Processando ordens..."):
            try:
                response = client.chat.completions.create(
                    model=MODELO_CHAT,
                    messages=st.session_state.messages
                )
                
                resposta_texto = response.choices[0].message.content
                
                # Exibe a resposta final e salva na memória do chat
                st.write(resposta_texto)
                st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                
            except Exception as e:
                st.error(f"Erro ao conectar com o SmartUltra: {e}")

# 6. O aviso solicitado posicionado logo abaixo da caixa de texto
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 0.8rem; margin-top: 10px;'> "
    "IAs cometem erros, pesquise em abas confiáveis."
    "</p>", 
    unsafe_allow_html=True
)
