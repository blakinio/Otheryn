"""Export conservative cyclic object animations for the browser atlas."""
from __future__ import annotations
import json,shutil
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
			i=_idx(f,l,px,py,pz,p)
			if i>=len(f.sprite_ids):return None
			sh=sheet_for_sprite(r.sheets,f.sprite_ids[i])
			if not sh or sh.sprite_size!=(32,32):return None
	return a,f,px,py,pz

def _phase(r,f,px,py,pz,p):
	out=bytearray(4096)
	for l in range(f.layers):
		d=r.sprite(f.sprite_ids[_idx(f,l,px,py,pz,p)])
		if not d or d[:2]!=(32,32):raise ValueError('invalid eligible animation sprite')
		_blend(out,32,32,d[2],32,32,0,0)
	return encode_png(32,32,bytes(out))

def _clean(tiles,r,bounds,omit):
	x1,x2,y1,y2,z=map(int,bounds);w=(x2-x1+1)*32;h=(y2-y1+1)*32;out=bytearray(w*h*4)
	for tile in tiles:
		if tile.position.z!=z or not(x1<=tile.position.x<=x2 and y1<=tile.position.y<=y2):continue
		items=_items(tile);s,e=_hooks(items,r)
		for n,item in enumerate(items):
			if (tile.position.x,tile.position.y,tile.position.z,n) in omit:continue
			for a,_sid,(sw,sh,pix) in r.item_sprites(item,tile.position.x,tile.position.y,tile.position.z,s,e):
				dx,dy=a.shift or (0,0);xx=(tile.position.x-x1)*32-(sw-32)-dx;yy=(tile.position.y-y1)*32-(sh-32)-dy
				if a.height:xx-=a.height;yy-=a.height
				_blend(out,w,h,pix,sw,sh,xx,yy)
	return w,h,bytes(out)
def _crop(data,w,h,x,y):
	if x<0 or y<0 or x+32>w or y+32>h:raise ValueError('underlay outside chunk')
	out=bytearray()
	for row in range(y,y+32):out.extend(data[(row*w+x)*4:(row*w+x+32)*4])
	return bytes(out)

def enrich_environment_animations(asset_dir:Path,output:Path)->dict[str,int]:
	manifest_path=output/'manifest.json';spool=output/'.spool'
	zero={'instances':0,'uniqueAnimations':0,'chunks':0,'staticFallbacks':0}
	if not manifest_path.exists() or not(spool/'spool.json').exists():return zero
	root=output/'data'/'environment-animations';shutil.rmtree(root,ignore_errors=True);root.mkdir(parents=True)
	r=AssetRenderer(asset_dir);manifest=json.loads(manifest_path.read_text(encoding='utf-8'));made=set();instances=chunks=fallbacks=0
	for chunk in manifest.get('chunks',[]):
		z,cx,cy=int(chunk['z']),int(chunk['chunkX']),int(chunk['chunkY']);sp=spool/f'z{z}'/f'{cx}_{cy}.bin'
		if not sp.exists():continue
		tiles=list(decode_spool_tiles(sp));selected=[];omit=set()
		for tile in tiles:
			items=_items(tile)
			if not tile.items:continue
			s,e=_hooks(items,r);n=len(items)-1;item=items[n];a=r.appearances.get(item.server_id)
			if not a or not a.frames or a.frames[0].animation_phases<=1:continue
			c=_candidate(r,item,tile.position.x,tile.position.y,tile.position.z,s,e)
			if not c:fallbacks+=1;continue
			selected.append((tile,n,item,c,s,e));omit.add((tile.position.x,tile.position.y,tile.position.z,n))
		if not selected:continue
		w,h,clean=_clean(tiles,r,chunk['bounds'],omit);records=[]
		for tile,n,item,c,s,e in selected:
			a,f,px,py,pz=c;sub=-1 if item.subtype is None else int(item.subtype);key=f'{item.server_id}-{sub}-{px}-{py}-{pz}-{int(s)}-{int(e)}';frames=[f'data/environment-animations/frames/{key}/{p}.png' for p in range(f.animation_phases)]
			if key not in made:
				for p,rel in enumerate(frames):path=output/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(_phase(r,f,px,py,pz,p))
				made.add(key)
			under=f'data/environment-animations/underlays/z{z}/{cx}_{cy}/{tile.position.x}_{tile.position.y}_{n}.png';path=output/under;path.parent.mkdir(parents=True,exist_ok=True);xx=(tile.position.x-int(chunk['bounds'][0]))*32;yy=(tile.position.y-int(chunk['bounds'][2]))*32;path.write_bytes(encode_png(32,32,_crop(clean,w,h,xx,yy)))
			ranges=[[lo,hi] for lo,hi in f.phase_durations];rec={'position':{'x':tile.position.x,'y':tile.position.y,'z':tile.position.z},'serverId':item.server_id,'animationKey':key,'frames':frames,'underlay':under,'phaseDurationsMs':[max(1,(lo+hi)//2) for lo,hi in f.phase_durations],'durationRangesMs':ranges,'defaultStartPhase':f.default_start_phase,'synchronized':f.synchronized,'randomStartPhase':f.random_start_phase,'loopType':f.loop_type,'loopCount':f.loop_count,'policy':'cyclic-appearance'}
			if item.subtype is not None:rec['subtype']=item.subtype
			records.append(rec);instances+=1
		path=root/'chunks'/f'z{z}'/f'{cx}_{cy}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'schemaVersion':1,'records':records},separators=(',',':'),sort_keys=True)+'\n',encoding='utf-8');chunks+=1
	stats={'instances':instances,'uniqueAnimations':len(made),'chunks':chunks,'staticFallbacks':fallbacks};index={'schemaVersion':1,'animationZoom':ANIMATION_ZOOM,'statistics':stats,'policy':{'cyclicAppearance':'browser animated from pinned object appearance phases','statefulAppearance':'not inferred; server-driven variants remain canonical static state','eligibility':'topmost visible object, 32x32 all phases/layers, no displacement/height','fallback':'unsupported or occluded animations remain deterministic static pixels'}};(root/'index.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n',encoding='utf-8');return stats
