# test_chatbot.py

import pytest
from unittest.mock import patch, MagicMock

# Importa as funções e variáveis do seu script chatbot
# Certifique-se de que chatbot.py está no mesmo diretório
import chatbot

# --- Fixtures do Pytest ---
# Uma fixture é uma função que o pytest executa antes de cada teste
# que a solicita. É ideal para configurar um estado inicial limpo.

@pytest.fixture
def session_data_inicial():
    """Fornece um dicionário de sessão limpo para cada teste."""
    return {
        'state': 'initial',
        'current_order': {},
        'order_total': 0.0,
        'subtotal_pedido': 0.0,
        'delivery_fee': 0.0,
        'final_total': 0.0,
        'address': '',
        'payment_method': '',
        'temp_flavor': None,
        'temp_size': None,
        'awaiting_change_needed': False,
        'chat_history': []
    }

# --- Testes para Funções Simples ---

def test_saudacao_string():
    """Verifica se a função de saudação retorna a string esperada."""
    assert "Olá! Bem-vindo à Pizzaria Delícia!" in chatbot.saudacao_string()
    assert "1. Ver Cardápio" in chatbot.saudacao_string()

def test_exibir_cardapio_string():
    """Verifica se o cardápio é gerado e contém itens esperados."""
    cardapio_str = chatbot.exibir_cardapio_string()
    assert "--- NOSSO CARDÁPIO ---" in cardapio_str
    assert "Calabresa" in cardapio_str
    assert "Quatro Queijos" in cardapio_str
    assert "R$ 40.00" in cardapio_str # Preço da calabresa M

# --- Testes para a Lógica Principal do Pedido (processar_pedido_bot) ---

def test_fluxo_pedido_inicio_ate_tamanho(session_data_inicial):
    """Testa o fluxo desde o início do pedido até a solicitação do tamanho."""
    session_data_inicial['state'] = 'awaiting_flavor'
    
    # Usuário escolhe um sabor
    response, session_data = chatbot.processar_pedido_bot("calabresa", session_data_inicial)
    
    # Verifica a resposta e o novo estado
    assert "Qual o *tamanho* desta pizza?" in response
    assert session_data['state'] == 'awaiting_size'
    assert session_data['temp_flavor'] == 'calabresa'

def test_fluxo_pedido_tamanho_ate_quantidade(session_data_inicial):
    """Testa o fluxo da escolha do tamanho até a solicitação da quantidade."""
    session_data_inicial['state'] = 'awaiting_size'
    session_data_inicial['temp_flavor'] = 'calabresa'
    
    # Usuário escolhe um tamanho
    response, session_data = chatbot.processar_pedido_bot("G", session_data_inicial)
    
    # Verifica a resposta e o novo estado
    assert "Quantas pizzas deste tamanho você gostaria?" in response
    assert session_data['state'] == 'awaiting_item_quantity'
    assert session_data['temp_size'] == 'G'

def test_fluxo_adicionar_item_ao_pedido(session_data_inicial):
    """Testa a adição de um item completo ao pedido."""
    session_data_inicial['state'] = 'awaiting_item_quantity'
    session_data_inicial['temp_flavor'] = 'portuguesa'
    session_data_inicial['temp_size'] = 'M'
    
    # Usuário informa a quantidade
    response, session_data = chatbot.processar_pedido_bot("2", session_data_inicial)
    
    # Verifica a resposta, o estado e os totais
    assert "*2x Portuguesa (M)* adicionada(s)" in response
    assert session_data['state'] == 'awaiting_flavor' # Pronto para novo item
    assert session_data['order_total'] == 90.00 # 2x 45.00
    assert "portuguesa m" in session_data['current_order']
    assert session_data['current_order']['portuguesa m'] == 2

def test_fluxo_finalizar_pedido_e_pagamento(session_data_inicial):
    """Testa o fluxo de finalização do pedido e escolha do pagamento."""
    # Prepara um pedido já existente
    session_data_inicial['state'] = 'awaiting_flavor'
    session_data_inicial['current_order'] = {'calabresa g': 1}
    session_data_inicial['order_total'] = 52.00
    
    # Usuário digita "fim"
    response, session_data = chatbot.processar_pedido_bot("fim", session_data_inicial)
    
    # Verifica o resumo e o novo estado
    assert "Resumo do Pedido" in response
    assert "Subtotal: R$ 52.00" in response
    assert "escolha a forma de pagamento" in response
    assert session_data['state'] == 'awaiting_payment_method'
    
    # Usuário escolhe cartão
    response, session_data = chatbot.processar_pedido_bot("cartao", session_data)
    
    # Verifica a resposta e o novo estado
    assert "Pagamento em Cartão selecionado" in response
    assert "informe seu endereço" in response
    assert session_data['state'] == 'awaiting_address'

