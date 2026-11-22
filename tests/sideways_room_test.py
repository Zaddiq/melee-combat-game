"""A drawn room whose entrances lie left and right (a book map turned on its side) still seats 1 to 4 players and up to 20 foes.
Run: python3 tests/sideways_room_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
ENC = {"name": "Sideways", "foe": "foes", "map": {"cols": 14, "rows": 6, "off": [], "wall": [[6, 4]], "north": [[0, 1], [0, 2], [0, 3], [0, 4]], "south": [[13, 1], [13, 2], [13, 3], [13, 4]]},
       "creatures": {"rat": {"name": "Rat", "st": 1, "dx": 10, "iq": 6, "w": "dagger"}},
       "foes": [{"c": "rat", "hex": [3 + i % 8, i // 8 + 1]} for i in range(18)]}
F = {"name": "Fred", "cls": "fighter", "race": "human", "total": 32, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("S1 18 foes are accepted (the limit is 20)", pg.evaluate("(e)=>checkEnc(e,true)", ENC) == "")
    for n in (1, 4):
        r = pg.evaluate("""([e,n,f])=>{ ENC=e; applyEnc(e); CREK='enc'; CREN=e.foes.length; NP=n; MODE='ffa'; applyMode(); syncMap(); starts.fill(null); G=null;
          for(let k=0;k<4;k++) slot[k]=k<n?fromBuilder(Object.assign({},f,{name:'P'+k}),k):null; startFight();
          const east=G.players.every(u=>u.p&&P.find(h=>h.q===u.q&&h.r===u.r&&h.e)); return [!!G, G.players.length, G.mobs.length, new Set(G.units.map(u=>u.q+','+u.r)).size===G.units.length, east]; }""", [ENC, n, F])
        ok(f"S{n+1} {n} player(s) start on the listed south hexes, {r[2]} foes, nobody shares a hex", r[0] and r[1] == n and r[2] == 18 and r[3] and r[4])
    ok("S6 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
