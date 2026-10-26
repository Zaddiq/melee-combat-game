from playwright.sync_api import sync_playwright
JS='''()=>{ const out=[]; for(const t of [20,24,28,32,36]){ me=fromBuilder({name:"m",race:"human",cls:"fighter",st:Math.ceil(t/2),dx:Math.floor(t/2),iq:8,a:"shortsw",b:"small",armor:"leather",d1:"dagger"}); const c={};
 for(let i=0;i<40;i++){ const f=makeOpponent(t); const k=f.race+" "+f.st+"/"+f.dx+" "+f.right+"+"+f.left+" "+f.armor+" adj"+adjDX(f); c[k]=(c[k]||0)+1; }
 out.push(t+": "+Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,4).map(e=>e[0]+" x"+e[1]).join(" | ")); } return out; }'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/melee-combat-game/arena.html'); print("\n".join(pg.evaluate(JS))); print(errs)
