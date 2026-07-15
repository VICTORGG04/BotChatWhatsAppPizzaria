import pytest
from unittest.mock import MagicMock, patch

from models import SessaoCliente


@pytest.fixture
def client():
    """Flask test client."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_session():
    """Sessão de exemplo para testes."""
    return SessaoCliente(
        state="initial",
        chat_history=[],
        current_order={},
        order_total=0.0
    )


@pytest.fixture
def session_with_order():
    """Sessão com pedido em andamento."""
    return SessaoCliente(
        state="awaiting_flavor",
        chat_history=[{"role": "user", "parts": [{"text": "2"}]}],
        current_order={"calabresa g": 1},
        order_total=52.00,
        temp_flavor="calabresa",
        temp_size="G"
    )


@pytest.fixture
def mock_session_manager():
    """Mock do session_manager."""
    with patch('app.session_manager') as mock:
        mock.get.return_value = SessaoCliente()
        mock.save.return_value = True
        mock.health_check.return_value = True
        yield mock


@pytest.fixture
def mock_verify_signature():
    """Mock da verificação de assinatura."""
    with patch('app.verify_whatsapp_signature') as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_processar_mensagem():
    """Mock do processamento de mensagem."""
    with patch('app.processar_mensagem') as mock:
        mock.return_value = ("Resposta do bot", SessaoCliente())
        yield mock


@pytest.fixture(autouse=True)
def setup_logging():
    """Configurar logging para testes."""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


# Fixtures para dados de webhook
@pytest.fixture
def webhook_payload_text():
    """Payload de webhook com mensagem de texto."""
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15551234567",
                        "phone_number_id": "123456789"
                    },
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": "5511999999999"
                    }],
                    "messages": [{
                        "from": "5511999999999",
                        "id": "wamid.123456789",
                        "timestamp": "1678888888",
                        "text": {"body": "Olá"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }


@pytest.fixture
def webhook_payload_multiple():
    """Payload com múltiplas mensagens."""
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [
                        {"from": "5511999999999", "id": "1", "timestamp": "1", "text": {"body": "Oi"}, "type": "text"},
                        {"from": "5511888888888", "id": "2", "timestamp": "2", "text": {"body": "Quero pizza"}, "type": "text"}
                    ]
                },
                "field": "messages"
            }]
        }]
    }