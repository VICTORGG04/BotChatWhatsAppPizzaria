import React from 'react';

const LOJA = {
  endereco: 'Rua das Pizzas, 123 - Centro',
  telefone: '(11) 99999-9999',
  horario: '18:00 às 00:00 - Todos os dias',
  bairros: ['Centro', 'Jardim América', 'Vila Nova', 'Santa Monica', 'Bela Vista'],
  taxa_entrega: 5.00,
  taxa_gratis_acima: 50.00,
  tempo_medio: '45 a 60 minutos',
  pedido_minimo: 25.00,
};

export default function LojaInfo() {
  const l = LOJA;
  return (
    <div>
      <div className="loja-destaque">
        <div className="ld-val">R$ {l.taxa_entrega.toFixed(2).replace('.', ',')}</div>
        <div className="ld-label">Taxa de entrega (grátis acima de R$ {l.taxa_gratis_acima.toFixed(2).replace('.', ',')})</div>
      </div>
      <div className="loja-destaque">
        <div className="ld-val">R$ {l.pedido_minimo.toFixed(2).replace('.', ',')}</div>
        <div className="ld-label">Pedido mínimo</div>
      </div>
      <div className="loja-destaque">
        <div className="ld-val">{l.tempo_medio}</div>
        <div className="ld-label">Tempo médio de entrega</div>
      </div>
      <div className="loja-card">
        <h3>Localização</h3>
        <div className="loja-row">
          <span className="loja-ico">📍</span>
          <span>{l.endereco}</span>
        </div>
      </div>
      <div className="loja-card">
        <h3>Contato</h3>
        <div className="loja-row">
          <span className="loja-ico">📞</span>
          <span>{l.telefone}</span>
        </div>
      </div>
      <div className="loja-card">
        <h3>Horário</h3>
        <div className="loja-row">
          <span className="loja-ico">🕐</span>
          <span>{l.horario}</span>
        </div>
      </div>
      <div className="loja-card">
        <h3>Área de Entrega</h3>
        <div className="loja-row">
          <span className="loja-ico">🚚</span>
          <div className="loja-bairros">
            {l.bairros.map((b, i) => <span key={i}>{b}</span>)}
          </div>
        </div>
      </div>
    </div>
  );
}
