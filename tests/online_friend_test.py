"""Fight a friend online: colosseum.html?friend=1 opens a table by itself, the host keeps Player 1, the friend gets Player 2,
and no pass-the-tablet screens appear. Fake Firebase (?net=mem)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
SETUP = """()=>{ for(let i=0;i<2;i++) slot[i]=fromBuilder({name:["Bo","Cy"][i],race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}); ui(); drawMap(); }"""
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    m = mk("index.html"); ok("F1 the menu has a Fight a friend online card", m.locator('a[href="colosseum.html?friend=1"]').count() == 1)
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.goto(BASE + "colosseum.html?net=mem&friend=1")
    host.wait_for_function("document.querySelector('#friendBox b')&&document.querySelector('#friendBox b').textContent.length>=3")
    code = host.inner_text("#friendBox b")
    ok("F2 the table opens by itself and the player count is two", host.evaluate("()=>NP")==2 and len(code) >= 3)
    ph = mk(f"phone.html?net=mem&room={code}"); ph.fill("#nm", "Friend"); ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("F3 the friend gets Player 2 (the host keeps Player 1)", ph.inner_text("#seat").startswith("You are Player 2"))
    host.wait_for_function("document.getElementById('friendBox').innerText.includes('has joined as Player 2')")
    host.evaluate(SETUP)
    host.evaluate("()=>startFight()")
    host.wait_for_function("G&&G.phase==='choose'")
    chooser = host.evaluate("()=>G.chooser")
    if chooser == 0: host.click("#b1")
    else: ph.wait_for_selector("#play .opt"); ph.click('#play .opt[data-b="0"]')
    host.wait_for_function("G.phase==='move'")
    for _ in range(2):
        who = host.evaluate("()=>G.players.indexOf(G.cur)")
        if who == 0: host.click("#bOk")
        else:
            ph.wait_for_function("lastP&&lastP.mode==='map'&&lastP.sc.hl"); ph.click('#play .opt[data-b="0"]')
        host.wait_for_function("(w)=>G.cur!==G.players[w]||G.phase!=='move'", arg=who)
    host.wait_for_function("['cover','pick'].includes(G.phase)")
    ok("F4 the host's own pick starts at once, with no pass-the-tablet screen", host.evaluate("()=>G.phase")=="pick" and "Pass the tablet" not in host.inner_text("#ctl"))
    ph.wait_for_function("lastP&&lastP.ph==='pick'&&lastP.btns.length>0")
    ph.click('#play .opt[data-b="0"]')
    host.click("[data-opt]")
    host.wait_for_function("G.turn===2||G.phase==='over'||G.phase==='choose'")
    ok("F5 both picks are in and the turn resolves", host.evaluate("()=>G.turn")>=1 and "Pass the tablet" not in host.inner_text("#ctl"))
    ok("F6 no script errors", not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
