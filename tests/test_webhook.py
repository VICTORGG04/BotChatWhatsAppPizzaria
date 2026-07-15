import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

from app import app
from models import SessaoCliente, WebhookPayload
from chatbot import processar_mensagem


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_session_manager():
    with patch('app.session_manager') as mock:
        mock.get.return_value = SessaoCliente()
        mock.save.return_value = True
        mock.health_check.return_value = True
        yield mock


class TestHealthCheck:
    """Testes para health check endpoint."""

    def test_health_check_healthy(self, client, mock_session_manager):
        mock_session_manager.health_check.return_value = True
        
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['redis'] == 'connected'

    def test_health_check_degraded(self, client, mock_session_manager):
        mock_session_manager.health_check.return_value = False
        
        response = client.get('/health')
        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'degraded'
        assert data['redis'] == 'disconnected'


class TestWebhookVerify:
    """Testes para verificação do webhook (GET)."""

    def test_verify_challenge_valid(self, client):
        with patch('app.settings') as mock_settings:
            mock_settings.whatsapp_verify_token = "test_token"
            
            response = client.get('/webhook?hub.mode=subscribe&hub.verify_token=test_token&hub.challenge=12345')
            assert response.status_code == 200
            assert response.data.decode() == "12345"

    def test_verify_challenge_invalid_token(self, client):
        with patch('app.settings') as mock_settings:
            mock_settings.whatsapp_verify_token = "correct_token"
            
            response = client.get('/webhook?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=12345')
            assert response.status_code == 403

    def test_verify_challenge_missing_params(self, client):
        response = client.get('/webhook')
        assert response.status_code == 200
        assert "Webhook endpoint" in response.data.decode()


class TestWebhookPost:
    """Testes para webhook POST."""

    def test_webhook_empty_payload(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            response = client.post('/webhook', data='', content_type='application/json')
            assert response.status_code == 400

    def test_webhook_invalid_json(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            response = client.post('/webhook', data='not json', content_type='application/json')
            assert response.status_code == 400

    def test_webhook_valid_message(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            with patch('app.processar_mensagem') as mock_processar:
                mock_processar.return_value = ("Resposta do bot", SessaoCliente())
                
                payload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "123",
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "5511999999999",
                                    "id": "wamid.test",
                                    "timestamp": "1234567890",
                                    "text": {"body": "Olá"},
                                    "type": "text"
                                }]
                            },
                            "field": "messages"
                        }]
                    }]
                }
                
                response = client.post('/webhook', json=payload)
                assert response.status_code == 200
                assert response.data.decode() == "OK"
                
                mock_processar.assert_called_once()
                mock_session_manager.save.assert_called_once()

    def test_webhook_multiple_messages(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            with patch('app.processar_mensagem') as mock_processar:
                mock_processar.return_value = ("Resposta", SessaoCliente())
                
                payload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [
                                    {"from": "5511999999999", "id": "1", "timestamp": "1", "text": {"body": "Oi"}, "type": "text"},
                                    {"from": "5511888888888", "id": "2", "timestamp": "2", "text": {"body": "Olá"}, "type": "text"}
                                ]
                            },
                            "field": "messages"
                        }]
                    }]
                }
                
                response = client.post('/webhook', json=payload)
                assert response.status_code == 200
                assert mock_processar.call_count == 2
                assert mock_session_manager.save.call_count == 2

    def test_webhook_missing_from_or_body(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            payload = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "id": "wamid.test",
                                "timestamp": "1234567890",
                                "text": {"body": "Olá"},
                                "type": "text"
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            response = client.post('/webhook', json=payload)
            assert response.status_code == 200  # Processa mas ignora mensagens inválidas


class TestWebhookSignature:
    """Testes para verificação de assinatura."""

    def test_webhook_invalid_signature(self, client):
        with patch('app.verify_whatsapp_signature', return_value=False):
            payload = {"entry": []}
            response = client.post('/webhook', json=payload)
            assert response.status_code == 401

    def test_webhook_valid_signature(self, client, mock_session_manager):
        with patch('app.verify_whatsapp_signature', return_value=True):
            with patch('app.processar_mensagem') as mock_processar:
                mock_processar.return_value = ("OK", SessaoCliente())
                
                payload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "5511999999999",
                                    "id": "1",
                                    "timestamp": "1",
                                    "text": {"body": "Oi"},
                                    "type": "text"
                                }]
                            },
                            "field": "messages"
                        }]
                    }]
                }
                
                response = client.post('/webhook', json=payload)
                assert response.status_code == 200


class TestAdminEndpoints:
    """Testes para endpoints administrativos."""

    def test_admin_pedidos(self, client):
        with patch('app.buscar_pedidos_hoje') as mock_buscar:
            mock_buscar.return_value = [
                {"numero_do_dia": 1, "total": 52.00, "status": "recebido"}
            ]
            
            response = client.get('/admin/pedidos')
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] == 1
            assert len(data['pedidos']) == 1

    def test_admin_stats(self, client):
        with patch('app.calcular_lucro_total_dia') as mock_lucro:
            mock_lucro.return_value = 150.75
            
            response = client.get('/admin/stats')
            assert response.status_code == 200
            data = response.get_json()
            assert data['lucro_dia'] == 150.75
            assert data['moeda'] == 'BRL'