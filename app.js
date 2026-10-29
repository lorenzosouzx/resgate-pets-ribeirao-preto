const bairros={Norte:['Jardim Interlagos','Jardim Helena','Parque dos Lagos','Alto do Ipiranga'],Sul:['Jardim Paulista','Vila Tibério','Campos Elíseos'],Leste:['Jardim Aeroporto','Quintino Facci II','Parque Ribeirão','Jardim Botânico'],Oeste:['Alto da Boa Vista','Nova Aliança'],Centro:['Centro','Vila Seixas','Jardim América']};
const especies=['Cão','Gato','Animal Silvestre','Outro'];
const statuses=['Aguardando Resgate','Resgatado','Em Tratamento','Adotado','Óbito'];
const situacoes=['Abandono','Maus-tratos','Atropelamento','Doença','Ferimento','Subnutrição','Preso/Enroscado'];
const zonas=Object.keys(bairros); const todosBairros=zonas.flatMap(z=>bairros[z]);
let seed=42; const rnd=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296);
const pick=a=>a[Math.floor(rnd()*a.length)];
const dados=Array.from({length:260},(_,i)=>{const zona=pick(zonas);return{id:`RP-${String(i+1).padStart(4,'0')}`,zona,bairro:pick(bairros[zona]),especie:pick(especies),situacao:pick(situacoes),status:pick(statuses)}});
const ids=['zona','bairro','especie','status']; const el=Object.fromEntries(ids.map(id=>[id,document.getElementById(id)]));
function options(select,values,all){select.innerHTML=`<option value="">${all}</option>`+values.map(v=>`<option>${v}</option>`).join('')}
options(el.zona,zonas,'Todas as zonas');options(el.bairro,todosBairros,'Todos os bairros');options(el.especie,especies,'Todas as espécies');options(el.status,statuses,'Todos os status');
el.zona.addEventListener('change',()=>{const atual=el.bairro.value;options(el.bairro,el.zona.value?bairros[el.zona.value]:todosBairros,'Todos os bairros');if([...el.bairro.options].some(o=>o.value===atual))el.bairro.value=atual;render()});
['bairro','especie','status'].forEach(id=>el[id].addEventListener('change',render));
document.getElementById('clear').addEventListener('click',()=>{ids.forEach(id=>el[id].value='');options(el.bairro,todosBairros,'Todos os bairros');render()});
document.getElementById('theme-toggle').addEventListener('click',()=>{document.body.classList.toggle('dark');document.getElementById('theme-toggle').textContent=document.body.classList.contains('dark')?'☀️ Modo claro':'🌙 Modo escuro';render()});
const count=(data,key)=>data.reduce((a,x)=>(a[x[key]]=(a[x[key]]||0)+1,a),{});
const filtered=()=>dados.filter(x=>(!el.zona.value||x.zona===el.zona.value)&&(!el.bairro.value||x.bairro===el.bairro.value)&&(!el.especie.value||x.especie===el.especie.value)&&(!el.status.value||x.status===el.status.value));
function layout(height){const dark=document.body.classList.contains('dark');return{height,margin:{l:45,r:20,t:10,b:45},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:dark?'#eef4ff':'#46536a',size:11},xaxis:{gridcolor:dark?'#2d3a55':'#e8edf4'},yaxis:{gridcolor:dark?'#2d3a55':'#e8edf4'},showlegend:false}}
function render(){const d=filtered();const cStatus=count(d,'status');const cards=[['📋','Ocorrências',d.length,'#1769b0'],['🚨','Aguardando',cStatus['Aguardando Resgate']||0,'#e63946'],['✅','Resgatados',cStatus.Resgatado||0,'#2a9d8f'],['🏥','Em tratamento',cStatus['Em Tratamento']||0,'#e0a800'],['🏠','Adotados',cStatus.Adotado||0,'#6c5ce7']];document.getElementById('kpis').innerHTML=cards.map(([i,n,v,c])=>`<article class="kpi"><span>${i} ${n}</span><b style="color:${c}">${v}</b><span>registros filtrados</span></article>`).join('');
  const cb=count(d,'bairro'), bz=Object.entries(cb).sort((a,b)=>a[1]-b[1]);Plotly.react('chart-bairros',[{type:'bar',orientation:'h',y:bz.map(x=>x[0]),x:bz.map(x=>x[1]),marker:{color:'#1769b0'},hovertemplate:'%{y}: %{x}<extra></extra>'}],layout(350),{displayModeBar:false,responsive:true});
  const cz=count(d,'zona');Plotly.react('chart-zonas',[{type:'bar',x:Object.keys(cz),y:Object.values(cz),marker:{color:['#e63946','#e9c46a','#2c7be5','#2a9d8f','#6c5ce7']},hovertemplate:'%{x}: %{y}<extra></extra>'}],layout(350),{displayModeBar:false,responsive:true});
  pie('chart-especies',count(d,'especie'),300);barH('chart-status',count(d,'status'),300);pie('chart-situacoes',count(d,'situacao'),300);
  document.getElementById('result-count').textContent=`${d.length} resultados`;document.getElementById('records').innerHTML=d.slice(0,100).map(x=>`<tr><td>${x.id}</td><td>${x.bairro}</td><td>${x.zona}</td><td>${x.especie}</td><td>${x.situacao}</td><td>${x.status}</td></tr>`).join('')||'<tr><td colspan="6">Nenhum registro encontrado.</td></tr>'}
function pie(id,obj,h){Plotly.react(id,[{type:'pie',labels:Object.keys(obj),values:Object.values(obj),hole:.45,textinfo:'percent',hovertemplate:'%{label}: %{value}<extra></extra>'}],{...layout(h),legend:{orientation:'h',y:-.15},showlegend:true,margin:{l:10,r:10,t:10,b:60}},{displayModeBar:false,responsive:true})}
function barH(id,obj,h){const a=Object.entries(obj).sort((x,y)=>x[1]-y[1]);Plotly.react(id,[{type:'bar',orientation:'h',y:a.map(x=>x[0]),x:a.map(x=>x[1]),marker:{color:'#2a9d8f'},hovertemplate:'%{y}: %{x}<extra></extra>'}],layout(h),{displayModeBar:false,responsive:true})}
window.addEventListener('load',render);

