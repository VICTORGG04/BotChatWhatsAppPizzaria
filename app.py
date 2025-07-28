import os
from flask import Flask, request
from chatbot import processar_pedido_bot, setup_database 

setup_database()

app = Flask(__name__)

sessoes_clientes = {}

@app.route('/webhook', methods=['POST'])
def webhook():

    try:
        dados = request.get_json()
        numero_cliente = dados.get('from')
        mensagem_cliente = dados.get('body')

        if not numero_cliente or not mensagem_cliente:
            return "Dados inválidos", 400

        if numero_cliente not in sessoes_clientes:
            sessoes_clientes[numero_cliente] = {
                'state': 'initial',
                'chat_history': []
            }
        
        sessao_atual = sessoes_clientes[numero_cliente]

        resposta_bot, sessao_atualizada = processar_pedido_bot(mensagem_cliente, sessao_atual)

        sessoes_clientes[numero_cliente] = sessao_atualizada

        print(f"Cliente [{numero_cliente}]: {mensagem_cliente}")
        print(f"Bot: {resposta_bot}")
        return "OK", 200

    except Exception as e:
        print(f"ERRO NO WEBHOOK: {e}")
        return "Erro interno", 500