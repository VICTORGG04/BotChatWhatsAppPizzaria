from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TamanhoPizza(str, Enum):
    M = "M"
    G = "G"
    GG = "GG"
    NA = "NA"


class MetodoPagamento(str, Enum):
    ESPECIE = "Espécie"
    CARTAO = "Cartão"
    PIX = "Pix"


class StatusPedido(str, Enum):
    RECEBIDO = "recebido"
    PREPARANDO = "preparando"
    SAIU_ENTREGA = "saiu_para_entrega"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class ItemCardapio(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    preco: float
    custo: float
    descricao: str


class ItemPedido(BaseModel):
    sabor: str
    tamanho: TamanhoPizza
    quantidade: int = Field(ge=1)
    preco: float = Field(ge=0)
    
    @property
    def subtotal(self) -> float:
        return self.preco * self.quantidade


class DadosPedido(BaseModel):
    numero_do_dia: int
    timestamp: datetime
    itens: List[ItemPedido]
    total: float = Field(ge=0)
    lucro: float
    pagamento: MetodoPagamento
    endereco: str
    observacoes: str = ""
    status: StatusPedido = StatusPedido.RECEBIDO


class SaborCardapio(BaseModel):
    nome: str
    nome_exibicao: Optional[str] = None
    tamanhos: dict[TamanhoPizza, ItemCardapio]
    categoria: str = "tradicional"
    
    @property
    def nome_formatado(self) -> str:
        return self.nome_exibicao if self.nome_exibicao else self.nome.replace("_", " ").title()


class Cardapio(BaseModel):
    sabores: dict[str, SaborCardapio]
    bebidas: list[dict] = []
    adicionais: list[dict] = []
    
    def get_preco(self, sabor: str, tamanho: TamanhoPizza) -> Optional[float]:
        sabor_norm = sabor.lower().replace(" ", "_")
        if sabor_norm in self.sabores and tamanho in self.sabores[sabor_norm].tamanhos:
            return self.sabores[sabor_norm].tamanhos[tamanho].preco
        return None
    
    def get_custo(self, sabor: str, tamanho: TamanhoPizza) -> Optional[float]:
        sabor_norm = sabor.lower().replace(" ", "_")
        if sabor_norm in self.sabores and tamanho in self.sabores[sabor_norm].tamanhos:
            return self.sabores[sabor_norm].tamanhos[tamanho].custo
        return None
    
    def buscar_sabor(self, query: str) -> Optional[str]:
        query = query.lower().strip()
        for key in self.sabores:
            if query in key:
                return key
        return None


class SessaoCliente(BaseModel):
    state: str = "initial"
    chat_history: List[dict] = Field(default_factory=list)
    current_order: dict = Field(default_factory=dict)
    order_total: float = 0.0
    temp_flavor: Optional[str] = None
    temp_size: Optional[TamanhoPizza] = None
    payment_method: Optional[MetodoPagamento] = None
    change_needed: Optional[str] = None
    address: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


class WebhookMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    text: Optional[dict] = None
    type: str
    
    @property
    def body(self) -> str:
        return self.text.get("body", "") if self.text else ""


class WebhookContact(BaseModel):
    profile: dict
    wa_id: str


class WebhookChange(BaseModel):
    value: dict
    field: str


class WebhookEntry(BaseModel):
    id: str
    changes: List[WebhookChange]


class WebhookPayload(BaseModel):
    object: str
    entry: List[WebhookEntry]
    
    def get_messages(self) -> List[WebhookMessage]:
        messages = []
        for entry in self.entry:
            for change in entry.changes:
                if change.value.get("messages"):
                    for msg_data in change.value["messages"]:
                        messages.append(WebhookMessage(**msg_data))
        return messages


class ResumoConversa(BaseModel):
    cliente: str
    pedido_resumido: str
    valor_total: float
    observacoes: str
    dificuldades: List[str] = Field(default_factory=list)