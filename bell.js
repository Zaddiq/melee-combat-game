"use strict";
/* bell.js: the bell (a different pitch for each player), the phone buzz and the screen wake lock, shared by colosseum.html and phone.html.
   Browsers only start sound after a tap on the page, so call Bell.unlock() from a button click (Join, Open the table, Sound). */
(function(){
const PITCH=[523.25,659.25,783.99,987.77];   /* C5, E5, G5, B5: player 1 to 4 */
const Bell={
  ctx:null, on:true, want:false, wl:null, store:null, pref:"bell-on",
  init(store,pref){ this.store=store; if(pref) this.pref=pref; try{ if(store.getItem(this.pref)==="0") this.on=false; }catch(e){} },
  setOn(v){ this.on=!!v; try{ this.store&&this.store.setItem(this.pref,this.on?"1":"0"); }catch(e){} },
  unlock(){ try{ if(!this.ctx){ const A=window.AudioContext||window.webkitAudioContext; if(!A) return false; this.ctx=new A(); } if(this.ctx.state==="suspended") this.ctx.resume(); return true; }catch(e){ return false; } },
  /* two strikes of a bell: a sine plus two quieter, inharmonic overtones, each dying away */
  ring(i){ if(!this.on||!this.unlock()) return false; const c=this.ctx, f=PITCH[((+i||0)%4+4)%4], t0=c.currentTime+0.03;
    for(let k=0;k<2;k++){ const t=t0+k*0.4; for(const [m,g] of [[1,.45],[2.76,.16],[5.4,.06]]){ const o=c.createOscillator(), a=c.createGain(); o.type="sine"; o.frequency.value=f*m;
      a.gain.setValueAtTime(0,t); a.gain.linearRampToValueAtTime(g,t+.01); a.gain.exponentialRampToValueAtTime(.001,t+1.5); o.connect(a); a.connect(c.destination); o.start(t); o.stop(t+1.6); } }
    Bell.rang=(Bell.rang||0)+1; return true; },
  buzz(){ try{ if(navigator.vibrate) navigator.vibrate([250,120,250]); }catch(e){} },   /* Android only: iPhones never vibrate from a web page */
  async awake(on){ this.want=!!on; try{
    if(on){ if(!("wakeLock" in navigator)) return false; if(!this.wl||this.wl.released) this.wl=await navigator.wakeLock.request("screen"); return true; }
    if(this.wl){ await this.wl.release(); this.wl=null; } return false; }catch(e){ return false; } }
};
document.addEventListener("visibilitychange",()=>{ if(!document.hidden&&Bell.want) Bell.awake(true); });   /* the lock is dropped when the page is hidden: take it again */
document.addEventListener("pointerdown",()=>{ if(Bell.on) Bell.unlock(); },{passive:true});
window.Bell=Bell;
})();
