from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/wizard-arena.html')
    r=pg.evaluate('''()=>{ me=fromBuilder({name:"T",race:"human",cls:"wizard",st:14,dx:14,iq:15,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Staff","Teleport"]}); foeMode={k:"random"}; foe=buildFoe(); startFight();
      let g=0; while(G.phase!=="pick"&&g++<20){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="renew") doRenew(); }
      ui(); [...document.querySelectorAll("[data-opt]")].find(e=>/Cast a spell/.test(e.textContent)).click();
      [...document.querySelectorAll("[data-sp]")][0].click(); const ph=G.phase, n=document.querySelectorAll("[data-dest]").length;
      const h=document.querySelectorAll("[data-dest]")[Math.floor(n/2)]; h.dispatchEvent(new MouseEvent("click",{bubbles:true}));
      return [ph,n,G.phase,G.log.slice(-4)]; }''')
    print(r, errs)
