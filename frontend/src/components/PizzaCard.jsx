import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

export default function PizzaCard({ sabor, adicionais, onToast }) {
  const [custOpen, setCustOpen] = useState(false);
  const { cart, customNotes, updateQty, setNote } = useCart();
  const { user } = useAuth();
  const [favs, setFavs] = useState([]);

  React.useEffect(() => {
    if (user) api.favoritos.listar().then(d => setFavs(d.favoritos || [])).catch(() => {});
  }, [user]);

  const chave = sabor.chave || sabor.nome;
  const isFav = favs.some(f => f.item_key === sabor.nome && f.tipo === 'sabor');

  const toggleFav = async () => {
    if (!user) { onToast('Faça login para favoritar', 'error'); return; }
    try {
      if (isFav) {
        const f = favs.find(f => f.item_key === sabor.nome && f.tipo === 'sabor');
        await api.favoritos.remover(f.id);
        setFavs(prev => prev.filter(x => x.id !== f.id));
      } else {
        const d = await api.favoritos.adicionar({ tipo: 'sabor', item_key: sabor.nome, nome: sabor.nome_formatado || sabor.nome });
        setFavs(prev => [...prev, d.favorito]);
      }
    } catch (e) { onToast(e.message, 'error'); }
  };

  return (
    <div className="pizza-card">
      <div className="pizza-header">
        <span>{sabor.nome_formatado || sabor.nome}</span>
        <button className="fav-star" onClick={toggleFav}>{isFav ? '⭐' : '☆'}</button>
      </div>
      <div className="pizza-desc">{sabor.tamanhos?.[Object.keys(sabor.tamanhos || {})[0]]?.descricao || ''}</div>
      {Object.entries(sabor.tamanhos || {}).map(([tam, info]) => {
        const k = `sabor:${chave}-${tam}`;
        return (
          <div key={tam} className="pizza-size">
            <span className="ps-label">{tam}</span>
            <span className="ps-preco">R$ {info.preco.toFixed(2)}</span>
            <div className="ps-qty">
              <button className="qty-minus" onClick={() => updateQty(k, -1)}>&minus;</button>
              <span className="qty-val">{cart[k] || 0}</span>
              <button className="qty-plus" onClick={() => updateQty(k, 1)}>+</button>
            </div>
          </div>
        );
      })}
      <div className="cust-toggle" onClick={() => setCustOpen(!custOpen)}>
        <span>Customizar</span>
        <span className={`cust-arrow ${custOpen ? 'open' : ''}`}>&#9660;</span>
      </div>
      <div className={`cust-panel ${custOpen ? 'open' : ''}`}>
        <div className="cust-remover">
          <label>Remover ingredientes:</label>
          <input className="cust-input" placeholder="Ex: Sem cebola, sem azeitona" maxLength="80"
            value={customNotes[chave] || ''}
            onChange={e => setNote(chave, e.target.value)} />
        </div>
        <div className="cust-adicionais">
          {adicionais.map(ad => {
            const ak = `adicional:${ad.chave}`;
            return (
              <div key={ad.chave} className="cust-adi-item">
                <span className="cust-adi-nome">{ad.nome}</span>
                {ad.preco > 0 ? <span className="cust-adi-preco">+R$ {ad.preco.toFixed(2)}</span>
                  : <span className="cust-adi-gratis">Grátis</span>}
                <div className="ps-qty">
                  <button className="qty-minus" onClick={() => updateQty(ak, -1)}>&minus;</button>
                  <span className="qty-val">{cart[ak] || 0}</span>
                  <button className="qty-plus" onClick={() => updateQty(ak, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
