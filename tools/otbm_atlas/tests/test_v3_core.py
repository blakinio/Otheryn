from __future__ import annotations
from collections import Counter
import tempfile,unittest
from pathlib import Path
from tools.otbm_atlas.assets import Appearance,SpriteInfo
from tools.otbm_atlas import atlas
from tools.otbm_atlas.mechanics import resolve_mechanics
from tools.otbm_atlas.render import _item_patterns,render_tiles
from tools.otbm_atlas.semantic import Item,Position,Tile
def app(**kw):
	base=dict(appearance_id=1,name="x",is_ground=False,clip=False,bottom=False,top=False,stackable=False,splash=False,fluid_container=False,shift=None,height=None,frames=());base.update(kw);return Appearance(**base)
class FakeRenderer:
	def __init__(self):self.missing_appearances=Counter();self.missing_sprites=Counter();self.calls=[]
	def item_sprites(self,item,x,y,z):self.calls.append(item.server_id);return iter(())
class V3CoreTests(unittest.TestCase):
	def test_authoritative_version(self):self.assertEqual(atlas.ATLAS_VERSION,3)
	def test_stack_and_fluid_patterns(self):
		stack=SpriteInfo(4,2,1,1,tuple(range(8)),1,0);fluid=SpriteInfo(4,3,1,1,tuple(range(12)),1,0);self.assertEqual(_item_patterns(app(stackable=True),stack,Item(1,25),10,11,7),(2,1,0));self.assertEqual(_item_patterns(app(fluid_container=True),fluid,Item(1,2),0,0,7),(3,1,0))
	def test_nested_container_children_are_not_visible_stack(self):
		r=FakeRenderer();tile=Tile(Position(1,2,7),None,0,None,(Item(100,children=(Item(200),)),));_,report=render_tiles(iter((tile,)),r,(1,1,2,2,7));self.assertEqual(r.calls,[100]);self.assertEqual(report["childItems"],2)
	def test_dynamic_uid_tables_do_not_guess(self):
		with tempfile.TemporaryDirectory() as d:
			root=Path(d);(root/"x.lua").write_text("local config={ [2246]={}, [1]={} }\nlocal x=config[item.uid]\n",encoding="utf-8");report=resolve_mechanics({"uniqueIds":[{"uniqueId":2246}],"actionIds":[]},root);self.assertEqual(report["resolutions"][0]["status"],"UNRESOLVED")
if __name__=="__main__":unittest.main()
