import http.server,socketserver,threading,functools,json
from playwright.sync_api import sync_playwright
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=__file__.rsplit("/tests/",1)[0]);H.log_message=lambda *a,**k:None
srv=socketserver.TCPServer(("127.0.0.1",0),H);BASE=f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever,daemon=True).start()
n=0;bad=0
def ok(m,c):
    global n,bad; n+=1; bad+=not c; print(("PASS " if c else "FAIL ")+m)
CH={"name":"B","race":"human","cls":"fighter","st":14,"dx":14,"iq":8,"a":"lbow","b":"none","s1":"large","d1":"mace","d2":"none","armor":"none","camp":{"v":1,"langs":[],"tal":[],"purse":0,"inv":{}}}
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(e))
    pg.goto(BASE+"colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.select_option("#npSel","1"); pg.evaluate("(o)=>{ setP(0,fromBuilder(o),'x'); }",CH); pg.click("#bGo")
    pg.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); } }")
    st=pg.evaluate("()=>{const u=G.players[0]; return [u.right,u.left,u.slung,u.dag.join()]}")
    two=pg.evaluate("()=>options(G.players[0],G.mobs[0]).find(x=>x.t==='ready2')")
    ok("R1 setup: bow in hand, shield slung, mace carried",st==["lbow","none","large","mace"])
    ok("R2 with the bow in hand the pick screen offers Mace and Large shield together",two is not None and "Mace" in two["label"] and "Large shield" in two["label"])
    held=pg.evaluate("()=>{ const u=G.players[0]; const o=options(u,G.mobs[0]).find(x=>x.t==='ready2'); u.act={t:'ready2',it:o.it,it2:o.it2}; const pr=[o.it,o.it2].sort((x,y)=>(y.src==='slung')-(x.src==='slung')); applyReady(u,pr[0]); applyReady(u,pr[1]); return [u.right,u.left,u.slung,u.dag.length,G.floor.length]; }")
    ok("R3 doing it: mace right, shield left, bow slung on the back, nothing dropped",held==["mace","large","lbow",0,0])
    ok("R4 no script errors",not errs)
print(f"{n-bad}/{n} passed")
