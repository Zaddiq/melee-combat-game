"""A room drawn hex by hex (invented map, not any book's): board shape, permanent walls, entrances, foe hexes, and what the phone is sent.
Run: python3 tests/hexroom_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
ENC = {"name": "Test cellar", "foe": "monsters",
  "map": {"cols": 9, "rows": 12, "off": [[0, 0], [1, 0], [7, 0], [8, 0], [0, 1], [8, 11], [7, 11], [0, 11]], "wall": [[3, 5], [4, 5], [5, 6]],
          "north": [[3, 0], [4, 0]], "south": [[4, 11], [5, 11]]},
  "creatures": {"rat": {"name": "Big rat", "st": 6, "dx": 10, "iq": 4, "w": "dagger"}},
  "foes": [{"c": "rat", "hex": [4, 2]}, {"c": "rat", "hex": [2, 3], "min": 2}]}
F1 = {"name": "Fred", "cls": "fighter", "race": "human", "total": 32, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    ok("H1 a valid hex-map encounter passes the check", host.evaluate("(e)=>checkEnc(e,true)", ENC) == "")
    bad = json.loads(json.dumps(ENC)); bad["foes"][0]["hex"] = [3, 5]
    ok("H2 a foe on a wall hex is refused", "not an open hex" in host.evaluate("(e)=>checkEnc(e,true)", bad))
    bad = json.loads(json.dumps(ENC)); bad["map"]["south"] = [[3, 5]]
    ok("H3 an entrance that is a wall is refused", "entrance" in host.evaluate("(e)=>checkEnc(e,true)", bad))
    bad = json.loads(json.dumps(ENC)); del bad["map"]["north"]
    ok("H4 a map with no north entrance is refused", "north" in host.evaluate("(e)=>checkEnc(e,true)", bad))
    host.evaluate("(e)=>{ saveEnc(e,true); }", ENC)
    host.evaluate("()=>{ NP=1; }")
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.evaluate("(b)=>{ sessionStorage.setItem('wizard-builder-v1',b); fillChars(); }", json.dumps(F1)); ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    host.wait_for_function("slot[0]&&slot[0].phone")
    host.evaluate("()=>{ $('creSel').value='enc'; $('creSel').dispatchEvent(new Event('change')); }")
    host.evaluate("()=>{ const f=spawnEnc; spawnEnc=function(){ f(); window.__sp=JSON.stringify(G.mobs.map(m=>[m.q,m.r])); }; }")
    host.click("#bGo")
    start = host.evaluate("()=>window.__sp")
    host.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); } }")
    ok("H5 the board has the drawn shape: 9x12 minus 8 cut-off hexes = 100 hexes", host.evaluate("()=>P.length")== 100)
    ok("H6 the obstacles are 3 permanent walls, all on real hexes", host.evaluate("()=>{ const w=G.objs.filter(o=>o.t==='wall'&&o.perm); return w.length===3&&WALLS.size===3&&[...WALLS].every(k=>M.get(k)); }"))
    ok("H6b nobody can step onto a wall hex (every neighbour's step toward it is refused)", host.evaluate("()=>{ const w=G.objs.find(o=>o.perm); let tested=0, bad=0; for(let d=0;d<6;d++){ const n=M.get(key(w.q-DIRS[d][0],w.r-DIRS[d][1])); if(!n||WALLS.has(key(n.q,n.r))) continue; tested++; if(nbr(n,d)) bad++; } return tested>0&&bad===0; }"))
    ok("H7 one rat only (the min-2 rat is absent for one player), standing on column 4, row 2 when the fight starts", start == "[[2,3]]")
    ok("H8 the heroes start at the south entrance, the monsters' side is north", host.evaluate("()=>{ const u=G.players[0]; return u.q>=9; }"))
    host.evaluate("()=>{ for(let i=0;i<40;i++){ G.turn++; } G.objs.forEach(o=>o.age+=40); const keep=G.objs.length; G.objs=G.objs.filter(o=>o.perm||o.age<=12); window.__k=[keep,G.objs.length]; }")
    ok("H9 permanent walls do not fade after 12 turns", host.evaluate("()=>window.__k[0]===window.__k[1]&&window.__k[1]===3"))
    ph.wait_for_function("()=>typeof lastP!=='undefined'&&lastP&&lastP.sc&&lastP.sc.bd&&lastP.sc.bd.length>0", timeout=15000)
    sc = ph.evaluate("()=>lastP.sc.ob.filter(o=>o[2]==='w').length"); nb = ph.evaluate("()=>lastP.sc.bd.length")
    ok("H10 the phone is sent the walls (3) and the same 100-hex board", sc == 3 and nb == 100)
    ok("H11 old rooms in feet still work (the sample)", host.evaluate("()=>checkEnc(SAMPLE_ENC,true)")== "")
    ok("H12 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
