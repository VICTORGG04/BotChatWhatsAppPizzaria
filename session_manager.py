import json
import logging
from typing import Optional
from redis import Redis
from redis.exceptions import RedisError

from config import settings
from models import SessaoCliente

logger = logging.getLogger(__name__)


class SessionManager:
    """Gerenciador de sessões com Redis."""
    
    SESSION_PREFIX = "pizzaria:session:"
    DEFAULT_TTL = 1800  # 30 minutos
    
    def __init__(self):
        self._redis: Optional[Redis] = None
        self._connect()
    
    def _connect(self) -> None:
        try:
            self._redis = Redis.from_url(
                settings.redis_connection_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self._redis.ping()
            logger.info("Redis conectado com sucesso")
        except RedisError as e:
            logger.error(f"Falha ao conectar Redis: {e}")
            self._redis = None
    
    def _key(self, phone: str) -> str:
        return f"{self.SESSION_PREFIX}{phone}"
    
    def get(self, phone: str) -> SessaoCliente:
        """Recupera sessão ou cria nova."""
        if not self._redis:
            return SessaoCliente()
        
        try:
            data = self._redis.get(self._key(phone))
            if data:
                session_dict = json.loads(data)
                return SessaoCliente(**session_dict)
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao ler sessão: {e}")
        
        return SessaoCliente()
    
    def save(self, phone: str, session: SessaoCliente, ttl: int = None) -> bool:
        """Salva sessão com TTL."""
        if not self._redis:
            return False
        
        try:
            session_data = session.model_dump(mode="json")
            self._redis.setex(
                self._key(phone),
                ttl or settings.session_ttl_seconds,
                json.dumps(session_data, default=str)
            )
            return True
        except RedisError as e:
            logger.error(f"Erro ao salvar sessão: {e}")
            return False
    
    def delete(self, phone: str) -> bool:
        """Remove sessão."""
        if not self._redis:
            return False
        
        try:
            self._redis.delete(self._key(phone))
            return True
        except RedisError as e:
            logger.error(f"Erro ao deletar sessão: {e}")
            return False
    
    def extend(self, phone: str, ttl: int = None) -> bool:
        """Estende TTL da sessão."""
        if not self._redis:
            return False
        
        try:
            return self._redis.expire(self._key(phone), ttl or settings.session_ttl_seconds)
        except RedisError as e:
            logger.error(f"Erro ao estender sessão: {e}")
            return False
    
    def health_check(self) -> bool:
        """Verifica saúde do Redis."""
        try:
            return self._redis is not None and self._redis.ping()
        except RedisError:
            return False


session_manager = SessionManager()