"""Starting a Colosseum game through the real buttons: 2 players against 3 wolves (no shortcut into startFight).
Run: python3 tests/colosseum_start_test.py  (needs Playwright)."""
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
    pg.select_option("#npSel", "2"); pg.select_option("#creSel", "wolf"); pg.select_option("#creN", "3")
    pg.click("#ex0"); pg.click("#ex1")
    ok("T1 with creatures chosen and both fighters loaded, the setup offers a way forward (not 'put two teams in play')", "at least two teams" not in pg.inner_text("#ctl") and pg.locator("#bNext").count() == 1)
    ok("T2 the setup says where facing can be changed", "small circles" in pg.inner_text("#ctl"))
    pg.screenshot(path="/tmp/claude-0/place1.png")
    pg.click("#bNext")
    ok("T3 the last player's step has the Start button", pg.locator("#bGo").count() == 1)
    pg.click("#bGo")
    ok("T4 clicking Start begins the fight: 2 players and 3 wolves on the board", pg.evaluate("()=>!!G&&G.players.length===2&&G.mobs.length===3"))
    ok("T5 every player starts facing the nearest wolf (it is in front of them)", pg.evaluate("()=>G.players.every(u=>{ const m=G.mobs.filter(x=>x.hp>0).sort((a,b)=>hdist(u,a)-hdist(u,b))[0]; return inFront(u,m); })"))
    ok("T6 and every wolf faces its nearest player", pg.evaluate("()=>G.mobs.every(m=>{ const h=G.players.slice().sort((a,b)=>hdist(m,a)-hdist(m,b))[0]; return inFront(m,h); })"))
    ok("T7 the movement phase offers the facing circles", pg.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='move'){ if(G.phase==='choose') choose(true); else break; } return G.phase==='move'; }") and (pg.evaluate("()=>drawMap()") or True) and pg.locator("[data-face]").count() >= 6)
    pg.screenshot(path="/tmp/claude-0/move1.png")
    f0 = pg.evaluate("()=>G.cur.f"); want = (f0 + 2) % 6
    pg.locator(f'[data-face="{want}"]').first.click(force=True)
    ok("T8 clicking a facing circle turns the figure to that direction", pg.evaluate("()=>G.cur.f") == want and want != f0)
    ok("T9 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
