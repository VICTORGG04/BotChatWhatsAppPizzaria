# app.py

# Chatbot de pizzaria com IA (Google Gemini) integrado ao WhatsApp (via Twilio).

from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

from twilio.rest import Client

load_dotenv()

# --- Configuração da IA (Google Gemini) ---
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não configurada nas variáveis de ambiente.")
genai.configure(api_key=GEMINI_API_KEY)

# --- Configuração da Twilio (BSP) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_WHATSAPP_NUMBER:
    print("ATENÇÃO: Credenciais da Twilio incompletas. O envio de mensagens via WhatsApp pode não funcionar.")

# --- CARDÁPIO DA PIZZARIA ---
CARDAPIO = {
    "margherita": {"preco": 35.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Manjericão"]},
    "calabresa": {"preco": 40.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Calabresa", "Cebola"]},
    "portuguesa": {"preco": 45.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Presunto", "Ovo", "Cebola"]},
    "quatro queijos": {"preco": 50.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Parmesão", "Gorgonzola", "Provolone"]},
    "frango com catupiry": {"preco": 55.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Frango desfiado", "Catupiry"]},
}

# --- FUNÇÕES DO CHATBOT ---
def saudacao_string():
    return (
        "Olá! Bem-vindo à Pizzaria Delícia!\n"
        "Sou seu assistente virtual. Como posso ajudar?\n"
        "1. Ver Cardápio\n"
        "2. Fazer Pedido\n"
        "3. Falar com Atendente\n"
        "4. Sair"
    )

def exibir_cardapio_string():
    cardapio_str = "--- NOSSO CARDÁPIO ---\n"
    for sabor, detalhes in CARDAPIO.items():
        sabor_formatado = sabor.replace("_", " ").title()
        ingredientes_str = ", ".join(detalhes['ingredientes'])
        cardapio_str += f"- {sabor_formatado}: R$ {detalhes['preco']:.2f} - Ingredientes: {ingredientes_str}.\n"
    cardapio_str += "----------------------"
    return cardapio_str

def processar_pedido_bot(user_message, session_data):
    if 'current_order' not in session_data:
        session_data['current_order'] = {}
        session_data['order_total'] = 0.0
        session_data['state'] = 'awaiting_flavor'

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
            session_data['state'] = 'initial'
            response_message = "Pedido cancelado. Como posso ajudar agora?\n" + saudacao_string()
        else:
            matched_sabor = None
            for key_sabor in CARDAPIO.keys():
                if sabor_input in key_sabor or key_sabor in sabor_input:
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
                session_data['state'] = 'awaiting_flavor'
                response_message = f"{quantidade}x {sabor.title()} adicionada(s) ao seu pedido.\nDigite outro sabor ou 'fim' para finalizar."
        except ValueError:
            response_message = "Entrada inválida. Por favor, insira um número inteiro para a quantidade."

    elif current_state == 'awaiting_address':
        session_data['address'] = user_message.strip()
        response_message = (
            f"Confirmado! Seu pedido totalizou R$ {session_data['order_total']:.2f} e será entregue em: {session_data['address']}.\n"
            "Aguarde a confirmação final de um de nossos atendentes.\n"
            "Obrigado por escolher a Pizzaria Delícia!"
        )
        session_data['current_order'] = {}
        session_data['order_total'] = 0.0
        session_data['address'] = ''
        session_data['state'] = 'initial'
        
    return response_message, session_data

# --- FUNÇÃO DE IA PARA RESUMIR CONVERSA ---
def resumir_conversa_com_ia(chat_history):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
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
    chat_history = user_session.get('chat_history', [])

    resumo_gerado_ia = resumir_conversa_com_ia(chat_history)

    bot_message_to_user = (
        "Ok! Estou transferindo você para um de nossos atendentes. "
        "Ele(a) terá acesso ao histórico da nossa conversa e um resumo gerado por IA.\n"
        "Por favor, aguarde um momento."
    )

    print(f"\n--- LOG DE TRANSFERÊNCIA PARA ATENDENTE ---")
    print(f"Usuário: {user_id}")
    print(f"Resumo da Conversa (IA): {resumo_gerado_ia}")
    print(f"Histórico Completo (para referência):")
    for msg in chat_history:
        if 'parts' in msg and len(msg['parts']) > 0 and 'text' in msg['parts'][0]:
            print(f"  {msg['role'].title()}: {msg['parts'][0]['text']}")
        else:
            print(f"  {msg['role'].title()}: [Mensagem não textual ou mal formatada]")
    print(f"Status: Chamado aberto no sistema de atendimento para {user_id}.")
    print(f"--- FIM DO LOG DE TRANSFERÊNCIA SIMULADA ---\n")

    return bot_message_to_user

# --- APLICATIVO FLASK ---
app = Flask(__name__)

user_sessions = {}

# --- FUNÇÃO PARA ENVIAR MENSAGENS DE VOLTA PARA O WHATSAPP (VIA BSP) ---
def send_whatsapp_message(to_number, message_text):
    # Adaptação para Twilio
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_NUMBER:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=message_text,
                to=f'whatsapp:{to_number}'
            )
            print(f"Mensagem enviada com sucesso para {to_number} via Twilio. SID: {message.sid}")
            return message.sid
        except Exception as e:
            print(f"Erro ao enviar mensagem para {to_number} via Twilio: {e}")
            return None
    else:
        print("ATENÇÃO: Credenciais da Twilio incompletas ou não configuradas. Mensagem não enviada via Twilio.")
        print(f"Simulando envio para {to_number}: {message_text}")
        return {"status": "failed", "message": "No configured BSP for sending messages"}


# --- WEBHOOK DO FLASK PARA RECEBER MENSAGENS DO WHATSAPP (VIA BSP) ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # --- Lógica para Verificação do Webhook (Método GET) ---
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "SEU_TOKEN_DE_VERIFICACAO_SECRETO")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verificado com sucesso!")
            return challenge, 200
        else:
            print("Falha na verificação do webhook: token ou modo incorreto.")
            return "Verification token mismatch", 403

    # --- Lógica para Mensagens Recebidas (Método POST) ---
    # ATENÇÃO: A ESTRUTURA DOS DADOS (payload) DA TWILIO É DIFERENTE DA API DA META!
    # A Twilio envia os dados como 'application/x-www-form-urlencoded', acessível via request.form.
    
    user_message = ""
    from_number = ""
    
    try:
        # BLOCO DE EXTRAÇÃO CORRETO PARA TWILIO (prioridade)
        if request.form:
            user_message = request.form.get('Body', '').strip()
            from_number = request.form.get('From', '').replace('whatsapp:', '')
            
            if not user_message and not from_number:
                print("Webhook POST recebido sem Body ou From (possivelmente notificação de status da Twilio). Ignorando.")
                return jsonify({"status": "ignored", "message": "No relevant message data."}), 200
        
        # Fallback para outros BSPs (API da Meta JSON)
        elif request.is_json:
            data = request.json # A variável 'data' é definida AQUI se a requisição for JSON.
            entry = data.get('entry', [])
            if not entry: raise ValueError("No 'entry' found in webhook data.")
            changes = entry[0].get('changes', [])
            if not changes: raise ValueError("No 'changes' found in webhook data.")
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            if not messages: raise ValueError("No 'messages' found in webhook data.")
            
            message_info = messages[0]
            from_number = message_info.get('from')
            message_type = message_info.get('type')

            if message_type == 'text':
                user_message = message_info.get('text', {}).get('body', '')
            else:
                bot_response = "Desculpe, só consigo processar mensagens de texto no momento."
                send_whatsapp_message(from_number, bot_response) 
                return jsonify({"status": "success", "message": bot_response}), 200
        else:
            print(f"Erro: Content-Type não suportado. Headers recebidos: {request.headers}")
            return "Unsupported Media Type", 415 

    except Exception as e:
        print(f"Erro ao extrair dados do webhook: {e}. Dados recebidos: {request.data}")
        return jsonify({"status": "error", "message": str(e)}), 200 

    print(f"Mensagem recebida de {from_number}: {user_message}")

    user_session = user_sessions.get(from_number, {'state': 'initial', 'chat_history': []})
    user_session['chat_history'].append({"role": "user", "parts": [{"text": user_message}]})

    bot_response = ""
    current_state = user_session['state']
    
    if current_state == 'initial':
        user_input_normalized = user_message.strip().lower()
        if "olá" in user_input_normalized or "oi" in user_input_normalized:
            bot_response = saudacao_string()
        elif user_input_normalized == '1':
            # --- Explicação para o Cardápio ---
            bot_response = (
                "Aqui está o nosso cardápio de pizzas:\n\n"
                f"{exibir_cardapio_string()}\n\n"
                "Para fazer um pedido, digite '2' ou 'fazer pedido'. "
                "Para falar com um atendente, digite '3'."
            )
        elif user_input_normalized == '2':
            # --- Explicação para Fazer Pedido ---
            response_message_intro = (
                "Certo! Para fazer seu pedido, siga estes passos:\n"
                "1. Digite o **sabor da pizza** que você deseja.\n"
                "2. Em seguida, o bot perguntará a **quantidade**.\n"
                "3. Você pode adicionar quantos sabores quiser. Quando terminar, digite **'fim'**.\n"
                "4. Se mudar de ideia a qualquer momento, digite **'cancelar'**.\n\n"
                "Aqui estão os sabores disponíveis para começar:\n"
            )
            # Reutiliza a exibição do cardápio para mostrar os sabores
            sabores_disponiveis = ", ".join([s.replace("_", " ").title() for s in CARDAPIO.keys()])
            bot_response = response_message_intro + f"{sabores_disponiveis}\n\nQual sabor você gostaria de adicionar?"
            user_session['state'] = 'awaiting_flavor'
        elif user_input_normalized == '3':
            bot_response = falar_com_atendente_inteligente(from_number, user_session)
            user_session['state'] = 'initial'
        elif user_input_normalized == '4':
            bot_response = "Obrigado por usar nosso serviço! Até logo!"
            user_sessions.pop(from_number, None)
        else:
            bot_response = "Desculpe, não entendi. Por favor, escolha uma das opções (1-4)."
            
    elif current_state.startswith('awaiting_'): 
        bot_response, user_session = processar_pedido_bot(user_message, user_session)
        
    user_session['chat_history'].append({"role": "model", "parts": [{"text": bot_response}]})
    user_sessions[from_number] = user_session
    
    print(f"Respondendo a {from_number}: {bot_response}")

    send_whatsapp_message(from_number, bot_response) 

    return jsonify({"status": "success"}), 200

# --- EXECUTAR O APLICATIVO FLASK ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))