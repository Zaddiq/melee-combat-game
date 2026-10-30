"""Random play for 3 and 4 players (free for all and teams) in colosseum.html. Run: python3 tests/fuzz/colosseumfz.py"""
from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const races=Object.keys(RACES), ws=Object.keys(W).filter(k=>!W[k].hid&&k!=="mg"&&k!=="staff"), ar=Object.keys(ARMOR);
 const rnd=a=>a[Math.floor(Math.random()*a.length)];
 const out={games:0,over:0,errors:[],escapes:0,wiz:0};
 const mkp=g=>{ const r=rnd(races), R=RACES[r], wz=Math.random()<.35; return fromBuilder(Object.assign({name:"P"+g+Math.random().toString(36).slice(2,4),race:r,cls:wz?"wizard":"fighter",st:R.st+Math.floor(Math.random()*7),dx:R.dx+Math.floor(Math.random()*7),iq:wz?15:R.iq,a:wz?"none":rnd(ws),b:Math.random()<.5?rnd(["small","large"]):"none",armor:rnd(ar),d1:"dagger"},wz?{spells:["Staff","Summon Wolf","Summon Bear","Fire","Blur","Stone Flesh","Giant Rope","Sleep","Image"]}:{})); };
 const layouts=[[3,[0,1,2,3]],[3,[0,1,0,3]],[4,[0,1,2,3]],[4,[0,1,0,1]],[4,[0,1,0,3]]];
 for(let g=0;g<20;g++){
  try{
   const [n,tm]=rnd(layouts); G=null; NP=n; for(let i=0;i<4;i++) team[i]=tm[i]; starts.fill(null);
   const names=new Set(); for(let i=0;i<4;i++){ slot[i]=i<n?mkp(i+1):null; if(slot[i]) names.add(slot[i].name); }
   startFight(); if(!G){ out.errors.push("no fight started"); continue; }
   let guard=0;
   while(G.phase!=="over"&&guard++<900){
     ui(); drawMap(); const ph=G.phase;
     if(ph==="choose") choose(Math.random()<.5);
     else if(ph==="move"){ const R2=[...G.reach.values()]; const t=rnd(R2); G.cur.q=t.q;G.cur.r=t.r;G.moved=t.c; G.cur.f=Math.random()<.7?faceToward(G.cur,G.oth):Math.floor(Math.random()*6);
        if(Math.random()<.01&&!G.eng&&G.players.filter(x=>x.hp>0&&!x.esc).length>2){ out.escapes++; quitDuel(G.cur,"escape"); } else confirmMove(); }
     else if(ph==="cover") showPick();
     else if(ph==="rcover") G.phase="renew";
     else if(ph==="renew"){ for(const r of G.rlist) r.on=Math.random()<.6; doRenew(); }
     else if(ph==="pick"){ const L=G.opts; const att=L.filter(x=>["attack","dual","hattack","hth"].includes(x.t)); const o2=(att.length&&Math.random()<.7)?rnd(att):(L.length?rnd(L):{t:"none"});
        if(o2.t==="cast"){ const sl=castList(G.cur,G.oth); if(sl.length){ const x=rnd(sl); out.wiz++; takePick({t:"cast",sp:x.sp,n:x.n,on:x.on,objId:x.objId,form:x.form,dest:x.tele?rnd(P):x.hexsel?rnd(creaHexes(G.cur,G.oth,x.hexsel,x.sp,x.form)||[P[0]]):undefined}); } else takePick({t:"none"}); }
        else if(o2.t==="disengage"||o2.t==="hesc"){ const fr=freeNeighbors(G.cur); takePick(fr.length?{t:o2.t,dest:rnd(fr)}:{t:"none"}); } else takePick(o2); }
     else if(ph==="retreat") doRetreat(rnd([...G.ropts.values()]));
     else if(ph==="advance") doAdvance(Math.random()<.5);
     else { out.errors.push("stuck "+ph); break; }
   }
   out.games++; if(G.phase==="over") out.over++;
   if(G.phase==="over"){ if(G.xp.length!==n) out.errors.push("xp lines "+G.xp.length+" for "+n); const live=G.players.filter(u=>u.hp>0&&!u.esc); if(G.winners&&G.winners.some(u=>u.hp<=0||u.esc)) out.errors.push("a downed player won"); if(new Set(live.map(sideOf)).size>1) out.errors.push("ended with two sides standing"); }
   if(G.log.some(l=>/undefined|NaN|\[object/.test(l))) out.errors.push("bad text: "+G.log.filter(l=>/undefined|NaN|\[object/.test(l))[0]);
  }catch(e){ out.errors.push(String(e.stack||e).slice(0,400)); }
 }
 return out;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    import os; pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','colosseum.html')))
    r=pg.evaluate(JS); print({k:v for k,v in r.items() if k!='errors'})
    seen=set()
    for e in r['errors']:
        k=e[:80]
        if k not in seen: seen.add(k); print(e[:600])
    print(errs[:3])
