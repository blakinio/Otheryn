"""Write the dependency-free static atlas viewer."""

from __future__ import annotations

from pathlib import Path

VIEWER_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Otheryn full map atlas</title><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#111;color:#eee;font:14px system-ui}canvas{position:absolute;inset:0}
#controls{position:absolute;z-index:2;left:12px;top:12px;background:#181818e8;padding:10px;border:1px solid #555;border-radius:6px;display:grid;gap:6px}
label{display:flex;gap:5px;align-items:center}input[type=number]{width:74px}button,select,input{background:#292929;color:#eee;border:1px solid #666;padding:3px}
#status{position:absolute;z-index:2;right:12px;bottom:12px;background:#181818dd;padding:6px}
</style></head><body><canvas id="map"></canvas><div id="controls">
<label>Floor <select id="floor"></select></label><div><input id="x" type="number" placeholder="X"><input id="y" type="number" placeholder="Y"><input id="z" type="number" min="0" max="15" placeholder="Z"><button id="jump">Jump</button></div>
<label><input type="checkbox" data-overlay="actionIds"> AID</label><label><input type="checkbox" data-overlay="uniqueIds"> UID</label>
<label><input type="checkbox" data-overlay="teleports"> Teleports</label><label><input type="checkbox" data-overlay="houseDoors"> House doors</label>
<label><input type="checkbox" data-overlay="monsterSpawns"> Monsters</label><label><input type="checkbox" data-overlay="npcSpawns"> NPCs</label>
</div><div id="status">Loading manifest…</div><script>
const canvas=document.querySelector('#map'),ctx=canvas.getContext('2d'),status=document.querySelector('#status'),floorSelect=document.querySelector('#floor');
let manifest,chunks=[],z=7,scale=.18,centerX=32360,centerY=32230,drag=null,overlays={},enabled=new Set(),images=new Map();
function resize(){canvas.width=innerWidth*devicePixelRatio;canvas.height=innerHeight*devicePixelRatio;draw()} addEventListener('resize',resize);
function worldToScreen(x,y){return[(x-centerX)*32*scale+canvas.width/2,(y-centerY)*32*scale+canvas.height/2]}
function screenToWorld(x,y){return[(x-canvas.width/2)/(32*scale)+centerX,(y-canvas.height/2)/(32*scale)+centerY]}
function loadImage(path){if(!images.has(path)){const image=new Image;image.src=path;image.onload=draw;images.set(path,image)}return images.get(path)}
function draw(){if(!manifest)return;ctx.clearRect(0,0,canvas.width,canvas.height);for(const c of chunks){if(c.z!==z)continue;const [sx,sy]=worldToScreen(c.bounds[0],c.bounds[2]),w=c.imageWidth*scale,h=c.imageHeight*scale;if(sx>canvas.width||sy>canvas.height||sx+w<0||sy+h<0)continue;const image=loadImage(c.path);if(image.complete)ctx.drawImage(image,sx,sy,w,h)}
 for(const group of enabled)for(const fact of overlays[group]||[]){const p=fact.position;if(!p||p.z!==z)continue;const [sx,sy]=worldToScreen(p.x+.5,p.y+.5);ctx.fillStyle=group==='teleports'?'#00ffff':group==='monsterSpawns'?'#ff3333':group==='npcSpawns'?'#33ff66':'#ffff00';ctx.beginPath();ctx.arc(sx,sy,Math.max(3,5*scale),0,Math.PI*2);ctx.fill()}}
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY,centerX,centerY];canvas.setPointerCapture(e.pointerId)};canvas.onpointermove=e=>{const [wx,wy]=screenToWorld(e.clientX*devicePixelRatio,e.clientY*devicePixelRatio);status.textContent=`X ${Math.floor(wx)} Y ${Math.floor(wy)} Z ${z}`;if(drag){centerX=drag[2]-(e.clientX-drag[0])*devicePixelRatio/(32*scale);centerY=drag[3]-(e.clientY-drag[1])*devicePixelRatio/(32*scale);draw()}};canvas.onpointerup=()=>drag=null;
canvas.onwheel=e=>{e.preventDefault();scale=Math.max(.03,Math.min(4,scale*Math.exp(-e.deltaY*.001)));draw()};
floorSelect.onchange=()=>{z=+floorSelect.value;draw()};document.querySelector('#jump').onclick=()=>{centerX=+document.querySelector('#x').value||centerX;centerY=+document.querySelector('#y').value||centerY;const jumpZ=document.querySelector('#z').value;if(jumpZ!==''){z=Math.max(0,Math.min(15,+jumpZ));floorSelect.value=z}draw()};
for(const box of document.querySelectorAll('[data-overlay]'))box.onchange=()=>{box.checked?enabled.add(box.dataset.overlay):enabled.delete(box.dataset.overlay);draw()};
Promise.all([fetch('manifest.json').then(r=>r.json()),fetch('data/mechanics.json').then(r=>r.ok?r.json():{}).catch(()=>({})),fetch('data/spawns.json').then(r=>r.ok?r.json():{}).catch(()=>({}))]).then(([m,mechanics,spawns])=>{manifest=m;chunks=m.chunks;overlays={...mechanics,...spawns};const floors=[...new Set(chunks.map(c=>c.z))].sort((a,b)=>a-b);floorSelect.innerHTML=floors.map(v=>`<option ${v===z?'selected':''}>${v}</option>`).join('');status.textContent='Drag to pan · wheel to zoom';resize()});
</script></body></html>'''


def write_viewer(output: str | Path) -> Path:
	path = Path(output) / "index.html"
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(VIEWER_HTML, encoding="utf-8", newline="\n")
	return path
