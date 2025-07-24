# chatbot.py

# Versão do chatbot para ser executada diretamente no terminal.
# Ideal para testar a lógica do fluxo de conversa rapidamente.

import os
from dotenv import load_dotenv

# Configuração da IA (Google Gemini)
import google.generativeai as genai

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("AVISO: GEMINI_API_KEY não configurada. A funcionalidade de resumo da IA não estará disponível.")
    genai_model = None
else:
    genai.configure(api_key=GEMINI_API_KEY)
    genai_model = genai.GenerativeModel('gemini-pro')

# --- CARDÁPIO DA PIZZARIA (COM TAMANHOS E PREÇOS MÉDIOS) ---
CARDAPIO = {
    "margherita": {
        "M": {"preco": 35.00, "descricao": "Molho, muçarela e manjericão."},
        "G": {"preco": 45.00, "descricao": "Molho, muçarela e manjericão."},
        "GG": {"preco": 55.00, "descricao": "Molho, muçarela e manjericão."}
    },
    "calabresa": {
        "M": {"preco": 40.00, "descricao": "Molho, muçarela, calabresa e cebola."},
        "G": {"preco": 52.00, "descricao": "Molho, muçarela, calabresa e cebola."},
        "GG": {"preco": 63.00, "descricao": "Molho, muçarela, calabresa e cebola."}
    },
    "portuguesa": {
        "M": {"preco": 45.00, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."},
        "G": {"preco": 58.00, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."},
        "GG": {"preco": 70.00, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."}
    },
    "quatro queijos": {
        "M": {"preco": 50.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."},
        "G": {"preco": 65.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."},
        "GG": {"preco": 78.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."}
    },
    "frango com catupiry": {
        "M": {"preco": 55.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."},
        "G": {"preco": 72.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."},
        "GG": {"preco": 85.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."}
    },
    # --- Sabores Especiais ---
    "chocolate branco com morango": {
        "M": {"preco": 50.00, "descricao": "Chocolate branco cremoso e morangos frescos."},
        "G": {"preco": 65.00, "descricao": "Chocolate branco cremoso e morangos frescos."},
        "GG": {"preco": 78.00, "descricao": "Chocolate branco cremoso e morangos frescos."}
    },
    "chocolate preto com confetti": {
        "M": {"preco": 48.00, "descricao": "Chocolate meio amargo e granulados coloridos."},
        "G": {"preco": 62.00, "descricao": "Chocolate meio amargo e granulados coloridos."},
        "GG": {"preco": 75.00, "descricao": "Chocolate meio amargo e granulados coloridos."}
    },
    "camarão com catupiry": {
        "M": {"preco": 65.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."},
        "G": {"preco": 85.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."},
        "GG": {"preco": 100.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."}
    }
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

def exibir_menu_opcoes():
    return (
        "1. Ver Cardápio\n"
        "2. Fazer Pedido\n"
        "3. Falar com Atendente\n"
        "4. Sair"
    )

def exibir_cardapio_string():
    cardapio_str = "--- NOSSO CARDÁPIO ---\n"
    for sabor, tamanhos in CARDAPIO.items():
        sabor_formatado = sabor.replace("_", " ").title()
        
        precos_tamanhos = []
        for tamanho_sigla in ["M", "G", "GG"]:
            if tamanho_sigla in tamanhos:
                precos_tamanhos.append(f"{tamanho_sigla}: R$ {tamanhos[tamanho_sigla]['preco']:.2f}")
        
        cardapio_str += f"- *{sabor_formatado}*: {' | '.join(precos_tamanhos)}\n"
        
        sabores_especiais = [
            "chocolate branco com morango",
            "chocolate preto com confetti",
            "camarão com catupiry"
        ]
        if sabor in sabores_especiais:
            descricao = tamanhos["M"]["descricao"]
            cardapio_str += f"  _Ingredientes: {descricao}_\n"
            
    cardapio_str += "----------------------"
    return cardapio_str

def processar_pedido_bot(user_message, session_data):
    # Prints de depuração para entender o fluxo
    print(f"\n--- DEBUG: Início de processar_pedido_bot ---")
    print(f"DEBUG: Estado na entrada: '{session_data.get('state')}'")
    print(f"DEBUG: Mensagem do usuário na entrada: '{user_message}'")

    # --- INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO (MAIS ROBUSTA) ---
    if 'current_order' not in session_data or session_data['current_order'] is None:
        session_data['current_order'] = {}
    if 'order_total' not in session_data: session_data['order_total'] = 0.0
    if 'subtotal_pedido' not in session_data: session_data['subtotal_pedido'] = 0.0
    if 'delivery_fee' not in session_data: session_data['delivery_fee'] = 0.0
    if 'final_total' not in session_data: session_data['final_total'] = 0.0
    if 'address' not in session_data: session_data['address'] = ''
    if 'payment_method' not in session_data: session_data['payment_method'] = ''
    if 'temp_flavor' not in session_data: session_data['temp_flavor'] = None
    if 'temp_size' not in session_data: session_data['temp_size'] = None
    if 'awaiting_change_needed' not in session_data: session_data['awaiting_change_needed'] = False


    current_state = session_data['state']
    response_message = ""
    user_input_normalized = user_message.lower().strip()

    # --- Lógica de estados do pedido ---
    if current_state == 'awaiting_flavor':
        print(f"DEBUG: Processando estado 'awaiting_flavor' com input: '{user_input_normalized}'")
        
        if user_input_normalized == 'fim':
            if session_data['current_order']:
                resumo = "Seu pedido foi finalizado com sucesso!\n*Resumo do Pedido:*\n"
                print(f"DEBUG RESUMO: current_order no FIM: {session_data['current_order']}")
                for sabor_full, qtd_full in session_data['current_order'].items():
                    sabor_base, tamanho = sabor_full.rsplit(' ', 1) if ' ' in sabor_full and sabor_full.split()[-1] in ["m", "g", "gg"] else (sabor_full, "m")
                    preco_item = CARDAPIO.get(sabor_base, {}).get(tamanho.upper(), {}).get("preco", 0)
                    print(f"DEBUG RESUMO ITEM: Sabor_full: '{sabor_full}', Sabor_base: '{sabor_base}', Tamanho Extraído: '{tamanho}', Preco_item: {preco_item}")
                    resumo += f"*{qtd_full}x {sabor_base.replace('_', ' ').title()} ({tamanho.upper()})* (R$ {preco_item:.2f} cada)\n"
                
                session_data['subtotal_pedido'] = session_data['order_total']
                resumo += f"*Subtotal: R$ {session_data['order_total']:.2f}*\n\n"
                
                response_message = resumo + (
                    "Agora, por favor, escolha a forma de pagamento:\n"
                    "1. Espécie\n"
                    "2. Cartão\n"
                    "3. Pix"
                )
                session_data['state'] = 'awaiting_payment_method'
            else:
                response_message = "Nenhum item adicionado ao pedido. Digite o sabor da pizza ou 'cancelar'."
            return response_message, session_data
        
        elif user_input_normalized == 'cancelar':
            session_data['current_order'] = {}
            session_data['order_total'] = 0.0
            session_data['state'] = 'initial'
            response_message = "Pedido cancelado. Como posso ajudar agora?\n\n" + exibir_menu_opcoes()
            return response_message, session_data
        
        else: # Usuário digitou um sabor
            matched_sabor = None
            for key_sabor in CARDAPIO.keys():
                if user_input_normalized in key_sabor:
                    matched_sabor = key_sabor
                    break
            
            if matched_sabor:
                session_data['temp_flavor'] = matched_sabor
                session_data['state'] = 'awaiting_size'
                response_message = (
                    f"Certo, *{matched_sabor.title()}*! Qual o *tamanho* desta pizza?\n"
                    "_Opções: M, G, GG_"
                )
            else:
                response_message = (
                    "Desculpe, não consegui encontrar este sabor no cardápio. "
                    "Por favor, digite o nome do sabor novamente.\n"
                    "Você pode digitar *'cardápio'* para ver as opções."
                )
            return response_message, session_data

    elif current_state == 'awaiting_size':
        print(f"DEBUG: Processando estado 'awaiting_size' com input: '{user_input_normalized}'")
        sabor_selecionado = session_data.get('temp_flavor')
        
        if not sabor_selecionado:
            session_data['state'] = 'awaiting_flavor'
            return "Parece que o sabor anterior não foi salvo. Por favor, digite o sabor da pizza novamente.", session_data

        tamanho_input = user_input_normalized.upper()

        if tamanho_input in ["M", "G", "GG"] and tamanho_input in CARDAPIO[sabor_selecionado]:
            session_data['temp_size'] = tamanho_input
            session_data['state'] = 'awaiting_item_quantity'
            response_message = f"Ótimo! Você escolheu *{tamanho_input}* para a pizza de *{sabor_selecionado.title()}*. Quantas pizzas deste tamanho você gostaria?"
        else:
            response_message = (
                f"Tamanho inválido para a pizza de *{sabor_selecionado.title()}*. "
                "Por favor, escolha entre *M, G ou GG*."
            )
        return response_message, session_data

    elif current_state == 'awaiting_item_quantity':
        print(f"DEBUG: Processando estado 'awaiting_item_quantity' com input: '{user_input_normalized}'")
        sabor_selecionado = session_data.get('temp_flavor')
        tamanho_selecionado = session_data.get('temp_size')

        if not sabor_selecionado or not tamanho_selecionado:
            session_data['state'] = 'awaiting_flavor'
            return "Parece que o sabor ou tamanho anterior não foi salvo. Por favor, reinicie a adição do item.", session_data
        
        # --- Lidar com "fim" ou "cancelar" AQUI antes de tentar converter para int ---
        if user_input_normalized == 'fim':
            if session_data['current_order']:
                resumo = "Seu pedido foi finalizado com sucesso!\n*Resumo do Pedido:*\n"
                print(f"DEBUG RESUMO: current_order no FIM: {session_data['current_order']}")
                for sabor_full, qtd_full in session_data['current_order'].items():
                    sabor_base, tamanho = sabor_full.rsplit(' ', 1) if ' ' in sabor_full and sabor_full.split()[-1] in ["m", "g", "gg"] else (sabor_full, "m")
                    preco_item = CARDAPIO.get(sabor_base, {}).get(tamanho.upper(), {}).get("preco", 0)
                    print(f"DEBUG RESUMO ITEM: Sabor_full: '{sabor_full}', Sabor_base: '{sabor_base}', Tamanho Extraído: '{tamanho}', Preco_item: {preco_item}")
                    resumo += f"*{qtd_full}x {sabor_base.replace('_', ' ').title()} ({tamanho.upper()})* (R$ {preco_item:.2f} cada)\n"
                
                session_data['subtotal_pedido'] = session_data['order_total']
                resumo += f"*Subtotal: R$ {session_data['order_total']:.2f}*\n\n"
                
                response_message = resumo + (
                    "Agora, por favor, escolha a forma de pagamento:\n"
                    "1. Espécie\n"
                    "2. Cartão\n"
                    "3. Pix"
                )
                session_data['state'] = 'awaiting_payment_method'
            else:
                response_message = "Nenhum item adicionado ao pedido. Digite o sabor da pizza ou *'cancelar'* para sair."
                session_data['state'] = 'awaiting_flavor'
            return response_message, session_data

        elif user_input_normalized == 'cancelar':
            session_data['current_order'] = {}
            session_data['order_total'] = 0.0
            session_data['state'] = 'initial'
            response_message = "Pedido cancelado. Como posso ajudar agora?\n\n" + exibir_menu_opcoes()
            return response_message, session_data
        
        try:
            quantidade = int(user_input_normalized)
            if quantidade <= 0:
                response_message = "Quantidade inválida. Por favor, insira um número maior que zero."
            else:
                pizza_preco = CARDAPIO[sabor_selecionado][tamanho_selecionado]["preco"]
                
                sabor_com_tamanho = f"{sabor_selecionado} {tamanho_selecionado.lower()}"
                session_data['current_order'][sabor_com_tamanho] = session_data['current_order'].get(sabor_com_tamanho, 0) + quantidade
                session_data['order_total'] += pizza_preco * quantidade
                
                session_data['temp_flavor'] = None
                session_data['temp_size'] = None
                session_data['state'] = 'awaiting_flavor'
                
                response_message = (
                    f"*{quantidade}x {sabor_selecionado.title()} ({tamanho_selecionado.upper()})* adicionada(s) ao seu pedido.\n\n"
                    "Para adicionar mais pizzas, digite o *sabor*. Quando tiver tudo, digite *'fim'* para finalizar."
                )
            return response_message, session_data
        except ValueError:
            response_message = "Entrada inválida. Por favor, digite apenas números para a quantidade."
            return response_message, session_data
            
    elif current_state == 'awaiting_payment_method':
        print(f"DEBUG: Processando estado 'awaiting_payment_method' com input: '{user_input_normalized}'")
        opcao_pagamento = user_input_normalized
        if opcao_pagamento in ['1', 'espécie', 'especie']:
            session_data['payment_method'] = 'Espécie'
            response_message = (
                "*Pagamento em Espécie selecionado!* O pagamento será feito na entrega.\n\n"
                "Você precisará de troco? Se sim, para qual valor? (Ex: 'Sim, para 50' ou 'Não')"
            )
            session_data['state'] = 'awaiting_change_needed'
        elif opcao_pagamento in ['2', 'cartão', 'cartao']:
            session_data['payment_method'] = 'Cartão'
            response_message = (
                "*Pagamento em Cartão selecionado!* O pagamento será feito na entrega.\n"
                "Por favor, informe seu endereço para entrega."
            )
            session_data['state'] = 'awaiting_address'
        elif opcao_pagamento in ['3', 'pix']:
            session_data['payment_method'] = 'Pix'
            PIX_KEY = os.getenv("PIX_KEY", "111.222.333-44 (CPF)")
            response_message = f"*Pagamento via Pix selecionado!* Por favor, faça a transferência para:\n\n*Chave-Pix para o pagamento:* {PIX_KEY}\n\nApós realizar o Pix, me informe seu endereço para entrega."
            session_data['state'] = 'awaiting_address'
        else:
            response_message = (
                "Opção de pagamento inválida. Por favor, escolha '1' (Espécie), '2' (Cartão) ou '3' (Pix)."
            )
        return response_message, session_data

    elif current_state == 'awaiting_change_needed':
        print(f"DEBUG: Processando estado 'awaiting_change_needed' com input: '{user_input_normalized}'")
        if "não" in user_input_normalized or "nao" in user_input_normalized:
            session_data['change_needed'] = "Não"
            response_message = "Certo, sem troco. Por favor, informe seu endereço para entrega."
            session_data['state'] = 'awaiting_address'
        elif "sim" in user_input_normalized:
            parts = user_input_normalized.split()
            troco_para = None
            for part in parts:
                try:
                    troco_para = float(part.replace(',', '.'))
                    break
                except ValueError:
                    continue
            
            if troco_para is not None and troco_para > session_data['subtotal_pedido']:
                session_data['change_needed'] = f"Sim, para R$ {troco_para:.2f}"
                response_message = f"Certo, troco para R$ {troco_para:.2f}. Por favor, informe seu endereço para entrega."
                session_data['state'] = 'awaiting_address'
            else:
                response_message = "Valor de troco inválido ou menor que o total do pedido. Por favor, digite 'Sim, para [valor]' ou 'Não'."
        else:
            response_message = "Não entendi. Por favor, digite 'Sim, para [valor]' (ex: 'Sim, para 50') ou 'Não' se não precisar de troco."
        return response_message, session_data


    elif current_state == 'awaiting_address':
        print(f"DEBUG: Processando estado 'awaiting_address' com input: '{user_input_normalized}'")
        session_data['address'] = user_message.strip()
        response_message = (
            f"Endereço: _{session_data['address']}_ confirmado! "
            "Sua taxa de entrega será calculada e confirmada por um de nossos atendentes."
            "\n\n*Seu pedido foi enviado para nossa equipe!* Em breve você receberá a confirmação final. "
            "*Obrigado por escolher a Pizzaria Delícia!* 🍕"
        )
        # Limpa o estado da sessão após finalizar o pedido
        session_data['current_order'] = {}
        session_data['order_total'] = 0.0
        session_data['subtotal_pedido'] = 0.0
        session_data['delivery_fee'] = 0.0
        session_data['final_total'] = session_data['subtotal_pedido']
        session_data['address'] = ''
        session_data['payment_method'] = ''
        session_data['temp_flavor'] = None
        session_data['temp_size'] = None
        session_data['state'] = 'initial'
        if 'change_needed' in session_data and session_data['change_needed'] != False: # Verifica se a chave existe e não é False
            response_message += f"\n_Troco: {session_data['change_needed']}_"
        session_data['change_needed'] = False
        return response_message, session_data
    
    # Mensagem de fallback: se o estado da sessão não for um dos 'awaiting_' conhecidos,
    print(f"--- DEBUG: Estado NÃO TRATADO em processar_pedido_bot: '{current_state}' com input: '{user_input_normalized}' ---")
    return "Desculpe, não entendi. Você pode tentar 'cardápio' ou 'pedido'?", session_data

# --- FUNÇÃO DE IA PARA RESUMIR CONVERSA (Terminal) ---
def resumir_conversa_com_ia_terminal(chat_history):
    if not os.getenv("GEMINI_API_KEY"):
        return "Resumo da IA não disponível (chave GEMINI_API_KEY ausente ou não configurada)."
    
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

# --- LÓGICA PRINCIPAL DO CHATBOT NO TERMINAL ---
def main_terminal():
    current_user_session = {'state': 'initial', 'chat_history': []}

    print("Iniciando o Chatbot de Pizzaria no Terminal...")

    print("\n" + saudacao_string())

    while True:
        user_input = input("Você: ").strip()

        current_user_session['chat_history'].append({"role": "user", "parts": [{"text": user_input}]})

        bot_response = ""
        user_input_normalized = user_input.lower()

        if current_user_session['state'] == 'initial':
            if "olá" in user_input_normalized or "oi" in user_input_normalized:
                bot_response = saudacao_string()
            elif user_input_normalized == '1':
                bot_response = (
                    "🍕 *Seja bem-vindo ao nosso delicioso Cardápio!* 🍕\n\n"
                    "Prepare-se para escolher sua pizza favorita. Temos opções para todos os gostos:\n\n"
                    f"{exibir_cardapio_string()}"
                    "\n\nPara fazer seu pedido, digite *'2'*. Se precisar de ajuda, digite *'3'*."
                )
            elif user_input_normalized == '2':
                response_message_intro = (
                    "✨ *Vamos montar seu pedido!* ✨\n\n"
                    "Para adicionar pizzas ao seu carrinho, siga estes passos simples:\n"
                    "1️⃣ Digite o *sabor da pizza* que você deseja.\n"
                    "2️⃣ Em seguida, o bot perguntará o *tamanho* (M, G ou GG).\n"
                    "3️⃣ Por último, informe a *quantidade*.\n"
                    "   _Exemplo de sequência:_\n"
                    "   _Você: Calabresa_\n"
                    "   _Bot: Qual o tamanho? (M, G, GG)_\n"
                    "   _Você: G_\n"
                    "   _Bot: Quantas pizzas?_\n"
                    "   _Você: 2_\n\n"
                    "Quando tiver tudo, digite a palavra *'fim'* para finalizar.\n"
                    "Se precisar cancelar o pedido a qualquer momento, digite *'cancelar'*.\n\n"
                    "*Sabores disponíveis:*\n"
                )
                sabores_disponiveis = ", ".join([f"*{s.replace('_', ' ').title()}*" for s in CARDAPIO.keys()])
                bot_response = response_message_intro + f"{sabores_disponiveis}\n\nQual sabor de pizza você gostaria de adicionar primeiro?"
                current_user_session['state'] = 'awaiting_flavor'
            elif user_input_normalized == '3':
                print(f"\n--- LOG DE TRANSFERÊNCIA PARA ATENDENTE (Terminal) ---")
                print(f"Resumo da Conversa (IA): {resumir_conversa_com_ia_terminal(current_user_session['chat_history'])}")
                print(f"--- FIM DO LOG DE TRANSFERÊNCIA SIMULADA ---\n")
                bot_response = "Ok! Simulei a transferência. Um atendente virtual foi notificado com o resumo da nossa conversa."
                current_user_session['state'] = 'initial'
            elif user_input_normalized == '4':
                bot_response = "Obrigado por usar nosso serviço! Volte sempre! 👋"
                print(bot_response)
                break
            else:
                bot_response = "Desculpe, não entendi. Por favor, escolha uma das opções (1-4)."
        
        elif current_user_session['state'].startswith('awaiting_'):
            bot_response, current_user_session = processar_pedido_bot(user_input, current_user_session)
            
        current_user_session['chat_history'].append({"role": "model", "parts": [{"text": bot_response}]})
        
        print(f"Bot: {bot_response}")

if __name__ == "__main__":
    main_terminal()