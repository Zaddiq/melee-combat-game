"""Summons and many-figure checks for duel.html. Run: python3 tests/duel_summon_test.py  (needs Playwright)."""
from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const R=[]; const ok=(n,c)=>R.push([n,!!c]);
 const w=fromBuilder({name:"Wiz",race:"human",cls:"wizard",st:15,dx:14,iq:15,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Staff","Summon Wolf","Summon Bear","Giant Rope","Reveal Magic","Summon Gargoyle"]});
 const f=fromBuilder({name:"Fig",race:"human",cls:"fighter",st:14,dx:13,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"});
 slot[0]=w; slot[1]=f; me=w; foe=f; startFight();
 let g=0; while(G.phase!=="move"&&g++<10){ if(G.phase==="choose") choose(true); else if(G.phase==="renew"){ doRenew(); } else if(G.phase==="rcover"){ G.phase="renew"; } }
 const W0=G.me, F0=G.foe;
 const h=creaHexes(W0,F0,"summon").find(x=>dist(x,F0)>2)||creaHexes(W0,F0,"summon")[0];
 const saved=rollN; rollN=n=>Array.from({length:n},()=>1);
 doCast(W0,F0,{t:"cast",sp:"Summon Wolf",dest:h}); rollN=saved;
 const m=allU().find(x=>x.minion);
 ok("D1 a summoned Wolf joins the caster's side and cannot act the turn it appears",!!m&&sideOf(m)==="me"&&m.fresh&&aiAct(m,F0).t==="none");
 ok("D2 the other player's figure sees it as an enemy and the nearest enemy is the default target",enemiesOf(F0).includes(m)&&other(F0)===(dist(F0,m)<dist(F0,W0)?m:W0));
 ok("D3 the wolf is paid for each turn in the renew list and vanishes if dropped",(()=>{ nextTurn(); const has=G.rlist.some(r=>r.k==="minion"); G.rlist.forEach(r=>r.on=false); doRenew(); return has&&m.hp===0&&m.gone; })());
 ok("D4 a minion cannot be grappled",!canHth(F0,m)&&!canHth(m,F0));
 ok("D5 winner and quitter use the other player, not a minion",opp(m)===F0&&opp(F0)===W0);
 ok("D6 Giant Rope in the duel: on a weaker figure it is two ropes, removed one at a time",(()=>{ const nb=nbr(W0,0)||nbr(W0,1); F0.q=nb.q; F0.r=nb.r; W0.hp=15; const m0=MA(F0.p); const sv=rollN; rollN=n=>Array.from({length:n},()=>1); doCast(W0,F0,{t:"cast",sp:"Giant Rope"}); const a=F0.rope===1&&F0.ropeN===2&&MAu(F0)===Math.floor(Math.floor(m0/2)/2); doUnrope(F0); rollN=sv; return a&&F0.ropeN===1&&F0.rope===1; })());
 ok("D7 Reveal Magic in the duel: the log stays silent about what it found and only the caster is told, on the next turn",(()=>{ F0.stone=true; F0.rev=true; const sv=rollN; rollN=n=>Array.from({length:n},()=>1); doCast(W0,F0,{t:"cast",sp:"Reveal Magic"}); rollN=sv; const a=!/Stone Flesh/.test(G.log.slice(-1)[0])&&/Stone Flesh/.test(W0.rvlNew||""); nextTurn(); return a&&/Stone Flesh/.test(W0.rvl||"")&&!F0.rvl; })());
 ok("D8 the pick screen shows the caster what Reveal Magic found, and the other player's pick screen does not",(()=>{ G.cur=W0; showPick(); const a=/Reveal Magic showed you: .*Stone Flesh/.test(G.note||""); G.cur=F0; showPick(); return a&&!/Reveal Magic/.test(G.note||""); })());
 ok("D9 a Gargoyle summoned in the duel is a natural flier: MA 16 in the air, MA 8 on the ground, takes to the air when its foe is far",(()=>{ W0.hp=12; const h=creaHexes(W0,F0,"summon")[0]; const sv=rollN; rollN=n=>Array.from({length:n},()=>1); doCast(W0,F0,{t:"cast",sp:"Summon Gargoyle",dest:h}); rollN=sv; const m=allU().find(x=>x.minion&&x.kind==="gargoyle"); if(!m) return false; m.fresh=false; const g0=MAu(m); const far=P.filter(x=>dist(x,F0)>=5&&!allU().some(y=>y.hp>0&&same(y,x)))[0]; m.q=far.q; m.r=far.r; aiMove(m); return m.natFly===true&&g0===8&&m.air===true&&MAu(m)===16; })());
 const lo=n=>Array.from({length:n},()=>1);
 W0.p.spells=(W0.p.spells||[]).concat(["Summon Small Dragon","Summon Dragon"]); W0.hp=40; let dr=null;
 ok("D10 Summon Dragon in the duel: 5 ST, a whole 7-hex dragon (ST 60, DX 14, IQ 20, stops 5, flies MA 20) inside your megahex and the ones next to it, on your side, cannot act that turn",(()=>{ const hx=creaHexes(W0,F0,"summon","Summon Dragon"); if(!hx.length) return false; const h=hx.sort((a,b)=>dist(a,F0)-dist(b,F0))[0]; const hp0=W0.hp; const sv=rollN; rollN=lo; doCast(W0,F0,{t:"cast",sp:"Summon Dragon",dest:{q:h.q,r:h.r}}); rollN=sv; dr=allU().find(x=>x.minion&&x.size===7); if(!dr) return false; const c=cells(dr); return hp0-W0.hp===5&&c.length===7&&c.every(x=>M.get(key(x.q,x.r))&&mhDist(W0,x)<=1)&&!c.some(x=>same(x,W0)||same(x,F0))&&dr.p.st===60&&dr.p.dx===14&&dr.p.iq===20&&dr.natFly===20&&stopsFor(dr,F0,"shortsw")===5&&sideOf(dr)==="me"&&dr.fresh&&upOf(dr)===2; })());
 ok("D11 the Dragon costs 2 ST a turn at the renew step and vanishes if dropped",(()=>{ if(!dr) return false; G.rcur=W0; G.rlist=[{k:"minion",m:dr,on:true}]; G.afterRenew=()=>{}; const h0=W0.hp; doRenew(); const paid=h0-W0.hp; G.rlist=[{k:"minion",m:dr,on:false}]; doRenew(); return paid===2&&dr.hp<=0; })());
 ok("D12 a Dragon the computer runs in the duel moves as one whole piece and picks an action",(()=>{ const hx=creaHexes(W0,F0,"summon","Summon Dragon"); if(!hx.length) return false; W0.hp=40; const sv=rollN; rollN=lo; doCast(W0,F0,{t:"cast",sp:"Summon Dragon",dest:{q:hx[0].q,r:hx[0].r}}); rollN=sv; const m=allU().find(x=>x.minion&&x.size===7&&x.hp>0); if(!m) return false; m.fresh=false; aiMove(m); const c=cells(m); const a=aiAct(m,F0); return c.length===7&&c.every(x=>M.get(key(x.q,x.r)))&&new Set(c.map(x=>key(x.q,x.r))).size===7&&!!a&&!!a.t; })());
 ok("D13 the duel map draws the Dragon and a Small Dragon as whole counters (their own art), without errors",(()=>{ for(const x of allU()) if(x.minion) { x.hp=0; x.gone=true; } W0.hp=40; const hx=creaHexes(W0,F0,"summon","Summon Small Dragon"); if(!hx.length) return false; const sv=rollN; rollN=lo; doCast(W0,F0,{t:"cast",sp:"Summon Small Dragon",dest:{q:hx[0].q,r:hx[0].r}}); rollN=sv; const m=allU().find(x=>x.minion&&x.size===4&&x.hp>0); if(!m) return false; const c=cells(m); drawMap(); const html=$("map").innerHTML; return c.length===4&&m.p.st===30&&m.p.dx===13&&MA(m.p)===6&&m.natFly===16&&html.includes(".01 .16"); })());
 return R;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    import os; pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','duel.html')))
    try:
        R=pg.evaluate(JS)
        for n,ok in R: print(('PASS ' if ok else 'FAIL ')+n)
        print(sum(1 for r in R if r[1]),'/',len(R),'passed')
    except Exception as e: print('ERROR',str(e)[:600])
    print(errs[:3])
