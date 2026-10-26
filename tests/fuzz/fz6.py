from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const races=Object.keys(RACES), ws=Object.keys(W), sh=Object.keys(SHIELDS), ar=Object.keys(ARMOR);
 const rnd=a=>a[Math.floor(Math.random()*a.length)];
 const out={games:0,errors:[],stuck:0,over:0};
 for(let g=0;g<150;g++){
  const r=rnd(races), R=RACES[r];
  const o={name:"T"+g,race:r,cls:Math.random()<.3?"wizard":"fighter",st:R.st+Math.floor(Math.random()*8),dx:R.dx+Math.floor(Math.random()*8),iq:R.iq,
    a:rnd(ws.concat(["none"])),b:rnd(sh.concat(["mg","none","dagger","club"])),s1:rnd(ws.concat(sh,["none"])),d1:rnd(["dagger","mg","none"]),d2:rnd(["none","dagger"]),armor:rnd(ar),
    spells:Math.random()<.5?["Staff"]:[]};
  try{
   me=fromBuilder(o); foe=makeOpponent(me.st+me.dx); startFight();
   let guard=0;
   while(G.phase!=="over"&&guard++<300){
     ui(); drawMap(); const ph=G.phase;
     if(ph==="choose") choose(Math.random()<.5);
     else if(ph==="move"){ const R2=[...G.reach.values()]; const t=R2[Math.floor(Math.random()*R2.length)]; G.me.q=t.q;G.me.r=t.r;G.moved=t.c; G.me.f=Math.random()<.7?faceToward(G.me,G.foe):Math.floor(Math.random()*6); confirmMove(); }
     else if(ph==="pick"){ const L=G.opts; const att=L.filter(x=>x.t.startsWith("attack")||x.t==="dual"||x.t==="hattack"||x.t==="hth"||x.t==="hdraw"||x.t==="drop"||x.t==="rise"||(x.t==="fire"&&x.pos)); const o2=(att.length&&Math.random()<.8)?rnd(att):(L.length?rnd(L):{t:"none"});
        if(o2.t==="disengage"||o2.t==="hesc"){ const fr=freeNeighbors(G.me); if(fr.length) resolveTurn({t:o2.t,dest:rnd(fr)}); else resolveTurn({t:"none"}); } else resolveTurn(o2); }
     else if(ph==="retreat") doRetreat(rnd([...G.ropts.values()]));
     else if(ph==="advance") doAdvance(Math.random()<.5);
     else { out.stuck++; out.errors.push("stuck phase "+ph+" "+JSON.stringify(o)); break; }
   }
   out.hth=(out.hth||0)+(G.log.some(l=>/hand to hand/.test(l))?1:0); out.games++; if(G.phase==="over") out.over++;
  }catch(e){ out.errors.push(String(e.stack||e).slice(0,300)+" | "+JSON.stringify(o)); }
 }
 return out;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/arena.html')
    r=pg.evaluate(JS); print({k:v for k,v in r.items() if k!='errors'}); 
    seen=set()
    for e in r['errors']:
        k=e.split('\n')[0][:80]
        if k not in seen: seen.add(k); print(e[:600]); print()
    print(errs[:3])
