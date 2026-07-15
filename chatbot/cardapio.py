from models import Cardapio, SaborCardapio, ItemCardapio, TamanhoPizza
from config import settings
import json
from pathlib import Path


CARDAPIO_PADRAO = {
    "margherita": {
        "M": {"preco": 35.00, "custo": 12.50, "descricao": "Molho, muçarela e manjericão."},
        "G": {"preco": 45.00, "custo": 16.00, "descricao": "Molho, muçarela e manjericão."},
        "GG": {"preco": 55.00, "custo": 20.00, "descricao": "Molho, muçarela e manjericão."}
    },
    "calabresa": {
        "M": {"preco": 40.00, "custo": 15.00, "descricao": "Molho, muçarela, calabresa e cebola."},
        "G": {"preco": 52.00, "custo": 19.50, "descricao": "Molho, muçarela, calabresa e cebola."},
        "GG": {"preco": 63.00, "custo": 24.00, "descricao": "Molho, muçarela, calabresa e cebola."}
    },
    "portuguesa": {
        "M": {"preco": 45.00, "custo": 17.00, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."},
        "G": {"preco": 58.00, "custo": 22.00, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."},
        "GG": {"preco": 70.00, "custo": 26.50, "descricao": "Molho, muçarela, presunto, ovos, cebola e azeitona."}
    },
    "quatro queijos": {
        "M": {"preco": 50.00, "custo": 20.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."},
        "G": {"preco": 65.00, "custo": 25.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."},
        "GG": {"preco": 78.00, "custo": 30.00, "descricao": "Molho, muçarela, parmesão, gorgonzola e provolone."}
    },
    "frango com catupiry": {
        "M": {"preco": 55.00, "custo": 21.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."},
        "G": {"preco": 72.00, "custo": 28.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."},
        "GG": {"preco": 85.00, "custo": 33.00, "descricao": "Molho, muçarela, frango desfiado e catupiry."}
    },
    "chocolate branco com morango": {
        "M": {"preco": 50.00, "custo": 18.00, "descricao": "Chocolate branco cremoso e morangos frescos."},
        "G": {"preco": 65.00, "custo": 24.00, "descricao": "Chocolate branco cremoso e morangos frescos."},
        "GG": {"preco": 78.00, "custo": 29.00, "descricao": "Chocolate branco cremoso e morangos frescos."}
    },
    "chocolate preto com confetti": {
        "M": {"preco": 48.00, "custo": 17.50, "descricao": "Chocolate meio amargo e granulados coloridos."},
        "G": {"preco": 62.00, "custo": 22.50, "descricao": "Chocolate meio amargo e granulados coloridos."},
        "GG": {"preco": 75.00, "custo": 28.00, "descricao": "Chocolate meio amargo e granulados coloridos."}
    },
    "camarao com catupiry": {
        "M": {"preco": 65.00, "custo": 28.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."},
        "G": {"preco": 85.00, "custo": 35.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."},
        "GG": {"preco": 100.00, "custo": 42.00, "descricao": "Molho, muçarela, camarão salteado e catupiry."}
    }
}


def carregar_cardapio_json(caminho: str = "cardapio.json") -> Cardapio:
    """Carrega cardápio de arquivo JSON se existir, senão usa padrão."""
    path = Path(caminho)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return _dict_para_cardapio(data)
        except Exception:
            pass
    return _dict_para_cardapio(CARDAPIO_PADRAO)


def _dict_para_cardapio(data: dict) -> Cardapio:
    sabores = {}
    for nome, tamanhos in data.items():
        tamanhos_tipados = {}
        for tam, info in tamanhos.items():
            tamanho = TamanhoPizza(tam)
            tamanhos_tipados[tamanho] = ItemCardapio(
                preco=info["preco"],
                custo=info["custo"],
                descricao=info.get("descricao", "")
            )
        sabores[nome] = SaborCardapio(nome=nome, tamanhos=tamanhos_tipados)
    return Cardapio(sabores=sabores)


def salvar_cardapio_json(cardapio: Cardapio, caminho: str = "cardapio.json") -> bool:
    """Salva cardápio em arquivo JSON."""
    try:
        data = {}
        for nome, sabor in cardapio.sabores.items():
            data[nome] = {}
            for tamanho, info in sabor.tamanhos.items():
                data[nome][tamanho.value] = {
                    "preco": info.preco,
                    "custo": info.custo,
                    "descricao": info.descricao
                }
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


cardapio = carregar_cardapio_json()


def formatar_cardapio_whatsapp(cardapio: Cardapio) -> str:
    """Formata cardápio para exibição no WhatsApp (markdown)."""
    linhas = ["🍕 *NOSSO CARDÁPIO* 🍕\n"]
    for sabor in cardapio.sabores.values():
        linhas.append(f"*{sabor.nome_formatado}*")
        precos = []
        for tam in [TamanhoPizza.M, TamanhoPizza.G, TamanhoPizza.GG]:
            if tam in sabor.tamanhos:
                preco = sabor.tamanhos[tam].preco
                precos.append(f"{tam.value}: R$ {preco:.2f}")
        linhas.append(" | ".join(precos))
        if TamanhoPizza.M in sabor.tamanhos:
            linhas.append(f"_{sabor.tamanhos[TamanhoPizza.M].descricao}_")
        linhas.append("")
    linhas.append("───────────────")
    return "\n".join(linhas)


def listar_sabores_formatados(cardapio: Cardapio) -> str:
    """Lista sabores formatados para mensagem."""
    sabores = [f"*{s.nome_formatado}*" for s in cardapio.sabores.values()]
    return ", ".join(sabores)