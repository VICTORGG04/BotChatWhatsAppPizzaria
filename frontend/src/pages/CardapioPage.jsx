import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { api } from '../api';
import PizzaCard from '../components/PizzaCard';
import BebidaCard from '../components/BebidaCard';
import ComboCard from '../components/ComboCard';
import Cart from '../components/Cart';
import AuthModal from '../components/AuthModal';
import LojaInfo from '../components/LojaInfo';

const TABS = [
  { id: 'tradicionais', label: '🍕 Tradicionais', desc: 'Todas as pizzas tradicionais acompanham molho de tomate artesanal, muçarela e orégano.' },
  { id: 'especiais', label: '👑 Especiais', desc: 'Criações exclusivas com ingredientes selecionados.' },
  { id: 'doces', label: '🍫 Doces', desc: 'A sobremesa ideal em formato de pizza.' },
  { id: 'bebidas', label: '🥤 Bebidas', desc: '' },
  { id: 'combos', label: '🔥 Combos', desc: '' },
  { id: 'loja', label: '📍 Loja', desc: '' },
];

export default function CardapioPage() {
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('tradicionais');
  const [cartOpen, setCartOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState(null);
  const [lojaStatus, setLojaStatus] = useState(null);
  const { user } = useAuth();
  const { totalItems } = useCart();

  useEffect(() => {
    api.cardapio().then(setData).catch(e => showToast(e.message, 'error'));
    api.lojaStatus().then(setLojaStatus).catch(() => {});
  }, []);

  // Poll loja status every 60s
  useEffect(() => {
    const iv = setInterval(() => api.lojaStatus().then(setLojaStatus).catch(() => {}), 60000);
    return () => clearInterval(iv);
  }, []);

  const showToast = (msg, type) => {
    setToastMsg({ msg, type });
    setTimeout(() => setToastMsg(null), 3000);
  };

  const saboresPorCategoria = useMemo(() => {
    if (!data) return { tradicional: [], especial: [], doce: [] };
    const map = { tradicional: [], especial: [], doce: [] };
    for (const [chave, sabor] of Object.entries(data.sabores)) {
      const cat = sabor.categoria && map[sabor.categoria] ? sabor.categoria : 'tradicional';
      map[cat].push({ chave, ...sabor });
    }
    return map;
  }, [data]);

  return (
    <div>
      <div className="header">
        <div className="header-row">
          <h1>🍕 PayPizzas</h1>
          <button className="auth-btn" onClick={() => setAuthOpen(true)}>
            {user ? `👤 ${user.nome || user.email}` : '👤 Entrar'}
          </button>
        </div>
        <p className="sub">Monte seu pedido e envie pelo WhatsApp</p>
        <div className={`loja-status ${lojaStatus?.aberta ? 'aberta' : 'fechada'}`}>
          <span className="dot"></span>
          <span>{lojaStatus?.aberta ? 'Loja Aberta' : 'Loja Fechada'}</span>
        </div>
      </div>

      <div className="container">
        <div className="tabs">
          {TABS.map(t => (
            <button key={t.id} className={`tab ${activeTab === t.id ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}>{t.label}</button>
          ))}
        </div>

        {TABS.filter(t => t.id !== 'loja' && t.id !== 'bebidas' && t.id !== 'combos').map(t => (
          <div key={t.id} className={`tab-content ${activeTab === t.id ? 'active' : ''}`}>
            {t.desc && <p className="cat-desc">{t.desc}</p>}
            {saboresPorCategoria[t.id]?.map(s => (
              <PizzaCard key={s.chave} sabor={s} adicionais={data?.adicionais || []}
                onToast={showToast} />
            ))}
            {saboresPorCategoria[t.id]?.length > 0 && t.id !== 'doces' && (
              <button className="meio-btn" onClick={() => setActiveTab('meio-modal')}>Montar Pizza Meio a Meio</button>
            )}
          </div>
        ))}

        <div className={`tab-content ${activeTab === 'bebidas' ? 'active' : ''}`}>
          {data?.bebidas?.map(b => <BebidaCard key={b.chave} item={b} />)}
        </div>

        <div className={`tab-content ${activeTab === 'combos' ? 'active' : ''}`}>
          <p className="cat-desc">Escolha seu combo e personalize os sabores das pizzas.</p>
          {COMBOS_LIST.map(c => (
            <ComboCard key={c.chave} combo={c} sabores={data?.sabores || {}}
              onToast={showToast} />
          ))}
        </div>

        <div className={`tab-content ${activeTab === 'loja' ? 'active' : ''}`}>
          <LojaInfo />
        </div>

        {/* Meio a Meio Modal */}
        {activeTab === 'meio-modal' && (
          <MeioModal sabores={data?.sabores || {}} onClose={() => setActiveTab('tradicionais')} onToast={showToast} />
        )}
      </div>

      <button className={`cart-fab ${totalItems > 0 ? 'show' : ''}`} onClick={() => setCartOpen(true)}>
        Carrinho <span className="badge">{totalItems}</span>
      </button>

      <Cart open={cartOpen} onClose={() => setCartOpen(false)} onToast={showToast} cardapioData={data} />
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} onToast={showToast} />

      {toastMsg && <div className={`toast ${toastMsg.type}`}>{toastMsg.msg}</div>}
    </div>
  );
}

const COMBOS_LIST = [
  { chave: 'combo_familia', nome: 'Combo Família', descricao: '2 pizzas G + 1 Coca-Cola 2L + 1 borda recheada', preco: 139.90, economia: 10.10, icone: '👨‍👩‍👧‍👦', qtdPizzas: 2, tamanho: 'G' },
  { chave: 'combo_casal', nome: 'Combo Casal', descricao: '1 pizza G + 1 suco + 1 borda recheada', preco: 74.90, economia: 6.10, icone: '💑', qtdPizzas: 1, tamanho: 'G' },
  { chave: 'combo_festa', nome: 'Combo Festa', descricao: '4 pizzas M + 2 Coca 2L + 2 bordas', preco: 199.90, economia: 20.10, icone: '🎉', qtdPizzas: 4, tamanho: 'M' },
  { chave: 'promo_semana', nome: 'Promo Semana', descricao: 'Pizza G + borda grátis + 1 Coca lata', preco: 72.90, economia: 6.10, icone: '🔥', qtdPizzas: 1, tamanho: 'G' },
  { chave: 'combo_kids', nome: 'Combo Kids', descricao: 'Pizza M + suco + brinde', preco: 52.90, economia: 5.10, icone: '🧒', qtdPizzas: 1, tamanho: 'M' },
  { chave: 'duas_pizzas_g', nome: '2 Pizzas G', descricao: '2 pizzas G + 1 Coca-Cola 2L', preco: 129.90, economia: 12.10, icone: '🍕🍕', qtdPizzas: 2, tamanho: 'G' },
];

function getPreco(sabor, tam) {
  return sabor?.tamanhos?.[tam]?.preco || sabor?.tamanhos?.[Object.keys(sabor.tamanhos || {})[0]]?.preco || 0;
}

function getNome(sabor) { return sabor?.nome_formatado || sabor?.nome || ''; }

function MeioModal({ sabores, onClose, onToast }) {
  const [s1, setS1] = useState('');
  const [s2, setS2] = useState('');
  const [tam, setTam] = useState('M');
  const { updateQty } = useCart();
  const saboresList = Object.values(sabores);
  const tamanhos = ['M', 'G', 'GG'];

  const p1 = getPreco(sabores[s1], tam);
  const p2 = getPreco(sabores[s2], tam);
  const preco = Math.max(p1, p2);
  const nome1 = getNome(sabores[s1]);
  const nome2 = getNome(sabores[s2]);

  const add = () => {
    if (!s1 || !s2 || s1 === s2) { onToast('Selecione 2 sabores diferentes', 'error'); return; }
    const key = `meio:${s1}+${s2}-${tam}`;
    updateQty(key, 1);
    onToast('Meio a meio adicionado!', 'success');
    onClose();
  };

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()}>
        <h2>Montar Meio a Meio <button onClick={onClose}>&times;</button></h2>
        <div className="modal-section">
          <label>Sabor 1</label>
          <select value={s1} onChange={e => setS1(e.target.value)}>
            <option value="">Selecione...</option>
            {saboresList.map(s => <option key={s.nome} value={s.nome}>{getNome(s)}</option>)}
          </select>
        </div>
        <div className="modal-section">
          <label>Sabor 2</label>
          <select value={s2} onChange={e => setS2(e.target.value)}>
            <option value="">Selecione...</option>
            {saboresList.map(s => <option key={s.nome} value={s.nome}>{getNome(s)}</option>)}
          </select>
        </div>
        <div className="modal-section">
          <label>Tamanho</label>
          <select value={tam} onChange={e => setTam(e.target.value)}>
            {tamanhos.filter(t => sabores[s1]?.tamanhos?.[t] || sabores[s2]?.tamanhos?.[t]).map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="modal-preview">
          <div className="mp-nome">{s1 && s2 ? `1/2 ${nome1} + 1/2 ${nome2} (${tam})` : 'Selecione 2 sabores'}</div>
          <div className="mp-preco">{s1 && s2 ? `R$ ${preco.toFixed(2)}` : 'R$ 0,00'}</div>
        </div>
        <button className="modal-add" onClick={add}>Adicionar ao Carrinho</button>
      </div>
    </div>
  );
}
