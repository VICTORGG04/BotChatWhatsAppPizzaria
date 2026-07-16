from models import Cardapio, SaborCardapio, ItemCardapio, TamanhoPizza
from config import settings
import json
from pathlib import Path


CARDAPIO_PADRAO = {
    "sabores": {
        "margherita_classica": {
            "categoria": "tradicional",
            "nome_exibicao": "Margherita Cl\u00e1ssica",
            "M": {"preco": 38.90, "custo": 14.00, "descricao": "Muçarela, rodelas de tomate fresco, manjericão e azeite de oliva."},
            "G": {"preco": 48.90, "custo": 18.00, "descricao": "Muçarela, rodelas de tomate fresco, manjericão e azeite de oliva."}
        },
        "calabresa_especial": {
            "categoria": "tradicional",
            "nome_exibicao": "Calabresa Especial",
            "M": {"preco": 40.00, "custo": 15.00, "descricao": "Muçarela, calabresa fatiada e cebola roxa."},
            "G": {"preco": 50.00, "custo": 19.00, "descricao": "Muçarela, calabresa fatiada e cebola roxa."}
        },
        "frango_catupiry": {
            "categoria": "tradicional",
            "nome_exibicao": "Frango com Catupiry",
            "M": {"preco": 42.00, "custo": 16.00, "descricao": "Peito de frango desfiado temperado e o legítimo Catupiry."},
            "G": {"preco": 54.00, "custo": 20.00, "descricao": "Peito de frango desfiado temperado e o legítimo Catupiry."}
        },
        "portuguesa": {
            "categoria": "tradicional",
            "nome_exibicao": "Portuguesa",
            "M": {"preco": 42.00, "custo": 16.00, "descricao": "Presunto, ovos, cebola, ervilha, muçarela e azeitonas pretas."},
            "G": {"preco": 54.00, "custo": 20.00, "descricao": "Presunto, ovos, cebola, ervilha, muçarela e azeitonas pretas."}
        },
        "quatro_queijos_casa": {
            "categoria": "especial",
            "nome_exibicao": "Quatro Queijos da Casa",
            "M": {"preco": 46.00, "custo": 18.00, "descricao": "Muçarela, provolone, gorgonzola e creme de requeijão maçaricado."},
            "G": {"preco": 58.00, "custo": 22.00, "descricao": "Muçarela, provolone, gorgonzola e creme de requeijão maçaricado."}
        },
        "parma_rucula": {
            "categoria": "especial",
            "nome_exibicao": "Parma & R\u00facula",
            "M": {"preco": 49.90, "custo": 20.00, "descricao": "Muçarela, presunto do tipo Parma, rúcula fresca e lascas de parmesão."},
            "G": {"preco": 62.00, "custo": 25.00, "descricao": "Muçarela, presunto do tipo Parma, rúcula fresca e lascas de parmesão."}
        },
        "pepperoni_hot_honey": {
            "categoria": "especial",
            "nome_exibicao": "Pepperoni & Hot Honey",
            "M": {"preco": 48.00, "custo": 19.00, "descricao": "Muçarela, pepperoni artesanal e um fio de mel picante infusionado na casa."},
            "G": {"preco": 60.00, "custo": 24.00, "descricao": "Muçarela, pepperoni artesanal e um fio de mel picante infusionado na casa."}
        },
        "brigadeiro_premium": {
            "categoria": "doce",
            "nome_exibicao": "Brigadeiro Premium",
            "M": {"preco": 35.00, "custo": 12.00, "descricao": "Chocolate ao leite artesanal e granulado belga."}
        },
        "romeu_julieta": {
            "categoria": "doce",
            "nome_exibicao": "Romeu e Julieta",
            "M": {"preco": 36.00, "custo": 13.00, "descricao": "Muçarela, goiabada cascão cremosa e requeijão de corte."}
        }
    }
}

