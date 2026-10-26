from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1100,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/wizard-arena.html')
    pg.evaluate('''()=>{ me=fromBuilder({name:"Tarn",race:"human",cls:"wizard",st:15,dx:14,iq:15,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Staff","Summon Wolf","Summon Bear"]}); foeMode={k:"wizard"}; foe=buildFoe(); startFight();
      let g=0; while(G.phase!=="pick"&&g++<20){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="renew") doRenew(); }
      const h=creaHexes(G.me,G.foe,"summon")[3]; summonMinion(G.me,"wolf",h); const h2=creaHexes(G.foe,G.me,"summon")[2]; summonMinion(G.foe,"bear",h2); ui(); drawMap(); }''')
    pg.screenshot(path='/tmp/claude-0/-home-claude/9d29f0d7-f765-5431-b054-2ee8616c7d7c/scratchpad/shot.png'); print(errs)
