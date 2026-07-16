import json
from models import TamanhoPizza


def gerar_cardapio_html(empresa_numero: str, cardapio) -> str:
    sabores_por_categoria = {"tradicional": [], "especial": [], "doce": []}
    for chave, sabor in cardapio.sabores.items():
        tamanhos = []
        for tam in [TamanhoPizza.M, TamanhoPizza.G, TamanhoPizza.GG]:
            if tam in sabor.tamanhos:
                item = sabor.tamanhos[tam]
                tamanhos.append({
                    "tamanho": tam.value,
                    "preco": item.preco,
                    "descricao": item.descricao
                })
        entry = {"chave": chave, "nome": sabor.nome_formatado, "descricao": tamanhos[0]["descricao"] if tamanhos else "", "tamanhos": tamanhos}
        cat = sabor.categoria if sabor.categoria in sabores_por_categoria else "tradicional"
        sabores_por_categoria[cat].append(entry)

    loja_info = {
        "endereco": "Rua das Pizzas, 123 - Centro",
        "telefone": "(11) 99999-9999",
        "horario": "18:00 as 00:00 - Todos os dias",
        "bairros": ["Centro", "Jardim America", "Vila Nova", "Santa Monica", "Bela Vista"],
        "taxa_entrega": 5.00,
        "taxa_gratis_acima": 50.00,
        "tempo_medio": "45 a 60 minutos",
        "pedido_minimo": 25.00
    }

    combos = [
        {"nome": "Combo Familia", "descricao": "2 pizzas G + 1 Coca-Cola 2L + 1 borda recheada", "preco": 139.90, "economia": 10.10, "icone": "👨‍👩‍👧‍👦"},
        {"nome": "Combo Casal", "descricao": "1 pizza G + 1 suco + 1 borda recheada", "preco": 74.90, "economia": 6.10, "icone": "💑"},
        {"nome": "Combo Festa", "descricao": "4 pizzas M + 2 Coca 2L + 2 bordas", "preco": 199.90, "economia": 20.10, "icone": "🎉"},
        {"nome": "Promo Semana", "descricao": "Pizza G + borda gratis + 1 Coca lata", "preco": 72.90, "economia": 6.10, "icone": "🔥"},
        {"nome": "Combo Kids", "descricao": "Pizza M + suco + brinde", "preco": 52.90, "economia": 5.10, "icone": "🧒"},
        {"nome": "2 Pizzas G", "descricao": "2 pizzas G + 1 Coca-Cola 2L", "preco": 129.90, "economia": 12.10, "icone": "🍕🍕"},
    ]

    return _HTML_TEMPLATE \
        .replace("__TRADICIONAIS__", json.dumps(sabores_por_categoria["tradicional"], ensure_ascii=False)) \
        .replace("__ESPECIAIS__", json.dumps(sabores_por_categoria["especial"], ensure_ascii=False)) \
        .replace("__DOCES__", json.dumps(sabores_por_categoria["doce"], ensure_ascii=False)) \
        .replace("__BEBIDAS_JSON__", json.dumps(cardapio.bebidas, ensure_ascii=False)) \
        .replace("__ADICIONAIS_JSON__", json.dumps(cardapio.adicionais, ensure_ascii=False)) \
        .replace("__LOJA_INFO_JSON__", json.dumps(loja_info, ensure_ascii=False)) \
        .replace("__COMBOS_JSON__", json.dumps(combos, ensure_ascii=False)) \
        .replace("__WA_NUMERO__", empresa_numero)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>PayPizzas - Cardapio</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f0f23;color:#eee;min-height:100vh;-webkit-font-smoothing:antialiased}