BEBIDAS_PADRAO = [
    {"chave": "coca_2l", "nome": "Coca-Cola 2L", "preco": 12.00, "custo": 5.00},
    {"chave": "coca_lata", "nome": "Coca-Cola Lata", "preco": 6.00, "custo": 2.50},
    {"chave": "guarana_2l", "nome": "Guaraná 2L", "preco": 10.00, "custo": 4.00},
    {"chave": "guarana_lata", "nome": "Guaraná Lata", "preco": 5.00, "custo": 2.00},
    {"chave": "fanta_laranja", "nome": "Fanta Laranja 2L", "preco": 10.00, "custo": 4.00},
    {"chave": "suco_laranja", "nome": "Suco de Laranja", "preco": 8.00, "custo": 3.00},
    {"chave": "suco_uva", "nome": "Suco de Uva", "preco": 8.00, "custo": 3.00},
    {"chave": "agua", "nome": "Água Mineral", "preco": 4.00, "custo": 1.50},
    {"chave": "agua_gas", "nome": "Água com Gás", "preco": 5.00, "custo": 2.00},
    {"chave": "heineken", "nome": "Cerveja Heineken", "preco": 8.00, "custo": 4.50},
    {"chave": "brahma", "nome": "Cerveja Brahma", "preco": 6.00, "custo": 3.00},
    {"chave": "skol", "nome": "Cerveja Skol", "preco": 5.00, "custo": 2.50},
]

ADICIONAIS_PADRAO = [
    {"chave": "borda_catupiry", "nome": "Borda Recheada Catupiry", "preco": 8.00, "custo": 3.00},
    {"chave": "borda_cheddar", "nome": "Borda Recheada Cheddar", "preco": 8.00, "custo": 3.00},
    {"chave": "extra_mucarela", "nome": "Extra Muçarela", "preco": 5.00, "custo": 2.00},
    {"chave": "extra_catupiry", "nome": "Extra Catupiry", "preco": 6.00, "custo": 2.50},
    {"chave": "extra_cheddar", "nome": "Extra Cheddar", "preco": 6.00, "custo": 2.50},
    {"chave": "bacon_extra", "nome": "Bacon Extra", "preco": 7.00, "custo": 3.00},
    {"chave": "molho_especial", "nome": "Molho Especial", "preco": 3.00, "custo": 1.00},
    {"chave": "oregano", "nome": "Orégano", "preco": 0.00, "custo": 0.00},
]


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
    for nome, tamanhos in data.get("sabores", data).items():
        # Support both old and new format
        if isinstance(tamanhos, dict):
            categoria = tamanhos.get("categoria", "tradicional") if isinstance(tamanhos.get("categoria"), str) else "tradicional"
            nome_exibicao = tamanhos.get("nome_exibicao") if isinstance(tamanhos.get("nome_exibicao"), str) else None
            tamanhos_tipados = {}
            for tam, info in tamanhos.items():
                if tam in [t.value for t in TamanhoPizza]:
                    tamanho = TamanhoPizza(tam)
                    tamanhos_tipados[tamanho] = ItemCardapio(
                        preco=info["preco"],
                        custo=info["custo"],
                        descricao=info.get("descricao", "")
                    )
            if tamanhos_tipados:
                sabores[nome] = SaborCardapio(nome=nome, nome_exibicao=nome_exibicao, tamanhos=tamanhos_tipados, categoria=categoria)

    return Cardapio(
        sabores=sabores,
        bebidas=data.get("bebidas", BEBIDAS_PADRAO),
        adicionais=data.get("adicionais", ADICIONAIS_PADRAO),
    )


def salvar_cardapio_json(cardapio: Cardapio, caminho: str = "cardapio.json") -> bool:
    """Salva cardápio em arquivo JSON."""
    try:
        data = {"sabores": {}, "bebidas": cardapio.bebidas, "adicionais": cardapio.adicionais}
        for nome, sabor in cardapio.sabores.items():
            entry = {"categoria": sabor.categoria}
            if sabor.nome_exibicao:
                entry["nome_exibicao"] = sabor.nome_exibicao
            for tamanho, info in sabor.tamanhos.items():
                entry[tamanho.value] = {
                    "preco": info.preco,
                    "custo": info.custo,
                    "descricao": info.descricao
                }
            data["sabores"][nome] = entry
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