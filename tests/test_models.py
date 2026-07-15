import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from models import (
    SessaoCliente, EstadoConversa, TamanhoPizza, MetodoPagamento,
    StatusPedido, ItemPedido, DadosPedido, ItemCardapio, SaborCardapio,
    Cardapio, WebhookMessage, WebhookPayload
)
from config import Settings


class TestModels:
    """Testes para modelos Pydantic."""

    def test_item_pedido_subtotal(self):
        item = ItemPedido(
            sabor="Calabresa",
            tamanho=TamanhoPizza.G,
            quantidade=2,
            preco=52.00,
            custo=19.50
        )
        assert item.subtotal == 104.00
        assert item.lucro == 65.00
        assert item.chave_unica == "calabresa g"

    def test_tamanho_pizza_enum(self):
        assert TamanhoPizza.M.value == "M"
        assert TamanhoPizza.G.value == "G"
        assert TamanhoPizza.GG.value == "GG"

    def test_metodo_pagamento_enum(self):
        assert MetodoPagamento.ESPECIE.value == "Espécie"
        assert MetodoPagamento.CARTAO.value == "Cartão"
        assert MetodoPagamento.PIX.value == "Pix"

    def test_status_pedido_enum(self):
        assert StatusPedido.RECEBIDO.value == "recebido"
        assert StatusPedido.PREPARANDO.value == "preparando"
        assert StatusPedido.ENTREGUE.value == "entregue"

    def test_sessao_cliente_defaults(self):
        sessao = SessaoCliente()
        assert sessao.state == "initial"
        assert sessao.current_order == {}
        assert sessao.order_total == 0.0
        assert sessao.chat_history == []

    def test_dados_pedido_creation(self):
        itens = [
            ItemPedido(sabor="Margherita", tamanho=TamanhoPizza.M, quantidade=1, preco=35.00, custo=12.50)
        ]
        pedido = DadosPedido(
            numero_do_dia=1,
            timestamp="2024-01-01T12:00:00",
            itens=itens,
            total=35.00,
            lucro=22.50,
            pagamento=MetodoPagamento.PIX,
            endereco="Rua Teste, 123",
            observacoes=""
        )
        assert pedido.numero_do_dia == 1
        assert len(pedido.itens) == 1
        assert pedido.status == StatusPedido.RECEBIDO

    def test_webhook_message_body_property(self):
        msg = WebhookMessage(
            from_="5511999999999",
            id="wamid.test",
            timestamp="1234567890",
            text={"body": "Olá"},
            type="text"
        )
        assert msg.body == "Olá"

    def test_webhook_payload_get_messages(self):
        payload = WebhookPayload(
            object="whatsapp_business_account",
            entry=[{
                "id": "123",
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "5511999999999",
                            "id": "wamid.test",
                            "timestamp": "1234567890",
                            "text": {"body": "Teste"},
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        )
        messages = payload.get_messages()
        assert len(messages) == 1
        assert messages[0].body == "Teste"


class TestConfig:
    """Testes para configuração."""

    def test_settings_redis_url(self, monkeypatch):
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")
        monkeypatch.setenv("REDIS_PASSWORD", "")
        
        settings = Settings()
        assert "redis://localhost:6379/0" in settings.redis_connection_url

    def test_settings_redis_url_with_password(self, monkeypatch):
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")
        monkeypatch.setenv("REDIS_PASSWORD", "secret123")
        
        settings = Settings()
        assert "redis://:secret123@localhost:6379/0" == settings.redis_connection_url

    def test_is_production_property(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "production")
        settings = Settings()
        assert settings.is_production is True
        
        monkeypatch.setenv("APP_ENV", "development")
        settings = Settings()
        assert settings.is_production is False