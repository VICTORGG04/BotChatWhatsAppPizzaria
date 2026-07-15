import hmac
import hashlib
import logging
from functools import wraps
from flask import request, abort

from config import settings

logger = logging.getLogger(__name__)


def verify_whatsapp_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica a assinatura HMAC-SHA256 do WhatsApp Business API.
    """
    if not signature or not signature.startswith("sha256="):
        logger.warning("Assinatura WhatsApp ausente ou formato inválido")
        return False
    
    if not settings.whatsapp_app_secret:
        logger.warning("WHATSAPP_APP_SECRET não configurado - pulando verificação")
        return True  # Em dev, permitir sem secret
    
    expected_signature = signature[7:]  # Remove 'sha256='
    app_secret = settings.whatsapp_app_secret.encode('utf-8')
    computed_hash = hmac.new(app_secret, payload, hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(computed_hash, expected_signature)


def whatsapp_webhook_required(f):
    """Decorator para validar assinatura do WhatsApp no webhook."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Em desenvolvimento, pular se não tiver secret
        if not settings.whatsapp_app_secret and settings.app_env != "production":
            return f(*args, **kwargs)
        
        signature = request.headers.get("X-Hub-Signature-256", "")
        payload = request.get_data()
        
        if not verify_whatsapp_signature(payload, signature):
            logger.warning(
                "Webhook WhatsApp rejeitado: assinatura inválida",
                extra={"ip": request.remote_addr}
            )
            abort(401, description="Assinatura WhatsApp inválida")
        
        return f(*args, **kwargs)
    return decorated_function


def verify_whatsapp_webhook_challenge():
    """Verifica challenge de verificação do webhook (GET)."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook WhatsApp verificado com sucesso")
        return challenge, 200
    
    if mode == "subscribe":
        logger.warning("Token de verificação WhatsApp inválido")
        abort(403, description="Token de verificação inválido")
    
    return None