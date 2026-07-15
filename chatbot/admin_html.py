ADMIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyPizzas - Painel Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 4px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .stat-card h3 { font-size: 13px; text-transform: uppercase; color: #888; margin-bottom: 8px; }
        .stat-card .value { font-size: 28px; font-weight: bold; }
        .stat-card .value.green { color: #27ae60; }
        .stat-card .value.blue { color: #2980b9; }
        .stat-card .value.orange { color: #e67e22; }
        .actions { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #e67e22; color: white; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .orders { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
        .orders h2 { padding: 16px 20px; background: #fafafa; border-bottom: 1px solid #eee; font-size: 16px; }
        .order-item { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
        .order-item:last-child { border-bottom: none; }
        .order-item:hover { background: #fafafa; }
        .order-num { font-weight: bold; font-size: 18px; min-width: 40px; }
        .order-info { flex: 1; }
        .order-info .items { font-size: 14px; color: #555; margin-bottom: 4px; }
        .order-info .meta { font-size: 12px; color: #999; }
        .order-status { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-recebido { background: #ffeaa7; color: #856404; }
        .status-preparando { background: #81ecec; color: #006064; }
        .status-saiu { background: #74b9ff; color: #003366; }
        .status-entregue { background: #55efc4; color: #00695c; }
        .status-cancelado { background: #ff7675; color: #7f0000; }
        .order-price { font-weight: bold; color: #27ae60; font-size: 16px; min-width: 80px; text-align: right; }
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        .empty p { font-size: 18px; margin-bottom: 8px; }
        .badge { background: #e74c3c; color: white; border-radius: 50%; padding: 2px 8px; font-size: 12px; margin-left: 6px; }
        select.status-select { padding: 4px 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; background: white; }
        @media (max-width: 600px) {
            .order-item { flex-direction: column; align-items: flex-start; }
            .order-price { text-align: left; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PyPizzas 🍕</h1>
        <p>Painel de Gerenciamento de Pedidos</p>
    </div>
    <div class="container">
        <div class="stats" id="stats">
            <div class="stat-card"><h3>Pedidos Hoje</h3><div class="value blue" id="total-orders">0</div></div>
            <div class="stat-card"><h3>Faturamento</h3><div class="value green" id="total-revenue">R$ 0,00</div></div>
            <div class="stat-card"><h3>Lucro</h3><div class="value orange" id="total-profit">R$ 0,00</div></div>
            <div class="stat-card"><h3>Status</h3><div class="value" id="status-online">Offline</div></div>
        </div>
        <div class="actions">
            <a href="/admin/exportar-excel" class="btn btn-success">📊 Exportar Excel</a>
            <a href="/pix/qrcode" class="btn btn-warning" target="_blank">💳 QR Code PIX</a>
            <button class="btn btn-primary" onclick="location.reload()">🔄 Atualizar</button>
        </div>
        <div class="orders">
            <h2>Pedidos do Dia <span class="badge" id="order-count">0</span></h2>
            <div id="orders-list"></div>
        </div>
    </div>
    <script>
        const STATUS_MAP = {
            'recebido': 'Recebido',
            'preparando': 'Preparando',
            'saiu': 'Saiu p/ Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        };

        async function loadData() {
            try {
                const [pedidosRes, statsRes, healthRes] = await Promise.all([
                    fetch('/admin/pedidos'),
                    fetch('/admin/stats'),
                    fetch('/health')
                ]);
                const pedidos = await pedidosRes.json();
                const stats = await statsRes.json();
                const health = await healthRes.json();

                document.getElementById('total-orders').textContent = pedidos.total;
                document.getElementById('total-revenue').textContent = `R$ ${(stats.lucro_dia || 0).toFixed(2)}`;
                document.getElementById('total-profit').textContent = `R$ ${(stats.lucro_dia || 0).toFixed(2)}`;
                document.getElementById('order-count').textContent = pedidos.total;

                const statusEl = document.getElementById('status-online');
                statusEl.textContent = health.status === 'healthy' ? '🟢 Online' : '🔴 Offline';
                statusEl.style.color = health.status === 'healthy' ? '#27ae60' : '#e74c3c';

                const list = document.getElementById('orders-list');
                if (pedidos.pedidos.length === 0) {
                    list.innerHTML = '<div class="empty"><p>📭 Nenhum pedido hoje</p><span>Os pedidos aparecerão aqui automaticamente</span></div>';
                    return;
                }

                list.innerHTML = pedidos.pedidos.map(p => {
                    let itens = p.itens_pedido || '[]';
                    try { itens = JSON.parse(itens).map(i => `${i.quantidade}x ${i.sabor}${i.tamanho ? ' ('+i.tamanho+')' : ''}`).join(', '); } catch(e) {}
                    const hora = p.timestamp ? p.timestamp.slice(11, 16) : '';
                    const statusClass = `status-${p.status || 'recebido'}`;
                    return `
                        <div class="order-item">
                            <div class="order-num">#${p.numero_do_dia}</div>
                            <div class="order-info">
                                <div class="items">${itens}</div>
                                <div class="meta">${hora} &middot; ${p.metodo_pagamento || ''} &middot; ${p.endereco || 'Sem endereço'}</div>
                            </div>
                            <span class="order-status ${statusClass}">${STATUS_MAP[p.status] || p.status}</span>
                            <div class="order-price">R$ ${(p.total_pedido || 0).toFixed(2)}</div>
                        </div>
                    `;
                }).join('');
            } catch(e) {
                document.getElementById('orders-list').innerHTML = '<div class="empty"><p>❌ Erro ao carregar</p><span>Tente novamente</span></div>';
            }
        }

        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>"""
