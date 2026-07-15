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
        .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #e67e22; color: white; }
        .btn-danger { background: #e74c3c; color: white; }

        .pix-section { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 24px; display: none; }
        .pix-section.open { display: block; }
        .pix-grid { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
        .pix-qr { text-align: center; }
        .pix-qr img { width: 200px; height: 200px; border: 2px solid #eee; border-radius: 12px; }
        .pix-info { flex: 1; min-width: 250px; }
        .pix-info h3 { color: #e74c3c; margin-bottom: 8px; }
        .pix-key { background: #f8f8f8; padding: 10px 14px; border-radius: 8px; font-family: monospace; font-size: 14px; word-break: break-all; margin: 8px 0; border: 1px solid #eee; }
        .pix-amount { display: flex; gap: 8px; align-items: center; margin: 12px 0; flex-wrap: wrap; }
        .pix-amount input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; width: 150px; }
        .btn-copy { background: #f0f0f0; border: 1px solid #ddd; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
        .btn-copy:hover { background: #e0e0e0; }
        .copied-msg { color: #27ae60; font-size: 13px; display: none; margin-left: 8px; }
        .toggle-pix { background: none; border: 1px dashed #ccc; color: #888; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; }
        .toggle-pix:hover { border-color: #e67e22; color: #e67e22; }

        .orders { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
        .orders h2 { padding: 16px 20px; background: #fafafa; border-bottom: 1px solid #eee; font-size: 16px; display: flex; align-items: center; justify-content: space-between; }
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
        .pix-badge { background: #e67e22; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 4px; }
        .order-price { font-weight: bold; color: #27ae60; font-size: 16px; min-width: 80px; text-align: right; }
        .order-actions { display: flex; gap: 6px; align-items: center; }
        .order-pix-btn { background: none; border: 1px solid #e67e22; color: #e67e22; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
        .order-pix-btn:hover { background: #e67e22; color: white; }
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        .empty p { font-size: 18px; margin-bottom: 8px; }
        .badge { background: #e74c3c; color: white; border-radius: 50%; padding: 2px 8px; font-size: 12px; margin-left: 6px; }
        @media (max-width: 600px) {
            .order-item { flex-direction: column; align-items: flex-start; }
            .order-price { text-align: left; }
            .pix-grid { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PyPizzas</h1>
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
            <a href="/admin/exportar-excel" class="btn btn-success"> Exportar Excel</a>
            <button class="btn btn-warning" onclick="togglePix()"> QR Code PIX</button>
            <button class="btn btn-primary" onclick="location.reload()"> Atualizar</button>
        </div>

        <div class="pix-section" id="pix-section">
            <h3 style="margin-bottom:16px;color:#e67e22;">Pagamento PIX</h3>
            <div class="pix-grid">
                <div class="pix-qr">
                    <img id="pix-img" src="/pix/qrcode" alt="QR Code PIX">
                    <p style="font-size:12px;color:#999;margin-top:8px;">QR Code atualizado automaticamente</p>
                </div>
                <div class="pix-info">
                    <h3>Pague com PIX</h3>
                    <p style="font-size:14px;color:#555;margin-bottom:8px;">Escaneie o QR Code ao lado ou use a chave abaixo:</p>
                    <div class="pix-key" id="pix-key-text">124.320.804-08</div>
                    <button class="btn-copy" onclick="copyPixKey()"> Copiar Chave</button>
                    <span class="copied-msg" id="copied-msg">Copiado!</span>
                    <div class="pix-amount">
                        <label>Valor (opcional):</label>
                        <input type="number" id="pix-amount-input" step="0.01" min="0" placeholder="Ex: 45,90" oninput="updatePixQr()">
                        <span style="font-size:13px;color:#999;">R$</span>
                    </div>
                    <details style="margin-top:12px;">
                        <summary style="cursor:pointer;font-size:13px;color:#888;">Código copia e cola (avançado)</summary>
                        <textarea id="pix-brcode" readonly style="width:100%;height:60px;margin-top:8px;padding:8px;font-size:11px;font-family:monospace;border:1px solid #ddd;border-radius:6px;background:#fafafa;"></textarea>
                    </details>
                </div>
            </div>
        </div>

        <div class="orders">
            <h2>
                <span>Pedidos do Dia <span class="badge" id="order-count">0</span></span>
                <button class="toggle-pix" onclick="showPixForSelected()"> Gerar PIX p/ Pedido</button>
            </h2>
            <div id="orders-list"></div>
        </div>
    </div>

    <script>
        let currentOrders = [];

        function togglePix() {
            const section = document.getElementById('pix-section');
            section.classList.toggle('open');
            if (section.classList.contains('open')) updatePixQr();
        }

        function updatePixQr() {
            const amount = document.getElementById('pix-amount-input').value;
            const baseUrl = window.location.origin;
            let url = baseUrl + '/pix/qrcode';
            if (amount && parseFloat(amount) > 0) url += '?amount=' + parseFloat(amount);
            document.getElementById('pix-img').src = url + '&t=' + Date.now();

            fetch(url + '&format=brcode&t=' + Date.now())
                .then(r => r.text())
                .then(t => document.getElementById('pix-brcode').value = t)
                .catch(() => {});
        }

        function copyPixKey() {
            const key = document.getElementById('pix-key-text').textContent;
            navigator.clipboard.writeText(key).then(() => {
                const msg = document.getElementById('copied-msg');
                msg.style.display = 'inline';
                setTimeout(() => msg.style.display = 'none', 2000);
            });
        }

        function showPixForSelected() {
            togglePix();
            if (currentOrders.length > 0) {
                const total = currentOrders.reduce((s, p) => s + (p.total_pedido || 0), 0);
                document.getElementById('pix-amount-input').value = total.toFixed(2);
                updatePixQr();
            }
        }

        function generatePixForOrder(orderNum, total) {
            togglePix();
            document.getElementById('pix-amount-input').value = total.toFixed(2);
            updatePixQr();
            document.getElementById('pix-section').scrollIntoView({ behavior: 'smooth' });
        }

        const STATUS_MAP = {
            'recebido': 'Recebido', 'preparando': 'Preparando',
            'saiu': 'Saiu p/ Entrega', 'entregue': 'Entregue', 'cancelado': 'Cancelado'
        };

        async function loadData() {
            try {
                const [pedidosRes, statsRes, healthRes] = await Promise.all([
                    fetch('/admin/pedidos'), fetch('/admin/stats'), fetch('/health')
                ]);
                const pedidos = await pedidosRes.json();
                const stats = await statsRes.json();
                const health = await healthRes.json();
                currentOrders = pedidos.pedidos || [];

                document.getElementById('total-orders').textContent = pedidos.total;
                document.getElementById('total-revenue').textContent = `R$ ${(stats.lucro_dia || 0).toFixed(2)}`;
                document.getElementById('total-profit').textContent = `R$ ${(stats.lucro_dia || 0).toFixed(2)}`;
                document.getElementById('order-count').textContent = pedidos.total;

                const statusEl = document.getElementById('status-online');
                statusEl.textContent = health.status === 'healthy' ? ' Online' : ' Offline';
                statusEl.style.color = health.status === 'healthy' ? '#27ae60' : '#e74c3c';

                const list = document.getElementById('orders-list');
                if (!currentOrders.length) {
                    list.innerHTML = '<div class="empty"><p> Nenhum pedido hoje</p><span>Os pedidos aparecerão aqui automaticamente</span></div>';
                    return;
                }

                list.innerHTML = currentOrders.map(p => {
                    let itens = p.itens_pedido || '[]';
                    try { itens = JSON.parse(itens).map(i => `${i.quantidade}x ${i.sabor}${i.tamanho ? ' ('+i.tamanho+')' : ''}`).join(', '); } catch(e) {}
                    const hora = p.timestamp ? p.timestamp.slice(11, 16) : '';
                    const isPix = (p.metodo_pagamento || '').toLowerCase() === 'pix';
                    return `
                        <div class="order-item">
                            <div class="order-num">#${p.numero_do_dia}</div>
                            <div class="order-info">
                                <div class="items">${itens}</div>
                                <div class="meta">${hora} &middot; ${p.metodo_pagamento || ''}${isPix ? '<span class="pix-badge">PIX</span>' : ''} &middot; ${p.endereco || 'Sem endereço'}</div>
                            </div>
                            <span class="order-status status-${p.status || 'recebido'}">${STATUS_MAP[p.status] || p.status}</span>
                            <div class="order-actions">
                                <div class="order-price">R$ ${(p.total_pedido || 0).toFixed(2)}</div>
                                ${isPix ? `<button class="order-pix-btn" onclick="generatePixForOrder(${p.numero_do_dia}, ${p.total_pedido || 0})"> PIX</button>` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
            } catch(e) {
                document.getElementById('orders-list').innerHTML = '<div class="empty"><p> Erro ao carregar</p><span>Tente novamente</span></div>';
            }
        }

        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>"""
