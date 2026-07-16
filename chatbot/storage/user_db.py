import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from models import User, EnderecoUsuario, FavoritoUsuario

DB_PATH = Path("pizzaria.db")


def _get_conn():
    return sqlite3.connect(str(DB_PATH))


def _init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome TEXT DEFAULT '',
            telefone TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS enderecos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endereco TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            item_key TEXT NOT NULL,
            nome TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );
        CREATE INDEX IF NOT EXISTS idx_enderecos_user ON enderecos(user_id);
        CREATE INDEX IF NOT EXISTS idx_favoritos_user ON favoritos(user_id);
    """)
    conn.commit()
    conn.close()


def _hash_senha(senha: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((salt + senha).encode()).hexdigest()}"


def _verificar_senha(senha: str, hash_str: str) -> bool:
    salt, h = hash_str.split(":", 1)
    return h == hashlib.sha256((salt + senha).encode()).hexdigest()


def criar_usuario(email: str, senha: str, nome: str = "") -> User:
    _init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("INSERT INTO usuarios (email, senha_hash, nome) VALUES (?, ?, ?)",
                          (email.lower(), _hash_senha(senha), nome))
        conn.commit()
        user = User(id=cur.lastrowid, email=email, nome=nome, created_at=datetime.now().isoformat())
        return user
    except sqlite3.IntegrityError:
        raise ValueError("Email já cadastrado")
    finally:
        conn.close()


def autenticar_usuario(email: str, senha: str) -> User:
    _init_db()
    conn = _get_conn()
    try:
        row = conn.execute("SELECT id, email, senha_hash, nome, telefone, created_at FROM usuarios WHERE email = ?",
                          (email.lower(),)).fetchone()
        if not row:
            raise ValueError("Email não encontrado")
        if not _verificar_senha(senha, row[2]):
            raise ValueError("Senha incorreta")
        return User(id=row[0], email=row[1], nome=row[3], telefone=row[4], created_at=row[5])
    finally:
        conn.close()


def buscar_usuario_por_id(user_id: int) -> User:
    _init_db()
    conn = _get_conn()
    try:
        row = conn.execute("SELECT id, email, '', nome, telefone, created_at FROM usuarios WHERE id = ?",
                          (user_id,)).fetchone()
        if not row:
            raise ValueError("Usuário não encontrado")
        return User(id=row[0], email=row[1], nome=row[3], telefone=row[4], created_at=row[5])
    finally:
        conn.close()


def atualizar_usuario(user_id: int, nome: str = None, telefone: str = None) -> User:
    _init_db()
    conn = _get_conn()
    try:
        if nome is not None:
            conn.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (nome, user_id))
        if telefone is not None:
            conn.execute("UPDATE usuarios SET telefone = ? WHERE id = ?", (telefone, user_id))
        conn.commit()
        return buscar_usuario_por_id(user_id)
    finally:
        conn.close()


def listar_enderecos(user_id: int) -> list[EnderecoUsuario]:
    _init_db()
    conn = _get_conn()
    try:
        rows = conn.execute("SELECT id, user_id, endereco, created_at FROM enderecos WHERE user_id = ? ORDER BY id",
                          (user_id,)).fetchall()
        return [EnderecoUsuario(id=r[0], user_id=r[1], endereco=r[2], created_at=r[3]) for r in rows]
    finally:
        conn.close()


def adicionar_endereco(user_id: int, endereco: str) -> EnderecoUsuario:
    _init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("INSERT INTO enderecos (user_id, endereco) VALUES (?, ?)", (user_id, endereco))
        conn.commit()
        return EnderecoUsuario(id=cur.lastrowid, user_id=user_id, endereco=endereco, created_at=datetime.now().isoformat())
    finally:
        conn.close()


def remover_endereco(user_id: int, endereco_id: int) -> None:
    _init_db()
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM enderecos WHERE id = ? AND user_id = ?", (endereco_id, user_id))
        conn.commit()
    finally:
        conn.close()


def listar_favoritos(user_id: int) -> list[FavoritoUsuario]:
    _init_db()
    conn = _get_conn()
    try:
        rows = conn.execute("SELECT id, user_id, tipo, item_key, nome, created_at FROM favoritos WHERE user_id = ? ORDER BY id",
                          (user_id,)).fetchall()
        return [FavoritoUsuario(id=r[0], user_id=r[1], tipo=r[2], item_key=r[3], nome=r[4], created_at=r[5]) for r in rows]
    finally:
        conn.close()


def adicionar_favorito(user_id: int, tipo: str, item_key: str, nome: str = "") -> FavoritoUsuario:
    _init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("INSERT INTO favoritos (user_id, tipo, item_key, nome) VALUES (?, ?, ?, ?)",
                          (user_id, tipo, item_key, nome))
        conn.commit()
        return FavoritoUsuario(id=cur.lastrowid, user_id=user_id, tipo=tipo, item_key=item_key, nome=nome,
                              created_at=datetime.now().isoformat())
    finally:
        conn.close()


def remover_favorito(user_id: int, favorito_id: int) -> None:
    _init_db()
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM favoritos WHERE id = ? AND user_id = ?", (favorito_id, user_id))
        conn.commit()
    finally:
        conn.close()
