/* M7 Neural Graph Explorer v1 — zero-dependency, 2D Canvas.
   Directed, verified supplier→customer edges. Motion is visual only.
   Evidence proxy is NOT a purchasing share, statistical correlation or probability. */
(function(){
"use strict";
const canvas=document.getElementById("graphCanvas");
const root=document.getElementById("graphExplorer");
if(!canvas||!root)return;
const ctx=canvas.getContext("2d");
if(!ctx)return;
const $=id=>document.getElementById(id);
const esc=x=>String(x==null?"":x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safe=u=>typeof u==="string"&&/^https:\/\//.test(u)?u:null;
const colors={m7:"#86aaff",direct:"#48ead2",tier2:"#ae94ff",tier3:"#ffbf74",unknown:"#50637d"};
const m7=["AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA"];
const I={
 en:{title:"NEURAL SUPPLY GRAPH",sub:"Verified supplier → customer links · evidence-weighted only",find:"Search ticker or company…",fit:"Fit",layers:"Layers",orbit:"Orbit",all:"All 47 nodes",motion:"Flow",hint:"Drag nodes · scroll to zoom · click to trace paths",select:"Select a node to explore its upstream links and M7 paths.",unverified:"No verified path; economic exposure remains unknown.",direct:"Direct",indirect:"Indirect",paths:"documented paths",source:"Primary source",score:"Evidence proxy",links:"verified links",only:"Verified network",noLinks:"No verified relationship edges.",m7:"M7 customer",company:"Supplier",flow:"Directed supply path",noScores:"This is not a financial correlation or purchase percentage.",tier:"Tier",clear:"Clear focus"},
 "zh-CN":{title:"神经网络供应链图谱",sub:"已核验供应商 → 客户关系 · 仅证据加权",find:"搜索股票代码或公司…",fit:"适应画面",layers:"分层",orbit:"星系",all:"全部47节点",motion:"流动效果",hint:"拖动节点 · 滚轮缩放 · 点击追踪路径",select:"选择节点，查看上游关系与通往七巨头的证据路径。",unverified:"没有已核实路径；经济敞口仍未知。",direct:"直接",indirect:"间接",paths:"已核实路径",source:"原始来源",score:"证据代理值",links:"已核实关系",only:"仅证据网络",noLinks:"暂无核实的关系边。",m7:"七巨头客户",company:"供应商",flow:"有向供应路径",noScores:"这不是财务相关系数或采购百分比。",tier:"层级",clear:"清除聚焦"},
 fr:{title:"GRAPHE NEURONAL DES FOURNISSEURS",sub:"Liens fournisseur → client vérifiés, pondérés par les preuves",find:"Chercher titre ou entreprise…",fit:"Ajuster",layers:"Niveaux",orbit:"Orbite",all:"47 nœuds",motion:"Flux",hint:"Déplacer · zoomer · cliquer pour suivre les chemins",select:"Sélectionnez un nœud pour explorer les liens documentés.",unverified:"Aucun chemin vérifié ; exposition inconnue.",direct:"Direct",indirect:"Indirect",paths:"chemins vérifiés",source:"Source primaire",score:"Indice des preuves",links:"liens vérifiés",only:"Réseau vérifié",noLinks:"Aucun lien vérifié.",m7:"Client M7",company:"Fournisseur",flow:"Chemin orienté",noScores:"Ni corrélation financière, ni part d’achat.",tier:"Niveau",clear:"Effacer"},
 es:{title:"GRAFO NEURONAL DE PROVEEDORES",sub:"Relaciones proveedor → cliente verificadas",find:"Buscar símbolo o empresa…",fit:"Ajustar",layers:"Capas",orbit:"Órbita",all:"47 nodos",motion:"Flujo",hint:"Arrastrar · ampliar · seleccionar rutas",select:"Seleccione un nodo para explorar sus relaciones.",unverified:"Sin ruta verificada; exposición desconocida.",direct:"Directo",indirect:"Indirecto",paths:"rutas verificadas",source:"Fuente primaria",score:"Índice de evidencia",links:"relaciones verificadas",only:"Red verificada",noLinks:"No hay relaciones verificadas.",m7:"Cliente M7",company:"Proveedor",flow:"Ruta dirigida",noScores:"No es correlación financiera ni porcentaje de compras.",tier:"Nivel",clear:"Limpiar"},
 ja:{title:"ニューラル供給ネットワーク",sub:"確認済みの供給者 → 顧客関係・根拠に基づく重み",find:"銘柄・企業を検索…",fit:"全体表示",layers:"階層",orbit:"軌道",all:"全47ノード",motion:"流動表示",hint:"ドラッグ・ズーム・クリックで経路追跡",select:"ノードを選択してサプライチェーン経路を確認。",unverified:"検証済み経路なし。経済的な関係は不明。",direct:"直接",indirect:"間接",paths:"確認済み経路",source:"一次資料",score:"根拠代理指数",links:"確認済み関係",only:"確認済みネットワーク",noLinks:"確認済み関係がありません。",m7:"M7顧客",company:"サプライヤー",flow:"有向供給経路",noScores:"財務的な相関係数・購買割合ではありません。",tier:"階層",clear:"選択解除"}
};
let state={nodes:[],edges:[],paths:[],data:null,selected:null,hover:null,selectedPath:null,showAll:false,motion:!matchMedia("(prefers-reduced-motion: reduce)").matches,mode:"layers",scale:1,panX:0,panY:0,drag:null,frame:0,lastSignature:"",width:1,height:1,dpr:1,initialized:false};
const world={w:1470,h:870};
let lang=()=>window.M7_I18N&&I[window.M7_I18N.language]?window.M7_I18N.language:"en";
const t=k=>(I[lang()]||I.en)[k]||I.en[k]||k;
function nodeById(id){return state.nodes.find(n=>n.id===id);}
function activeGraph(){return $("network")?.classList.contains("active");}
function visibleNodes(){return state.nodes.filter(n=>state.showAll||n.tier!==4);}
function activeNode(id){return state.nodes.some(n=>n.id===id&& (state.showAll||n.tier!==4));}
function setText(id,value){const e=$(id);if(e)e.textContent=value;}
function updateLanguage(){
 setText("gHeader",t("title"));setText("gSub",t("sub"));setText("gFit",t("fit"));
 setText("gLayout",state.mode==="layers"?t("orbit"):t("layers"));setText("gClear",t("clear"));
 setText("gHint",t("hint"));setText("gNote",t("noScores"));
 const q=$("gSearch");if(q)q.placeholder=t("find");
 const v=$("gAllLabel");if(v)v.textContent=t("all");
 const f=$("gFlowLabel");if(f)f.textContent=t("motion");
 renderInfo();
}
function signature(d){return String(d?.retrieved_at_utc||"")+"|"+String(d?.model_version||"")+"|"+(d?.network?.verified_edges?.length||0);}
function setData(data){
 if(!data)return;
 if(state.data===data && state.lastSignature===signature(data)){return;}
 const previous=state.selected;
 state.data=data;state.lastSignature=signature(data);
 const suppliers=(data.suppliers||[]).map(s=>({id:s.ticker,name:s.name||s.ticker,type:"vendor",sector:s.sector||"",value:s.network_reach}));
 const customers=m7.map(id=>({id,name:id,type:"m7"}));
 const paths=(data.network?.paths||[]).filter(p=>Array.isArray(p.path)&&p.path.length>=2);
 const edges=(data.network?.verified_edges||[]).filter(e=>e.verified===true&&safe(e.source)&&e.date && e.date<=String(data.as_of||"9999-12-31"));
 const tier=new Map();
 for(const p of paths){if(p.supplier&&p.hops>=1 && p.hops<=3)tier.set(p.supplier,Math.min(tier.get(p.supplier)||4,p.hops));}
 state.paths=paths;
 state.edges=edges.map((e,i)=>({id:i,from:e.supplier,to:e.customer,weight:Number(e.proxy_weight)||.8,source:e.source,date:e.date,kind:e.kind,raw:e})).filter(e=>suppliers.some(n=>n.id===e.from)&&(suppliers.some(n=>n.id===e.to)||m7.includes(e.to)));
 const nodes=[...suppliers,...customers].map(n=>({...n,tier:n.type==="m7"?0:(tier.get(n.id)||4),x:0,y:0,tx:0,ty:0,r:n.type==="m7"?19:12,dragged:false}));
 state.nodes=nodes;
 layout(true);
 setText("gNodeTotal",String(nodes.length));setText("gEdgeTotal",String(state.edges.length));
 setText("gPathTotal",String(paths.length));setText("gModel",data.network?.graph_version||"v3");
 state.selected=nodes.some(n=>n.id===previous)?previous:null;
 if(state.selected && !activeNode(state.selected))state.selected=null;
 if(state.selectedPath && !paths.some(p=>p.path.join(">")===state.selectedPath))state.selectedPath=null;
 resize(true);renderInfo();
}
function layout(fresh){
 const groups=[[],[],[],[],[]];for(const n of state.nodes)groups[n.tier].push(n);
 const xs=state.mode==="layers"?[1240,925,650,380,122]:[740,740,740,740,740];
 for(let tier=0;tier<=4;tier++){
  let group=groups[tier];
  group.sort((a,b)=>a.id.localeCompare(b.id));
  group.forEach((n,i)=>{
    let targetX,targetY;
    if(state.mode==="layers"){
     const slot=(world.h-120)/(group.length+1);
     targetX=xs[tier]+Math.sin(i*2.17+tier*1.8)*(tier===4?28:38);
     targetY=60+slot*(i+1);
    }else{
     const radius=[120,260,390,495,625][tier];
     const angle=-Math.PI/2+2*Math.PI*(i+.18*tier)/(group.length||1);
     targetX=750+radius*Math.cos(angle);
     targetY=438+radius*.64*Math.sin(angle);
    }
    n.tx=targetX;n.ty=targetY;
    if(fresh||(!n.dragged&&(!Number.isFinite(n.x)||n.x===0))){n.x=targetX;n.y=targetY;}
  });
 }
}
function resize(reset=false){
 const bounds=canvas.getBoundingClientRect();
 if(!bounds.width)return;
 const w=Math.max(300,bounds.width),h=Math.max(420,bounds.height);
 const dpr=Math.min(window.devicePixelRatio||1,2);
 if(w!==state.width||h!==state.height||dpr!==state.dpr){
  state.width=w;state.height=h;state.dpr=dpr;
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  if(!state.initialized)reset=true;
 }
 if(reset||!state.initialized){
  const fit=Math.min(w/world.w,h/world.h)*.92;
  state.scale=Math.max(.28,fit);
  state.panX=(w-world.w*state.scale)/2;
  state.panY=(h-world.h*state.scale)/2;
  state.initialized=true;
 }
 paint(performance.now());
}
function point(e){const b=canvas.getBoundingClientRect();return {x:e.clientX-b.left,y:e.clientY-b.top};}
function toWorld(p){return {x:(p.x-state.panX)/state.scale,y:(p.y-state.panY)/state.scale};}
function nearNode(p){
 const w=toWorld(p);let result=null,dist=1e9;
 for(const n of visibleNodes()){
  const d=Math.hypot(n.x-w.x,n.y-w.y);
  if(d<Math.max(n.r+12,26/state.scale) && d<dist){result=n;dist=d;}
 }
 return result;
}
function clientWeight(n){
 const d=state.data?.network?.exposures?.[n.id];
 return d?.verified_in_graph?Number(d.reach).toFixed(3):"Unknown";
}
function pathForNode(node){
 if(!node)return[];
 const all=state.paths;
 if(node.type==="m7")return all.filter(p=>p.customer===node.id);
 return all.filter(p=>p.supplier===node.id||p.path.includes(node.id));
}
function highlightSet(){
 if(state.selectedPath){
  const p=state.paths.find(p=>p.path.join(">")===state.selectedPath);
  if(p)return new Set(p.path);
 }
 const anchor=state.hover||state.selected;
 if(!anchor)return null;
 let s=new Set([anchor]);
 const paths=pathForNode(nodeById(anchor));
 for(const p of paths)for(const id of p.path)s.add(id);
 for(const e of state.edges)if(e.from===anchor||e.to===anchor){s.add(e.from);s.add(e.to);}
 return s;
}
function curved(ctx,a,b,offset=0){
 const dx=b.x-a.x,dy=b.y-a.y;
 const curve=Math.min(85,Math.abs(dx)*.11);
 const cx=(a.x+b.x)/2,cy=(a.y+b.y)/2-curve+offset;
 ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.quadraticCurveTo(cx,cy,b.x,b.y);
 return {cx,cy};
}
function qpoint(a,b,cx,cy,t){
 const j=1-t;
 return {x:j*j*a.x+2*j*t*cx+t*t*b.x,y:j*j*a.y+2*j*t*cy+t*t*b.y};
}
function paint(now){
 if(!canvas.width || !canvas.height)return;
 ctx.setTransform(state.dpr,0,0,state.dpr,0,0);
 const W=state.width,H=state.height;
 ctx.clearRect(0,0,W,H);
 const grad=ctx.createRadialGradient(W*.48,H*.42,20,W*.48,H*.42,W*.72);
 grad.addColorStop(0,"#101e3a");grad.addColorStop(.55,"#091528");grad.addColorStop(1,"#07101f");
 ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
 ctx.strokeStyle="rgba(109,160,215,.065)";ctx.lineWidth=1;
 for(let x=0;x<W;x+=36){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
 for(let y=0;y<H;y+=36){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
 for(let i=0;i<90;i++){
  const x=((i*127.7)%1000)/1000*W,y=((i*83.9)%1000)/1000*H;
  ctx.fillStyle="rgba(132,178,231,"+(.08+(i%5)*.032)+")";
  ctx.fillRect(x,y,1.2,1.2);
 }
 ctx.save();ctx.translate(state.panX,state.panY);ctx.scale(state.scale,state.scale);
 if(state.mode==="layers"){
  const guides=[[122,"UNVERIFIED"],[380,"TIER 3"],[650,"TIER 2"],[925,"DIRECT"],[1240,"MAGNIFICENT 7"]];
  for(const [x,label] of guides){
   ctx.strokeStyle="rgba(110,175,226,.12)";ctx.setLineDash([5,13]);
   ctx.beginPath();ctx.moveTo(x,8);ctx.lineTo(x,world.h-8);ctx.stroke();ctx.setLineDash([]);
   ctx.fillStyle="rgba(154,184,229,.45)";ctx.font="700 12px system-ui";
   ctx.textAlign="center";ctx.fillText(label,x,28);
  }
 }
 const highlighted=highlightSet();
 for(const e of state.edges){
  const a=nodeById(e.from),b=nodeById(e.to);
  if(!a||!b||!activeNode(a.id)||!activeNode(b.id))continue;
  const isFocus=!highlighted||(highlighted.has(a.id)&&highlighted.has(b.id));
  const pathOn=state.selectedPath&&state.selectedPath.split(">").some((id,i,arr)=>arr[i+1]===b.id&&id===a.id);
  const opacity=isFocus?(state.selectedPath?(pathOn?1:.08):.55):.07;
  const pts=curved(ctx,a,b);
  ctx.strokeStyle=pathOn?"rgba(255,203,130,.88)":"rgba(87,217,229,"+opacity+")";
  ctx.lineWidth=pathOn?3.8:(isFocus?2.1:1.0);
  ctx.shadowBlur=pathOn?23:(isFocus?10:0);ctx.shadowColor=pathOn?"#ffc174":"#42dcf4";
  ctx.stroke();ctx.shadowBlur=0;
  if(isFocus&&state.motion){
   const travel=(now*.00014+e.id*.133)%1;
   const q=qpoint(a,b,pts.cx,pts.cy,travel);
   const halo=ctx.createRadialGradient(q.x,q.y,0,q.x,q.y,pathOn?12:8);
   halo.addColorStop(0,pathOn?"rgba(255,232,171,.98)":"rgba(172,249,255,.9)");
   halo.addColorStop(1,"rgba(61,225,241,0)");
   ctx.fillStyle=halo;ctx.beginPath();ctx.arc(q.x,q.y,pathOn?12:8,0,Math.PI*2);ctx.fill();
   ctx.fillStyle=pathOn?"#ffe0a1":"#a4f9ff";
   ctx.beginPath();ctx.arc(q.x,q.y,2.4,0,Math.PI*2);ctx.fill();
  }
 }
 for(const n of visibleNodes()){
  const focus=!highlighted||highlighted.has(n.id);
  const chosen=state.selected===n.id || state.hover===n.id;
  const color=colors[n.type==="m7"?"m7":n.tier===1?"direct":n.tier===2?"tier2":n.tier===3?"tier3":"unknown"];
  const radius=n.r+(chosen?2:0);
  ctx.globalAlpha=focus?1:.20;
  const glow=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,radius*3.1);
  glow.addColorStop(0,color+"85");glow.addColorStop(.37,color+"26");glow.addColorStop(1,color+"00");
  ctx.fillStyle=glow;ctx.beginPath();ctx.arc(n.x,n.y,radius*3.1,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#101d32";ctx.strokeStyle=color;ctx.lineWidth=n.type==="m7"?2.6:1.7;
  ctx.beginPath();ctx.arc(n.x,n.y,radius,0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.fillStyle=color;ctx.beginPath();ctx.arc(n.x,n.y,n.type==="m7"?5.3:3.8,0,Math.PI*2);ctx.fill();
  if(chosen){
   const pulse=state.motion?(2+Math.sin(now*.003)*2):2;
   ctx.strokeStyle=color+"a9";ctx.lineWidth=1.5;
   ctx.beginPath();ctx.arc(n.x,n.y,radius+9+pulse,0,Math.PI*2);ctx.stroke();
  }
  ctx.textAlign="center";ctx.font=(n.type==="m7"?"800 ":"700 ")+"13px system-ui,sans-serif";
  ctx.fillStyle=n.type==="m7"?"#d5e7ff":"#dceef7";
  ctx.fillText(n.id,n.x,n.y+radius+19);
  ctx.globalAlpha=1;
 }
 ctx.restore();
 // Viewport HUD.
 ctx.font="11px system-ui";ctx.fillStyle="rgba(158,194,229,.58)";
 ctx.textAlign="left";ctx.fillText("M7 / GRAPH INTELLIGENCE  •  VERIFIED EVIDENCE",18,H-17);
 ctx.textAlign="right";ctx.fillText(Math.round(state.scale*100)+"%  /  "+state.mode.toUpperCase(),W-18,H-17);
}
function renderInfo(){
 const panel=$("gInsight");if(!panel)return;
 const n=nodeById(state.selected);
 if(!n){panel.innerHTML='<div class="g-placeholder"><span class="g-orb">◉</span><strong>'+esc(t("title"))+'</strong><p>'+esc(t("select"))+'</p></div>';return;}
 const paths=pathForNode(n).sort((a,b)=>b.weight-a.weight).slice(0,12);
 const badge=n.type==="m7"?t("m7"):(n.tier===4?t("unverified"):t("tier")+" "+n.tier);
 let html='<div class="g-insight-header"><div><div class="g-kicker">'+esc(badge)+'</div><h3>'+esc(n.id)+'</h3><div class="g-insight-name">'+esc(n.name)+'</div></div><span class="g-icon-badge">'+(n.type==="m7"?"M7":"T"+n.tier)+'</span></div>';
 if(n.type!=="m7")html+='<div class="g-scoreline"><span>'+esc(t("score"))+'</span><strong>'+esc(clientWeight(n))+'</strong></div>';
 if(!paths.length){html+='<p class="g-empty-info">'+esc(t("unverified"))+'</p>';}
 else{
  html+='<div class="g-section-title">'+paths.length+' '+esc(t("paths"))+'</div>';
  html+='<div class="g-path-list">'+paths.map(p=>{
   const active=state.selectedPath===p.path.join(">")?' active':'';
   return '<button type="button" class="g-path-entry'+active+'" data-graph-path="'+esc(p.path.join(">"))+'"><span>'+esc(p.path.join(" → "))+'</span><b>'+Number(p.weight).toFixed(3)+'</b></button>';
  }).join("")+'</div>';
  const chosen=state.paths.find(p=>p.path.join(">")===state.selectedPath);
  if(chosen && (chosen.path.includes(n.id))){
   html+='<div class="g-proof"><b>'+esc(t("flow"))+'</b><div>'+esc(chosen.path.join(" → "))+'</div><small>'+esc(t("noScores"))+'</small>'+chosen.sources.map((u,i)=>safe(u)?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(t("source"))+' '+(i+1)+' · '+esc(chosen.dates?.[i]||"")+' ↗</a>':"").join("")+'</div>';
  }
 }
 panel.innerHTML=html;
 panel.querySelectorAll("[data-graph-path]").forEach(button=>{
  button.addEventListener("click",()=>{
   const key=button.getAttribute("data-graph-path");
   state.selectedPath=state.selectedPath===key?null:key;renderInfo();paint(performance.now());
  });
 });
}
function selectNode(n){
 state.selected=n?.id||null;state.selectedPath=null;state.hover=null;
 if(n&&n.type==="vendor" && $("networkFilter")){
  $("networkFilter").value=n.id;
  // Keep the original linked relationship evidence panel synced.
  if(typeof renderRelations==="function")renderRelations();
 }
 renderInfo();paint(performance.now());
}
function setHover(n,p){
 const id=n?.id||null;
 if(state.hover===id)return;
 state.hover=id;
 canvas.style.cursor=n?"pointer":state.drag?"grabbing":"grab";
 const tooltip=$("gTooltip");
 if(!tooltip)return;
 if(!n){tooltip.hidden=true;return;}
 tooltip.hidden=false;
 tooltip.style.left=Math.max(9,Math.min(state.width-205,p.x+16))+"px";
 tooltip.style.top=Math.max(8,Math.min(state.height-90,p.y-18))+"px";
 tooltip.innerHTML='<strong>'+esc(n.id)+'</strong><small>'+esc(n.name)+' · '+esc(n.type==="m7"?t("m7"):n.tier===4?t("unverified"):t("tier")+" "+n.tier)+'</small>';
}
canvas.addEventListener("pointerdown",e=>{
 if(e.button!==0 && e.pointerType==="mouse")return;
 const p=point(e),n=nearNode(p);
 state.drag={node:n?.id||null,x:p.x,y:p.y,panX:state.panX,panY:state.panY,nx:n?.x,ny:n?.y,moved:false};
 try{canvas.setPointerCapture(e.pointerId);}catch(_){}
});
canvas.addEventListener("pointermove",e=>{
 const p=point(e);
 if(state.drag){
  const d=state.drag;if(Math.hypot(p.x-d.x,p.y-d.y)>5)d.moved=true;
  if(d.moved){
   if(d.node){const n=nodeById(d.node);if(n){n.x=d.nx+(p.x-d.x)/state.scale;n.y=d.ny+(p.y-d.y)/state.scale;n.dragged=true;}}
   else{state.panX=d.panX+(p.x-d.x);state.panY=d.panY+(p.y-d.y);}
   setHover(null,p);
  }
 }else setHover(nearNode(p),p);
});
canvas.addEventListener("pointerup",e=>{
 const d=state.drag;
 if(!d)return;
 if(!d.moved){const n=d.node?nodeById(d.node):nearNode(point(e));selectNode(n);}
 state.drag=null;
 try{canvas.releasePointerCapture(e.pointerId);}catch(_){}
});
canvas.addEventListener("pointercancel",()=>{state.drag=null;});
canvas.addEventListener("pointerleave",()=>{if(!state.drag){state.hover=null;if($("gTooltip"))$("gTooltip").hidden=true;}});
canvas.addEventListener("wheel",e=>{
 e.preventDefault();
 const p=point(e),before=toWorld(p);
 state.scale=Math.max(.22,Math.min(2.8,state.scale*Math.exp(-e.deltaY*.0013)));
 state.panX=p.x-before.x*state.scale;state.panY=p.y-before.y*state.scale;
 paint(performance.now());
},{passive:false});
canvas.addEventListener("dblclick",()=>resize(true));
$("gFit")?.addEventListener("click",()=>resize(true));
$("gClear")?.addEventListener("click",()=>{
 state.selectedPath=null;state.selected=null;if($("gSearch"))$("gSearch").value="";
 if($("networkFilter"))$("networkFilter").value="all";
 renderInfo();paint(performance.now());
});
$("gLayout")?.addEventListener("click",()=>{
 state.mode=state.mode==="layers"?"orbit":"layers";
 for(const n of state.nodes)n.dragged=false;
 layout(true);resize(true);updateLanguage();
});
$("gAll")?.addEventListener("change",e=>{state.showAll=e.target.checked;paint(performance.now());});
$("gFlow")?.addEventListener("change",e=>{state.motion=e.target.checked;paint(performance.now());});
$("gPlus")?.addEventListener("click",()=>{state.scale=Math.min(3,state.scale*1.2);paint(performance.now());});
$("gMinus")?.addEventListener("click",()=>{state.scale=Math.max(.22,state.scale/1.2);paint(performance.now());});
$("gSearch")?.addEventListener("input",e=>{
 const q=e.target.value.trim().toLowerCase();
 if(!q)return;
 const n=state.nodes.find(n=>n.id.toLowerCase()===q)||state.nodes.find(n=>n.id.toLowerCase().startsWith(q)||n.name.toLowerCase().includes(q));
 if(n){if(n.tier===4)state.showAll=true;$("gAll").checked=state.showAll;selectNode(n);}
});
const languageSelector=$("m7Language");
languageSelector?.addEventListener("change",()=>setTimeout(updateLanguage,0));
new ResizeObserver(()=>{if(activeGraph())resize(false);}).observe(root);
const _goto=window.M7GraphViz||null;
window.M7GraphViz={setData,resize,focus(id){const n=nodeById(id);if(n){if(n.tier===4)state.showAll=true;selectNode(n);}},state};
const oldSVG=$("networkSvg");
if(oldSVG)oldSVG.style.display="none";
root.classList.add("g-ready");
setData(window.M7_LIVE_DATA||null);
updateLanguage();
(function frame(now){
 state.frame=requestAnimationFrame(frame);
 if(!activeGraph()||document.hidden)return;
 // Keep motion visual and low-cost, without mutating underlying research data.
 if(state.motion||state.drag)paint(now);
}) (performance.now());
})();