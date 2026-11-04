"""Playtest fixes: one phone against the computer. Facing can be chosen on the phone before the fight; End movement is on screen (not under the results bar) on a small phone; connection info sits below the game stuff.
Fake Firebase (?net=mem)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url, vp=None):
        pg = ctx.new_page()
        if vp: pg.set_viewport_size(vp)
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.fill("#onName", "FIXX"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=FIXX", {"width": 360, "height": 640}); ph.fill("#nm", "Bo"); ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    host.select_option("#npSel", "1")
    host.evaluate("""()=>{ slot[0]=fromBuilder({name:"Bo",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}); ui(); drawMap(); }""")
    ph.wait_for_function("lastP&&lastP.sc&&lastP.sc.hk==='start'")
    ok("P1 the start screen has the six facing circles", ph.evaluate("!!lastP.sc.fc") and ph.locator("#pmap [data-f]").count() == 6)
    ok("P2 the connection card is under the game area (not above the map)", ph.evaluate("()=>document.getElementById('play').getBoundingClientRect().top<document.getElementById('inCard').getBoundingClientRect().top"))
    want = 2
    ph.locator(f'#pmap [data-f="{want}"]').dispatch_event("click")
    ph.wait_for_function("(w)=>lastP.sc.fc.f===w", arg=want)
    ok("P3 tapping a circle chooses the starting facing", host.evaluate("()=>Online.startFace[0]") == want)
    host.evaluate("()=>startFight()"); host.wait_for_function("G&&['choose','move'].includes(G.phase)")
    ok("P4 the figure starts facing the way the phone chose (and the choice is cleared)", host.evaluate("()=>G.players[0].f") == want and host.evaluate("()=>Object.keys(Online.startFace).length") == 0)
    if host.evaluate("()=>G.phase")=="choose" and host.evaluate("()=>G.players.indexOf(G.chooser===undefined?null:G.players[G.chooser])")==0:
        ph.wait_for_selector("#play .opt"); ph.click('#play .opt[data-b="0"]')
    host.wait_for_function("G.phase==='move'&&G.cur===G.players[0]", timeout=60000)
    ph.wait_for_function("lastP&&lastP.mode==='map'&&lastP.sc.hl&&lastP.btns.some(b=>b.l==='End movement')")
    hl = ph.evaluate("lastP.sc.hl"); t = max(hl, key=lambda x: x[2])
    ph.locator(f'#pmap [data-h="{t[0]},{t[1]}"]').dispatch_event("click")
    ph.wait_for_function("lastP&&lastP.btns.some(b=>b.l==='Undo move')")
    ph.evaluate("window.scrollTo(0,0)")
    vis = ph.evaluate("""()=>{ const b=[...document.querySelectorAll('#play .opt')].find(x=>x.textContent.includes('End movement')); const r=b.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return {onScreen:r.bottom<=innerHeight&&r.top>=0, top:!!e&&(e===b||b.contains(e))}; }""")
    ok("P5 after moving, End movement is on screen without scrolling and nothing covers it (small phone)", vis["onScreen"] and vis["top"])
    ok("P6 the results bar shows one line by default", ph.locator("#resBar div").count() <= 1 or ph.locator("#resBar div").count() == 1)
    ph.click("#play .opt:has-text('End movement')")
    host.wait_for_function("G.phase!=='move'||G.cur!==G.players[0]")
    ok("P7 End movement on the phone ends the turn", host.evaluate("()=>G.phase!==\"move\"||G.cur!==G.players[0]"))
    ok("P8 no script errors", not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
