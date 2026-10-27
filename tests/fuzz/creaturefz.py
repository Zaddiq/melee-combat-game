from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const rnd=a=>a[Math.floor(Math.random()*a.length)];
 const out={games:0,over:0,errors:[],casts:0,renew:0,foeCasts:0,wizFoe:0};
 const SPN=["Staff","Magic Fist","Blur","Drop Weapon","Slow Movement","Clumsiness","Aid","Trip","Sleep","Fireball","Freeze","Stone Flesh","Stop","Lightning","Iron Flesh","Speed Movement","Dazzle","Blast","Break Weapon","Remove Thrown Spell","Spell Shield","Death Spell","Reverse Missiles","Flight","Teleport","Fire","Shadow","Create Wall","Rope","Destroy Creation","Summon Wolf","Summon Myrmidon","Summon Bear","Summon Gargoyle","Summon Giant","Image","Illusion","Dispel Illusions","Confusion","Shock Shield","Avert","Invisibility","Mage Sight","Slippery Floor","Control Person","Control Animal"];
 const KINDS=['wolf','bear','gargoyle','giant']; const seenAir=[0]; for(let g=0;g<48;g++){
  try{
   me=fromBuilder({name:"W"+g,race:"human",cls:g%2?"wizard":"wizard",st:9+ri(5),dx:11+ri(3),iq:14,a:"none",b:"none",armor:rnd(["none","cloth","leather"]),d1:"dagger",silver:true,spells:SPN.slice()});
   foeMode={k:"creature",kind:KINDS[g%4],n:(g%3===0?2:1)}; foe=buildFoe(); startFight();
   let guard=0;
   while(G.phase!=="over"&&guard++<300){
     ui(); drawMap(); const ph=G.phase;
     if(ph==="choose") choose(Math.random()<.5);
     else if(ph==="move"){ const R2=[...G.reach.values()]; const t=rnd(R2); G.me.q=t.q;G.me.r=t.r;G.moved=t.c; G.me.f=faceToward(G.me,G.foe); confirmMove(); }
     else if(ph==="renew"){ out.renew++; G.rlist.forEach(r=>r.on=Math.random()<.7); doRenew(); }
     else if(ph==="spells"){ const x=rnd(G.sopts); resolveTurn({t:"cast",sp:x.sp,n:x.n,on:x.on,dest:x.tele?rnd(P):x.hexsel?rnd(creaHexes(G.me,G.foe,x.hexsel)):undefined,objId:x.objId,form:x.form}); }
     else if(ph==="pick"){ const L=G.opts; const c=L.filter(x=>x.t==="cast"); const o2=(c.length&&Math.random()<.7)?rnd(c):(L.length?rnd(L):{t:"none"});
        if(o2.t==="cast"){ const sl=castList(G.me,G.foe); if(sl.length){ const x=rnd(sl); out.casts++; resolveTurn({t:"cast",sp:x.sp,n:x.n,on:x.on,dest:x.tele?rnd(P):x.hexsel?rnd(creaHexes(G.me,G.foe,x.hexsel)):undefined,objId:x.objId,form:x.form}); } else resolveTurn({t:"none"}); }
        else if(o2.t==="disengage"||o2.t==="hesc"){ const fr=freeNeighbors(G.me); resolveTurn(fr.length?{t:o2.t,dest:rnd(fr)}:{t:"none"}); } else resolveTurn(o2); }
     else if(ph==="retreat") doRetreat(rnd([...G.ropts.values()]));
     else if(ph==="advance") doAdvance(Math.random()<.5);
     else { out.errors.push("stuck "+ph); break; }
   }
   out.games++; if(G.phase==="over") out.over++; if(KINDS[g%4]==="gargoyle"&&G.log.some(l=>/takes to the air/.test(l))) seenAir[0]++; if(G.log.some(l=>/^.*casts /.test(l)&&!/^You/.test(l))) out.foeCasts++;
   if(G.log.some(l=>/undefined|NaN/.test(l))) out.errors.push("bad text: "+G.log.filter(l=>/undefined|NaN/.test(l))[0]);
  }catch(e){ out.errors.push(String(e.stack||e).slice(0,400)); }
 }
 out.gargoyleFlew=seenAir[0]; return out;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/wizard-arena.html')
    r=pg.evaluate(JS); print({k:v for k,v in r.items() if k!='errors'})
    seen=set()
    for e in r['errors']:
        k=e[:90]
        if k not in seen: seen.add(k); print(e[:600])
    print(errs[:3])
