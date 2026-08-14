"""Export conservative cyclic object animations for the browser atlas."""
from __future__ import annotations
import json,math,shutil
from pathlib import Path
from .assets import encode_png,sheet_for_sprite
from .environment_spool import decode_spool_tiles
from .render import AssetRenderer,_blend,_item_patterns
ANIMATION_ZOOM=1.5

def _items(tile):return ([] if tile.ground is None else [tile.ground])+list(tile.items)
def _hooks(items,r):
	s=e=False
	for item in items:
		a=r.appearances.get(item.server_id)
		if a:s=s or a.hook_direction==1;e=e or a.hook_direction==2
	return s,e
def _idx(f,l,x,y,z,p):return ((((p*f.pattern_depth+z)*f.pattern_height+y)*f.pattern_width+x)*f.layers+l)
def _candidate(r,item,x,y,z,s,e):
	a=r.appearances.get(item.server_id)
	if not a or not a.frames:return None
	f=a.frames[0]
	if f.animation_phases<=1 or a.shift not in (None,(0,0)) or a.height not in (None,0):return None
	px,py,pz=_item_patterns(a,f,item,x,y,z,s,e)
	for p in range(f.animation_phases):
		for l in range(f.layers):
			i=_idx(f,l,px,py,pz,p);sh=sheet_for_sprite(r.sheets,f.sprite_ids[i]) if i<len(f.sprite_ids) else None
			if not sh or sh.sprite_size!=(32,32):return None
	return a,f,px,py,pz
def _dangerous(r,item):
	a=r.appearances.get(item.server_id)
	if not a or not a.frames:return False
	if a.shift not in (None,(0,0)) or a.height not in (None,0):return True
	for sid in a.frames[0].sprite_ids:
		sh=sheet_for_sprite(r.sheets,sid)
		if sh and sh.sprite_size!=(32,32):return True
	return False
def _phase(r,f,px,py,pz,p):
	out=bytearray(4096)
	for l in range(f.layers):
		d=r.sprite(f.sprite_ids[_idx(f,l,px,py,pz,p)])
		if not d or d[:2]!=(32,32):raise ValueError('invalid eligible animation sprite')
		_blend(out,32,32,d[2],32,32,0,0)
	return encode_png(32,32,bytes(out))
def _underlay(tile,r):
	items=_items(tile);s,e=_hooks(items,r);out=bytearray(4096)
	for item in items[:-1]:
		for a,_sid,(sw,sh,pix) in r.item_sprites(item,tile.position.x,tile.position.y,tile.position.z,s,e):
			dx,dy=a.shift or (0,0);x=-(sw-32)-dx;y=-(sh-32)-dy
			if a.height:x-=a.height;y-=a.height
			_blend(out,32,32,pix,sw,sh,x,y)
	return encode_png(32,32,bytes(out))
def _overlap_radius(r):
	shift=0
	for a in r.appearances.values():
		if a.shift:shift=max(shift,abs(a.shift[0]),abs(a.shift[1]))
		if a.height:shift=max(shift,a.height)
	return max(1,math.ceil((64+shift)/32))
def _durations(frame):
	# assets.py currently maps protobuf 0/0 to 1/1. The pinned object assets contain
	# no genuine 1ms phases, so restore OTClient's first-nonzero fallback semantics.
	ranges=list(frame.phase_durations);fallback=next((v for v in ranges if v!=(1,1)),(1,1));return [fallback if v==(1,1) else v for v in ranges]

def enrich_environment_animations(asset_dir:Path,output:Path)->dict[str,int]:
	manifest_path=output/'manifest.json';spool=output/'.spool';zero={'instances':0,'uniqueAnimations':0,'chunks':0,'staticFallbacks':0}
	if not manifest_path.exists() or not(spool/'spool.json').exists():return zero
	root=output/'data'/'environment-animations';shutil.rmtree(root,ignore_errors=True);root.mkdir(parents=True);r=AssetRenderer(asset_dir);radius=_overlap_radius(r);manifest=json.loads(manifest_path.read_text(encoding='utf-8'));made=set();instances=chunks=fallbacks=0
	for chunk in manifest.get('chunks',[]):
		z,cx,cy=int(chunk['z']),int(chunk['chunkX']),int(chunk['chunkY']);sp=spool/f'z{z}'/f'{cx}_{cy}.bin'
		if not sp.exists():continue
		tiles=list(decode_spool_tiles(sp));by_pos={(t.position.x,t.position.y):t for t in tiles};danger={pos for pos,t in by_pos.items() if any(_dangerous(r,i) for i in _items(t))};records=[]
		x1,x2,y1,y2,_=map(int,chunk['logicalBounds'])
		for tile in tiles:
			items=_items(tile)
			if not tile.items:continue
			s,e=_hooks(items,r);item=items[-1];a=r.appearances.get(item.server_id)
			if not a or not a.frames or a.frames[0].animation_phases<=1:continue
			c=_candidate(r,item,tile.position.x,tile.position.y,tile.position.z,s,e)
			if not c:fallbacks+=1;continue
			x,y=tile.position.x,tile.position.y
			if x-x1<radius or x2-x<radius or y-y1<radius or y2-y<radius or any((nx,ny) in danger for nx in range(x-radius,x+radius+1) for ny in range(y-radius,y+radius+1) if (nx,ny)!=(x,y)):
				fallbacks+=1;continue
			a,f,px,py,pz=c;sub=-1 if item.subtype is None else int(item.subtype);key=f'{item.server_id}-{sub}-{px}-{py}-{pz}-{int(s)}-{int(e)}';frames=[f'data/environment-animations/frames/{key}/{p}.png' for p in range(f.animation_phases)]
			if key not in made:
				for p,rel in enumerate(frames):path=output/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(_phase(r,f,px,py,pz,p))
				made.add(key)
			under=f'data/environment-animations/underlays/z{z}/{cx}_{cy}/{x}_{y}.png';path=output/under;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(_underlay(tile,r));ranges=_durations(f);loop=-1 if f.loop_type>1 else f.loop_type
			rec={'position':{'x':x,'y':y,'z':tile.position.z},'serverId':item.server_id,'animationKey':key,'frames':frames,'underlay':under,'phaseDurationsMs':[max(1,(lo+hi)//2) for lo,hi in ranges],'durationRangesMs':[[lo,hi] for lo,hi in ranges],'defaultStartPhase':f.default_start_phase,'synchronized':f.synchronized,'randomStartPhase':f.random_start_phase,'loopType':loop,'loopCount':f.loop_count,'policy':'cyclic-appearance'}
			if item.subtype is not None:rec['subtype']=item.subtype
			records.append(rec);instances+=1
		if records:
			path=root/'chunks'/f'z{z}'/f'{cx}_{cy}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'schemaVersion':1,'records':records},separators=(',',':'),sort_keys=True)+'\n',encoding='utf-8');chunks+=1
	stats={'instances':instances,'uniqueAnimations':len(made),'chunks':chunks,'staticFallbacks':fallbacks};index={'schemaVersion':1,'animationZoom':ANIMATION_ZOOM,'overlapSafetyRadiusTiles':radius,'statistics':stats,'policy':{'cyclicAppearance':'browser animated from pinned object appearance phases','statefulAppearance':'not inferred; server-driven variants remain canonical static state','eligibility':'topmost 32x32 non-displaced object with no nearby cross-tile sprite risk','fallback':'unsupported, edge-risk or occluded animations remain deterministic static pixels'}};(root/'index.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n',encoding='utf-8');return stats
