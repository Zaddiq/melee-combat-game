from playwright.sync_api import sync_playwright
import sys
page=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1100,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/'+page)
    if page=='wizard-arena.html':
        r=pg.evaluate('''()=>{ me=fromBuilder({name:"Tarn",race:"human",cls:"wizard",st:15,dx:14,iq:15,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Staff","Summon Wolf"]}); foeMode={k:"random"}; foe=buildFoe(); startFight();
          let g=0; while(G.phase!=="pick"&&g++<20){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="renew") doRenew(); }
          const h=creaHexes(G.me,G.foe,"summon")[3]; summonMinion(G.me,"wolf",h); G.me.act={t:"none"}; resolveTurn({t:"none"}); ui(); drawMap(); return [G.phase,G.log.slice(-3)]; }''')
        print(r)
        for i in range(8):
            ph=pg.evaluate("G.phase")
            print(i,ph, pg.evaluate("document.getElementById('ctl').innerText.slice(0,120)"))
            if ph=="renew":
                btn=pg.query_selector("[data-rn]"); print("toggle", btn.inner_text() if btn else None)
                pg.click("#bRn")
            elif ph=="choose": pg.click("#b1")
            elif ph=="move": pg.click("#bOk")
            else: break
    print(errs)
