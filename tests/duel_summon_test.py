"""Summons and many-figure checks for duel.html. Run: python3 tests/duel_summon_test.py  (needs Playwright)."""
from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const R=[]; const ok=(n,c)=>R.push([n,!!c]);
 const w=fromBuilder({name:"Wiz",race:"human",cls:"wizard",st:15,dx:14,iq:15,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Staff","Summon Wolf","Summon Bear"]});
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
