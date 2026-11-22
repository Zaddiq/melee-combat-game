"""A computer wizard as the Colosseum's opponent. Run: python3 tests/wizard_opp_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
F1 = {"name": "Fred", "cls": "fighter", "race": "human", "total": 32, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("W1 the computer-side box offers a computer wizard", "wizard" in pg.eval_on_selector_all("#creSel option", "e=>e.map(x=>x.value)"))
    seen = []
    for i in range(8):
        pg.reload(); pg.select_option("#npSel", "1"); pg.select_option("#creSel", "wizard"); pg.evaluate("(o)=>{ setP(0,fromBuilder(o),'x'); }", F1); pg.click("#bGo")
        seen.append(pg.evaluate("""()=>{ const m=G.mobs[0], p=m.p; const bad=p.spells.filter(n=>(SPIQ[n]||99)>p.iq); return {cls:p.cls,st:p.st,dx:p.dx,iq:p.iq,tot:p.st+p.dx+p.iq,n:p.spells.length,staff:p.spells.includes('Staff'),fist:p.spells.includes('Magic Fist'),bad:bad.length,caster:!!m.caster,armor:p.armor,right:m.right}; }"""))
    ok("W2 it is a wizard with IQ 11-14 and a ST of at least 10", all(s["cls"] == "wizard" and 11 <= s["iq"] <= 14 and s["st"] >= 10 for s in seen))
    ok("W3 it is sized to the player's total (32 points, give or take 1 for rounding)", all(abs(s["tot"] - 32) <= 1 for s in seen))
    ok("W4 it knows Staff and Magic Fist, no spell above its IQ, and at least 4 spells", all(s["staff"] and s["fist"] and s["bad"] == 0 and s["n"] >= 4 for s in seen))
    ok("W5 it wears no armor, carries the staff, and is flagged as a caster", all(s["armor"] == "none" and s["right"] == "staff" and s["caster"] for s in seen))
    # play a couple of fights: no errors, and it casts something
    casts = 0
    for g in range(3):
        pg.reload(); pg.select_option("#npSel", "1"); pg.select_option("#creSel", "wizard"); pg.evaluate("(o)=>{ setP(0,fromBuilder(o),'x'); window.__c=0; const d=doCast; doCast=function(u,o,pa){ if(u.side==='mob') window.__c++; return d.apply(this,arguments); }; }", F1); pg.click("#bGo")
        for _ in range(60):
            ph = pg.evaluate("()=>G.phase")
            if ph == "over": break
            if ph == "resolve" or pg.locator("#bNext:has-text('Next turn')").count(): pg.evaluate("()=>endTurn()")
            elif pg.locator("#ctl [data-opt]").count(): pg.locator("#ctl [data-opt]").first.click()
            else: pg.evaluate("()=>{ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); }")
        casts += pg.evaluate("()=>window.__c")
    ok("W6 in real play the wizard casts spells", casts > 0)
    ok("W7 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
