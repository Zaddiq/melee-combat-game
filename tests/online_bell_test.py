"""Online table: the bell (a pitch per player), phone sound, wake lock and rejoining in the middle of a pick. Fake Firebase (?net=mem).
Run: python3 tests/online_bell_test.py  (needs Playwright). The bell's real sound, vibration and the screen lock cannot be heard or seen here:
the tests check that the right calls are made (a wrapper counts every ring that was actually started) and that the Web Audio path runs without errors."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

BEGIN = """(n)=>{ G=null; NP=n; MODE="ffa"; for(let i=0;i<4;i++) tmAB[i]=i%2; applyMode(); starts.fill(null);
  for(let i=0;i<4;i++) slot[i]=i<n?fromBuilder({name:"P"+(i+1),race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}):null; startFight(); }"""
TOPICK = """()=>{ let g=0; while(g++<60&&G.phase!=="over"&&!["cover","pick"].includes(G.phase)){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="rcover") G.phase="renew"; else if(G.phase==="renew") doRenew(); else break; } ui(); }"""
SPY = "()=>{ window.__rings=[]; const o=Bell.ring.bind(Bell); Bell.ring=i=>{ const r=o(i); if(r) window.__rings.push(i); return r; }; }"
FAKE_WL = "Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:async()=>{ window.__wl=(window.__wl||0)+1; return {released:false,release:async()=>{}}; }}});"

with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    ctx.add_init_script(FAKE_WL)
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload(); host.evaluate(SPY)
    host.click("#online summary"); host.fill("#onName", "BELL"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    host.wait_for_function("window.__wl>=1")
    ok("B1 the tablet asks to keep its screen awake when the table opens", host.evaluate("()=>window.__wl")>=1)
    def phone(name):
        pg = mk("phone.html?net=mem&room=BELL"); pg.evaluate(SPY); pg.fill("#nm", name); pg.click("#go")
        pg.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')"); return pg
    A = phone("Bo"); B = phone("Cy")
    ok("B2 each phone asks to keep its screen awake once it joins", A.evaluate("()=>window.__wl")>=1 and B.evaluate("()=>window.__wl")>=1)

    NONE = lambda pg: max(pg.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"), 0)
    host.evaluate(BEGIN, 2); host.evaluate(TOPICK); host.wait_for_function("G.phase==='cover'&&Object.keys(__online.state().sess).length===2")
    A.wait_for_selector("#play .opt"); B.wait_for_selector("#play .opt")
    host.wait_for_timeout(1200); host.evaluate("()=>{ ui(); ui(); ui(); }")
    RH=lambda: host.evaluate("()=>window.__rings"); RA=lambda: A.evaluate("()=>window.__rings"); RB=lambda: B.evaluate("()=>window.__rings")
    h0=len(RH())
    ok("B3 when the picks begin the tablet rings every phone player's own pitch (player 1, then player 2, one after the other), and redraws add nothing", RH()[-2:]==[0,1] and len(RH())==h0)
    ok("B4 each phone rings its own pitch (player 1's phone C5-ish 0, player 2's phone 1) and never the other's", RA()[-1:]==[0] and set(RA())<={0,1} and RB()[-1:]==[1] and set(RB())<={0,1})
    b0=len(RB()); host.click("#bRing"); B.wait_for_function(f"window.__rings.length>={b0+1}")
    ok("B6 'Ring again' rings the tablet for everyone still picking and the waiting phones again", RH()[-2:]==[0,1] and len(RH())==h0+2 and RB()[-1:]==[1])
    A.click(f'#play .opt[data-b="{NONE(A)}"]'); A.wait_for_function("document.getElementById('play').textContent.includes('Your pick is in')")
    host.click("#bRing"); host.wait_for_timeout(300)
    ok("B5 once a phone has picked, 'Ring again' rings only the players who have not", RH()[-1:]==[1] and len(RH())==h0+3)

    # a phone that went to sleep and comes back in the middle of its pick
    B.reload()
    B.wait_for_selector("#play .opt")
    ok("B7 a phone that reloads in the middle of its pick gets its choices back", B.locator("#play .opt").count()>1 and "Player 2" in B.inner_text("#seat"))
    B.click(f'#play .opt[data-b="{NONE(B)}"]'); host.wait_for_function("G.turn===2")
    ok("B8 and its pick still counts: both picks go in and the turn resolves", host.evaluate("()=>G.turn")==2)

    # sound off on the tablet: no more rings there
    n0 = host.evaluate("()=>window.__rings.length")
    host.click("#onBell"); host.evaluate(TOPICK); host.wait_for_function("G.phase==='cover'&&Object.keys(__online.state().sess).length===2"); host.wait_for_timeout(1000)
    n = host.evaluate("()=>window.__rings.length")
    ok("B9 with the tablet bell off, nothing rings on the tablet", host.evaluate("()=>!Bell.on") and n==n0)
    host.click("#onBell")
    ok("B10 the bell can be turned on again", host.evaluate("()=>Bell.on"))
    A.click("#snd")
    ok("B11 a phone can switch its own sound off", "off" in A.inner_text("#snd"))
    ok("B12 the Web Audio path ran without errors (the tablet really started rings)", host.evaluate("()=>Bell.ctx&&Bell.rang>=3"))
    ok("B13 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
