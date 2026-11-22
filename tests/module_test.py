"""A module: several encounters in order (invented rooms, not any book's). Run: python3 tests/module_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
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
    base = pg.evaluate("()=>JSON.parse(JSON.stringify(SAMPLE_ENC))")
    def room(n): r = json.loads(json.dumps(base)); r["name"] = n; return r
    mod = {"module": "Test cellars", "encounters": [room("Room one"), room("Room two"), room("Room three")]}
    pg.evaluate("()=>{ $('encCard').open=true; $('setup').open=true; }")
    ok("M1 no module bar before one is loaded", not pg.is_visible("#modBar"))
    pg.fill("#encJson", json.dumps(mod)); pg.click("#encApply")
    ok("M2 pasting a module loads room 1 and shows where you are", pg.evaluate("()=>ENC.name==='Room one'&&MOD.i===0") and "room 1 of 3" in pg.inner_text("#modName") and pg.is_visible("#modBar"))
    ok("M3 Previous is off on the first room", pg.is_disabled("#modPrev") and not pg.is_disabled("#modNext"))
    pg.click("#modNext")
    ok("M4 Next goes to room 2 and makes it the encounter", pg.evaluate("()=>ENC.name==='Room two'&&MOD.i===1") and "room 2 of 3" in pg.inner_text("#modName"))
    pg.reload()
    ok("M5 after a reload the module and the place in it come back", pg.evaluate("()=>MOD&&MOD.i===1&&ENC.name==='Room two'"))
    pg.evaluate("()=>{ $('encCard').open=true; $('setup').open=true; }")
    bad = json.loads(json.dumps(mod)); bad["encounters"][2]["foes"] = [{"c": "dragon9", "at": [.5, .5]}]
    pg.fill("#encJson", json.dumps(bad)); pg.click("#encApply")
    ok("M6 a bad room is refused and named by number; the old module stays", "Room 3" in pg.inner_text("#encMsg") and pg.evaluate("()=>MOD.encounters.length===3&&MOD.encounters[2].foes.length===4"))
    # next-room button after a win
    pg.evaluate("()=>{ CREK='enc'; $('creSel').value='enc'; $('creSel').dispatchEvent(new Event('change')); }")
    pg.select_option("#npSel", "1"); pg.click("#ex0"); pg.click("#bGo")
    pg.evaluate("()=>{ G.mobs.forEach(m=>m.hp=0); endCheck(); ui(); }")
    ok("M7 after a win the fight-over panel offers the next room by name", pg.locator("#bMod").count() == 1 and "Room three" in pg.inner_text("#bMod"))
    pg.click("#bMod")
    ok("M8 pressing it loads room 3 and returns to the setup screen", pg.evaluate("()=>ENC.name==='Room three'&&MOD.i===2&&!G"))
    ok("M9 on the last room there is no Next", pg.is_disabled("#modNext"))
    pg.click("#modDrop")
    ok("M10 stopping the module hides the bar and forgets it", not pg.is_visible("#modBar") and pg.evaluate("()=>MOD===null&&!localStorage.getItem('colosseum-module')"))
    e = json.loads(json.dumps(base)); e["foes"][0]["min"] = 3; e["foes"][1]["max"] = 2
    pg.reload(); pg.evaluate("(e)=>{ saveEnc(e,true); }", e)
    counts = []
    for n in ("1", "3"):
        pg.reload(); pg.select_option("#npSel", n); pg.select_option("#creSel", "enc")
        for i in range(int(n)): pg.click(f"#ex{i}")
        for _ in range(int(n) - 1): pg.click("#bNext")
        pg.click("#bGo"); counts.append(pg.evaluate("()=>G.mobs.length"))
    ok("M12 a foe with min 3 only comes for 3+ players and one with max 2 only for 1-2 (4 foes: 3 for one player, 3 for three)", counts == [3, 3])
    pg.reload(); pg.evaluate("()=>{ localStorage.clear(); }"); pg.reload()
    bad = json.loads(json.dumps(base)); bad["foes"][0]["min"] = 7
    ok("M13 min/max outside 1-4 are refused", "players, 1 to 4" in pg.evaluate("(e)=>checkEnc(e,true)", bad))
    ok("M11 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
