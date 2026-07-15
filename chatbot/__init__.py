"""
Chatbot Pizzaria - Módulo principal refatorado.

Arquitetura modular:
- cardapio.py: Gerenciamento do cardápio
- states.py: Máquina de estados da conversa
- service.py: Orquestração do processamento de pedidos
- ai.py: Integração com Gemini AI
- storage/: Backends de persistência (SQLite, Google Sheets, Excel)
"""

from chatbot.cardapio import cardapio, formatar_cardapio_whatsapp, listar_sabores_formatados, carregar_cardapio_json
from chatbot.states import processar_mensagem, EstadoConversa
from chatbot.service import processar_e_salvar_pedido, formatar_resumo_pedido
from chatbot.ai import resumir_conversa, processar_mensagem_ia

__all__ = [
    "cardapio",
    "formatar_cardapio_whatsapp",
    "listar_sabores_formatados",
    "carregar_cardapio_json",
    "processar_mensagem",
    "EstadoConversa",
    "processar_e_salvar_pedido",
    "formatar_resumo_pedido",
    "resumir_conversa",
    "processar_mensagem_ia",
]

__version__ = "2.0.0"