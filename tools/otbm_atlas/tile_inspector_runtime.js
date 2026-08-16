import {BoundedLRU,DETAIL_SCALE} from './viewer-runtime.js';

const canvas=document.querySelector('#map');
const toggle=document.querySelector('#tileInspector');
const tooltip=document.querySelector('#tileInspectorTooltip');
const markerTooltip=document.querySelector('#tooltip');
const cache=new BoundedLRU(48,24*1024*1024);
const pending=new Map();
let manifest=null;
let generation=0;
let pointerDown=false;

function readState(){
  const p=new URL(location.href).searchParams;
  return{x:+p.get('x')||32360,y:+p.get('y')||32230,z:p.has('z')&&Number.isFinite(+p.get('z'))?+p.get('z'):7,zoom:+p.get('zoom')||.18};
}

function worldAt(clientX,clientY){
  const state=readState(),dpr=devicePixelRatio||1;
  return{
    x:Math.floor((clientX*dpr-canvas.width/2)/(32*state.zoom)+state.x),
    y:Math.floor((clientY*dpr-canvas.height/2)/(32*state.zoom)+state.y),
    z:state.z,
    zoom:state.zoom,
  };
}

function chunkFor(position){
  if(!manifest)return null;
  return manifest.chunks.find(chunk=>chunk.z===position.z&&chunk.logicalBounds[0]<=position.x&&chunk.logicalBounds[1]>=position.x&&chunk.logicalBounds[2]<=position.y&&chunk.logicalBounds[3]>=position.y)||null;
}

function loadShard(chunk){
  const key=`${chunk.z}/${chunk.chunkX}_${chunk.chunkY}`;
  const cached=cache.get(key);if(cached)return Promise.resolve(cached);
  if(pending.has(key))return pending.get(key);
  const request=fetch(`data/tile-inspector/z${chunk.z}/${chunk.chunkX}_${chunk.chunkY}.json`)
    .then(response=>response.ok?response.json():{schemaVersion:1,records:[]})
    .catch(()=>({schemaVersion:1,records:[]}))
    .then(value=>{cache.set(key,value,JSON.stringify(value).length*2);pending.delete(key);return value});
  pending.set(key,request);return request;
}

function idLine(label,item){
  if(!item)return`${label}: none`;
  const attrs=[];
  if(Number.isFinite(+item.actionId))attrs.push(`AID ${item.actionId}`);
  if(Number.isFinite(+item.uniqueId))attrs.push(`UID ${item.uniqueId}`);
  return`${label}: ${item.serverId}${attrs.length?` (${attrs.join(', ')})`:''}`;
}

function show(clientX,clientY,position,record,message){
  const lines=[`X ${position.x}  Y ${position.y}  Z ${position.z}`];
  if(message)lines.push(message);
  else if(record){
    lines.push(idLine('Ground ID',record.ground));
    if(record.items?.length)record.items.forEach((item,index)=>lines.push(idLine(`Item ${index+1}`,item)));
    else lines.push('Items: none');
  }else lines.push('Tile: empty / unavailable');
  tooltip.textContent=lines.join('\n');
  tooltip.style.left=`${Math.min(innerWidth-260,clientX+14)}px`;
  tooltip.style.top=`${Math.min(innerHeight-120,clientY+14)}px`;
  tooltip.hidden=false;
}

async function inspect(clientX,clientY){
  if(!toggle?.checked||!manifest||pointerDown){if(tooltip)tooltip.hidden=true;return}
  if(markerTooltip)markerTooltip.hidden=true;
  const position=worldAt(clientX,clientY),current=++generation;
  if(position.zoom<DETAIL_SCALE){show(clientX,clientY,position,null,'Tile inspector available at detail zoom (≥ 1.0)');return}
  const chunk=chunkFor(position);
  if(!chunk){show(clientX,clientY,position,null,null);return}
  const shard=await loadShard(chunk);
  if(current!==generation||!toggle.checked)return;
  const record=(shard.records||[]).find(value=>value.x===position.x&&value.y===position.y&&value.z===position.z)||null;
  show(clientX,clientY,position,record,null);
}

if(canvas&&toggle&&tooltip){
  toggle.addEventListener('change',()=>{generation++;tooltip.hidden=true;if(markerTooltip)markerTooltip.hidden=true});
  canvas.addEventListener('pointerdown',()=>{pointerDown=true;generation++;tooltip.hidden=true});
  canvas.addEventListener('pointermove',event=>{if(!pointerDown&&event.pointerType!=='touch')inspect(event.clientX,event.clientY)});
  canvas.addEventListener('pointerup',event=>{pointerDown=false;if(event.pointerType==='touch'&&toggle.checked)setTimeout(()=>inspect(event.clientX,event.clientY),0)});
  canvas.addEventListener('pointercancel',()=>{pointerDown=false;generation++;tooltip.hidden=true});
  canvas.addEventListener('pointerleave',()=>{if(!toggle.checked||!pointerDown)tooltip.hidden=true});
  canvas.addEventListener('keydown',event=>{if(toggle.checked&&(event.key==='Enter'||event.key===' ')){inspect(canvas.clientWidth/2,canvas.clientHeight/2);event.preventDefault()}});
  fetch('manifest.json').then(response=>response.ok?response.json():null).then(value=>{manifest=value}).catch(()=>{});
}