def test_fluxo_final_com_endereco_e_reset(session_data_inicial):
    """Testa a confirmação do endereço e o reset da sessão."""
    # Prepara um pedido pronto para endereço
    session_data_inicial['state'] = 'awaiting_address'
    session_data_inicial['current_order'] = {'calabresa g': 1}
    session_data_inicial['order_total'] = 52.00
    
    # Usuário informa o endereço
    endereco = "Rua dos Testes, 123"
    response, session_data = chatbot.processar_pedido_bot(endereco, session_data_inicial)

    # Verifica a mensagem final e se a sessão foi limpa
    assert f"Endereço: _{endereco}_ confirmado!" in response
    assert "Obrigado por escolher a Pizzaria Delícia!" in response
    assert session_data['state'] == 'initial'
    assert session_data['current_order'] == {}
    assert session_data['order_total'] == 0.0

# --- Testes de Casos de Falha e Entradas Inválidas ---

def test_sabor_invalido(session_data_inicial):
    """Verifica se o bot lida com um sabor que não existe no cardápio."""
    session_data_inicial['state'] = 'awaiting_flavor'
    response, session_data = chatbot.processar_pedido_bot("sabor inexistente", session_data_inicial)
    
    assert "não consegui encontrar este sabor" in response
    assert session_data['state'] == 'awaiting_flavor' # Mantém o estado

def test_tamanho_invalido(session_data_inicial):
    """Verifica se o bot lida com um tamanho inválido para uma pizza."""
    session_data_inicial['state'] = 'awaiting_size'
    session_data_inicial['temp_flavor'] = 'margherita'
    
    response, session_data = chatbot.processar_pedido_bot("P", session_data_inicial) # Tamanho 'P' não existe
    
    assert "Tamanho inválido" in response
    assert "escolha entre *M, G ou GG*" in response
    assert session_data['state'] == 'awaiting_size' # Mantém o estado

def test_quantidade_invalida(session_data_inicial):
    """Verifica se o bot lida com uma quantidade não numérica."""
    session_data_inicial['state'] = 'awaiting_item_quantity'
    session_data_inicial['temp_flavor'] = 'margherita'
    session_data_inicial['temp_size'] = 'M'
    
    response, session_data = chatbot.processar_pedido_bot("duas", session_data_inicial) # "duas" não é um número
    
    assert "Entrada inválida. Por favor, digite apenas números" in response
    assert session_data['state'] == 'awaiting_item_quantity' # Mantém o estado

def test_cancelar_pedido(session_data_inicial):
    """Verifica se a funcionalidade de cancelar o pedido reseta a sessão."""
    session_data_inicial['state'] = 'awaiting_flavor'
    session_data_inicial['current_order'] = {'calabresa g': 1} # Simula um pedido em andamento
    session_data_inicial['order_total'] = 52.00
    
    response, session_data = chatbot.processar_pedido_bot("cancelar", session_data_inicial)

    assert "Pedido cancelado" in response
    assert session_data['state'] == 'initial'
    assert session_data['current_order'] == {}
    assert session_data['order_total'] == 0.0

# --- Testes para a Função de IA (com Mock) ---

@patch('chatbot.genai.GenerativeModel') # Substitui o modelo do Gemini por um mock
def test_resumir_conversa_com_ia_sucesso(mock_generative_model):
    """
    Testa a função de resumo com a API do Gemini mockada para simular sucesso.
    """
    # Configura o mock para retornar um valor específico quando chamado
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "Resumo gerado pela IA."
    mock_generative_model.return_value = mock_model_instance

    # Simula um histórico de chat
    chat_history = [
        {'role': 'user', 'parts': [{'text': 'Quero uma pizza de calabresa'}]},
        {'role': 'model', 'parts': [{'text': 'Qual o tamanho?'}]}
    ]

    # Chama a função com a API "desligada" (mockada)
    resumo = chatbot.resumir_conversa_com_ia_terminal(chat_history)
    
    assert resumo == "Resumo gerado pela IA."
    # Verifica se o método `generate_content` foi chamado
    mock_model_instance.generate_content.assert_called_once()

@patch('chatbot.os.getenv') # Mocka a função os.getenv
def test_resumir_conversa_sem_api_key(mock_getenv):
    """
    Testa o comportamento da função de resumo quando a chave de API não está configurada.
    """
    # Configura o mock para simular que a variável de ambiente não existe
    mock_getenv.return_value = None
    
    resumo = chatbot.resumir_conversa_com_ia_terminal([])
    
    assert "Resumo da IA não disponível" in resumo