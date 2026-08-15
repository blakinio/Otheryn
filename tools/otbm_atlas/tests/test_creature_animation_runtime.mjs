import assert from 'node:assert/strict';
import {creatureAnimationSelection} from '../creature_animation_runtime.js';

const descriptor={
  schemaVersion:1,
  outfitKey:'35-0-0-0-0-0',
  presentationGroup:'moving',
  presentationDirection:'south',
  groups:{
    moving:{
      animationKey:'monster-35-0-0-0-0-0-moving',
      phaseDurationsMs:[100,100],
      defaultStartPhase:0,
      synchronized:true,
      randomStartPhase:false,
      loopType:0,
      loopCount:0,
      frames:{south:['phase-0.png','phase-1.png'],north:['north-0.png','north-1.png']},
    },
  },
};
const record={position:{x:32360,y:32230,z:7}};
const first=creatureAnimationSelection(descriptor,record,0);
const second=creatureAnimationSelection(descriptor,record,100);
assert.equal(first.direction,'south');
assert.equal(first.phase,0);
assert.equal(first.path,'phase-0.png');
assert.equal(second.phase,1);
assert.equal(second.path,'phase-1.png');
assert.notEqual(first.path,second.path);
assert.equal(creatureAnimationSelection({schemaVersion:2},record,0),null);
console.log('creature animation runtime selection: PASS');
