# test_simulacao_hardcore.py

import pytest
import random
from collections import Counter

# Importa as funções e o cardápio do nosso módulo de simulação
from simulacao_pizzaria import gerar_simulacao_pedidos, gerar_relatorio_final, CARDAPIO
def test_simulacao_hardcore_auditoria_completa_de_100_pedidos():

    # --- ETAPA 1: CONFIGURAÇÃO E GERAÇÃO DOS DADOS ---
    NUM_PEDIDOS_PARA_TESTAR = 100
    SEMENTE_RANDOM = 42  # Usar uma semente garante que o teste seja reprodutível
    random.seed(SEMENTE_RANDOM)

    print(f"\nIniciando auditoria hardcore com {NUM_PEDIDOS_PARA_TESTAR} pedidos...")
    
    # Gera a lista de 100 pedidos que será auditada
    pedidos_gerados = gerar_simulacao_pedidos(num_pedidos=NUM_PEDIDOS_PARA_TESTAR)
    # Verificação básica: a quantidade de pedidos está correta?
    assert len(pedidos_gerados) == NUM_PEDIDOS_PARA_TESTAR
    print(f"✔ OK: {len(pedidos_gerados)} pedidos foram gerados corretamente.")


    # --- ETAPA 2: AUDITORIA INDIVIDUAL DE CADA PEDIDO ---
    for pedido in pedidos_gerados:
        # Para cada pedido, verificamos a integridade dos seus dados internos
        assert "id_pedido" in pedido
        assert "itens" in pedido
        assert "subtotal" in pedido
        
        # O pedido deve ter pelo menos um item
        assert len(pedido['itens']) > 0

        subtotal_calculado_manualmente = 0.0
        
        for item in pedido['itens']:
            # O sabor da pizza existe no cardápio?
            assert item['sabor'] in CARDAPIO, f"Pedido #{pedido['id_pedido']} tem sabor inválido: {item['sabor']}"
            # O tamanho da pizza existe para esse sabor?
            assert item['tamanho'] in CARDAPIO[item['sabor']], f"Pedido #{pedido['id_pedido']} tem tamanho inválido: {item['tamanho']} para {item['sabor']}"   
            # O preço do item no pedido é o mesmo que o preço no cardápio?
            preco_correto_do_cardapio = CARDAPIO[item['sabor']][item['tamanho']]['preco']
            assert item['preco'] == preco_correto_do_cardapio, f"Preço incorreto no Pedido #{pedido['id_pedido']}"
            subtotal_calculado_manualmente += item['preco']

        # O subtotal registrado no pedido é igual à soma manual dos preços dos itens?
        assert pedido['subtotal'] == pytest.approx(subtotal_calculado_manualmente), f"Subtotal do Pedido #{pedido['id_pedido']} está calculado incorretamente."

    print(f"✔ OK: Todos os {len(pedidos_gerados)} pedidos passaram na auditoria individual de integridade.")


    # --- ETAPA 3: AUDITORIA DO RELATÓRIO FINAL ---
    # Gera o relatório com base nos dados que acabamos de auditar
    relatorio = gerar_relatorio_final(pedidos_gerados)

    # Recalcula as métricas do zero para comparar com o relatório
    faturamento_bruto_auditado = sum(p['subtotal'] for p in pedidos_gerados)
    total_pizzas_auditado = sum(len(p['itens']) for p in pedidos_gerados)
    
    # Conta todos os sabores de todas as pizzas vendidas
    todos_sabores_vendidos = [item['sabor'] for pedido in pedidos_gerados for item in pedido['itens']]
    contagem_sabores_auditada = Counter(todos_sabores_vendidos)
    pizza_mais_popular_auditada = contagem_sabores_auditada.most_common(1)[0][0]

    # Compara os valores auditados com os valores do relatório
    assert relatorio['faturamento_bruto'] == pytest.approx(faturamento_bruto_auditado)
    assert relatorio['total_pizzas_vendidas'] == total_pizzas_auditado
    assert relatorio['pizza_mais_popular'] == pizza_mais_popular_auditada
    assert relatorio['total_pedidos'] == NUM_PEDIDOS_PARA_TESTAR
    
    print("✔ OK: O relatório final reflete perfeitamente os dados auditados.")
    print("--- Auditoria Hardcore Concluída com Sucesso! ---")