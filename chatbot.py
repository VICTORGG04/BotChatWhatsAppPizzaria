CARDAPIO = {
    "margherita": {"preco": 35.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Manjericão"]},
    "calabresa": {"preco": 40.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Calabresa", "Cebola"]},
    "portuguesa": {"preco": 45.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Presunto", "Ovo", "Cebola"]},
    "quatro queijos": {"preco": 50.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Parmesão", "Gorgonzola", "Provolone"]}, # Adicionei espaço
    "frango com catupiry": {"preco": 55.00, "ingredientes": ["Massa", "Molho de tomate", "Queijo", "Frango desfiado", "Catupiry"]}, # Adicionei espaço
}

def saudacao():
    print("Olá! Bem-vindo à Pizzaria Delícia!")
    print("Sou seu assistente virtual. Como posso ajudar?")
    print("1. Ver Cardápio")
    print("2. Fazer Pedido")
    print("3. Falar com Atendente")
    print("4. Sair")

def exibir_cardapio():
    print("\n--- NOSSO CARDÁPIO ---")
    for sabor, detalhes in CARDAPIO.items():
        sabor_formatado = sabor.replace("_", " ").title()
        ingredientes_str = ", ".join(detalhes['ingredientes'])
        print(f"- {sabor_formatado}: R$ {detalhes['preco']:.2f} - Ingredientes: {ingredientes_str}.")
    print("----------------------")
    
def fazer_pedido():
    pedido = {}
    total_pedido = 0.0
    print("\nÓtimo! Para fazer seu pedido, digite o nome do sabor da pizza.")
    print("Digite 'fim' para finalizar o pedido ou 'cancelar' para cancelar o pedido.")

    while True:
        sabor_input = input("Digite o sabor da pizza: ").lower().strip()

        if sabor_input == 'fim':
            break
        elif sabor_input == 'cancelar':
            return {}, 0.0

        if sabor_input not in CARDAPIO:
            print("Desculpe, mas esse sabor não está no nosso cardápio. Por favor, veja a lista de sabores disponíveis.")
            exibir_cardapio()
            continue

        try:
            quantidade = int(input(f"Quantas Pizzas de {sabor_input.title()} você gostaria? "))
            if quantidade <= 0:
                print("Quantidade inválida. Por favor, insira um número maior que zero.")
                continue
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")
            continue

        preco_pizza = CARDAPIO[sabor_input]['preco']
        pedido[sabor_input] = pedido.get(sabor_input, 0) + quantidade
        total_pedido += preco_pizza * quantidade
        print(f"{quantidade}x {sabor_input.title()} adicionada(s) ao seu pedido.") 

    if pedido:
        print("\nSeu pedido foi finalizado com sucesso!")
        print("Resumo do Pedido:")
        for sabor_final, quantidade_final in pedido.items(): 
            print(f"{quantidade_final}x {sabor_final.replace('_', ' ').title()} - (R$ {CARDAPIO[sabor_final]['preco']:.2f} cada)")
        return pedido, total_pedido 
    else:
        print("Nenhum item adicionado ao Pedido.")
        return {}, 0.0
    
def finalizar_pedido(pedido, total_pedido):
    if not pedido:
        print("Não há pedido para finalizar.") 
        return

    print(f"\nSeu pedido totalizou R$ {total_pedido:.2f}") 
    endereco = input("Por favor, informe o endereço de entrega: ")
    print(f"Pedido enviado para {endereco}. Agradecemos pela preferência!")
    print("\nAguarde a confirmação do atendente.")
    print("\nObrigado por escolher a Pizzaria Delícia!")
    
def falar_com_atendente():
    print("\nVocê será transferido para um de nossos atendente.")
    print("Por favor, aguarde enquanto conectamos você.")
    
def main():
    while True:
        saudacao()
        opcao = input("Escolha uma opção (1-4): ").strip()

        if opcao == '1':
            exibir_cardapio()
        elif opcao == '2':
            pedido, total_pedido = fazer_pedido()
            if pedido: 
                finalizar_pedido(pedido, total_pedido)
        elif opcao == '3':
            falar_com_atendente()
        elif opcao == '4':
            print("Obrigado por usar nosso serviço! Até logo!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma das opções entre 1 e 4.")
        if opcao != '4':
            input("\nPressione Enter para continuar...")
            
if __name__ == "__main__":
    main()