import os
import logging
from flask import Flask, request, jsonify, abort

from config import settings
from models import SessaoCliente, WebhookPayload
from session_manager import session_manager
from security import whatsapp_webhook_required, verify_whatsapp_webhook_challenge
from chatbot import processar_mensagem

# Configurar logging estruturado
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    stream=None,
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
)

logger = structlog.get_logger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "app": "PyPizzas - Bot WhatsApp",
        "version": "2.0.0",
        "status": "running",
        "webhook": "/webhook",
        "health": "/health"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint para Docker/load balancer."""
    redis_ok = session_manager.health_check()
    
    return jsonify({
        "status": "healthy" if redis_ok else "degraded",
        "service": "pizzaria-bot",
        "version": "2.0.0",
        "redis": "connected" if redis_ok else "disconnected"
    }), 200 if redis_ok else 503


@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """Verificação do webhook WhatsApp (challenge)."""
    result = verify_whatsapp_webhook_challenge()
    if result:
        challenge, status = result
        return challenge, status
    return "Webhook endpoint", 200


@app.route('/webhook', methods=['POST'])
@whatsapp_webhook_required
def webhook():
    """
    Webhook principal para receber mensagens do WhatsApp Business API.
    """
    try:
        payload = request.get_json()
        
        if not payload:
            logger.warning("Payload vazio recebido")
            abort(400, description="Payload inválido")
        
        # Log estruturado da requisição
        logger.info("Webhook recebido", payload_keys=list(payload.keys()))
        
        # Processar mensagens
        webhook_data = WebhookPayload(**payload)
        
        for message in webhook_data.get_messages():
            phone_number = message.from_
            text = message.body
            
            if not phone_number or not text:
                continue
            
            # Recuperar/criar sessão
            sessao = session_manager.get(phone_number)
            
            # Adicionar ao histórico
            sessao.chat_history.append({"role": "user", "parts": [{"text": text}]})
            
            # Processar mensagem
            response, updated_sessao = processar_mensagem(text, sessao)
            
            # Adicionar resposta ao histórico
            updated_sessao.chat_history.append({"role": "model", "parts": [{"text": response}]})
            
            # Salvar sessão atualizada
            session_manager.save(phone_number, updated_sessao)
            
            # Log da interação
            logger.info(
                "Mensagem processada",
                phone=phone_number[-4:],  # Log apenas últimos 4 dígitos
                state=updated_sessao.state,
                response_length=len(response)
            )
            
            # TODO: Enviar resposta via WhatsApp API
            # await enviar_mensagem_whatsapp(phone_number, response)
        
        return "OK", 200
        
    except Exception as e:
        logger.error("Erro no webhook", error=str(e), exc_info=True)
        abort(500, description="Erro interno do servidor")


@app.route('/admin/pedidos', methods=['GET'])
def admin_pedidos():
    """Endpoint admin para listar pedidos do dia (protegido por IP/API key em produção)."""
    from chatbot.storage.sqlite import buscar_pedidos_hoje
    
    pedidos = buscar_pedidos_hoje()
    return jsonify({
        "total": len(pedidos),
        "pedidos": pedidos
    })


@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    """Endpoint admin para estatísticas."""
    from chatbot.storage.sqlite import calcular_lucro_total_dia
    
    lucro = calcular_lucro_total_dia()
    return jsonify({
        "lucro_dia": lucro,
        "moeda": "BRL"
    })


@app.errorhandler(400)
def bad_request(e):
    logger.warning("Bad request", error=str(e))
    return jsonify({"error": "Requisição inválida", "message": str(e)}), 400


@app.errorhandler(401)
def unauthorized(e):
    logger.warning("Unauthorized", error=str(e))
    return jsonify({"error": "Não autorizado", "message": str(e)}), 401


@app.errorhandler(500)
def internal_error(e):
    logger.error("Internal server error", error=str(e), exc_info=True)
    return jsonify({"error": "Erro interno", "message": "Erro no processamento"}), 500


if __name__ == '__main__':
    # Setup database on startup
    from chatbot.storage.sqlite import setup_database
    setup_database()
    
    logger.info("Iniciando Pizzaria Bot", host=settings.host, port=settings.port)
    app.run(host=settings.host, port=settings.port, debug=settings.debug)