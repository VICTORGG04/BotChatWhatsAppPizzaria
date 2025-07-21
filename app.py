# app.py

from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv # Para carregar a chave API do .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração da IA (Google Gemini) ---
import google.generativeai as genai

# Obtém a chave API da variável de ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("A chave GEMINI_API_KEY não está configurada no arquivo .env ou nas variáveis de ambiente.")

genai.configure(api_key=GEMINI_API_KEY)

# --- CARDÁPIO DA PIZZARIA ---
# Usando chaves em minúsculas para facilitar a comparação com a entrada do usuário
CARDAPIO = {
    "margherita": {"preco": 35.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Manjericão"]},
    "calabresa": {"preco": 40.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Calabresa", "Cebola"]},
    "portuguesa": {"preco": 45.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Presunto", "Ovo", "Cebola"]},
    "quatro queijos": {"preco": 50.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Parmesão", "Gorgonzola", "Provolone"]},
    "frango com catupiry": {"preco": 55.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Frango desfiado", "Catupiry"]},
}

# --- FUNÇÕES DO CHATBOT ADAPTADAS PARA API ---
# Elas NÃO terão mais 'input()' nem 'print()' diretamente.
# Elas receberão dados como argumentos e retornarão strings como resposta do bot.

def saudacao_string():
    """Retorna a mensagem de saudação e menu inicial."""
    return (
        "Olá! Bem-vindo à Pizzaria Delícia!\n"
        "Sou seu assistente virtual. Como posso ajudar?\n"
        "1. Ver Cardápio\n"
        "2. Fazer Pedido\n"
        "3. Falar com Atendente\n"
        "4. Sair"
    )

def exibir_cardapio_string():
    """Retorna o cardápio formatado como uma string."""
    cardapio_str = "--- NOSSO CARDÁPIO ---\n"
    for sabor, detalhes in CARDAPIO.items():
        sabor_formatado = sabor.replace("_", " ").title()
        ingredientes_str = ", ".join(detalhes['ingredientes'])
        cardapio_str += f"- {sabor_formatado}: R$ {detalhes['preco']:.2f} - Ingredientes: {ingredientes_str}.\n"
    cardapio_str += "----------------------"
    return cardapio_str

def processar_pedido_bot(user_message, session_data):
    """
    Processa a mensagem do usuário para o fluxo de pedido.
    session_data: um dicionário para manter o estado da conversa (pedido atual, total, etc.)
    Retorna a resposta do bot e o session_data atualizado.
    """
    # Inicializa o pedido e total na sessão se não existirem
    if 'current_order' not in session_data:
        session_data['current_order'] = {}
        session_data['order_total'] = 0.0
        session_data['state'] = 'awaiting_flavor' # Novo estado: esperando o sabor

    current_state = session_data['state']
    response_message = ""

    if current_state == 'awaiting_flavor':
        sabor_input = user_message.lower().strip()

        if sabor_input == 'fim':
            if session_data['current_order']:
                resumo = "Seu pedido foi finalizado com sucesso!\nResumo do Pedido:\n"
                for sabor_final, quantidade_final in session_data['current_order'].items():
                    resumo += f"{quantidade_final}x {sabor_final.replace('_', ' ').title()} - (R$ {CARDAPIO[sabor_final]['preco']:.2f} cada)\n"
                resumo += f"Total: R$ {session_data['order_total']:.2f}\nQual seu endereço para entrega?"
                session_data['state'] = 'awaiting_address'
                response_message = resumo
            else:
                response_message = "Nenhum item adicionado ao pedido. Digite o sabor da pizza ou 'cancelar'."
        elif sabor_input == 'cancelar':
            session_data['current_order'] = {}
            session_data['order_total'] = 0.0
            session_data['state'] = 'initial' # Volta para o estado inicial
            response_message = "Pedido cancelado. Como posso ajudar agora?\n" + saudacao_string()
        else:
            # Procura o sabor no cardápio
            matched_sabor = None
            for key_sabor in CARDAPIO.keys():
                if sabor_input in key_sabor or key_sabor in sabor_input: # Permite correspondência parcial
                    matched_sabor = key_sabor
                    break

            if matched_sabor:
                session_data['awaiting_quantity_for'] = matched_sabor
                session_data['state'] = 'awaiting_quantity'
                response_message = f"Certo, {matched_sabor.title()}! Quantas pizzas de {matched_sabor.title()} você gostaria?"
            else:
                response_message = "Desculpe, esse sabor não está no cardápio ou não entendi. Tente um sabor válido ou 'cardápio'."

    elif current_state == 'awaiting_quantity':
        sabor = session_data.get('awaiting_quantity_for')
        try:
            quantidade = int(user_message.strip())
            if quantidade <= 0:
                response_message = "Quantidade inválida. Por favor, insira um número maior que zero."
            else:
                preco_pizza = CARDAPIO[sabor]['preco']
                session_data['current_order'][sabor] = session_data['current_order'].get(sabor, 0) + quantidade
                session_data['order_total'] += preco_pizza * quantidade
                session_data['state'] = 'awaiting_flavor' # Volta para o estado de espera de sabor
                response_message = f"{quantidade}x {sabor.title()} adicionada(s) ao seu pedido. Digite outro sabor ou 'fim' para finalizar."
        except ValueError:
            response_message = "Entrada inválida. Por favor, insira um número inteiro para a quantidade."

    elif current_state == 'awaiting_address':
        session_data['address'] = user_message.strip()
        response_message = (
            f"Confirmado! Seu pedido totalizou R$ {session_data['order_total']:.2f} e será entregue em: {session_data['address']}.\n"
            "Aguarde a confirmação final de um de nossos atendentes.\n"
            "Obrigado por escolher a Pizzaria Delícia!"
        )
        # Limpa o estado da sessão após finalizar o pedido
        session_data['current_order'] = {}
        session_data['order_total'] = 0.0
        session_data['address'] = ''
        session_data['state'] = 'initial'
        
    return response_message, session_data

# --- FUNÇÃO DE IA PARA RESUMIR CONVERSA ---
def resumir_conversa_com_ia(chat_history):
    """
    Usa a IA (Google Gemini) para resumir o histórico da conversa para o atendente.
    chat_history: Lista de dicionários com {"role": "user/model", "parts": [{"text": "mensagem"}]}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Construir o prompt com o histórico da conversa
        prompt_parts = [
            "Você é um assistente que resume conversas de chatbot. Com base no histórico da conversa a seguir, por favor, gere um breve resumo para um atendente humano. Inclua o principal problema ou pedido do cliente e quaisquer detalhes importantes. Seja conciso e direto. Se o usuário estava fazendo um pedido, resuma o pedido atual.\n\n"
        ]
        
        for msg in chat_history:
            if msg['role'] == 'user':
                prompt_parts.append(f"Cliente: {msg['parts'][0]['text']}\n")
            elif msg['role'] == 'model':
                prompt_parts.append(f"Bot: {msg['parts'][0]['text']}\n")
        
        prompt_parts.append("\nResumo para o atendente:")

        response = model.generate_content(prompt_parts)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao resumir conversa com IA: {e}")
        return "Não foi possível gerar um resumo automático no momento."

def falar_com_atendente_inteligente(user_id, user_session):
    """
    Transfere para atendente, gerando um resumo da conversa com IA.
    user_session: os dados da sessão do usuário, incluindo o histórico de chat.
    """
    chat_history = user_session.get('chat_history', [])

    # Gera o resumo da conversa usando a IA
    resumo_gerado_ia = resumir_conversa_com_ia(chat_history)

    # Mensagem que o bot envia para o usuário
    bot_message_to_user = (
        "Ok! Estou transferindo você para um de nossos atendentes. "
        "Ele(a) terá acesso ao histórico da nossa conversa e um resumo gerado por IA.\n"
        "Por favor, aguarde um momento."
    )

    # --- SIMULAÇÃO DE ENVIO PARA UM SISTEMA DE ATENDIMENTO HUMANO ---
    # Em um cenário real, você faria uma requisição HTTP POST para a API de um CRM
    # (Ex: Zendesk, Freshdesk, Chatwoot, ou seu próprio sistema de atendimento).
    # Esta requisição enviaria o 'user_id', 'resumo_gerado_ia' e talvez o 'chat_history' completo.
    
    print(f"\n--- LOG DE TRANSFERÊNCIA PARA ATENDENTE ---")
    print(f"Usuário: {user_id}")
    print(f"Resumo da Conversa (IA): {resumo_gerado_ia}")
    print(f"Histórico Completo (para referência):")
    for msg in chat_history:
        print(f"  {msg['role'].title()}: {msg['parts'][0]['text']}")
    print(f"Status: Chamado aberto no sistema de atendimento para {user_id}.")
    print(f"--- FIM DO LOG DE TRANSFERÊNCIA SIMULADA ---\n")

    return bot_message_to_user

# --- APLICATIVO FLASK ---
app = Flask(__name__)

# Dicionário para simular sessões de usuário.
# Em produção, use um banco de dados (Redis, PostgreSQL) para persistência.
user_sessions = {} # Chave: ID do usuário (número de telefone), Valor: dict com dados da sessão

# --- FUNÇÃO PARA ENVIAR MENSAGENS DE VOLTA PARA O WHATSAPP (VIA BSP) ---
# ESTA FUNÇÃO É GENÉRICA E PRECISA SER ADAPTADA AO SEU BSP ESPECÍFICO!
# Consulte a documentação do seu Business Solution Provider (Zenvia, Twilio, Blip, etc.).
def send_whatsapp_message(to_number, message_text):
    # Exemplo com um BSP hipotético. SUBSTITUA PELOS SEUS DADOS REAIS!
    # Você precisará de:
    # 1. A URL da API de mensagens do seu BSP.
    # 2. Seu token de autenticação do BSP.
    
    # Exemplo (Twilio):
    # account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    # auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    # from_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER") # Seu número Twilio WhatsApp
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     from_=f'whatsapp:{from_whatsapp_number}',
    #     body=message_text,
    #     to=f'whatsapp:{to_number}'
    # )
    # print(f"Mensagem Twilio SID: {message.sid}")

    # Exemplo (Requisição HTTP genérica, adapte o payload e headers!)
    bsp_api_url = "https://api.seubsp.com/v1/messages" # <-- SUBSTITUA PELA URL REAL DO SEU BSP
    bsp_api_token = "SEU_TOKEN_DE_AUTENTICACAO_DO_BSP" # <-- SUBSTITUA PELO SEU TOKEN REAL DO BSP

    headers = {
        "Authorization": f"Bearer {bsp_api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
        # O payload pode ter outros campos específicos do BSP (template_id, context, etc.)
    }

    try:
        response = requests.post(bsp_api_url, headers=headers, json=payload)
        response.raise_for_status() # Lança um erro para status HTTP ruins (4xx, 5xx)
        print(f"Mensagem enviada com sucesso para {to_number} via BSP.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para {to_number} via BSP: {e}")
        return None

# --- WEBHOOK DO FLASK PARA RECEBER MENSAGENS DO WHATSAPP (VIA BSP) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json # Os dados enviados pelo BSP do WhatsApp

    # --- EXTRAÇÃO DA MENSAGEM DO USUÁRIO ---
    # IMPORTANTE: O FORMATO DOS DADOS VARIA MUITO ENTRE OS BSPs!
    # Este é um exemplo comum para a API oficial do WhatsApp, mas seu BSP pode ter um formato diferente.
    user_message = ""
    from_number = ""
    
    try:
        # Exemplo de extração para a estrutura da Meta (WhatsApp Business API)
        entry = data.get('entry', [])
        if not entry:
            return jsonify({"status": "no_entry"}), 200

        changes = entry[0].get('changes', [])
        if not changes:
            return jsonify({"status": "no_changes"}), 200

        value = changes[0].get('value', {})
        messages = value.get('messages', [])
        if not messages:
            return jsonify({"status": "no_messages"}), 200
        
        message_info = messages[0]
        from_number = message_info.get('from') # Número do usuário
        message_type = message_info.get('type')

        if message_type == 'text':
            user_message = message_info.get('text', {}).get('body', '')
        else:
            # Por enquanto, só lidamos com texto
            bot_response = "Desculpe, só consigo processar mensagens de texto no momento."
            send_whatsapp_message(from_number, bot_response) 
            return jsonify({"status": "success", "message": bot_response}), 200

    except Exception as e:
        print(f"Erro ao extrair dados do webhook: {e}. Dados recebidos: {data}")
        return jsonify({"status": "error", "message": str(e)}), 400

    print(f"Mensagem recebida de {from_number}: {user_message}")

    # --- RECUPERAR OU CRIAR SESSÃO DO USUÁRIO ---
    # 'from_number' é a ID única do usuário para gerenciar o estado da conversa
    user_session = user_sessions.get(from_number, {'state': 'initial', 'chat_history': []})

    # Adicionar a mensagem do usuário ao histórico da sessão
    user_session['chat_history'].append({"role": "user", "parts": [{"text": user_message}]})

    # --- LÓGICA PRINCIPAL DO CHATBOT ---
    bot_response = ""
    current_state = user_session['state']
    
    # Lógica para o menu inicial
    if current_state == 'initial':
        user_input_normalized = user_message.strip().lower()
        if "olá" in user_input_normalized or "oi" in user_input_normalized:
            bot_response = saudacao_string()
        elif user_input_normalized == '1':
            bot_response = exibir_cardapio_string()
        elif user_input_normalized == '2':
            # Inicia o fluxo de pedido
            bot_response, user_session = processar_pedido_bot("iniciar", user_session) # Sinal para iniciar pedido
            user_session['state'] = 'awaiting_flavor' # Atualiza o estado
        elif user_input_normalized == '3':
            bot_response = falar_com_atendente_inteligente(from_number, user_session)
            # Após a transferência, o bot pode voltar ao estado inicial ou aguardar ação do atendente
            user_session['state'] = 'initial' 
        elif user_input_normalized == '4':
            bot_response = "Obrigado por usar nosso serviço! Até logo!"
            user_sessions.pop(from_number, None) # Remove a sessão ao sair
        else:
            bot_response = "Desculpe, não entendi. Por favor, escolha uma das opções (1-4)."
            
    # Lógica para fluxos específicos (como o pedido)
    elif current_state.startswith('awaiting_'): 
        bot_response, user_session = processar_pedido_bot(user_message, user_session)
        
    # --- SALVAR O ESTADO ATUALIZADO DA SESSÃO ---
    # Adicionar a resposta do bot ao histórico da sessão
    user_session['chat_history'].append({"role": "model", "parts": [{"text": bot_response}]})
    user_sessions[from_number] = user_session
    
    print(f"Respondendo a {from_number}: {bot_response}")

    # --- PASSO FINAL: ENVIAR A MENSAGEM DE VOLTA PARA O USUÁRIO VIA BSP ---
    send_whatsapp_message(from_number, bot_response) 

    # Retorna uma resposta de sucesso para o BSP (eles esperam isso)
    return jsonify({"status": "success"}), 200

# --- EXECUTAR O APLICATIVO FLASK ---
if __name__ == '__main__':
    # Para desenvolvimento, o servidor do Flask é suficiente.
    # Em produção, você usaria um servidor WSGI como Gunicorn ou uWSGI.
    app.run(host='0.0.0.0', port=5000) # '0.0.0.0' para ser acessível externamente se necessário