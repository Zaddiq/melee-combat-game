"""The campaign copy (campaign/) keeps its own storage, leaves the old pages alone, and has the magic weapons. Magic weapons: a hero's named weapon with a DX bonus (counts while readied) and a damage bonus.
Run: python3 tests/magic_items_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"broad": 80}, "talentFor": {"broad": "sword"}, "misc": []}
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
HERO = {"name": "Sam", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": "mg_1", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [],
        "camp": {"v": 1, "langs": 0, "tal": [], "purse": 0, "inv": {"mg_1": 1}, "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0},
                 "magic": [{"id": "mg_1", "n": "Dawnbringer", "base": "broad", "dx": 1, "dm": 1, "note": "flames on command"},
                           {"id": "mg_2", "n": "Bad", "base": "bite", "dx": 1, "dm": 0}, {"id": "x", "n": "Bad2", "base": "broad"}, {"id": "mg_3", "n": "Bad3", "base": "mg_1"}]}}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "campaign/colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    f = pg.evaluate("(h)=>{ const f=fromBuilder(h); return [f.right,W.mg_1&&W.mg_1.n,W.mg_1&&W.mg_1.m,!!W.mg_2,!!W.x,!!W.mg_3,adjDX(f)]; }", HERO)
    ok("M1 the sword joins the weapon table with its name and +1 damage; bad entries are dropped", f[:6] == ["mg_1", "Dawnbringer", 1, False, False, False])
    ok("M2 readied, its +1 DX is in adjusted DX (12+1)", f[6] == 13)
    ok("M3 in the fight the same +1 shows in adjDXu, and not when sheathed", pg.evaluate("""(h)=>{ const f=fromBuilder(h); const u={p:f,right:'mg_1',left:'none',hp:14}; const a=adjDXu(u,'single',null);
        const v={p:f,right:'broad',left:'none',hp:14}; return a-adjDXu(v,'single',null); }""", HERO) == 1)
    pg.goto(BASE + "campaign/campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    pg.evaluate("(h)=>{ localStorage.setItem('wizard-builder-v1',JSON.stringify(h)); }", HERO); pg.reload()
    ok("M4 the builder shows the sword with its numbers", pg.evaluate("()=>document.querySelectorAll('#magic [data-m]').length")==1 and "Dawnbringer" in pg.inner_text("#magic"))
    ex = pg.evaluate("()=>exportChar()")
    ok("M5 export carries only the good item", [m["id"] for m in ex["camp"]["magic"]] == ["mg_1"] and ex["a"] == "mg_1")
    ok("M6 the builder's adjusted DX counts the readied sword", pg.evaluate("()=>adjDX()") == 13)
    pg.evaluate("()=>localStorage.setItem('magic-items-v1',JSON.stringify([{id:'cat1',kind:'shield',n:'Warding Shield',base:'small',stops:2,found:1}]))"); pg.reload()
    pg.select_option("#magicPick", "cat1"); pg.click("#magicAdd")
    ok("M7 adding makes a second item with a new id", pg.evaluate("()=>C.magic.map(m=>m.id)") == ["mg_1", "mg_2"] and pg.evaluate("()=>SHIELDS.mg_2.stops") == 3)
    pg.click("[data-mdel=mg_1]")
    ok("M8 removing clears the slot and the gear", pg.evaluate("()=>[C.a,C.inv.mg_1,C.magic.length]") == ["none", None, 1])
    ok("M9 no page errors", not errs)
    pg.goto(BASE + "campaign/colosseum.html"); pg.evaluate("localStorage.setItem('wizard-builder-v1','CAMP')")
    ok("F1 campaign saves under its own name", pg.evaluate("()=>[Object.keys(localStorage).every(k=>k.startsWith('campaign:')), localStorage.getItem('wizard-builder-v1')]") == [True, "CAMP"])
    pg.goto(BASE + "builder.html"); ok("F2 the old builder cannot see it", pg.evaluate("()=>localStorage.getItem('wizard-builder-v1')") != "CAMP")
    pg.goto(BASE + "colosseum.html"); pg.evaluate("()=>{ localStorage.setItem('colosseum-encounter','OLD'); }")
    pg.goto(BASE + "campaign/colosseum.html"); ok("F3 nor the old encounter", pg.evaluate("()=>localStorage.getItem('colosseum-encounter')") is None)
    pg.goto(BASE + "colosseum.html"); ok("F4 the old colosseum has no magic table", pg.evaluate("()=>typeof RULES.addMagic")=="undefined")
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
