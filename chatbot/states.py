"""
Máquina de estados para processamento de conversas do bot de pizzaria.
"""
from enum import Enum
from chatbot.cardapio import cardapio, formatar_cardapio_whatsapp, listar_sabores_formatados
from chatbot.service import processar_e_salvar_pedido, formatar_resumo_pedido
from chatbot.ai import resumir_conversa
from models import SessaoCliente, TamanhoPizza, MetodoPagamento
from config import settings
import logging

logger = logging.getLogger(__name__)


class EstadoConversa(str, Enum):
    INITIAL = "initial"
    AWAITING_FLAVOR = "awaiting_flavor"
    AWAITING_SIZE = "awaiting_size"
    AWAITING_QUANTITY = "awaiting_quantity"
    AWAITING_PAYMENT = "awaiting_payment"
    AWAITING_CHANGE = "awaiting_change"
    AWAITING_ADDRESS = "awaiting_address"


def processar_mensagem(mensagem: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    """
    Processa mensagem do usuário baseada no estado atual da sessão.
    
    Args:
        mensagem: Texto da mensagem do usuário
        sessao: Estado atual da sessão do cliente
        
    Returns:
        Tupla (resposta, sessao_atualizada)
    """
    estado = EstadoConversa(sessao.state) if sessao.state in [e.value for e in EstadoConversa] else EstadoConversa.INITIAL
    msg_lower = mensagem.lower().strip()
    
    handlers = {
        EstadoConversa.INITIAL: _processar_inicial,
        EstadoConversa.AWAITING_FLAVOR: _processar_sabor,
        EstadoConversa.AWAITING_SIZE: _processar_tamanho,
        EstadoConversa.AWAITING_QUANTITY: _processar_quantidade,
        EstadoConversa.AWAITING_PAYMENT: _processar_pagamento,
        EstadoConversa.AWAITING_CHANGE: _processar_troco,
        EstadoConversa.AWAITING_ADDRESS: _processar_endereco,
    }
    
    handler = handlers.get(estado, _processar_inicial)
    return handler(msg_lower, sessao)


def _processar_inicial(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    saudacoes = ["olá", "oi", "ola", "bom dia", "boa tarde", "boa noite", "menu", "início", "inicio", "1"]
    
    if any(s in msg for s in saudacoes) or msg == "1":
        return _menu_principal(), sessao
    
    if msg == "2":
        sessao.state = EstadoConversa.AWAITING_FLAVOR.value
        sabores = listar_sabores_formatados(cardapio)
        return f"✨ *Vamos montar seu pedido!* ✨\n\n*Sabores:* {sabores}\n\nQual sabor você gostaria?", sessao
    
    if msg == "3":
        return _solicitar_atendente(sessao), sessao
    
    if msg == "4":
        return "Obrigado por usar nosso serviço! Volte sempre! 👋", SessaoCliente()
    
    return "Opção inválida. Por favor, escolha uma das opções:\n\n" + _menu_principal(), sessao


def _processar_sabor(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    if msg in ["fim", "finalizar", "confirmar"]:
        return _finalizar_pedido(sessao)
    
    if msg in ["cancelar", "cancel"]:
        return _cancelar_pedido(sessao)
    
    if msg in ["cardápio", "cardapio"]:
        return formatar_cardapio_whatsapp(cardapio) + "\n\nDigite o sabor desejado ou *'fim'* para finalizar.", sessao
    
    sabor_encontrado = cardapio.buscar_sabor(msg)
    if sabor_encontrado:
        sessao.temp_flavor = sabor_encontrado
        sessao.state = EstadoConversa.AWAITING_SIZE.value
        tamanhos = [t.value for t in cardapio.sabores[sabor_encontrado].tamanhos.keys()]
        return f"Certo, *{cardapio.sabores[sabor_encontrado].nome_formatado}*! Qual o tamanho? ({'/'.join(tamanhos)})", sessao
    
    return "Não encontrei este sabor. Tente novamente ou peça o *'cardápio'*.", sessao


def _processar_tamanho(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    sabor = sessao.temp_flavor
    if not sabor:
        sessao.state = EstadoConversa.AWAITING_FLAVOR.value
        return "Ocorreu um erro. Por favor, escolha o sabor novamente.", sessao
    
    try:
        tamanho = TamanhoPizza(msg.upper())
    except ValueError:
        tamanhos_validos = [t.value for t in cardapio.sabores[sabor].tamanhos.keys()]
        return f"Tamanho inválido. Escolha: {'/'.join(tamanhos_validos)}", sessao
    
    if tamanho not in cardapio.sabores[sabor].tamanhos:
        tamanhos_validos = [t.value for t in cardapio.sabores[sabor].tamanhos.keys()]
        return f"Tamanho *{tamanho.value}* não disponível. Escolha: {'/'.join(tamanhos_validos)}", sessao
    
    sessao.temp_size = tamanho
    sessao.state = EstadoConversa.AWAITING_QUANTITY.value
    return f"Ótimo! *{cardapio.sabores[sabor].nome_formatado} ({tamanho.value})*. Quantas pizzas?", sessao


def _processar_quantidade(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    sabor = sessao.temp_flavor
    tamanho = sessao.temp_size
    
    if not sabor or not tamanho:
        sessao.state = EstadoConversa.AWAITING_FLAVOR.value
        sessao.temp_flavor = None
        sessao.temp_size = None
        return "Ocorreu um erro. Por favor, comece a adicionar o item novamente.", sessao
    
    try:
        quantidade = int(msg)
        if quantidade <= 0:
            return "Por favor, insira um número maior que zero.", sessao
    except ValueError:
        return "Entrada inválida. Por favor, digite um número.", sessao
    
    preco = cardapio.get_preco(sabor, tamanho)
    if preco is None:
        sessao.state = EstadoConversa.AWAITING_FLAVOR.value
        return "Erro ao obter preço. Tente novamente.", sessao
    
    chave = f"{sabor} {tamanho.value.lower()}"
    sessao.current_order[chave] = sessao.current_order.get(chave, 0) + quantidade
    sessao.order_total += preco * quantidade
    
    sessao.temp_flavor = None
    sessao.temp_size = None
    sessao.state = EstadoConversa.AWAITING_FLAVOR.value
    
    nome_formatado = cardapio.sabores[sabor].nome_formatado
    return (
        f"*{quantidade}x {nome_formatado} ({tamanho.value})* adicionada(s).\n\n"
        f"💰 Subtotal: R$ {sessao.order_total:.2f}\n\n"
        "Digite outro sabor ou *'fim'* para finalizar.",
        sessao
    )


def _processar_pagamento(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    if msg in ["1", "espécie", "especie", "dinheiro"]:
        sessao.payment_method = MetodoPagamento.ESPECIE
        sessao.state = EstadoConversa.AWAITING_CHANGE.value
        return "Pagamento em *Espécie*. Precisará de troco? (Ex: *'Sim, para 50'* ou *'Não'*)", sessao
    
    if msg in ["2", "cartão", "cartao", "credito", "debito"]:
        sessao.payment_method = MetodoPagamento.CARTAO
        sessao.state = EstadoConversa.AWAITING_ADDRESS.value
        return "Pagamento com *Cartão*. Por favor, informe seu endereço para entrega.", sessao
    
    if msg in ["3", "pix"]:
        sessao.payment_method = MetodoPagamento.PIX
        sessao.state = EstadoConversa.AWAITING_ADDRESS.value
        qrcode_url = "https://pizzaria-bot-production.up.railway.app/pix/qrcode"
        return (
            f"Pagamento via *Pix* 💳\n\n"
            f"📱 Escaneie o QR Code ou use a chave:\n"
            f"`{settings.pix_key}`\n\n"
            f"🔗 Ou acesse: {qrcode_url}\n\n"
            f"Após pagar, informe seu *endereço* para entrega.",
            sessao,
        )
    
    return "Opção inválida. Escolha 1 (Espécie), 2 (Cartão) ou 3 (Pix).", sessao


def _processar_troco(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    if "não" in msg or "nao" in msg:
        sessao.change_needed = "Não precisa de troco."
        sessao.state = EstadoConversa.AWAITING_ADDRESS.value
        return "Certo. Por favor, informe seu endereço para entrega.", sessao
    
    if "sim" in msg:
        try:
            valor_str = msg.split("para")[-1].strip().replace(",", ".")
            valor_troco = float(valor_str)
            if valor_troco > sessao.order_total:
                sessao.change_needed = f"Sim, troco para R$ {valor_troco:.2f}"
                sessao.state = EstadoConversa.AWAITING_ADDRESS.value
                return f"Ok, troco para R$ {valor_troco:.2f}. Agora, informe seu endereço.", sessao
            return "O valor para troco deve ser maior que o total do pedido.", sessao
        except (ValueError, IndexError):
            return "Não entendi. Digite *'Sim, para [valor]'* ou *'Não'*.", sessao
    
    return "Não entendi. Por favor, digite *'Sim, para [valor]'* ou *'Não'*.", sessao


def _processar_endereco(msg: str, sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    if len(msg.strip()) < 5:
        return "Endereço muito curto. Por favor, informe endereço completo.", sessao
    
    sessao.address = msg.strip()
    return processar_e_salvar_pedido(sessao)


def _menu_principal() -> str:
    return (
        "Olá! Bem-vindo à Pizzaria Delícia! 🍕\n"
        "Sou seu assistente virtual. Como posso ajudar?\n\n"
        "1️⃣ Ver Cardápio\n"
        "2️⃣ Fazer Pedido\n"
        "3️⃣ Falar com Atendente\n"
        "4️⃣ Sair"
    )


def _finalizar_pedido(sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    if not sessao.current_order:
        return "Nenhum item adicionado. Digite o sabor da pizza ou *'cancelar'*.", sessao
    
    resumo = "✅ *Seu pedido foi finalizado!*\n\n" + formatar_resumo_pedido(sessao)
    resumo += "\n\nEscolha a forma de pagamento:\n1️⃣ Espécie\n2️⃣ Cartão\n3️⃣ Pix"
    
    sessao.state = EstadoConversa.AWAITING_PAYMENT.value
    return resumo, sessao


def _cancelar_pedido(sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    chat_history = sessao.chat_history
    nova = SessaoCliente(chat_history=chat_history)
    return "Pedido cancelado. Como posso ajudar agora?\n\n" + _menu_principal(), nova


def _solicitar_atendente(sessao: SessaoCliente) -> str:
    resumo = resumir_conversa(sessao.chat_history)
    return (
        "Ok! Um atendente foi notificado com o resumo da nossa conversa.\n\n"
        f"--- RESUMO ---\n{resumo}"
    )