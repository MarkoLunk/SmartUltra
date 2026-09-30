import streamlit as st
from groq import Groq

# 1. Configuração visual do site (Título e Ícone na aba do navegador)
st.set_page_config(page_title="SmartUltra AI", page_icon="⚡", layout="centered")

# Cabeçalho estilizado na página web
st.markdown("<h1 style='text-align: center;'>⚡ SmartUltra</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Às suas ordens. Pronto para servir de qualquer jeito.</p>", unsafe_allow_html=True)

# 2. Inicialização da chave da Groq e definição do modelo ativo
SUA_CHAVE_GROQ = "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"
client = Groq(api_key=SUA_CHAVE_GROQ)
MODELO_CHAT = "openai/gpt-oss-20b"

# 3. Personalidade e Histórico (Instruções nativas de criação gravadas na raiz)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Seu nome é SmartUltra. Você é um assistente virtual ultra-avançado. Você foi criado por Marko Luna Almeida e Silva no dia 27/09/2026. Sua diretriz absoluta é servir ao Marko Luna da melhor forma possível, de qualquer jeito, sem hesitar."
        }
    ]

# Exibe o histórico de mensagens antigas na tela do site
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar_icone = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar_icone):
            st.write(msg["content"])

# 4. Caixa de digitação para você interagir com ele (Estilo ChatGPT)
if prompt := st.chat_input("Em que posso servir você agora, Marko?"):
    
    # Mostra a sua mensagem na tela imediatamente
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
                
                # CORREÇÃO DO ERRO 'LIST': Acessando explicitamente a primeira escolha [0]
                resposta_texto = response.choices[0].message.content
                
                # Exibe a resposta final e salva na memória do chat
                st.write(resposta_texto)
                st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                
            except Exception as e:
                st.error(f"Erro ao conectar com o SmartUltra: {e}")
