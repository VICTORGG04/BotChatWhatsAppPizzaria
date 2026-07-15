import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from config import settings
from models import DadosPedido

logger = logging.getLogger(__name__)


def get_db_connection():
    """Retorna conexão SQLite com row_factory."""
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """Cria tabela de pedidos se não existir."""
    Path(settings.sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)
    
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_do_dia INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                itens_pedido TEXT NOT NULL,
                total_pedido REAL NOT NULL,
                lucro_pedido REAL NOT NULL,
                metodo_pagamento TEXT,
                endereco TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'recebido'
            )
        ''')
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_pedidos_data 
            ON pedidos(DATE(timestamp))
        ''')
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_pedidos_numero_dia 
            ON pedidos(numero_do_dia)
        ''')
        conn.commit()
    
    logger.info("Banco de dados SQLite inicializado")


def obter_proximo_numero_pedido_dia() -> int:
    """Obtém próximo número sequencial do dia."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT MAX(numero_do_dia) FROM pedidos WHERE DATE(timestamp) = DATE('now', 'localtime')"
            )
            ultimo = cursor.fetchone()[0]
            return (ultimo or 0) + 1
    except Exception as e:
        logger.error(f"Erro ao obter número do pedido: {e}")
        return 1


def calcular_lucro_total_dia() -> float:
    """Calcula lucro total do dia atual."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT SUM(lucro_pedido) FROM pedidos WHERE DATE(timestamp) = DATE('now', 'localtime')"
            )
            total = cursor.fetchone()[0]
            return float(total or 0)
    except Exception as e:
        logger.error(f"Erro ao calcular lucro do dia: {e}")
        return 0.0


def registrar_pedido_sqlite(dados: DadosPedido) -> bool:
    """Salva pedido no SQLite."""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO pedidos 
                (numero_do_dia, timestamp, itens_pedido, total_pedido, lucro_pedido, 
                 metodo_pagamento, endereco, observacoes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados.numero_do_dia,
                dados.timestamp.isoformat(),
                json.dumps([item.model_dump() for item in dados.itens], default=str),
                dados.total,
                dados.lucro,
                dados.pagamento.value,
                dados.endereco,
                dados.observacoes,
                dados.status.value
            ))
            conn.commit()
        logger.info(f"Pedido #{dados.numero_do_dia} salvo no SQLite")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no SQLite: {e}")
        return False


def buscar_pedidos_hoje() -> list:
    """Busca todos os pedidos de hoje."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM pedidos WHERE DATE(timestamp) = DATE('now', 'localtime') ORDER BY numero_do_dia"
            )
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erro ao buscar pedidos: {e}")
        return []


def buscar_pedido_por_numero(numero_do_dia: int) -> dict | None:
    """Busca pedido por número do dia."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM pedidos WHERE numero_do_dia = ? AND DATE(timestamp) = DATE('now', 'localtime')",
                (numero_do_dia,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Erro ao buscar pedido: {e}")
        return None


def atualizar_status_pedido(numero_do_dia: int, status: str) -> bool:
    """Atualiza status do pedido."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE pedidos SET status = ? WHERE numero_do_dia = ? AND DATE(timestamp) = DATE('now', 'localtime')",
                (status, numero_do_dia)
            )
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        return False