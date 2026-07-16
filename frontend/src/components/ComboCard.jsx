import React, { useState, useMemo } from 'react';
import { useCart } from '../contexts/CartContext';

export default function ComboCard({ combo, sabores, onToast }) {
  const [showModal, setShowModal] = useState(false);
  const { updateQty } = useCart();
  const { cart } = useCart();
  const chave = combo.chave;
  const k = `combo:${chave}`;
  const q = cart[k] || 0;
  const original = combo.preco + combo.economia;

  const saboresList = Object.entries(sabores).map(([nome, s]) => ({ nome, ...s }));
  const tamanhos = combo.tamanho;
  const tamanhosDisponiveis = useMemo(() => {
    const ts = [];
    for (const s of saboresList) {
      const tams = Object.keys(s.tamanhos || {});
      for (const t of tams) if (!ts.includes(t)) ts.push(t);
    }
    return ts;
  }, [saboresList]);

  return (
    <>
      <div className="combo-card">
        <div className="combo-icon">{combo.icone}</div>
        <div className="combo-info">
          <div className="combo-nome">{combo.nome}</div>
          <div className="combo-desc">{combo.descricao}</div>
          <div className="combo-preco-box">
            <span className="combo-original">R$ {original.toFixed(2)}</span>
            <span className="combo-preco">R$ {combo.preco.toFixed(2)}</span>
            <span className="combo-economia">Economia de R$ {combo.economia.toFixed(2)}</span>
          </div>
        </div>
        <div className="sc-qty">
          <button className="qty-minus" onClick={() => updateQty(k, -1)}>&minus;</button>
          <span className="qty-val">{q}</span>
          <button className="qty-plus" onClick={() => setShowModal(true)}>+</button>
        </div>
      </div>

      {showModal && (
        <ComboModal combo={combo} saboresList={saboresList} tamanhos={tamanhosDisponiveis}
          onConfirm={(chaves) => {
            updateQty(k, 1);
            setShowModal(false);
            onToast(`${combo.nome} adicionado!`, 'success');
          }}
          onClose={() => setShowModal(false)} />
      )}
    </>
  );
}

function ComboModal({ combo, saboresList, tamanhos, onConfirm, onClose }) {
  const [selections, setSelections] = useState(Array(combo.qtdPizzas).fill(''));
  const [tamanho, setTamanho] = useState(tamanhos.includes(combo.tamanho) ? combo.tamanho : tamanhos[0] || 'G');

  const allSelected = selections.every(s => s);
  const totalPreco = selections.reduce((sum, nome) => {
    const s = saboresList.find(x => x.nome === nome);
    if (!s) return sum;
    return sum + (s.tamanhos?.[tamanho]?.preco || 0);
  }, 0);
  const precoFinal = Math.max(combo.preco, totalPreco);

  const setSelection = (idx, val) => {
    setSelections(prev => {
      const n = [...prev];
      n[idx] = val;
      return n;
    });
  };

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()}>
        <h2>{combo.icone} {combo.nome} <button onClick={onClose}>&times;</button></h2>
        <p style={{ fontSize: 12, color: '#888', marginBottom: 10 }}>{combo.descricao}</p>

        <div className="modal-section">
          <label>Tamanho das pizzas</label>
          <select value={tamanho} onChange={e => setTamanho(e.target.value)}>
            {tamanhos.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {Array.from({ length: combo.qtdPizzas }).map((_, i) => (
          <div key={i} className="modal-section">
            <label>Pizza {i + 1}{selections[i] ? `: R$ ${(saboresList.find(s => s.nome === selections[i])?.tamanhos?.[tamanho]?.preco || 0).toFixed(2)}` : ''}</label>
            <select value={selections[i]} onChange={e => setSelection(i, e.target.value)}>
              <option value="">Selecione o sabor...</option>
              {saboresList.map(s => (
                <option key={s.nome} value={s.nome}
                  disabled={selections.filter((_, idx) => idx !== i).includes(s.nome) && selections[i] !== s.nome}>
                  {s.nome_formatado || s.nome} {s.tamanhos?.[tamanho] ? `(R$ ${s.tamanhos[tamanho].preco.toFixed(2)})` : ''}
                </option>
              ))}
            </select>
          </div>
        ))}

        <div className="modal-preview">
          <div className="mp-nome">{allSelected ? selections.map(s => saboresList.find(x => x.nome === s)?.nome_formatado || s).join(' + ') : 'Selecione os sabores'}</div>
          <div className="mp-preco">R$ {precoFinal.toFixed(2)}</div>
          {totalPreco > combo.preco && <div style={{ fontSize: 10, color: '#e74c3c' }}>Preço ajustado para o maior valor dos sabores</div>}
        </div>

        <button className="modal-add" disabled={!allSelected}
          style={!allSelected ? { opacity: 0.5 } : {}}
          onClick={() => allSelected && onConfirm(selections)}>
          Adicionar ao Carrinho
        </button>
      </div>
    </div>
  );
}
