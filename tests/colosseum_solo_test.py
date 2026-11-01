"""One player against the computer in colosseum.html (a computer fighter 'man' or a beast), through the real buttons.
Run: python3 tests/colosseum_solo_test.py  (needs Playwright)."""
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
    pg.select_option("#npSel", "1")
    ok("L1 choosing one player picks a computer fighter as the opponent (no 'none' choice)", pg.input_value("#creSel") == "man" and pg.locator("#creSel option[value=none]").count() == 0)
    ok("L2 the note says you fight alone against the computer", "alone" in pg.inner_text("#npNote"))
    pg.click("#ex0")
    ok("L3 with one fighter loaded the screen offers Start (not 'put two teams in play')", pg.locator("#bGo").count() == 1)
    pg.click("#bGo")
    ok("L4 the fight starts: one player and one computer fighter", pg.evaluate("()=>!!G&&G.players.length===1&&G.mobs.length===1&&G.mobs[0].kind==='man'"))
    ok("L5 the computer fighter has gear (a weapon, ST and DX near the player's total)", pg.evaluate("()=>{ const m=G.mobs[0]; return m.p.st>=6&&m.p.dx>=6&&(m.p.right!=='none'||m.p.left!=='none')&&Math.abs((m.p.st+m.p.dx)-(G.players[0].p.st+G.players[0].p.dx))<=3; }"))
    pg.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); else if(G.phase==='renew') doRenew(); else break; } }")
    ok("L6 picking goes straight to the options: no 'pass the tablet' cover screen for a lone player", pg.evaluate("()=>G.phase==='pick'") and "Pass the tablet" not in pg.inner_text("#ctl") and "look away" not in pg.inner_text("#ctl"))
    ok("L7 and the screen does not tell anyone to look away", "must not look" not in pg.inner_text("#ctl"))
    # a beast also works alone
    pg.evaluate("()=>{ G=null; $('setup').open=true; ui(); }")
    pg.select_option("#creSel", "wolf"); pg.select_option("#creN", "2")
    ok("L8 a lone player can also choose beasts (2 wolves)", pg.input_value("#creSel") == "wolf" and pg.locator("#bGo").count() == 1)
    # changing the setup in the middle of a fight asks, and then really changes it
    pg.evaluate("()=>{ G=null; $('setup').open=true; ui(); }")
    pg.select_option("#npSel", "2"); pg.select_option("#creSel", "wolf"); pg.click("#ex0"); pg.click("#ex1"); pg.click("#bNext"); pg.click("#bGo")
    ok("L10 a 2-player fight against wolves is running", pg.evaluate("()=>G&&G.players.length===2&&G.mobs.length>0"))
    pg.evaluate("()=>{ $('setup').open=true; }")
    pg.once("dialog", lambda d: d.dismiss()); pg.select_option("#npSel", "1")
    ok("L11 declining the question keeps the running 2-player fight", pg.evaluate("()=>NP===2&&G&&G.players.length===2") and pg.input_value("#npSel") == "2")
    pg.once("dialog", lambda d: d.accept()); pg.select_option("#npSel", "1")
    ok("L12 accepting it leaves the fight and sets one player (only one player on the map afterwards)", pg.evaluate("()=>NP===1&&!G&&document.querySelectorAll('#pcard1')[0].style.display==='none'") and pg.input_value("#npSel") == "1")
    pg.click("#bGo")
    ok("L13 and the next fight really has one player", pg.evaluate("()=>G&&G.players.length===1"))
    ok("L9 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
