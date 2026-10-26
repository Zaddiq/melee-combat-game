from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const races=Object.keys(RACES), ws=Object.keys(W), sh=Object.keys(SHIELDS), ar=Object.keys(ARMOR);
 const rnd=a=>a[Math.floor(Math.random()*a.length)];
 const out={games:0,over:0,errors:[],hth:0,winners:0};
 const mkp=g=>{ const r=rnd(races), R=RACES[r]; return fromBuilder({name:"P"+g+Math.random().toString(36).slice(2,4),race:r,cls:"fighter",st:R.st+Math.floor(Math.random()*8),dx:R.dx+Math.floor(Math.random()*8),iq:R.iq,a:rnd(ws.concat(["none"])),b:rnd(sh.concat(["mg","none","dagger"])),s1:rnd(ws.concat(sh,["none"])),d1:rnd(["dagger","mg","none"]),armor:rnd(ar)}); };
 for(let g=0;g<6;g++){
  try{
   slot[0]=mkp(1); slot[1]=mkp(2); if(slot[0].name===slot[1].name) slot[1].name+="x"; me=slot[0]; foe=slot[1]; startFight();
   let guard=0, covers=0;
   while(G.phase!=="over"&&guard++<400){
     ui(); drawMap(); const ph=G.phase;
     if(ph==="choose") choose(Math.random()<.5);
     else if(ph==="move"){ const R2=[...G.reach.values()]; const t=rnd(R2); G.cur.q=t.q;G.cur.r=t.r;G.moved=t.c; G.cur.f=Math.random()<.7?faceToward(G.cur,G.oth):Math.floor(Math.random()*6); confirmMove(); }
     else if(ph==="cover"){ covers++; showPick(); }
     else if(ph==="pick"){ const L=G.opts; const att=L.filter(x=>x.t==="attack"||x.t==="dual"||x.t==="hattack"||x.t==="hth"); const o2=(att.length&&Math.random()<.75)?rnd(att):(L.length?rnd(L):{t:"none"});
        if(o2.t==="disengage"||o2.t==="hesc"){ const fr=freeNeighbors(G.cur); takePick(fr.length?{t:o2.t,dest:rnd(fr)}:{t:"none"}); } else takePick(o2); }
     else if(ph==="retreat") doRetreat(rnd([...G.ropts.values()]));
     else if(ph==="advance") doAdvance(Math.random()<.5);
     else { out.errors.push("stuck "+ph); break; }
   }
   out.games++; if(G.phase==="over") out.over++; if(G.winner) out.winners++; if(G.log.some(l=>/hand to hand/.test(l))) out.hth++;
   if(G.log.some(l=>/\byou\b|\bYou\b|undefined|NaN/.test(l))) out.errors.push("bad text: "+G.log.filter(l=>/\byou\b|\bYou\b|undefined|NaN/.test(l))[0]);
  }catch(e){ out.errors.push(String(e.stack||e).slice(0,300)); }
 }
 return out;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/duel.html')
    r=pg.evaluate(JS); print({k:v for k,v in r.items() if k!='errors'}); 
    seen=set()
    for e in r['errors']:
        k=e[:80]
        if k not in seen: seen.add(k); print(e[:500])
    print(errs[:3])
