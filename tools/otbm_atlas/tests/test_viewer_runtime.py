from pathlib import Path
import json, subprocess, unittest


class ViewerRuntimeTests(unittest.TestCase):
	def test_modes_state_persistence_bounded_cache_and_animation_geometry(self):
		module = Path(__file__).parents[1] / "viewer_runtime.js"
		state = {'x': 1, 'y': 2, 'z': 7, 'zoom': .2, 'overlays': ['npc'], 'selectedMarker': 'm1', 'renderMode': 'auto'}
		script = f'''import * as r from {json.dumps(module.as_uri())};
const state={{x:1,y:2,z:7,zoom:.2,overlays:['npc'],selectedMarker:'m1',renderMode:'auto'}};
const storage={{value:null,setItem(k,v){{this.value=v}}}},history={{url:null,replaceState(a,b,u){{this.url=u}}}};
const switched=r.transitionState(r.transitionState(r.transitionState(state,'detailed'),'performance'),'auto');
const cache=new r.BoundedLRU(2,10);cache.set('a',1,4);cache.set('b',2,4);cache.get('a');cache.set('c',3,4);
const restored=r.parseViewState(r.viewUrl('https://x/',state),{{}});const visible=r.visibleChunks([{{z:7,logicalBounds:[0,127,0,127]}},{{z:8,logicalBounds:[0,127,0,127]}}],7,[0,10,0,10],0);
const legacyGeometry=r.environmentRecordGeometry({{}}),extendedGeometry=r.environmentRecordGeometry({{spriteSize:[64,32],drawOffsetPixels:[-35,-4]}}),extendedBounds=r.environmentRecordBounds({{position:{{x:100,y:200,z:7}},spriteSize:[64,32],drawOffsetPixels:[-32,0]}});
console.log(JSON.stringify({{parsed:['auto','detailed','performance'].map(v=>r.urlRenderMode('https://x/?render='+v)),invalid:r.resolveRenderMode('https://x/?render=no','bad'),precedence:r.resolveRenderMode('https://x/?render=performance','detailed'),layers:[r.baseLayer('detailed',.03),r.baseLayer('performance',4),r.baseLayer('auto',.1),r.baseLayer('auto',1)],switched,cache:[cache.size,cache.bytes,cache.get('b'),cache.get('a'),cache.get('c')],persist:r.persistMode(storage,history,'https://x/?x=1#y=2','detailed'),stored:storage.value,url:history.url,restored,visible:visible.length,coordinates:[r.parseCoordinateSearch('32369, 32241, 7'),r.parseCoordinateSearch('1,2,16'),r.parseCoordinateSearch('x,y,z')],legacyGeometry,extendedGeometry,extendedBounds}}));'''
		data = json.loads(subprocess.run(['node', '--input-type=module', '-e', script], check=True, text=True, capture_output=True).stdout)
		self.assertEqual(data['parsed'], ['auto', 'detailed', 'performance']); self.assertEqual(data['invalid'], 'auto'); self.assertEqual(data['precedence'], 'performance')
		self.assertEqual(data['layers'], ['detailed', 'overview', 'overview-low', 'detailed']); self.assertEqual({k: data['switched'][k] for k in state if k != 'renderMode'}, {k: state[k] for k in state if k != 'renderMode'})
		self.assertEqual(data['cache'], [2, 8, None, 1, 3]); self.assertEqual((data['persist'], data['stored']), ('detailed', 'detailed')); self.assertIn('render=detailed', data['url'])
		self.assertEqual(data['restored'], state); self.assertEqual(data['visible'], 1)
		self.assertEqual(data['coordinates'], [{'x': 32369, 'y': 32241, 'z': 7}, None, None])
		self.assertEqual(data['legacyGeometry'], {'width': 32, 'height': 32, 'offsetX': 0, 'offsetY': 0})
		self.assertEqual(data['extendedGeometry'], {'width': 64, 'height': 32, 'offsetX': -35, 'offsetY': -4})
		self.assertEqual(data['extendedBounds'], [99, 101, 200, 201])
