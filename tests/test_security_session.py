import pytest
from unittest.mock import patch, MagicMock
import hmac
import hashlib

from security import verify_whatsapp_signature, whatsapp_webhook_required, verify_whatsapp_webhook_challenge
from session_manager import SessionManager
from models import SessaoCliente


class TestSecurity:
    """Testes para segurança do webhook."""

    def test_verify_signature_valid(self):
        secret = "test_secret_123"
        payload = b'{"test": "data"}'
        
        # Gerar assinatura válida
        signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = secret
            assert verify_whatsapp_signature(payload, signature) is True

    def test_verify_signature_invalid(self):
        secret = "test_secret_123"
        payload = b'{"test": "data"}'
        signature = "sha256=invalid_signature"
        
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = secret
            assert verify_whatsapp_signature(payload, signature) is False

    def test_verify_signature_missing_prefix(self):
        secret = "test_secret_123"
        payload = b'{"test": "data"}'
        signature = "invalid_format"
        
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = secret
            assert verify_whatsapp_signature(payload, signature) is False

    def test_verify_signature_empty(self):
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = "secret"
            assert verify_whatsapp_signature(b"{}", "") is False
            assert verify_whatsapp_signature(b"{}", None) is False

    def test_verify_signature_no_secret_dev_mode(self):
        """Em dev sem secret, deve permitir."""
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = ""
            mock_settings.app_env = "development"
            assert verify_whatsapp_signature(b"{}", "sha256=anything") is True

    def test_verify_signature_no_secret_prod_mode(self):
        """Em produção sem secret, deve bloquear."""
        with patch('security.settings') as mock_settings:
            mock_settings.whatsapp_app_secret = ""
            mock_settings.app_env = "production"
            assert verify_whatsapp_signature(b"{}", "sha256=anything") is False


class TestSessionManager:
    """Testes para gerenciador de sessões."""

    @pytest.fixture
    def mock_redis(self):
        with patch('session_manager.Redis') as mock:
            instance = MagicMock()
            instance.ping.return_value = True
            instance.get.return_value = None
            instance.setex.return_value = True
            instance.delete.return_value = True
            instance.expire.return_value = True
            mock.from_url.return_value = instance
            mock.return_value = instance
            yield instance

    def test_get_session_new(self, mock_redis):
        manager = SessionManager()
        manager._redis = mock_redis
        mock_redis.get.return_value = None
        
        sessao = manager.get("5511999999999")
        assert isinstance(sessao, SessaoCliente)
        assert sessao.state == "initial"

    def test_get_session_existing(self, mock_redis):
        manager = SessionManager()
        manager._redis = mock_redis
        
        session_data = {
            "state": "awaiting_flavor",
            "current_order": {"calabresa g": 2},
            "order_total": 104.00,
            "chat_history": [{"role": "user", "parts": [{"text": "Oi"}]}]
        }
        import json
        mock_redis.get.return_value = json.dumps(session_data)
        
        sessao = manager.get("5511999999999")
        assert sessao.state == "awaiting_flavor"
        assert sessao.current_order == {"calabresa g": 2}
        assert sessao.order_total == 104.00

    def test_save_session(self, mock_redis):
        manager = SessionManager()
        manager._redis = mock_redis
        
        sessao = SessaoCliente(
            state="awaiting_size",
            current_order={"margherita m": 1},
            order_total=35.00
        )
        
        result = manager.save("5511999999999", sessao)
        assert result is True
        mock_redis.setex.assert_called_once()

    def test_delete_session(self, mock_redis):
        manager = SessionManager()
        manager._redis = mock_redis
        
        result = manager.delete("5511999999999")
        assert result is True
        mock_redis.delete.assert_called_once()

    def test_health_check(self, mock_redis):
        manager = SessionManager()
        manager._redis = mock_redis
        mock_redis.ping.return_value = True
        
        assert manager.health_check() is True
        
        mock_redis.ping.return_value = False
        assert manager.health_check() is False


class TestSessionManagerIntegration:
    """Testes de integração do session manager com mock completo."""

    def test_full_flow_get_modify_save(self):
        with patch('session_manager.Redis') as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            mock_redis.get.return_value = None
            mock_redis.setex.return_value = True
            mock_redis_class.from_url.return_value = mock_redis
            
            manager = SessionManager()
            
            # Get new session
            sessao = manager.get("5511999999999")
            assert sessao.state == "initial"
            
            # Modify session
            sessao.state = "awaiting_flavor"
            sessao.current_order["calabresa g"] = 1
            sessao.order_total = 52.00
            
            # Save
            result = manager.save("5511999999999", sessao)
            assert result is True
            
            # Verify data passed to Redis
            call_args = mock_redis.setex.call_args
            assert call_args is not None
            key = call_args[0][0]
            assert key == "pizzaria:session:5511999999999"