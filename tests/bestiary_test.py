"""Bestiary (campaign/bestiary.html): add/edit/remove monsters, import from a module, and pick them as the computer side in the Colosseum.
Run: python3 tests/bestiary_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
MOD = {"module": "Test", "encounters": [{"name": "r1", "foe": "x", "room": [40, 40], "creatures": {"ogre": {"name": "Ogre", "st": 28, "dx": 9, "iq": 6, "w": "club3", "armor": "bighide", "race": "human"}, "bad": {"name": "Bad", "st": 999, "dx": 0, "iq": 8, "w": "nope", "armor": "zzz"}}, "foes": [{"c": "ogre", "at": [.5, .5]}]}]}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "bestiary.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("B1 starts empty", pg.is_visible("#empty"))
    pg.click("#add"); pg.fill("#f_name", "Cave Troll"); pg.fill("#f_st", "26"); pg.fill("#f_dx", "10"); pg.fill("#f_iq", "6"); pg.select_option("#f_w", "club3"); pg.select_option("#f_armor", "bighide"); pg.fill("#f_note", "Regrows. Hates light."); pg.click("#save")
    ok("B2 a saved monster shows its stats, weapon damage and note", all(t in pg.inner_text("#list") for t in ["Cave Troll", "ST 26", "DX 10", "Hates light"]))
    pg.click("[data-edit=cave_troll]"); pg.fill("#f_st", "27"); pg.click("#save")
    ok("B3 editing changes it in place (still one)", pg.evaluate("()=>JSON.parse(localStorage.getItem('bestiary-v1')).map(x=>x.st)") == [27])
    pg.click("#add"); pg.fill("#f_name", ""); pg.click("#save"); ok("B4 a monster needs a name", "name" in pg.inner_text("#edMsg").lower())
    pg.click("#cancel")
    pg.evaluate("(m)=>localStorage.setItem('colosseum-module',JSON.stringify(m))", MOD); pg.click("#fromMod")
    names = pg.evaluate("()=>JSON.parse(localStorage.getItem('bestiary-v1')).map(x=>x.name)")
    ok("B5 the module's monsters are added once, with values checked", "Ogre" in names and "Bad" in names)
    bad = pg.evaluate("()=>JSON.parse(localStorage.getItem('bestiary-v1')).find(x=>x.name==='Bad')")
    ok("B6 out-of-range values fall back to plain ones", bad["st"] == 10 and bad["w"] == "none" and bad["armor"] == "none")
    pg.click("#fromMod"); ok("B7 adding the module again makes no copies", pg.evaluate("()=>JSON.parse(localStorage.getItem('bestiary-v1')).length") == 3)
    pg.fill("#q", "troll"); ok("B8 search narrows the list", pg.locator("#list .mon").count() == 1); pg.fill("#q", "")
    pg.once("dialog", lambda d: d.accept()); pg.click("[data-del=bad]"); ok("B9 remove works", pg.evaluate("()=>JSON.parse(localStorage.getItem('bestiary-v1')).length") == 2)
    pg.goto(BASE + "colosseum.html")
    opts = pg.evaluate("()=>[...document.querySelectorAll('#creSel optgroup option')].map(o=>o.textContent)")
    ok("B10 the Colosseum offers them under My bestiary", len(opts) == 2 and any("Cave Troll" in o for o in opts))
    pg.evaluate("()=>{ NP=1; CREK='b_cave_troll'; CREN=2; resetSetup(); }")
    ok("B11 picking one sets it up like the built-in beasts", pg.evaluate("()=>[mobOn(),CRE[CREK].st,formsFor({mh:1}).includes('b_ogre')]") == [True, 27, False])
    st = pg.evaluate("""()=>{ slot[0]=fromBuilder({name:'Hero',cls:'fighter',race:'human',total:36,st:14,dx:12,iq:10,a:'broad',b:'none',armor:'none',s1:'none',d1:'none'}); startFight(); return G.mobs.map(m=>[m.p.name,m.p.st,m.p.right]); }""")
    ok("B12 the fight starts with two of them at the stats given", st == [["Cave Troll", 27, "club3"], ["Cave Troll 2", 27, "club3"]])
    ok("B13 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
