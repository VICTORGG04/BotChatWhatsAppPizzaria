# simulacao_pizzaria.py

import random

# CARDÁPIO USADO NA SIMULAÇÃO
CARDAPIO = {
    "margherita": { "M": {"preco": 35.00}, "G": {"preco": 45.00}, "GG": {"preco": 55.00} },
    "calabresa": { "M": {"preco": 40.00}, "G": {"preco": 52.00}, "GG": {"preco": 63.00} },
    "portuguesa": { "M": {"preco": 45.00}, "G": {"preco": 58.00}, "GG": {"preco": 70.00} },
    "quatro queijos": { "M": {"preco": 50.00}, "G": {"preco": 65.00}, "GG": {"preco": 78.00} },
    "frango com catupiry": { "M": {"preco": 55.00}, "G": {"preco": 72.00}, "GG": {"preco": 85.00} },
    "chocolate branco com morango": { "M": {"preco": 50.00}, "G": {"preco": 65.00}, "GG": {"preco": 78.00} },
    "chocolate preto com confetti": { "M": {"preco": 48.00}, "G": {"preco": 62.00}, "GG": {"preco": 75.00} },
    "camarão com catupiry": { "M": {"preco": 65.00}, "G": {"preco": 85.00}, "GG": {"preco": 100.00} }
}

def _escolher_itens_pedido():
    """
    Função interna para escolher aleatoriamente as pizzas de um único pedido.
    Define a quantidade de pizzas e seus sabores/tamanhos de forma ponderada.
    """
    sabores_disponiveis = list(CARDAPIO.keys())
    tamanhos_disponiveis = ["M", "G", "GG"]
    
    # Define a popularidade para tornar a simulação mais realista
    pesos_popularidade = {
        "calabresa": 0.20, "frango com catupiry": 0.18, "portuguesa": 0.15,
        "margherita": 0.15, "quatro queijos": 0.12, "chocolate preto com confetti": 0.10,
        "chocolate branco com morango": 0.07, "camarão com catupiry": 0.03
    }

    # Escolhe quantas pizzas terá no pedido (mais chance de ser 1 ou 2)
    num_pizzas = random.choices([1, 2, 3, 4], weights=[0.50, 0.35, 0.12, 0.03], k=1)[0]
    
    itens_do_pedido = []
    subtotal = 0.0
    
    for _ in range(num_pizzas):
        sabor = random.choices(sabores_disponiveis, weights=list(pesos_popularidade.values()), k=1)[0]
        tamanho = random.choices(tamanhos_disponiveis, weights=[0.3, 0.5, 0.2], k=1)[0]
        
        preco = CARDAPIO[sabor][tamanho]["preco"]
        subtotal += preco
        itens_do_pedido.append({"sabor": sabor, "tamanho": tamanho, "preco": preco})
        
    return itens_do_pedido, subtotal

def gerar_simulacao_pedidos(num_pedidos=100):
    """
    Gera uma lista de pedidos simulados para uma noite movimentada na pizzaria.
    Cada pedido é um dicionário com detalhes da compra.
    """
    lista_pedidos_final = []
    formas_pagamento = ["Pix", "Cartão", "Espécie"]
    
    for i in range(1, num_pedidos + 1):
        itens, subtotal = _escolher_itens_pedido()
        pagamento = random.choices(formas_pagamento, weights=[0.5, 0.4, 0.1], k=1)[0]
        
        observacao = ""
        if pagamento == "Espécie" and random.random() > 0.5:
            # 50% de chance de um pedido em dinheiro precisar de troco
            valor_troco = (int(subtotal / 50) + 1) * 50
            observacao = f"Troco para R$ {valor_troco:.2f}"
            
        pedido = {
            "id_pedido": i,
            "itens": itens,
            "subtotal": subtotal,
            "pagamento": pagamento,
            "observacao": observacao
        }
        lista_pedidos_final.append(pedido)
        
    return lista_pedidos_final

def gerar_relatorio_final(lista_pedidos):
    """
    Calcula as estatísticas finais com base na lista de pedidos gerada.
    Retorna um dicionário com o resumo da noite.
    """
    if not lista_pedidos:
        return {}

    faturamento_bruto = sum(p['subtotal'] for p in lista_pedidos)
    total_pizzas_vendidas = sum(len(p['itens']) for p in lista_pedidos)
    
    contagem_sabores = {}
    for pedido in lista_pedidos:
        for item in pedido['itens']:
            sabor = item['sabor']
            contagem_sabores[sabor] = contagem_sabores.get(sabor, 0) + 1
            
    pizza_mais_popular = max(contagem_sabores, key=contagem_sabores.get) if contagem_sabores else "Nenhuma"
    
    relatorio = {
        "total_pedidos": len(lista_pedidos),
        "total_pizzas_vendidas": total_pizzas_vendidas,
        "faturamento_bruto": faturamento_bruto,
        "ticket_medio": faturamento_bruto / len(lista_pedidos),
        "pizza_mais_popular": pizza_mais_popular
    }
    
    return relatorio