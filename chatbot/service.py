import logging
from datetime import datetime
from chatbot.storage.sqlite import obter_proximo_numero_pedido_dia, calcular_lucro_total_dia
from chatbot.cardapio import cardapio
from models import (
    DadosPedido, ItemPedido, SessaoCliente, 
    TamanhoPizza, MetodoPagamento, StatusPedido
)
from tasks import (
    registrar_pedido_sqlite, 
    registrar_pedido_google_sheets, 
    registrar_pedido_excel
)

logger = logging.getLogger(__name__)


def processar_e_salvar_pedido(sessao: SessaoCliente) -> tuple[str, SessaoCliente]:
    """Processa pedido finalizado e salva assincronamente."""
    
    # Calcular custo e lucro
    custo_total = 0.0
    itens_para_salvar = []
    
    for chave, qtd in sessao.current_order.items():
        sabor_base, tamanho_str = chave.rsplit(' ', 1)
        tamanho = TamanhoPizza(tamanho_str.upper())
        
        custo_unit = cardapio.get_custo(sabor_base, tamanho) or 0
        preco_unit = cardapio.get_preco(sabor_base, tamanho) or 0
        
        custo_total += custo_unit * qtd
        
        itens_para_salvar.append(ItemPedido(
            sabor=sabor_base.title(),
            tamanho=tamanho,
            quantidade=qtd,
            preco=preco_unit,
            custo=custo_unit
        ))
    
    lucro = sessao.order_total - custo_total
    numero_pedido = obter_proximo_numero_pedido_dia()
    
    dados_pedido = DadosPedido(
        numero_do_dia=numero_pedido,
        timestamp=datetime.now(),
        itens=itens_para_salvar,
        total=sessao.order_total,
        lucro=lucro,
        pagamento=sessao.payment_method or MetodoPagamento.PIX,
        endereco=sessao.address or "Não informado",
        observacoes=sessao.change_needed or "",
        status=StatusPedido.RECEBIDO
    )
    
    # Enviar tarefas assíncronas
    pedido_dict = dados_pedido.model_dump(mode="json")
    
    registrar_pedido_sqlite.delay(pedido_dict)
    registrar_pedido_google_sheets.delay(pedido_dict)
    registrar_pedido_excel.delay(pedido_dict)
    
    # Calcular lucro do dia
    lucro_dia = calcular_lucro_total_dia()
    logger.info(f"💰 Lucro total do dia: R$ {lucro_dia:.2f}")
    
    # Resposta para cliente
    response = (
        f"✅ Endereço: *{sessao.address}* confirmado!\n\n"
        f"*Seu pedido #{numero_pedido} foi enviado para nossa equipe!* 🍕\n"
        f"Em breve você receberá a confirmação final.\n\n"
        f"*Obrigado por escolher a Pizzaria Delícia!* 🍕"
    )
    
    if sessao.change_needed and "Sim" in sessao.change_needed:
        response += f"\n_{sessao.change_needed}_"
    
    # Reset sessão mantendo histórico
    chat_history = sessao.chat_history
    nova_sessao = SessaoCliente(chat_history=chat_history)
    
    return response, nova_sessao


def formatar_resumo_pedido(sessao: SessaoCliente) -> str:
    """Formata resumo do pedido para exibição."""
    if not sessao.current_order:
        return "Carrinho vazio."
    
    linhas = ["*Resumo do Pedido:*\n"]
    for chave, qtd in sessao.current_order.items():
        sabor, tam = chave.rsplit(' ', 1)
        tamanho = TamanhoPizza(tam.upper())
        preco = cardapio.get_preco(sabor, tamanho) or 0
        linhas.append(f"*{qtd}x {sabor.title()} ({tamanho.value})* - R$ {preco:.2f} cada")
    
    linhas.append(f"\n*Subtotal: R$ {sessao.order_total:.2f}*")
    return "\n".join(linhas)