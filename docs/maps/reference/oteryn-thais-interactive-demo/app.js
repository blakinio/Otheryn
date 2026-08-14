const BOUNDS={minX:32280,minY:32155,maxX:32440,maxY:32305,z:7};
const W=BOUNDS.maxX-BOUNDS.minX+1,H=BOUNDS.maxY-BOUNDS.minY+1;
let scale=4, tx=0, ty=0, dragging=false, sx=0,sy=0,stx=0,sty=0, npcs=[], selected=null;
const shell=document.querySelector('.map-shell'), vp=document.querySelector('.viewport'), markers=document.querySelector('.markers'), img=document.querySelector('.map-img');
function apply(){vp.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`; document.querySelector('#zoomVal').textContent=Math.round(scale*100)+'%'; updateHash();}
function centerMap(){const r=shell.getBoundingClientRect();tx=(r.width-W*scale)/2;ty=(r.height-H*scale)/2;apply();}
function worldToPx(x,y){return [x-BOUNDS.minX,y-BOUNDS.minY]}
function renderMarkers(){
 markers.innerHTML='';
 const enabled=document.querySelector('#layerNpc').checked;
 if(!enabled)return;
 npcs.filter(n=>n.z===7&&n.x>=BOUNDS.minX&&n.x<=BOUNDS.maxX&&n.y>=BOUNDS.minY&&n.y<=BOUNDS.maxY).forEach(n=>{
   const [x,y]=worldToPx(n.x,n.y), e=document.createElement('div');e.className='marker';e.style.left=x+'px';e.style.top=y+'px';
   e.innerHTML=`<span class="tip">${esc(n.name)} · ${n.x}, ${n.y}, ${n.z}</span>`;
   e.onclick=(ev)=>{ev.stopPropagation();selectNpc(n,e)};markers.appendChild(e);
 });
 document.querySelector('#npcCount').textContent=markers.children.length;
}
function selectNpc(n,e){selected=n;document.querySelectorAll('.marker').forEach(m=>m.classList.remove('active'));if(e)e.classList.add('active');
 document.querySelector('#info').innerHTML=`<div class="info-title"><div class="info-icon">●</div><div><div class="info-name">${esc(n.name)}</div><div class="green" style="font-size:11px">NPC · źródło Canary</div></div></div>
 <div class="kv"><b>Pozycja</b><span>${n.x}, ${n.y}, ${n.z}</span></div><div class="kv"><b>Spawn time</b><span>${n.spawnTime} s</span></div>
 ${n.note?`<div class="kv"><b>Uwagi źródłowe</b><span>${esc(n.note)}</span></div>`:''}
 <div class="section source"><b>Provenance</b><br>blakinio/canary@cfca0e11a000535cf7f611c89f14aabdad360cd3<br>data-otservbr-global/world/otservbr-npc.xml</div>`;
 centerOn(n.x,n.y);
}
function centerOn(x,y){const r=shell.getBoundingClientRect(),p=worldToPx(x,y);tx=r.width/2-p[0]*scale;ty=r.height/2-p[1]*scale;apply();}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function setScale(ns,clientX=null,clientY=null){ns=Math.max(2,Math.min(9,ns));const r=shell.getBoundingClientRect(),mx=(clientX??(r.left+r.width/2))-r.left,my=(clientY??(r.top+r.height/2))-r.top;const wx=(mx-tx)/scale,wy=(my-ty)/scale;scale=ns;tx=mx-wx*scale;ty=my-wy*scale;apply();}
shell.addEventListener('wheel',e=>{e.preventDefault();setScale(scale+(e.deltaY<0?.5:-.5),e.clientX,e.clientY)},{passive:false});
shell.addEventListener('mousedown',e=>{dragging=true;shell.classList.add('dragging');sx=e.clientX;sy=e.clientY;stx=tx;sty=ty});
window.addEventListener('mousemove',e=>{if(dragging){tx=stx+e.clientX-sx;ty=sty+e.clientY-sy;apply()} const r=shell.getBoundingClientRect(),wx=Math.floor((e.clientX-r.left-tx)/scale)+BOUNDS.minX,wy=Math.floor((e.clientY-r.top-ty)/scale)+BOUNDS.minY;if(wx>=BOUNDS.minX&&wx<=BOUNDS.maxX&&wy>=BOUNDS.minY&&wy<=BOUNDS.maxY){document.querySelector('#liveCoord').textContent=`${wx}, ${wy}, 7`}});
window.addEventListener('mouseup',()=>{dragging=false;shell.classList.remove('dragging')});
shell.addEventListener('click',e=>{if(e.target.closest('.marker'))return;const r=shell.getBoundingClientRect(),x=Math.floor((e.clientX-r.left-tx)/scale)+BOUNDS.minX,y=Math.floor((e.clientY-r.top-ty)/scale)+BOUNDS.minY;if(x>=BOUNDS.minX&&x<=BOUNDS.maxX&&y>=BOUNDS.minY&&y<=BOUNDS.maxY){document.querySelector('#picked').textContent=`${x}, ${y}, 7`;document.querySelector('#info').innerHTML=`<div class="empty-info"><b>Tile</b><br>${x}, ${y}, 7<br><br>Kliknij zielony marker, aby zobaczyć zweryfikowanego NPC.</div>`;location.hash=`${x},${y},7:${scale.toFixed(1)}`}});
function updateHash(){if(selected)location.hash=`${selected.x},${selected.y},${selected.z}:${scale.toFixed(1)}`}
document.querySelector('#plus').onclick=()=>setScale(scale+.5);document.querySelector('#minus').onclick=()=>setScale(scale-.5);document.querySelector('#fit').onclick=centerMap;document.querySelector('#layerNpc').onchange=renderMarkers;
document.querySelector('#copy').onclick=async()=>{const t=document.querySelector('#picked').textContent;try{await navigator.clipboard.writeText(t);document.querySelector('#copy').textContent='Skopiowano';setTimeout(()=>document.querySelector('#copy').textContent='Kopiuj kordy',900)}catch{}}
const search=document.querySelector('#search'),results=document.querySelector('#results');
search.oninput=()=>{const q=search.value.trim().toLowerCase();results.innerHTML='';if(!q){results.style.display='none';return}npcs.filter(n=>n.name.toLowerCase().includes(q)&&n.x>=BOUNDS.minX&&n.x<=BOUNDS.maxX&&n.y>=BOUNDS.minY&&n.y<=BOUNDS.maxY).slice(0,12).forEach(n=>{const d=document.createElement('div');d.className='result';d.textContent=`${n.name} — ${n.x}, ${n.y}, ${n.z}`;d.onclick=()=>{search.value=n.name;results.style.display='none';selectNpc(n)};results.appendChild(d)});results.style.display=results.children.length?'block':'none'};
Promise.all([fetch('npcs.json').then(r=>r.json())]).then(([data])=>{npcs=data;renderMarkers();centerMap();});
window.addEventListener('resize',centerMap);
