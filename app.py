import os
from flask import Flask, request
# Importa a função principal e a de setup do seu outro ficheiro
from chatbot import processar_pedido_bot, setup_database 

# Inicializa o banco de dados assim que a aplicação começa
setup_database()

app = Flask(__name__)

# Dicionário para guardar a sessão de CADA cliente, identificado pelo número de telefone
sessoes_clientes = {}

# Esta é a URL que você fornecerá ao provedor da API do WhatsApp (ex: Twilio)
@app.route('/webhook', methods=['POST'])
def webhook():
    # A estrutura da mensagem recebida varia entre os provedores (Twilio, Zenvia, etc.)
    # Este é um EXEMPLO genérico. Você precisará ajustar conforme a documentação do seu provedor.
    try:
        dados = request.get_json()
        
        # Exemplo de extração de dados (pode ser diferente)
        numero_cliente = dados.get('from')
        mensagem_cliente = dados.get('body')

        if not numero_cliente or not mensagem_cliente:
            return "Dados inválidos", 400

        # Gerencia a sessão para este cliente específico
        if numero_cliente not in sessoes_clientes:
            sessoes_clientes[numero_cliente] = {
                'state': 'initial',
                'chat_history': []
            }
        
        sessao_atual = sessoes_clientes[numero_cliente]

        # Processa a mensagem usando a mesma lógica de antes
        resposta_bot, sessao_atualizada = processar_pedido_bot(mensagem_cliente, sessao_atual)

        # Atualiza a sessão do cliente com os novos dados
        sessoes_clientes[numero_cliente] = sessao_atualizada

        # AQUI viria a lógica para enviar a 'resposta_bot' de volta para o cliente
        # usando a biblioteca do seu provedor de API (ex: Twilio).
        # Exemplo: twilio_client.messages.create(to=numero_cliente, from_='whatsapp:+14155238886', body=resposta_bot)
        
        # Para depuração, podemos imprimir no log do servidor
        print(f"Cliente [{numero_cliente}]: {mensagem_cliente}")
        print(f"Bot: {resposta_bot}")

        # Retorna uma resposta 'OK' para a API do WhatsApp
        # A resposta exata pode variar. Alguns provedores esperam um formato JSON específico.
        return "OK", 200

    except Exception as e:
        print(f"ERRO NO WEBHOOK: {e}")
        return "Erro interno", 500