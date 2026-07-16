import React from 'react';
import { useCart } from '../contexts/CartContext';

export default function BebidaCard({ item }) {
  const { cart, updateQty } = useCart();
  const k = `bebida:${item.chave}`;
  return (
    <div className="simple-card">
      <div className="sc-info">
        <div className="sc-nome">{item.nome}</div>
        {item.preco > 0 ? <div className="sc-preco">R$ {item.preco.toFixed(2)}</div>
          : <div className="sc-preco sc-gratis">Grátis</div>}
      </div>
      <div className="sc-qty">
        <button className="qty-minus" onClick={() => updateQty(k, -1)}>&minus;</button>
        <span className="qty-val">{cart[k] || 0}</span>
        <button className="qty-plus" onClick={() => updateQty(k, 1)}>+</button>
      </div>
    </div>
  );
}
