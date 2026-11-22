"""The computer's single fighter is sized by ST+DX, plus a wizard's IQ above 8. Run: python3 tests/wizard_size_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
def opp_size(pg, hero):
    pg.reload(); pg.select_option("#npSel", "1"); pg.select_option("#creSel", "man")
    pg.evaluate("(o)=>{ setP(0,fromBuilder(o),'x'); }", hero); pg.click("#bGo")
    return pg.evaluate("()=>{ const m=G.mobs[0].p; return m.st+m.dx; }")
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()")
    W1 = {"name": "Wen", "cls": "wizard", "race": "human", "total": 32, "st": 9, "dx": 12, "iq": 11, "spells": ["Staff", "Magic Fist", "Blur"], "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
    W2 = dict(W1, iq=8, spells=[], total=29, name="Low")
    F1 = {"name": "Fred", "cls": "fighter", "race": "human", "total": 32, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
    ok("Z1 a wizard (ST 9, DX 12, IQ 11) is matched at 21 + 3 = 24", opp_size(pg, W1) == 24)
    ok("Z2 a wizard with IQ 8 gets no extra (21, but never under 16)", opp_size(pg, W2) == 21)
    ok("Z3 a fighter is sized as before (ST+DX = 28, IQ ignored)", opp_size(pg, F1) == 28)
    ok("Z4 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
