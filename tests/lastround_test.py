"""Bell volume levels + the 'Last round' block kept below the choices. Run: python3 tests/lastround_test.py"""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    r = pg.evaluate("()=>{ Bell.init(localStorage,'t'); const a=Bell.vol; Bell.nextVol(); const b=Bell.vol; Bell.nextVol(); Bell.nextVol(); return [a,b,Bell.vol,Bell.volName()]; }")
    ok("V1 volume starts at medium, cycles loud then wraps (quiet, medium)", r == [1, 2, 1, "medium"])
    ok("V2 the level is remembered", pg.evaluate("()=>{ Bell.vol=0; Bell.init(localStorage,'t'); return Bell.vol; }") == 1)
    pg.select_option("#npSel", "1"); pg.click("#ex0"); pg.click("#bGo")
    pg.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); } }")
    ok("V3 no Last round block before any round has been played", pg.locator("#lastRound").count() == 0)
    for _ in range(30):
        ph = pg.evaluate("()=>G.phase")
        if pg.evaluate("()=>G.last&&G.last.length>0") or ph == "over": break
        if ph == "resolve" or pg.locator("#bNext:has-text('Next turn')").count(): pg.evaluate("()=>endTurn()")
        elif pg.locator("#ctl [data-opt]").count(): pg.locator("#ctl [data-opt]").first.click()
        elif pg.locator("#ctl button:has-text('Next')").count(): pg.locator("#ctl button:has-text('Next')").first.click()
        else: pg.evaluate("()=>{ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); }")
    ok("V4 a round was recorded", pg.evaluate("()=>!!(G.last&&G.last.length)"))
    pg.evaluate("()=>ui()")
    ok("V5 the Last round block is on screen under the choices and above the log",
       pg.evaluate("()=>{ const l=document.getElementById('lastRound'), g=document.getElementById('log'); return !!l&&!!g&&(l.compareDocumentPosition(g)&4)>0; }"))
    ok("V6 it stays the same while the next round is being chosen", pg.evaluate("()=>{ const t=document.getElementById('lastRound').innerText; ui(); return document.getElementById('lastRound').innerText===t; }"))
    br.close()
    ok("V7 no script errors", not errs)
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
