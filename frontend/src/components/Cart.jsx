import React, { useState, useMemo } from 'react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

export default function Cart({ open, onClose, onToast, cardapioData }) {
  const sabores = cardapioData?.sabores || {};
  const bebidasList = cardapioData?.bebidas || [];
  const adicionaisList = cardapioData?.adicionais || [];
  const COMBOS = [
    { chave: 'combo_familia', preco: 139.90 },
    { chave: 'combo_casal', preco: 74.90 },
    { chave: 'combo_festa', preco: 199.90 },
    { chave: 'promo_semana', preco: 72.90 },
    { chave: 'combo_kids', preco: 52.90 },
    { chave: 'duas_pizzas_g', preco: 129.90 },
  ];
  const { cart, customNotes, removeItem, clearCart } = useCart();
  const { user } = useAuth();
  const [nome, setNome] = useState('');
  const [endereco, setEndereco] = useState('');
  const [enderecos, setEnderecos] = useState([]);
  const [pagamento, setPagamento] = useState('Especie');
  const [obs, setObs] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (open && user) {
      api.auth.me().then(d => {
        if (d.user?.nome) setNome(d.user.nome);
      }).catch(() => {});
      api.enderecos.listar().then(d => setEnderecos(d.enderecos || [])).catch(() => {});
    }
  }, [open, user]);

  const items = useMemo(() => {
    const result = []; let total = 0;
    for (const [key, qty] of Object.entries(cart)) {
      if (qty <= 0) continue;
      const info = getItemInfo(key, sabores, bebidasList, adicionaisList, COMBOS);
      if (!info) continue;
      const sub = qty * info.preco; total += sub;
      result.push({ key, ...info, qty, sub });
    }
    return { items: result, total };
  }, [cart, sabores, bebidasList, adicionaisList]);

  const finalizar = async () => {
    if (!nome.trim()) { onToast('Digite seu nome', 'error'); return; }
    if (!endereco.trim() && !user) { onToast('Digite o endereço', 'error'); return; }
    if (!endereco.trim() && user) { onToast('Selecione ou digite o endereço', 'error'); return; }

    setLoading(true);
    const itens = [];
    for (const [key, qty] of Object.entries(cart)) {
      if (qty <= 0) continue;
      const info = getItemInfo(key, sabores, bebidasList, adicionaisList, COMBOS);
      if (!info) continue;
      let categoria, sabor, tamanho;
      if (key.startsWith('sabor:')) { const p = key.slice(6).split('-'); categoria = 'sabor'; sabor = p[0]; tamanho = p[1]; }
      else if (key.startsWith('meio:')) { categoria = 'sabor'; sabor = key.slice(5); tamanho = ''; }
      else if (key.startsWith('bebida:')) { categoria = 'bebida'; sabor = key.slice(7); tamanho = ''; }
      else if (key.startsWith('combo:')) { categoria = 'combo'; sabor = key.slice(6); tamanho = ''; }
      else { categoria = 'adicional'; sabor = key.slice(10); tamanho = ''; }
      itens.push({ categoria, sabor, tamanho, quantidade: qty, preco: info.preco });
    }

    let observacoes = obs;
    const pizzaNotes = [];
    for (const [key] of Object.entries(cart)) {
      if (key.startsWith('sabor:')) {
        const saborChave = key.slice(6).split('-')[0];
        if (customNotes[saborChave]) {
          pizzaNotes.push(`${saborChave}: ${customNotes[saborChave]}`);
        }
      }
    }
    if (pizzaNotes.length > 0) {
      observacoes = observacoes ? observacoes + ' | ' + pizzaNotes.join(' | ') : pizzaNotes.join(' | ');
    }

    try {
      const data = await api.criarPedido({ nome: nome.trim(), itens, endereco: endereco.trim(), pagamento, observacoes });
      clearCart();
      window.location.href = data.whatsapp_link;
    } catch (e) {
      onToast(e.message, 'error');
      setLoading(false);
    }
  };

  return (
    <>
      <div className={`cart-overlay ${open ? 'open' : ''}`} onClick={onClose}></div>
      <div className={`cart-panel ${open ? 'open' : ''}`}>
        <div className="cart-header">
          Seu Pedido
          <button onClick={onClose}>&times;</button>
        </div>

        <div id="cartItems">
          {items.items.length === 0 ? (
            <div className="empty-cart"><p>&#x1F6D2;</p><span>Carrinho vazio</span></div>
          ) : (
            items.items.map(it => (
              <div key={it.key} className="cart-item">
                <div className="ci-info">
                  <div className="ci-nome">{it.nome}</div>
                  <div className="ci-cat">{it.cat}</div>
                  <div className="ci-meta">{it.qty}x R$ {it.preco.toFixed(2)}</div>
                  {it.cat === 'Pizza' && customNotes[it.key.slice(6).split('-')[0]] && (
                    <div className="cart-obs">Obs: {customNotes[it.key.slice(6).split('-')[0]]}</div>
                  )}
                </div>
                <span className="ci-preco">R$ {it.sub.toFixed(2)}</span>
                <button className="ci-remove" onClick={() => removeItem(it.key)}>&times;</button>
              </div>
            ))
          )}
        </div>

        {items.items.length > 0 && (
          <>
            <div className="cart-total">
              <span>Total</span>
              <span>R$ {items.total.toFixed(2)}</span>
            </div>

            <div className="checkout-section">
              <h3>Dados para Entrega</h3>
              <div className="form-group">
                <label>Seu Nome</label>
                <input type="text" value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome" maxLength="60" />
              </div>

              {enderecos.length > 0 && (
                <div className="form-group">
                  <label>Endereço Salvo</label>
                  <select className="endereco-select" onChange={e => setEndereco(e.target.value)} defaultValue="">
                    <option value="">Selecione um endereço...</option>
                    {enderecos.map(e => <option key={e.id} value={e.endereco}>{e.endereco}</option>)}
                  </select>
                </div>
              )}

              <div className="form-group">
                <label>Endereço de Entrega</label>
                <input type="text" value={endereco} onChange={e => setEndereco(e.target.value)}
                  placeholder="Rua, número, bairro, referência" />
              </div>

              <div className="form-group">
                <label>Pagamento</label>
                <select value={pagamento} onChange={e => setPagamento(e.target.value)}>
                  <option value="Especie">Espécie (Dinheiro)</option>
                  <option value="Cartao">Cartão (Crédito/Débito)</option>
                  <option value="Pix">PIX</option>
                </select>
              </div>

              <div className="form-group">
                <label>Observações</label>
                <textarea value={obs} onChange={e => setObs(e.target.value)} placeholder="Troco para quanto?"></textarea>
              </div>

              <button className="btn-finalizar" onClick={finalizar} disabled={loading}>
                {loading ? 'Enviando...' : 'Enviar Pedido'}
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}

function getItemInfo(key, sabores, bebidasList, adicionaisList, COMBOS) {
  if (key.startsWith('meio:')) {
    const rest = key.slice(5);
    const parts = rest.split('-');
    const saboresPart = parts[0];
    const tam = parts[1];
    const saboresKeys = saboresPart.split('+');
    let maxPreco = 0;
    for (const sk of saboresKeys) {
      const s = Object.values(sabores).find(x => x.nome_formatado === sk || x.nome === sk);
      if (s?.tamanhos?.[tam]) maxPreco = Math.max(maxPreco, s.tamanhos[tam].preco);
    }
    return { nome: `1/2 ${saboresKeys[0]} + 1/2 ${saboresKeys[1]} (${tam})`, cat: 'Pizza Meio a Meio', preco: maxPreco };
  }
  if (key.startsWith('sabor:')) {
    const p = key.slice(6).split('-');
    const saborNome = p[0];
    const tam = p[1];
    const s = Object.values(sabores).find(x => x.nome_formatado === saborNome || x.nome === saborNome);
    const preco = s?.tamanhos?.[tam]?.preco || 0;
    return { nome: `${saborNome} (${tam})`, cat: 'Pizza', preco };
  }
  if (key.startsWith('bebida:')) {
    const c = key.slice(7);
    const b = bebidasList.find(x => x.chave === c);
    return { nome: b?.nome || c, cat: 'Bebida', preco: b?.preco || 0 };
  }
  if (key.startsWith('combo:')) {
    const c = key.slice(6);
    const combo = COMBOS.find(x => x.chave === c);
    return { nome: c, cat: 'Combo', preco: combo?.preco || 0 };
  }
  if (key.startsWith('adicional:')) {
    const c = key.slice(10);
    const a = adicionaisList.find(x => x.chave === c);
    return { nome: a?.nome || c, cat: 'Adicional', preco: a?.preco || 0 };
  }
  return null;
}
