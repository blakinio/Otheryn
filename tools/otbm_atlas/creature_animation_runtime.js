import {BoundedLRU,environmentPhase,visibleChunks} from './viewer-runtime.js';

export const CREATURE_ANIMATION_SCALE=.45;
const CREATURE_KINDS=new Set(['npcSpawns','supplementalNpcSpawns','monsterSpawns','supplementalMonsterSpawns']);

export function creatureAnimationSelection(descriptor,record,elapsedMs){
  if(!descriptor||descriptor.schemaVersion!==1||!descriptor.groups)return null;
  const group=descriptor.groups[descriptor.presentationGroup];
  if(!group||!group.frames)return null;
  const preferred=descriptor.presentationDirection||'south';
  const direction=group.frames[preferred]?preferred:(group.frames.south?'south':Object.keys(group.frames)[0]);
  const frames=group.frames[direction];
  if(!Array.isArray(frames)||!frames.length)return null;
  const runtime={...group,animationKey:group.animationKey||`${descriptor.outfitKey||'creature'}-${descriptor.presentationGroup}`,position:record.position};
  const phase=environmentPhase(runtime,elapsedMs,Boolean(group.randomStartPhase))%frames.length;
  return{group:descriptor.presentationGroup,direction,phase,path:frames[phase]};
}

function installCreatureAnimation(){
  if(typeof document==='undefined')return;
  const map=document.querySelector('#map');if(!map)return;
  const overlay=document.createElement('canvas');overlay.id='creatureAnimations';overlay.setAttribute('aria-hidden','true');
  Object.assign(overlay.style,{position:'absolute',inset:'0',pointerEvents:'none',zIndex:'1'});
  const environment=document.querySelector('#environmentAnimations');(environment||map).insertAdjacentElement('afterend',overlay);
  const ctx=overlay.getContext('2d'),images=new BoundedLRU(256,64*1024*1024),shards=new BoundedLRU(64,8*1024*1024),descriptors=new BoundedLRU(128,4*1024*1024),starts=new BoundedLRU(2048,64*1024),pendingShards=new Set,pendingDescriptors=new Set;
  ctx.imageSmoothingEnabled=false;let manifest=null,last=0;
  const image=path=>{let value=images.get(path);if(value)return value;value=new Image;value.onload=()=>images.set(path,value,value.naturalWidth*value.naturalHeight*4);value.src=path;images.set(path,value,0);return value};
  const loadShard=(z,x,y)=>{const key=`${z}/${x}_${y}`;if(shards.get(key)||pendingShards.has(key))return;pendingShards.add(key);fetch(`data/chunks/z${z}/${x}_${y}.json`).then(r=>r.ok?r.json():{}).then(value=>shards.set(key,value,JSON.stringify(value).length*2)).finally(()=>pendingShards.delete(key))};
  const loadDescriptor=path=>{const cached=descriptors.get(path);if(cached)return cached;if(pendingDescriptors.has(path))return null;pendingDescriptors.add(path);fetch(path).then(r=>r.ok?r.json():{failed:true}).catch(()=>({failed:true})).then(value=>descriptors.set(path,value,JSON.stringify(value).length*2)).finally(()=>pendingDescriptors.delete(path));return null};
  const readState=()=>{const p=new URL(location.href).searchParams,stored=JSON.parse(localStorage.getItem('otheryn.atlas.layers')||'[]'),layers=p.has('layers')?p.get('layers').split(',').filter(Boolean):stored;return{x:+p.get('x')||32360,y:+p.get('y')||32230,z:p.has('z')&&Number.isFinite(+p.get('z'))?+p.get('z'):7,zoom:+p.get('zoom')||.18,layers}};
  const drawFallback=(record,left,top,size)=>{if(!record.sprite)return;const fallback=image(record.sprite);if(fallback.complete&&fallback.naturalWidth)ctx.drawImage(fallback,left,top,size,size)};
  const paint=now=>{requestAnimationFrame(paint);if(document.hidden||now-last<80)return;last=now;if(overlay.width!==map.width||overlay.height!==map.height){overlay.width=map.width;overlay.height=map.height;overlay.style.width=map.clientWidth+'px';overlay.style.height=map.clientHeight+'px';ctx.imageSmoothingEnabled=false}ctx.clearRect(0,0,overlay.width,overlay.height);if(!manifest)return;const state=readState();if(state.zoom<CREATURE_ANIMATION_SCALE)return;const enabled=state.layers.filter(kind=>CREATURE_KINDS.has(kind));if(!enabled.length)return;const hx=overlay.width/(64*state.zoom),hy=overlay.height/(64*state.zoom),bounds=[state.x-hx,state.x+hx,state.y-hy,state.y+hy];for(const chunk of visibleChunks(manifest.chunks,state.z,bounds,0)){const key=`${chunk.z}/${chunk.chunkX}_${chunk.chunkY}`;loadShard(chunk.z,chunk.chunkX,chunk.chunkY);const data=shards.get(key);if(!data)continue;for(const kind of enabled){for(const record of data[kind]||[]){const p=record.position;if(!p||p.z!==state.z||!record.spriteAnimation)continue;const x=(p.x+.5-state.x)*32*state.zoom+overlay.width/2,y=(p.y+.5-state.y)*32*state.zoom+overlay.height/2,size=Math.max(14,32*state.zoom),left=x-size/2,top=y-size/2,descriptor=loadDescriptor(record.spriteAnimation);if(!descriptor||descriptor.failed){drawFallback(record,left,top,size);continue}const group=descriptor.groups?.[descriptor.presentationGroup],startKey=`${kind}:${record.spriteAnimation}:${p.x}:${p.y}:${p.z}`;let started=starts.get(startKey);if(started===null){started=now;starts.set(startKey,started,32)}const clock=group?.synchronized?Date.now():Math.max(0,now-started),selection=creatureAnimationSelection(descriptor,record,clock);if(!selection){drawFallback(record,left,top,size);continue}const frame=image(selection.path);if(frame.complete&&frame.naturalWidth)ctx.drawImage(frame,left,top,size,size);else drawFallback(record,left,top,size)}}}};
  fetch('manifest.json').then(r=>r.json()).then(value=>{manifest=value;requestAnimationFrame(paint)}).catch(()=>{});
}

if(typeof document!=='undefined')queueMicrotask(()=>requestAnimationFrame(installCreatureAnimation));
