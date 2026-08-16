const canvas=document.querySelector('#map');
const zoomIn=document.querySelector('#zoomIn');
const zoomOut=document.querySelector('#zoomOut');
const jump=document.querySelector('#jump');
const floor=document.querySelector('#floor');
const xInput=document.querySelector('#x');
const yInput=document.querySelector('#y');
const zInput=document.querySelector('#z');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let lastPinchDistance=null;

function state(){
  const p=new URL(location.href).searchParams;
  return{x:+p.get('x')||32360,y:+p.get('y')||32230,z:p.has('z')&&Number.isFinite(+p.get('z'))?+p.get('z'):7,zoom:+p.get('zoom')||.18};
}

function distance(touches){
  if(touches.length<2)return null;
  return Math.hypot(touches[0].clientX-touches[1].clientX,touches[0].clientY-touches[1].clientY);
}

if(canvas){
  canvas.style.touchAction='none';
  canvas.addEventListener('touchstart',event=>{if(event.touches.length===2){lastPinchDistance=distance(event.touches);event.preventDefault()}},{passive:false});
  canvas.addEventListener('touchmove',event=>{
    if(event.touches.length!==2||!lastPinchDistance)return;
    const next=distance(event.touches);if(!next||next<=0)return;
    const ratio=next/lastPinchDistance;
    lastPinchDistance=next;
    const deltaY=-Math.log(ratio)/.001;
    canvas.dispatchEvent(new WheelEvent('wheel',{deltaY,cancelable:true,bubbles:false}));
    event.preventDefault();
  },{passive:false});
  canvas.addEventListener('touchend',event=>{if(event.touches.length<2)lastPinchDistance=null},{passive:true});
  canvas.addEventListener('touchcancel',()=>{lastPinchDistance=null},{passive:true});

  canvas.addEventListener('keydown',event=>{
    const current=state();
    const step=Math.max(1,Math.round(8/Math.max(.1,current.zoom)));
    let handled=true;
    if(event.key==='ArrowLeft')current.x-=step;
    else if(event.key==='ArrowRight')current.x+=step;
    else if(event.key==='ArrowUp')current.y-=step;
    else if(event.key==='ArrowDown')current.y+=step;
    else if(event.key==='+'||event.key==='='){zoomIn?.click();event.preventDefault();return}
    else if(event.key==='-'||event.key==='_'){zoomOut?.click();event.preventDefault();return}
    else if(event.key==='PageUp'||event.key==='PageDown'){
      const options=[...floor.options],index=Math.max(0,options.findIndex(option=>option.value===floor.value));
      const next=Math.max(0,Math.min(options.length-1,index+(event.key==='PageUp'?-1:1)));
      if(options[next]){floor.value=options[next].value;floor.dispatchEvent(new Event('change',{bubbles:true}))}
      event.preventDefault();return;
    }else handled=false;
    if(handled){
      xInput.value=String(Math.round(current.x));yInput.value=String(Math.round(current.y));zInput.value=String(current.z);jump.click();event.preventDefault();
    }
  });
}

document.documentElement.dataset.reducedMotion=reduced.matches?'reduce':'no-preference';
reduced.addEventListener?.('change',event=>{document.documentElement.dataset.reducedMotion=event.matches?'reduce':'no-preference'});
