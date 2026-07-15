import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

_model = None


def init_gemini() -> bool:
    """Inicializa modelo Gemini."""
    global _model
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY não configurada - IA desativada")
        return False
    
    try:
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(settings.gemini_model)
        logger.info("Gemini AI inicializado")
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar Gemini: {e}")
        return False


def resumir_conversa(chat_history: list) -> str:
    """Gera resumo da conversa para atendente."""
    if not _model:
        return "🤖 Resumo da IA não disponível (API não configurada)."
    
    if not chat_history:
        return "Nenhuma conversa para resumir."
    
    try:
        conversa = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('parts', [{}])[0].get('text', '')}"
            for msg in chat_history
        ])
        
        prompt = (
            "Resuma esta conversa de WhatsApp para um atendente de pizzaria. "
            "Foque no: pedido do cliente, itens, endereço, forma de pagamento, "
            "observações e qualquer dificuldade na conversa. Seja breve (máx 3 linhas):\n\n"
            f"{conversa}"
        )
        
        response = _model.generate_content(prompt)
        return response.text.strip() if response.text else "Não foi possível gerar resumo."
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo IA: {e}")
        return f"Erro ao gerar resumo: {str(e)}"


def processar_mensagem_ia(mensagem: str, contexto: str = "") -> str:
    """Processa mensagem livre com IA (fallback para comandos não reconhecidos)."""
    if not _model:
        return ""
    
    try:
        prompt = f"""Você é um atendente virtual de pizzaria. 
Contexto: {contexto}
Cliente: {mensagem}

Responda de forma natural e útil, mas SEMPRE guie para o cardápio ou pedido.
Não invente preços ou itens. Se não souber, diga para falar com atendente (opção 3).
Máximo 3 frases."""
        
        response = _model.generate_content(prompt)
        return response.text.strip() if response.text else ""
        
    except Exception as e:
        logger.error(f"Erro IA processar mensagem: {e}")
        return ""


# Inicializar na importação
init_gemini()