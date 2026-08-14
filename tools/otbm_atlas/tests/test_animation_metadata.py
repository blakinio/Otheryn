from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from tools.otbm_atlas.assets import load_object_appearances

def varint(value):
	out=bytearray()
	while value>0x7f:out.append((value&0x7f)|0x80);value>>=7
	out.append(value);return bytes(out)
def scalar(number,value):return varint(number<<3)+varint(value)
def field(number,payload):return varint(number<<3|2)+varint(len(payload))+payload

class AnimationMetadataTests(unittest.TestCase):
	def test_sprite_animation_timing_is_preserved(self):
		phase1=scalar(1,100)+scalar(2,140);phase2=scalar(1,200)+scalar(2,240)
		animation=scalar(1,1)+scalar(2,1)+scalar(4,0)+field(6,phase1)+field(6,phase2)
		sprite=scalar(1,1)+scalar(2,1)+scalar(3,1)+scalar(4,1)+scalar(5,10)+scalar(5,11)+field(6,animation)
		appearance=scalar(1,500)+field(2,field(3,sprite));root=field(1,appearance)
		with tempfile.TemporaryDirectory() as directory:
			path=Path(directory)/'appearances.dat';path.write_bytes(root);frame=load_object_appearances(path)[500].frames[0]
		self.assertEqual(frame.animation_phases,2);self.assertEqual(frame.default_start_phase,1);self.assertTrue(frame.synchronized);self.assertEqual(frame.phase_durations,((100,140),(200,240)))

if __name__=='__main__':unittest.main()
