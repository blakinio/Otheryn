export const RENDER_MODES = new Set(['auto','detailed','performance']);
export const STORAGE_KEY = 'otheryn.atlas.renderMode';
export const DETAIL_SCALE = 1;
export function normalizeRenderMode(value){return RENDER_MODES.has(value)?value:null}
export function urlRenderMode(href){const u=new URL(href);const query=normalizeRenderMode(u.searchParams.get('render'));if(query)return query;const hash=new URLSearchParams(u.hash.replace(/^#/,''));return normalizeRenderMode(hash.get('render'))}
export function resolveRenderMode(href,stored){return urlRenderMode(href)||normalizeRenderMode(stored)||'auto'}
export function baseLayer(mode,scale){if(mode==='detailed'||(mode==='auto'&&scale>=DETAIL_SCALE))return 'detailed';return scale<0.25?'overview-low':'overview'}
export function modeUrl(href,mode){const u=new URL(href);u.searchParams.set('render',normalizeRenderMode(mode)||'auto');return u.toString()}
export function transitionState(state,mode){return {...state,renderMode:normalizeRenderMode(mode)||'auto'}}
export function persistMode(storage,history,href,mode){const value=normalizeRenderMode(mode)||'auto';storage.setItem(STORAGE_KEY,value);history.replaceState(null,'',modeUrl(href,value));return value}
export function parseViewState(href,fallback={}){const u=new URL(href),p=u.searchParams,out={...fallback};for(const key of ['x','y','z','zoom'])if(p.has(key)&&Number.isFinite(+p.get(key)))out[key]=+p.get(key);if(p.has('layers'))out.overlays=p.get('layers').split(',').filter(Boolean);if(p.has('marker'))out.selectedMarker=p.get('marker')||null;out.renderMode=resolveRenderMode(href,fallback.renderMode);return out}
export function parseCoordinateSearch(value){const match=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/.exec(value);if(!match)return null;const [x,y,z]=match.slice(1).map(Number);return x<=65535&&y<=65535&&z<=15?{x,y,z}:null}
export function viewUrl(href,state){const u=new URL(href);for(const key of ['x','y','z','zoom'])if(Number.isFinite(state[key]))u.searchParams.set(key,String(state[key]));u.searchParams.set('render',normalizeRenderMode(state.renderMode)||'auto');if(state.overlays?.length)u.searchParams.set('layers',[...state.overlays].sort().join(','));else u.searchParams.delete('layers');if(state.selectedMarker)u.searchParams.set('marker',state.selectedMarker);else u.searchParams.delete('marker');return u.toString()}
export function visibleChunks(chunks,z,bounds,margin=1){return chunks.filter(c=>c.z===z&&c.logicalBounds[1]>=bounds[0]-margin*128&&c.logicalBounds[0]<=bounds[1]+margin*128&&c.logicalBounds[3]>=bounds[2]-margin*128&&c.logicalBounds[2]<=bounds[3]+margin*128)}
export class BoundedLRU {
  constructor(maxEntries=128,maxBytes=384*1024*1024){this.maxEntries=maxEntries;this.maxBytes=maxBytes;this.map=new Map;this.bytes=0}
  get size(){return this.map.size} get(key){const v=this.map.get(key);if(!v)return null;this.map.delete(key);this.map.set(key,v);return v.value}
  set(key,value,bytes=0){this.delete(key);this.map.set(key,{value,bytes});this.bytes+=bytes;while(this.map.size>this.maxEntries||this.bytes>this.maxBytes){const oldest=this.map.keys().next().value;this.delete(oldest)}return value}
  delete(key){const v=this.map.get(key);if(!v)return false;this.bytes-=v.bytes;this.map.delete(key);return true}
}
