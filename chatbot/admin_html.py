ADMIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PayPizzas - Admin</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#eef0f2;color:#333;font-size:15px}

@keyframes grad{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
@keyframes slide{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
@keyframes count{from{opacity:0;transform:scale(.5)}to{opacity:1;transform:scale(1)}}
@keyframes shimmer{0%{background-position:-200px 0}100%{background-position:calc(200px + 100%) 0}}
@keyframes toastIn{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes toastOut{from{opacity:1}to{opacity:0;transform:translateY(-20px)}}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-3px)}40%{transform:translateX(3px)}60%{transform:translateX(-2px)}80%{transform:translateX(2px)}}

.header{background:linear-gradient(135deg,#e74c3c,#c0392b,#e67e22,#c0392b);background-size:300% 300%;animation:grad 6s ease infinite;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(0,0,0,.15)}
.header h1{font-size:22px;text-shadow:0 1px 4px rgba(0,0,0,.2)}
.header span{font-size:13px;opacity:.9}
.container{max-width:1400px;margin:0 auto;padding:16px}
.row{display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap}

.card{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px 22px;flex:1;min-width:0;transition:all .25s ease;position:relative;overflow:hidden}
.card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.1)}
.card::after{content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:12px 0 0 12px}
.card:nth-child(1)::after{background:#2980b9}
.card:nth-child(2)::after{background:#27ae60}
.card:nth-child(3)::after{background:#8e44ad}
.card:nth-child(4)::after{background:#f39c12}
.card h3{font-size:11px;text-transform:uppercase;color:#888;margin-bottom:6px;letter-spacing:.5px}
.val{font-size:26px;font-weight:700;animation:count .4s ease-out}
.val.green{color:#27ae60}
.val.blue{color:#2980b9}
.val.purple{color:#8e44ad}

.actions{display:flex;gap:10px}
.btn{padding:9px 20px;border:none;border-radius:8px;font-size:14px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:6px;transition:all .2s;font-weight:500}
.btn-success{background:linear-gradient(135deg,#27ae60,#2ecc71);color:#fff;box-shadow:0 2px 8px rgba(39,174,96,.3)}
.btn-primary{background:linear-gradient(135deg,#3498db,#5dade2);color:#fff;box-shadow:0 2px 8px rgba(52,152,219,.3)}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.2)}
.btn:active{transform:translateY(0)}

.cols{display:grid;grid-template-columns:1fr 1.5fr 1.5fr;gap:12px;margin-bottom:14px}
.cols>div{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px 22px;transition:all .25s ease}
.cols>div:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.1)}
.cols h3{font-size:11px;text-transform:uppercase;color:#888;margin-bottom:10px;letter-spacing:.5px}
.item{display:flex;justify-content:space-between;padding:4px 0;font-size:14px;animation:slide .3s ease-out}
.item .l{color:#666}
.item .r{font-weight:600}
.bar-bg{background:#f0f0f0;border-radius:4px;height:8px;margin:4px 0 6px;overflow:hidden}
.bar{height:100%;border-radius:4px;transition:width .8s cubic-bezier(.22,1,.36,1)}

.orders{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);overflow:hidden}
.orders .hdr{padding:12px 20px;font-size:14px;font-weight:600;background:#fafafa;border-bottom:1px solid #eee;display:flex;justify-content:space-between}

.o{padding:10px 20px;border-bottom:1px solid #f3f3f3;display:flex;align-items:center;gap:12px;font-size:14px;flex-wrap:wrap;animation:slide .3s ease-out;transition:all .2s;border-left:3px solid transparent}
.o:last-child{border-bottom:none}
.o:hover{background:#f8f9fa;border-left-color:#e74c3c}
.od{font-weight:700;color:#e74c3c;min-width:36px;font-size:16px}
.oi{flex:1;min-width:140px}
.oi .t{color:#333}
.oi .m{font-size:13px;color:#888}
.st{padding:4px 12px;border-radius:14px;font-size:12px;font-weight:600;white-space:nowrap;transition:all .3s}
.st-r{background:#ffeaa7;color:#856404;animation:pulse 2s ease-in-out 3}
.st-p{background:#81ecec;color:#006064}
.st-s{background:#74b9ff;color:#003366}
.st-e{background:#55efc4;color:#00695c}
.st-c{background:#ff7675;color:#7f0000;text-decoration:line-through}
.op{font-weight:700;color:#27ae60;font-size:15px;white-space:nowrap;min-width:80px;text-align:right}
.empty{text-align:center;padding:50px;color:#999;font-size:15px}
.bdg{background:#e74c3c;color:#fff;border-radius:12px;padding:0 10px;font-size:12px;margin-left:8px}
.pb{background:linear-gradient(135deg,#e67e22,#f39c12);color:#fff;font-size:10px;padding:2px 6px;border-radius:4px;margin-left:4px}

.cb{background:none;border:1.5px solid #e74c3c;color:#e74c3c;border-radius:6px;padding:3px 10px;font-size:11px;cursor:pointer;white-space:nowrap;transition:all .2s;font-weight:500}
.cb:hover{background:#e74c3c;color:#fff;animation:shake .4s ease;box-shadow:0 2px 8px rgba(231,76,60,.3)}
.cb:disabled{opacity:.4;cursor:not-allowed;animation:none}

.toast{position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:10px;color:#fff;font-size:14px;z-index:999;animation:toastIn .3s ease-out;box-shadow:0 4px 20px rgba(0,0,0,.15);display:flex;align-items:center;gap:8px;max-width:360px}
.toast.out{animation:toastOut .3s ease-in forwards}
.toast.success{background:linear-gradient(135deg,#27ae60,#2ecc71)}
.toast.error{background:linear-gradient(135deg,#e74c3c,#e67e22)}

.loading{position:relative;overflow:hidden}
.loading::after{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);background-size:200px 100%;animation:shimmer 1.5s infinite}

@media(max-width:700px){.cols{grid-template-columns:1fr}.o{flex-wrap:wrap}.op{text-align:left}}
</style>
</head>
<body>
<div class="header">
<h1>PayPizzas</h1>
<span><span id="s-online">Offline</span> &middot; <a href="/cardapio" style="color:#fff">Cardapio</a></span>
</div>
<div class="container">
<div class="row" id="stats">
<div class="card loading"><h3>Pedidos</h3><div class="val blue" id="t-orders">0</div></div>
<div class="card loading"><h3>Faturamento</h3><div class="val green" id="t-revenue">R$0</div></div>
<div class="card loading"><h3>Ticket</h3><div class="val purple" id="t-avg">R$0</div></div>
<div class="card loading"><h3>Lucro</h3><div class="val green" id="t-profit">R$0</div></div>
<div class="actions" style="flex:none;align-items:center">
<a href="/admin/exportar-excel" class="btn btn-success">Excel</a>
<button class="btn btn-primary" onclick="location.reload()">Atualizar</button>
</div>
</div>

<div class="cols">
<div class="loading"><h3>Sabores Mais Vendidos</h3><div id="top-sab"></div></div>
<div class="loading"><h3>Pagamentos</h3><div id="top-pag"></div></div>
<div class="loading"><h3>Status</h3><div id="top-st"></div></div>
</div>

<div class="orders loading">
<div class="hdr"><span>Pedidos do Dia <span class="bdg" id="o-count">0</span></span></div>
<div id="o-list"></div>
</div>
</div>

<div id="toast"></div>

<script>
const C=['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e'];

function toast(msg,type){
const t=document.getElementById('toast');
t.className='toast '+type;
t.innerHTML='<span>'+(type==='success'?'':'')+'</span>'+msg;
setTimeout(()=>{t.className+=' out';setTimeout(()=>{t.className='toast'},300)},2500)
}

function bar(v,m,c,i){
const p=m>0?v/m*100:0;
return'<div class="bar-bg"><div class="bar" style="width:0%;background:'+c+'"></div></div>'
}

function procAna(ps){
const s={},pg={},st={};let tot=0,q=0,lc=0;
ps.forEach(p=>{tot+=p.total_pedido||0;lc+=p.lucro_pedido||0;q++;
const mt=p.metodo_pagamento||'?';pg[mt]=(pg[mt]||0)+1;
const stt=p.status||'recebido';st[stt]=(st[stt]||0)+1;
try{JSON.parse(p.itens_pedido||'[]').forEach(i=>{const n=i.sabor||'?';s[n]=(s[n]||0)+(i.quantidade||1)})}catch(e){}});
document.getElementById('t-avg').textContent='R$'+(q>0?(tot/q).toFixed(2):'0,00');
document.getElementById('t-profit').textContent='R$'+lc.toFixed(2);

const ss=Object.entries(s).sort((a,b)=>b[1]-a[1]),mx=ss.length?ss[0][1]:1;
document.getElementById('top-sab').innerHTML=ss.length?ss.map(([n,q],i)=>'<div class="item"><span class="l">'+(i+1)+'. '+n+'</span><span class="r">'+q+'x</span></div>'+bar(q,mx,C[i%8])).join(''):'<div class="item" style="color:#999">Nenhum</div>';

const mp=Math.max(...Object.values(pg),1);
document.getElementById('top-pag').innerHTML=Object.entries(pg).sort((a,b)=>b[1]-a[1]).map(([m,q],i)=>'<div class="item"><span class="l">'+m+'</span><span class="r">'+q+'</span></div>'+bar(q,mp,C[i%8])).join('');

const SL={recebido:'Recebido',preparando:'Preparando',saiu:'Saiu',entregue:'Entregue',cancelado:'Cancelado'};
const SC={recebido:'#ffeaa7',preparando:'#81ecec',saiu:'#74b9ff',entregue:'#55efc4',cancelado:'#ff7675'};
const ms=Math.max(...Object.values(st),1);
document.getElementById('top-st').innerHTML=Object.entries(st).sort((a,b)=>b[1]-a[1]).map(([s,q])=>'<div class="item"><span class="l">'+(SL[s]||s)+'</span><span class="r" style="color:'+(SC[s]||'#888')+'">'+q+'</span></div>'+bar(q,ms,SC[s]||'#888')).join('');

setTimeout(()=>{document.querySelectorAll('.bar').forEach((b,i)=>{b.style.width=b.parentElement.previousElementSibling?b.dataset.pct+'%':'0'})},100)
}

const SM={recebido:'Recebido',preparando:'Preparando',saiu:'Saiu p/ Entrega',entregue:'Entregue',cancelado:'Cancelado'};
const ST={recebido:'st-r',preparando:'st-p',saiu:'st-s',entregue:'st-e',cancelado:'st-c'};

async function cancelar(num,btn){
if(!confirm('Cancelar pedido #'+num+'?'))return;
btn.disabled=true;btn.textContent='...';
try{
const r=await fetch('/admin/pedido/'+num+'/status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'cancelado'})});
if(!r.ok)throw Error();
toast('Pedido #'+num+' cancelado','success');
load();
}catch(e){toast('Erro ao cancelar pedido','error');btn.disabled=false;btn.textContent='Cancelar'}
}

function removeLoading(){
document.querySelectorAll('.loading').forEach(el=>el.classList.remove('loading'))
}

async function load(){
try{
const [pr,hr]=await Promise.all([fetch('/admin/pedidos'),fetch('/health')]);
const p=await pr.json(),h=await hr.json(),os=p.pedidos||[];
removeLoading();
document.getElementById('t-orders').textContent=p.total;
document.getElementById('o-count').textContent=p.total;
const se=document.getElementById('s-online');
se.textContent=h.status==='healthy'?'Online':'Offline';
se.style.color=h.status==='healthy'?'#27ae60':'#e74c3c';
procAna(os);
const rev=os.reduce((s,o)=>s+(o.total_pedido||0),0);
document.getElementById('t-revenue').textContent='R$'+rev.toFixed(2);
const el=document.getElementById('o-list');
if(!os.length){el.innerHTML='<div class="empty">Nenhum pedido hoje</div>';return}
el.innerHTML=os.map(o=>{let it;
try{it=JSON.parse(o.itens_pedido||'[]').map(i=>i.quantidade+'x '+i.sabor+(i.tamanho?'('+i.tamanho+')':'')).join(', ')}catch(e){it=o.itens_pedido}
const hr=o.timestamp?o.timestamp.slice(11,16):'',isP=(o.metodo_pagamento||'').toLowerCase()==='pix',isC=o.status==='cancelado';
return'<div class="o"><span class="od">#'+o.numero_do_dia+'</span><div class="oi"><div class="t">'+it+'</div><div class="m">'+hr+' &middot; '+o.endereco+(isP?' <span class="pb">PIX</span>':'')+'</div></div><span class="st '+(ST[o.status]||'st-r')+'">'+(SM[o.status]||o.status)+'</span>'+(isC?'':'<button class="cb" onclick="cancelar('+o.numero_do_dia+',this)">Cancelar</button>')+'<span class="op">R$'+(o.total_pedido||0).toFixed(2)+'</span></div>'}).join('');
}catch(e){removeLoading();document.getElementById('o-list').innerHTML='<div class="empty">Erro ao carregar</div>'}
}
load();setInterval(load,30000);
</script>
</body>
</html>"""
