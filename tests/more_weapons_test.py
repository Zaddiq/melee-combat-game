"""The weapons the 2018 table has that the campaign pages lacked (bastard sword and others, numbers from the 2018 table).
Run: python3 tests/more_weapons_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"broad": 80, "twohsw": 120}, "talentFor": {"broad": "sword", "twohsw": "sword"}, "misc": []}
HERO = {"name": "Big", "cls": "fighter", "race": "human", "total": 36, "st": 15, "dx": 12, "iq": 9, "armor": "none", "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [], "camp": {"v": 1, "langs": 0, "tal": [], "purse": 1000, "inv": {}, "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0}, "magic": []}}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "campaign/campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    pg.evaluate("(h)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(h))", HERO); pg.reload()
    shop = pg.inner_text("#shop")
    ok("W1 the shop sells the bastard sword and the other added weapons at the 2018 prices", all(x in shop for x in ["Bastard sword (1 hand)", "Great sword", "Hatchet", "Trident", "Pike", "War ax", "Quarterstaff", "Spike shield", "Tower shield"]) and pg.inner_text("#pr_bastard") == "$100")
    ok("W2 the 2-hands bastard sword is not sold separately", "2 hands" not in shop)
    pg.click("#buy_bastard")
    ok("W3 after buying the one sword it can be readied one-handed or two-handed", pg.evaluate("()=>[fightList('a').includes('bastard'),fightList('a').includes('bastard2'),own('bastard2'),spent()]") == [True, True, 1, 100])
    pg.select_option("#ld_a", "bastard2")
    ok("W4 held in two hands it uses the sword talent (lacks it: -4 DX noted)", "Sword" in pg.inner_text("#fightNote") and pg.evaluate("()=>adjDX()") == 12)
    ex = pg.evaluate("()=>exportChar()")
    pg.goto(BASE + "campaign/colosseum.html")
    r = pg.evaluate("(h)=>{ const f=fromBuilder(h); return [f.right,W[f.right].d,W[f.right].m,W[f.right].two,dmg(f,'bastard'),dmg(f,'greatsw')]; }", ex)
    ok("W5 the Colosseum has them: two-handed bastard sword 3d-2, one-handed 2d+1, great sword 3d+1", r[:4] == ["bastard2", 3, -2, 1] and r[4] == "2d+1" and r[5] == "3d+1")
    pg.goto(BASE + "campaign/campaign-builder.html")
    ok("W6 the campaign pages' weapon table has them", pg.evaluate("()=>RULES.W.bastard&&RULES.W.greatsw&&RULES.W.bastard.grp==='Melee weapons'"))
    pg.goto(BASE.replace("", "") + "colosseum.html"); ok("W7 the old Colosseum still has no bastard sword", pg.evaluate("()=>!W.bastard"))
    ok("W8 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