@keyframes grad{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}@keyframes spin{to{transform:rotate(360deg)}}
@keyframes toastIn{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes toastOut{from{opacity:1}to{opacity:0;transform:translateY(-20px)}}
.header{background:linear-gradient(135deg,#e74c3c,#c0392b,#e67e22,#c0392b);background-size:300% 300%;animation:grad 6s ease infinite;padding:14px 12px;text-align:center;position:sticky;top:0;z-index:100}
.header h1{font-size:18px;letter-spacing:1px}.header p{font-size:11px;opacity:.75;margin-top:1px}
.container{max-width:640px;margin:0 auto;padding:8px;padding-bottom:100px}
.tabs{display:flex;gap:3px;margin-bottom:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding-bottom:2px}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;padding:6px 10px;border:none;border-radius:6px;background:#1a1a3e;color:#888;font-size:11px;font-weight:600;cursor:pointer;text-align:center;white-space:nowrap;transition:all .15s}
.tab:hover{background:#2a2a5e;color:#eee}
.tab.active{background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff}
.tab-content{display:none}.tab-content.active{display:block}

.pizza-card{background:linear-gradient(135deg,#1a1a3e,#16213e);border-radius:10px;margin-bottom:6px;padding:10px 12px;border:1px solid rgba(255,255,255,.04)}
.pizza-header{font-size:14px;color:#fff;font-weight:600;margin-bottom:1px}
.pizza-desc{font-size:11px;color:#666;margin-bottom:6px;line-height:1.3}
.pizza-size{display:flex;justify-content:space-between;align-items:center;padding:5px 8px;margin-bottom:3px;border-radius:6px;background:rgba(26,26,62,.5);border:1px solid #2a2a5e}
.pizza-size:last-child{margin-bottom:0}
.ps-label{font-size:13px;font-weight:700;color:#f39c12;min-width:26px}
.ps-preco{font-size:13px;color:#27ae60;font-weight:700;margin-right:auto;margin-left:6px}
.ps-qty{display:flex;align-items:center;gap:4px}
.ps-qty button,.sc-qty button{width:24px;height:24px;border:none;border-radius:50%;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-weight:700;transition:all .15s;flex-shrink:0}
.ps-qty .qty-minus,.sc-qty .qty-minus{background:#e74c3c;color:#fff}
.ps-qty .qty-plus,.sc-qty .qty-plus{background:#27ae60;color:#fff}
.ps-qty .qty-val,.sc-qty .qty-val{min-width:16px;text-align:center;font-weight:700;font-size:12px;color:#fff}

.simple-card{background:linear-gradient(135deg,#1a1a3e,#16213e);border-radius:10px;padding:10px 12px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(255,255,255,.04)}
.sc-info{flex:1;min-width:0}
.sc-nome{font-size:13px;color:#fff;font-weight:500}
.sc-preco{font-size:12px;color:#27ae60;font-weight:700;margin-top:1px}
.sc-gratis{color:#888;font-weight:400}
.sc-qty{display:flex;align-items:center;gap:4px;flex-shrink:0}

.meio-btn{display:block;width:100%;padding:8px;margin:8px 0 3px;border:2px dashed rgba(231,76,60,.35);border-radius:8px;background:rgba(231,76,60,.05);color:#e74c3c;font-size:12px;font-weight:600;cursor:pointer;text-align:center;transition:all .2s}
.meio-btn:hover{background:rgba(231,76,60,.1);border-color:#e74c3c}

.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.75);z-index:400}
.modal-overlay.open{display:block}
.modal-panel{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#1a1a3e;border-radius:14px;padding:16px;width:92%;max-width:440px;max-height:85vh;overflow-y:auto;z-index:401}
.modal-panel h2{font-size:16px;color:#fff;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center}
.modal-panel h2 button{background:rgba(231,76,60,.15);border:none;color:#e74c3c;font-size:18px;width:28px;height:28px;border-radius:50%;cursor:pointer}
.modal-section{margin-bottom:10px}
.modal-section label{font-size:11px;color:#888;display:block;margin-bottom:3px}
.modal-section select{width:100%;padding:8px;border-radius:6px;border:1px solid #2a2a5e;background:#0f0f23;color:#eee;font-size:12px;outline:none}
.modal-add{width:100%;padding:10px;border:none;border-radius:8px;background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff;font-size:13px;font-weight:700;cursor:pointer;margin-top:6px}
.modal-preview{background:rgba(39,174,96,.08);border:1px solid rgba(39,174,96,.2);border-radius:8px;padding:10px;margin:8px 0;text-align:center}
.modal-preview .mp-nome{font-size:13px;color:#2ecc71;font-weight:600}
.modal-preview .mp-preco{font-size:15px;color:#2ecc71;font-weight:700;margin-top:3px}

.combo-card{background:linear-gradient(135deg,#1a1a3e,#16213e);border-radius:10px;padding:10px 12px;margin-bottom:6px;border:1px solid rgba(255,255,255,.04);display:flex;align-items:center;gap:10px}
.combo-icon{font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:rgba(231,76,60,.1);border-radius:10px;flex-shrink:0}
.combo-info{flex:1;min-width:0}
.combo-nome{font-size:13px;color:#fff;font-weight:600}
.combo-desc{font-size:11px;color:#888;margin-top:1px;line-height:1.3}
.combo-preco-box{margin-top:3px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.combo-original{font-size:12px;color:#888;text-decoration:line-through}
.combo-preco{font-size:15px;color:#27ae60;font-weight:700}
.combo-economia{font-size:11px;color:#e74c3c;font-weight:500}

.loja-card{background:linear-gradient(135deg,#1a1a3e,#16213e);border-radius:10px;padding:12px 14px;margin-bottom:8px;border:1px solid rgba(255,255,255,.04)}
.loja-card h3{font-size:13px;color:#e74c3c;margin-bottom:8px;font-weight:600}
.loja-row{display:flex;align-items:flex-start;gap:8px;padding:5px 0;font-size:12px;color:#ccc}
.loja-row .loja-ico{font-size:14px;width:20px;text-align:center;flex-shrink:0}
.loja-row .loja-label{color:#888;min-width:65px;flex-shrink:0}
.loja-bairros{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}
.loja-bairros span{background:rgba(231,76,60,.12);color:#e74c3c;padding:2px 6px;border-radius:5px;font-size:10px}
.loja-destaque{background:linear-gradient(135deg,rgba(39,174,96,.1),rgba(39,174,96,.05));border:1px solid rgba(39,174,96,.2);border-radius:8px;padding:10px;margin-bottom:8px;text-align:center}
.loja-destaque .ld-val{font-size:18px;font-weight:700;color:#2ecc71}
.loja-destaque .ld-label{font-size:10px;color:#888;margin-top:1px}

.cart-fab{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff;border:none;border-radius:50px;padding:12px 22px;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 4px 20px rgba(231,76,60,.4);z-index:200;display:none;align-items:center;gap:6px;transition:all .2s}
.cart-fab.show{display:flex}
.cart-fab .badge{background:#fff;color:#e74c3c;border-radius:50%;padding:1px 7px;font-size:11px;font-weight:700}
.cart-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.65);z-index:300}
.cart-overlay.open{display:block}
.cart-panel{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(180deg,#1a1a3e,#0f0f23);border-radius:20px 20px 0 0;z-index:301;max-height:85vh;overflow-y:auto;transform:translateY(100%);transition:transform .3s;padding:16px}
.cart-panel.open{transform:translateY(0)}
.cart-panel h2{font-size:17px;margin-bottom:12px;color:#fff;display:flex;justify-content:space-between;align-items:center}
.cart-panel h2 button{background:rgba(231,76,60,.15);border:none;color:#e74c3c;font-size:18px;width:28px;height:28px;border-radius:50%;cursor:pointer}
.cart-item{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:12px;gap:6px}
.cart-item .ci-info{flex:1;min-width:0}
.cart-item .ci-nome{color:#fff;font-size:12px}
.cart-item .ci-cat{color:#e74c3c;font-size:9px;opacity:.5}
.cart-item .ci-meta{color:#888;font-size:10px;margin-top:1px}
.cart-item .ci-preco{color:#27ae60;font-weight:700;min-width:55px;text-align:right;font-size:12px;flex-shrink:0}
.cart-item .ci-remove{background:rgba(231,76,60,.12);border:none;color:#e74c3c;cursor:pointer;font-size:13px;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.cart-item .ci-remove:hover{background:#e74c3c;color:#fff}
.cart-total{display:flex;justify-content:space-between;padding:10px 0;font-size:17px;font-weight:700;color:#27ae60;border-top:2px solid rgba(255,255,255,.07);margin-top:3px}

.checkout-section{margin-top:12px}
.checkout-section h3{font-size:13px;color:#e74c3c;margin-bottom:10px}
.form-group{margin-bottom:8px}
.form-group label{display:block;font-size:11px;color:#888;margin-bottom:3px}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px;border-radius:6px;border:1px solid #2a2a5e;background:#1a1a3e;color:#fff;font-size:12px;outline:none;transition:border .15s}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:#e74c3c;box-shadow:0 0 0 2px rgba(231,76,60,.12)}
.form-group textarea{resize:vertical;min-height:40px;font-family:inherit}
.btn-finalizar{width:100%;padding:12px;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#25d366,#128c7e);color:#fff;display:flex;align-items:center;justify-content:center;gap:6px;margin-top:10px}
.btn-finalizar:disabled{opacity:.5;cursor:not-allowed}
.btn-finalizar .spinner{display:none;width:16px;height:16px;border:3px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}
.btn-finalizar.loading .spinner{display:inline-block}
.btn-finalizar.loading .btn-text{display:none}

.toast{position:fixed;top:16px;left:50%;transform:translateX(-50%);padding:10px 20px;border-radius:8px;color:#fff;font-size:12px;font-weight:500;z-index:999;display:none;text-align:center;animation:toastIn .3s ease-out;box-shadow:0 4px 16px rgba(0,0,0,.3);max-width:88%}
.toast.out{animation:toastOut .3s ease-in forwards}
.toast.error{background:linear-gradient(135deg,#e74c3c,#c0392b);display:block}
.toast.success{background:linear-gradient(135deg,#27ae60,#2ecc71);display:block}
.empty-cart{text-align:center;padding:30px 16px;color:#555}.empty-cart p{font-size:36px;margin-bottom:6px}
.loja-status{display:inline-flex;align-items:center;gap:3px;font-size:10px;padding:2px 7px;border-radius:8px;margin-top:3px;font-weight:500}
.loja-status.aberta{background:rgba(39,174,96,.2);color:#2ecc71}
.loja-status.fechada{background:rgba(231,76,60,.2);color:#e74c3c}
.loja-status .dot{width:4px;height:4px;border-radius:50%;display:inline-block}
.loja-status.aberta .dot{background:#2ecc71;animation:pulse 1.5s ease-in-out infinite}
.loja-status.fechada .dot{background:#e74c3c}
.cat-desc{font-size:11px;color:#777;padding:0 2px 8px;font-style:italic;line-height:1.3}
.cust-toggle{padding:6px 8px;font-size:11px;color:#e74c3c;cursor:pointer;border-top:1px solid rgba(255,255,255,.04);display:flex;justify-content:space-between;align-items:center;font-weight:500;margin-top:3px}
.cust-toggle:hover{color:#ff6b6b}
.cust-arrow{font-size:9px;transition:transform .2s}
.cust-arrow.open{transform:rotate(180deg)}
.cust-panel{display:none;padding:6px 8px 8px;border-top:1px solid rgba(255,255,255,.04);background:rgba(0,0,0,.1);border-radius:0 0 10px 10px}
.cust-panel.open{display:block}
.cust-remover{margin-bottom:6px}
.cust-remover label{font-size:10px;color:#888;display:block;margin-bottom:1px}
.cust-input{width:100%;padding:5px 7px;border-radius:5px;border:1px solid #2a2a5e;background:#0f0f23;color:#eee;font-size:11px;outline:none;box-sizing:border-box}
.cust-adicionais{display:flex;flex-direction:column;gap:3px}
.cust-adi-item{display:flex;align-items:center;gap:5px;padding:3px 5px;border-radius:5px;background:rgba(26,26,62,.3);font-size:11px}
.cust-adi-nome{flex:1;min-width:0;color:#ccc;font-size:11px}
.cust-adi-preco{color:#27ae60;font-size:10px;white-space:nowrap}
.cust-adi-gratis{color:#888;font-size:10px}
.ci-obs{font-size:10px;color:#e67e22;margin-top:1px}
</style>
</head>
<body>
<div class="header">
<h1>PayPizzas</h1>
<p>Monte seu pedido e envie pelo WhatsApp</p>
<div class="loja-status aberta" id="cardapioStatus"><span class="dot"></span><span id="cardapioStatusTexto">Verificando...</span></div>
</div>
<div class="container">
<div class="tabs" id="tabNav">
<button class="tab active" data-tab="tradicionais">🍕 Tradicionais</button>
<button class="tab" data-tab="especiais">👑 Especiais</button>
<button class="tab" data-tab="doces">🍫 Doces</button>
<button class="tab" data-tab="bebidas">🥤 Bebidas</button>
<button class="tab" data-tab="extras">🧀 Extras</button>
<button class="tab" data-tab="combos">🔥 Combos</button>
<button class="tab" data-tab="loja">📍 Loja</button>
</div>
<div class="tab-content active" id="tabTradicionais"><p class="cat-desc">Todas as pizzas tradicionais acompanham molho de tomate artesanal, muçarela e orégano.</p></div>
<div class="tab-content" id="tabEspeciais"><p class="cat-desc">Criações exclusivas com ingredientes selecionados.</p></div>
<div class="tab-content" id="tabDoces"><p class="cat-desc">A sobremesa ideal em formato de pizza.</p></div>
<div class="tab-content" id="tabBebidas"></div>
<div class="tab-content" id="tabExtras"></div>
<div class="tab-content" id="tabCombos"></div>
<div class="tab-content" id="tabLoja"></div>
</div>

<div class="modal-overlay" id="meioModal">
<div class="modal-panel">
<h2>Montar Meio a Meio <button id="btnCloseModal">&times;</button></h2>
<div class="modal-section"><label>Sabor 1</label><select id="mmSabor1"></select></div>
<div class="modal-section"><label>Sabor 2</label><select id="mmSabor2"></select></div>
<div class="modal-section"><label>Tamanho</label><select id="mmTamanho"><option value="M">M</option><option value="G">G</option></select></div>
<div class="modal-preview" id="mmPreview"><div class="mp-nome" id="mmNome">Selecione 2 sabores</div><div class="mp-preco" id="mmPreco">R$ 0,00</div></div>
<button class="modal-add" id="btnAddMeio">Adicionar ao Carrinho</button>
</div>
</div>

<button class="cart-fab" id="cartFab">Carrinho <span class="badge" id="cartCount">0</span></button>
<div class="cart-overlay" id="cartOverlay"></div>
<div class="cart-panel" id="cartPanel">
<h2>Seu Pedido <button id="btnCloseCart">&times;</button></h2>
<div id="cartItems"></div>
<div class="cart-total"><span>Total</span><span id="cartTotal">R$ 0,00</span></div>
<div class="checkout-section">
<h3>Dados para Entrega</h3>
<div class="form-group"><label>Seu Nome</label><input type="text" id="inputNome" placeholder="Seu nome" maxlength="60"></div>
<div class="form-group"><label>Endereco de Entrega</label><input type="text" id="inputEndereco" placeholder="Rua, numero, bairro, referencia"></div>
<div class="form-group"><label>Pagamento</label>
<select id="inputPagamento"><option value="Especie">Especie (Dinheiro)</option><option value="Cartao">Cartao (Credito/Debito)</option><option value="Pix">PIX</option></select></div>
<div class="form-group"><label>Observacoes</label><textarea id="inputObs" placeholder="Troco para quanto?"></textarea></div>
<button class="btn-finalizar" id="btnFinalizar"><span class="btn-text">Enviar Pedido</span><span class="spinner"></span></button>
</div>
</div>
</div>
<div id="toast" class="toast"></div>

<script>
var TRAD = __TRADICIONAIS__;
var ESP = __ESPECIAIS__;
var DOCES = __DOCES__;
var BEBIDAS = __BEBIDAS_JSON__;
var ADICIONAIS = __ADICIONAIS_JSON__;
var COMBOS = __COMBOS_JSON__;
var LOJA = __LOJA_INFO_JSON__;
var WA_NUMERO = "__WA_NUMERO__";
var TODOS_SABORES = [].concat(TRAD, ESP, DOCES);
var cart = {};
var customNotes = {};

document.addEventListener('click', function(e) {
    var btn = e.target.closest('.qty-minus, .qty-plus');
    if (btn) {
        var key = btn.dataset.key; var delta = parseInt(btn.dataset.delta);
        cart[key] = (cart[key] || 0) + delta;
        if (cart[key] <= 0) delete cart[key];
        var el = document.getElementById('qty-' + key); if (el) el.textContent = cart[key] || 0;
        var cel = document.getElementById('cqty-' + key); if (cel) cel.textContent = cart[key] || 0;
        updateFab(); return;
    }
    var tabBtn = e.target.closest('.tab');
    if (tabBtn) {
        document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
        document.querySelectorAll('.tab-content').forEach(function(t) { t.classList.remove('active'); });
        tabBtn.classList.add('active');
        var id = 'tab' + tabBtn.dataset.tab.charAt(0).toUpperCase() + tabBtn.dataset.tab.slice(1);
        document.getElementById(id).classList.add('active'); return;
    }
    if (e.target.closest('#cartFab')) { openCart(); return; }
    if (e.target.closest('#cartOverlay') || e.target.closest('#btnCloseCart')) { closeCart(); return; }
    if (e.target.closest('#btnCloseModal')) { closeModal(); return; }
    if (e.target.closest('.meio-btn')) { openModal(); return; }
    if (e.target.closest('#btnAddMeio')) { addMeio(); return; }
    var custToggle = e.target.closest('.cust-toggle');
    if (custToggle) {
        var chave = custToggle.dataset.chave;
        var panel = document.getElementById('cust-' + chave);
        panel.classList.toggle('open');
        custToggle.querySelector('.cust-arrow').classList.toggle('open');
        return;
    }
});

document.addEventListener('input', function(e) {
    var inp = e.target.closest('.cust-input');
    if (inp) {
        var chave = inp.dataset.chave;
        var val = inp.value.trim();
        if (val) customNotes[chave] = val; else delete customNotes[chave];
    }
});

function esc(s) { return String(s).replace(/[&<>"]/g, function(m) { if (m==='&') return '&amp;'; if (m==='<') return '&lt;'; if (m==='>') return '&gt;'; if (m==='"') return '&quot;'; return m; }); }

function renderPizzas(list, containerId) {
    var h = '';
    for (var i = 0; i < list.length; i++) {
        var s = list[i];
        h += '<div class="pizza-card">';
        h += '<div class="pizza-header">' + esc(s.nome) + '</div>';
        h += '<div class="pizza-desc">' + esc(s.descricao) + '</div>';
        for (var j = 0; j < s.tamanhos.length; j++) {
            var t = s.tamanhos[j];
            var k = 'sabor:' + s.chave + '-' + t.tamanho;
            var q = cart[k] || 0;
            h += '<div class="pizza-size"><span class="ps-label">' + t.tamanho + '</span><span class="ps-preco">R$ ' + t.preco.toFixed(2) + '</span><div class="ps-qty">';
            h += '<button class="qty-minus" data-key="' + k + '" data-delta="-1">&minus;</button>';
            h += '<span class="qty-val" id="qty-' + k + '">' + q + '</span>';
            h += '<button class="qty-plus" data-key="' + k + '" data-delta="1">+</button></div></div>';
        }
        h += '<div class="cust-toggle" data-chave="' + s.chave + '"><span>Customizar</span><span class="cust-arrow">&#9660;</span></div>';
        h += '<div class="cust-panel" id="cust-' + s.chave + '">';
        h += '<div class="cust-remover"><label>Remover ingredientes:</label><input class="cust-input" data-chave="' + s.chave + '" placeholder="Ex: Sem cebola, sem azeitona" maxlength="80" value="' + esc(customNotes[s.chave] || '') + '"></div>';
        h += '<div class="cust-adicionais">';
        for (var a = 0; a < ADICIONAIS.length; a++) {
            var ad = ADICIONAIS[a];
            var ak = 'adicional:' + ad.chave;
            var aq = cart[ak] || 0;
            h += '<div class="cust-adi-item"><span class="cust-adi-nome">' + esc(ad.nome) + '</span>';
            if (ad.preco > 0) h += '<span class="cust-adi-preco">+R$ ' + ad.preco.toFixed(2) + '</span>'; else h += '<span class="cust-adi-gratis">Gratis</span>';
            h += '<div class="ps-qty"><button class="qty-minus" data-key="' + ak + '" data-delta="-1">&minus;</button>';
            h += '<span class="qty-val" id="cqty-' + ak + '">' + aq + '</span>';
            h += '<button class="qty-plus" data-key="' + ak + '" data-delta="1">+</button></div></div>';
        }
        h += '</div></div>';
        h += '</div>';
    }
    if (containerId !== 'tabDoces') {
        h += '<button class="meio-btn">Montar Pizza Meio a Meio</button>';
    }
    document.getElementById(containerId).innerHTML = h;
}

function renderBebidas() {
    var h = '';
    for (var i = 0; i < BEBIDAS.length; i++) {
        var b = BEBIDAS[i]; var k = 'bebida:' + b.chave; var q = cart[k] || 0;
        h += '<div class="simple-card"><div class="sc-info"><div class="sc-nome">' + esc(b.nome) + '</div>';
        if (b.preco > 0) h += '<div class="sc-preco">R$ ' + b.preco.toFixed(2) + '</div>'; else h += '<div class="sc-preco sc-gratis">Gratis</div>';
        h += '</div><div class="sc-qty"><button class="qty-minus" data-key="' + k + '" data-delta="-1">&minus;</button><span class="qty-val" id="qty-' + k + '">' + q + '</span><button class="qty-plus" data-key="' + k + '" data-delta="1">+</button></div></div>';
    }
    document.getElementById('tabBebidas').innerHTML = h;
}

function renderAdicionais() {
    var h = '';
    for (var i = 0; i < ADICIONAIS.length; i++) {
        var a = ADICIONAIS[i]; var k = 'adicional:' + a.chave; var q = cart[k] || 0;
        h += '<div class="simple-card"><div class="sc-info"><div class="sc-nome">' + esc(a.nome) + '</div>';
        if (a.preco > 0) h += '<div class="sc-preco">R$ ' + a.preco.toFixed(2) + '</div>'; else h += '<div class="sc-preco sc-gratis">Gratis</div>';
        h += '</div><div class="sc-qty"><button class="qty-minus" data-key="' + k + '" data-delta="-1">&minus;</button><span class="qty-val" id="qty-' + k + '">' + q + '</span><button class="qty-plus" data-key="' + k + '" data-delta="1">+</button></div></div>';
    }
    document.getElementById('tabExtras').innerHTML = h;
}

function renderCombos() {
    var h = '';
    for (var i = 0; i < COMBOS.length; i++) {
        var c = COMBOS[i]; var original = c.preco + c.economia;
        h += '<div class="combo-card"><div class="combo-icon">' + c.icone + '</div><div class="combo-info"><div class="combo-nome">' + esc(c.nome) + '</div><div class="combo-desc">' + esc(c.descricao) + '</div><div class="combo-preco-box"><span class="combo-original">R$ ' + original.toFixed(2) + '</span> <span class="combo-preco">R$ ' + c.preco.toFixed(2) + '</span></div><div class="combo-economia">Economia de R$ ' + c.economia.toFixed(2) + '</div></div></div>';
    }
    document.getElementById('tabCombos').innerHTML = h;
}

function renderLoja() {
    var l = LOJA; var h = '';
    h += '<div class="loja-destaque"><div class="ld-val">' + l.taxa_entrega.toFixed(2).replace('.',',') + '</div><div class="ld-label">Taxa de entrega (gratis acima de R$ ' + l.taxa_gratis_acima.toFixed(2).replace('.',',') + ')</div></div>';
    h += '<div class="loja-destaque"><div class="ld-val">R$ ' + l.pedido_minimo.toFixed(2).replace('.',',') + '</div><div class="ld-label">Pedido minimo</div></div>';
    h += '<div class="loja-destaque"><div class="ld-val">' + l.tempo_medio + '</div><div class="ld-label">Tempo medio de entrega</div></div>';
    h += '<div class="loja-card"><h3>Localizacao</h3><div class="loja-row"><span class="loja-ico">📍</span><span class="loja-label">Endereco</span><span>' + esc(l.endereco) + '</span></div></div>';
    h += '<div class="loja-card"><h3>Contato</h3><div class="loja-row"><span class="loja-ico">📞</span><span class="loja-label">Telefone</span><span>' + l.telefone + '</span></div></div>';
    h += '<div class="loja-card"><h3>Horario</h3><div class="loja-row"><span class="loja-ico">🕐</span><span class="loja-label">Funcionamento</span><span>' + esc(l.horario) + '</span></div></div>';
    h += '<div class="loja-card"><h3>Area de Entrega</h3><div class="loja-row"><span class="loja-ico">🚚</span><span class="loja-label">Bairros</span><div class="loja-bairros">';
    for (var i = 0; i < l.bairros.length; i++) { h += '<span>' + esc(l.bairros[i]) + '</span>'; }
    h += '</div></div></div>';
    document.getElementById('tabLoja').innerHTML = h;
}

function updateFab() {
    var total = 0; for (var k in cart) total += cart[k];
    document.getElementById('cartCount').textContent = total;
    document.getElementById('cartFab').classList.toggle('show', total > 0);
}

function openCart() { document.getElementById('cartOverlay').classList.add('open'); document.getElementById('cartPanel').classList.add('open'); renderCart(); }
function closeCart() { document.getElementById('cartOverlay').classList.remove('open'); document.getElementById('cartPanel').classList.remove('open'); }

function buildSaboresOpts(sel) {
    var h = '';
    for (var i = 0; i < TODOS_SABORES.length; i++) {
        var s = TODOS_SABORES[i];
        var sizes = s.tamanhos.map(function(t){return t.tamanho}).join('/');
        h += '<option value="' + s.chave + '">' + esc(s.nome) + ' (' + sizes + ')</option>';
    }
    sel.innerHTML = h;
}

function openModal() {
    buildSaboresOpts(document.getElementById('mmSabor1'));
    buildSaboresOpts(document.getElementById('mmSabor2'));
    updatePreview();
    document.getElementById('meioModal').classList.add('open');
}

function closeModal() { document.getElementById('meioModal').classList.remove('open'); }

document.getElementById('mmSabor1').addEventListener('change', updatePreview);
document.getElementById('mmSabor2').addEventListener('change', updatePreview);
document.getElementById('mmTamanho').addEventListener('change', updatePreview);

function getPreco(chave, tam) {
    for (var i = 0; i < TODOS_SABORES.length; i++) {
        if (TODOS_SABORES[i].chave === chave) {
            for (var j = 0; j < TODOS_SABORES[i].tamanhos.length; j++) {
                if (TODOS_SABORES[i].tamanhos[j].tamanho === tam) return TODOS_SABORES[i].tamanhos[j].preco;
            }
        }
    }
    return 0;
}

function getNome(chave) {
    for (var i = 0; i < TODOS_SABORES.length; i++) {
        if (TODOS_SABORES[i].chave === chave) return TODOS_SABORES[i].nome;
    }
    return '';
}

function updatePreview() {
    var s1 = document.getElementById('mmSabor1').value;
    var s2 = document.getElementById('mmSabor2').value;
    var tam = document.getElementById('mmTamanho').value;
    if (s1 && s2) {
        var p1 = getPreco(s1, tam); var p2 = getPreco(s2, tam);
        var media = (p1 + p2) / 2;
        document.getElementById('mmNome').textContent = '1/2 ' + getNome(s1) + ' + 1/2 ' + getNome(s2) + ' (' + tam + ')';
        document.getElementById('mmPreco').textContent = 'R$ ' + media.toFixed(2);
    } else {
        document.getElementById('mmNome').textContent = 'Selecione 2 sabores';
        document.getElementById('mmPreco').textContent = 'R$ 0,00';
    }
}

function addMeio() {
    var s1 = document.getElementById('mmSabor1').value;
    var s2 = document.getElementById('mmSabor2').value;
    var tam = document.getElementById('mmTamanho').value;
    if (!s1 || !s2 || s1 === s2) { showToast('Selecione 2 sabores diferentes', 'error'); return; }
    var p1 = getPreco(s1, tam); var p2 = getPreco(s2, tam);
    var preco = (p1 + p2) / 2;
    var key = 'meio:' + s1 + '+' + s2 + '-' + tam;
    cart[key] = (cart[key] || 0) + 1;
    updateFab();
    closeModal();
    showToast('Meio a meio adicionado!', 'success');
}

function getItemInfo(key) {
    if (key.indexOf('meio:') === 0) {
        var rest = key.slice(5);
        var parts = rest.split('-');
        var saboresPart = parts[0];
        var tam = parts[1];
        var sabores = saboresPart.split('+');
        var p1 = getPreco(sabores[0], tam); var p2 = getPreco(sabores[1], tam);
        return { nome: '1/2 ' + getNome(sabores[0]) + ' + 1/2 ' + getNome(sabores[1]) + ' (' + tam + ')', cat: 'Pizza Meio a Meio', preco: (p1 + p2) / 2 };
    }
    if (key.indexOf('sabor:') === 0) {
        var p = key.slice(6).split('-');
        for (var i = 0; i < TODOS_SABORES.length; i++) {
            if (TODOS_SABORES[i].chave === p[0]) {
                for (var j = 0; j < TODOS_SABORES[i].tamanhos.length; j++) {
                    if (TODOS_SABORES[i].tamanhos[j].tamanho === p[1]) return { nome: TODOS_SABORES[i].nome + ' (' + p[1] + ')', cat: 'Pizza', preco: TODOS_SABORES[i].tamanhos[j].preco };
                }
            }
        }
    }
    if (key.indexOf('bebida:') === 0) { var c = key.slice(7); for (var i = 0; i < BEBIDAS.length; i++) { if (BEBIDAS[i].chave === c) return { nome: BEBIDAS[i].nome, cat: 'Bebida', preco: BEBIDAS[i].preco }; } }
    if (key.indexOf('adicional:') === 0) { var c = key.slice(10); for (var i = 0; i < ADICIONAIS.length; i++) { if (ADICIONAIS[i].chave === c) return { nome: ADICIONAIS[i].nome, cat: 'Adicional', preco: ADICIONAIS[i].preco }; } }
    return null;
}

function renderCart() {
    var container = document.getElementById('cartItems');
    var items = []; var total = 0;
    for (var key in cart) {
        var qty = cart[key]; if (qty <= 0) continue;
        var info = getItemInfo(key); if (!info) continue;
        var sub = qty * info.preco; total += sub;
        items.push({ key: key, nome: info.nome, cat: info.cat, qty: qty, preco: info.preco, sub: sub });
    }
    if (items.length === 0) { container.innerHTML = '<div class="empty-cart"><p>&#x1F6D2;</p><span>Carrinho vazio</span></div>'; document.getElementById('cartTotal').textContent = 'R$ 0,00'; return; }
    var h = '';
    for (var i = 0; i < items.length; i++) {
        var it = items[i];
        var note = '';
        if (it.key.indexOf('sabor:') === 0) {
            var saborChave = it.key.slice(6).split('-')[0];
            note = customNotes[saborChave] || '';
        }
        h += '<div class="cart-item"><div class="ci-info"><div class="ci-nome">' + esc(it.nome) + '</div><div class="ci-cat">' + it.cat + '</div><div class="ci-meta">' + it.qty + 'x R$ ' + it.preco.toFixed(2) + '</div>';
        if (note) h += '<div class="ci-obs">Obs: ' + esc(note) + '</div>';
        h += '</div><span class="ci-preco">R$ ' + it.sub.toFixed(2) + '</span><button class="ci-remove" data-key="' + it.key + '">&times;</button></div>';
    }
    container.innerHTML = h;
    document.getElementById('cartTotal').textContent = 'R$ ' + total.toFixed(2);
    container.querySelectorAll('.ci-remove').forEach(function(b) { b.addEventListener('click', function() { removerItem(this.dataset.key); }); });
}

function removerItem(key) {
    delete cart[key];
    var el = document.getElementById('qty-' + key); if (el) el.textContent = 0;
    var cel = document.getElementById('cqty-' + key); if (cel) cel.textContent = 0;
    updateFab(); renderCart();
}

function showToast(msg, type) {
    var t = document.getElementById('toast');
    t.textContent = msg; t.className = 'toast ' + type;
    setTimeout(function() { t.className += ' out'; setTimeout(function() { t.className = 'toast'; }, 300); }, 2800);
}

async function finalizarPedido() {
    var nome = document.getElementById('inputNome').value.trim();
    var endereco = document.getElementById('inputEndereco').value.trim();
    var pagamento = document.getElementById('inputPagamento').value;
    var obs = document.getElementById('inputObs').value.trim();
    if (!nome) { showToast('Digite seu nome', 'error'); return; }
    if (!endereco) { showToast('Digite o endereco', 'error'); return; }
    var itens = [];
    for (var key in cart) {
        var qty = cart[key]; if (qty <= 0) continue;
        var info = getItemInfo(key); if (!info) continue;
        var categoria, sabor, tamanho;
        if (key.indexOf('sabor:') === 0) { var p = key.slice(6).split('-'); categoria = 'sabor'; sabor = p[0]; tamanho = p[1]; }
        else if (key.indexOf('meio:') === 0) { categoria = 'sabor'; sabor = key.slice(5); tamanho = ''; }
        else if (key.indexOf('bebida:') === 0) { categoria = 'bebida'; sabor = key.slice(7); tamanho = ''; }
        else { categoria = 'adicional'; sabor = key.slice(10); tamanho = ''; }
        itens.push({ categoria: categoria, sabor: sabor, tamanho: tamanho, quantidade: qty, preco: info.preco });
    }
    if (itens.length === 0) { showToast('Adicione itens ao carrinho', 'error'); return; }
    var notasExtras = [];
    var seenSabores = {};
    for (var key in cart) {
        if (key.indexOf('sabor:') === 0) {
            var saborChave = key.slice(6).split('-')[0];
            if (customNotes[saborChave] && !seenSabores[saborChave]) {
                seenSabores[saborChave] = true;
                var saborNome = '';
                for (var si = 0; si < TODOS_SABORES.length; si++) {
                    if (TODOS_SABORES[si].chave === saborChave) { saborNome = TODOS_SABORES[si].nome; break; }
                }
                notasExtras.push(saborNome + ': ' + customNotes[saborChave]);
            }
        }
    }
    if (notasExtras.length > 0) {
        obs = obs ? obs + ' | ' + notasExtras.join(' | ') : notasExtras.join(' | ');
    }
    var btn = document.getElementById('btnFinalizar');
    btn.disabled = true; btn.classList.add('loading');
    try {
        var res = await fetch('/api/pedido/criar', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome, itens: itens, endereco: endereco, pagamento: pagamento, observacoes: obs })
        });
        var data = await res.json();
        if (!res.ok) throw new Error(data.erro || 'Erro');
        window.location.href = data.whatsapp_link;
    } catch (e) { showToast(e.message, 'error'); btn.disabled = false; btn.classList.remove('loading'); }
}

document.getElementById('btnFinalizar').addEventListener('click', finalizarPedido);

renderPizzas(TRAD, 'tabTradicionais');
renderPizzas(ESP, 'tabEspeciais');
renderPizzas(DOCES, 'tabDoces');
renderBebidas();
renderAdicionais();
renderCombos();
renderLoja();
fetch('/api/loja/status').then(function(r){return r.json()}).then(function(d){
    document.getElementById('cardapioStatus').className='loja-status '+(d.aberta?'aberta':'fechada');
    document.getElementById('cardapioStatusTexto').textContent=d.aberta?'Loja Aberta':'Loja Fechada';
}).catch(function(){});
</script>
</body>
</html>"""
