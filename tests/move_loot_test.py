"""Move an item between heroes from the tablet, give loot from the tablet, and sell loot in the campaign builder.
Run: python3 tests/move_loot_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
SW = {"id": "mg_1", "kind": "weapon", "n": "Dawnbringer", "base": "broad", "dx": 1, "dm": 1, "flame": 1, "lit": 0, "note": ""}
def hero(name, magic, a="none"):
    return {"name": name, "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": a, "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [],
            "camp": {"v": 1, "langs": 0, "tal": [], "purse": 20, "inv": ({"mg_1": 1} if magic else {}), "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0}, "magic": magic, "loot": []}}
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"broad": 80}, "talentFor": {"broad": "sword"}, "misc": []}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.evaluate("""([a,b])=>{ window.CALLS=[]; Online.isOn=()=>true; Online.result=f=>CALLS.push([f.name,JSON.stringify(f.phone.src)]); NP=2;
        for(const [i,o] of [[0,a],[1,b]]){ const f=fromBuilder(o); f.phone={uid:'u'+i,fj:'',name:o.name,key:o.name.toLowerCase(),src:o,rec:null}; slot[i]=f; } gvFill(); }""", [hero("Ann", [SW], "mg_1"), hero("Bob", [])])
    pg.click("#giveCard summary"); pg.wait_for_function("document.querySelectorAll('#mvFrom option').length>1")
    ok("M1 the move boxes list the seated players and Ann's sword", pg.eval_on_selector_all("#mvFrom option", "e=>e.length") == 2 and pg.eval_on_selector_all("#mvItem option", "e=>e.map(x=>x.textContent)") == ["Dawnbringer"])
    pg.select_option("#mvFrom", "0"); pg.select_option("#mvTo", "1"); pg.click("#mvGo")
    st = pg.evaluate("()=>[slot[0].phone.src,slot[1].phone.src,CALLS.length]")
    ok("M2 moved: gone from Ann (gear and hands cleared), now on Bob as owned", st[0]["camp"]["magic"] == [] and "mg_1" not in st[0]["camp"]["inv"] and st[0]["a"] == "none" and st[1]["camp"]["magic"][0]["n"] == "Dawnbringer" and st[1]["camp"]["inv"].get("mg_1") == 1)
    ok("M3 both phones are sent their new hero", st[2] == 2 and "moved" in pg.inner_text("#gvMsg").lower())
    pg.select_option("#mvFrom", "0"); pg.select_option("#mvTo", "0"); pg.click("#mvGo")
    ok("M4 moving to the same player is refused", "different players" in pg.inner_text("#gvMsg"))
    pg.select_option("#ltWho", "1"); pg.fill("#ltName", "Ruby"); pg.fill("#ltVal", "250"); pg.click("#ltGo")
    ok("M5 loot given: Bob carries Ruby worth $250", pg.evaluate("()=>slot[1].phone.src.camp.loot") == [{"n": "Ruby", "v": 250}])
    loot_hero = pg.evaluate("()=>slot[1].phone.src")
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    loot_hero["camp"]["loot"].append({"n": "Silver cup", "v": 40})
    pg.evaluate("(h)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(h))", loot_hero); pg.reload()
    ok("L1 the builder shows both loot items with their prices", "Ruby" in pg.inner_text("#loot") and "Sell for $250" in pg.inner_text("#loot") and "Silver cup" in pg.inner_text("#loot"))
    pg.click("[data-lsell='0']")
    ok("L2 selling one adds its worth to the money and removes it", pg.evaluate("()=>[C.purse,C.loot.map(x=>x.n)]") == [270, ["Silver cup"]])
    pg.fill("#lootN", "Old coins"); pg.fill("#lootV", "15"); pg.click("#lootAdd")
    ok("L3 loot can be added by hand", pg.evaluate("()=>C.loot.length") == 2)
    pg.click("#lootAll")
    ok("L4 sell all: money goes up by the total ($55) and the loot is gone", pg.evaluate("()=>[C.purse,C.loot.length]") == [325, 0] and "Left: $" in pg.inner_text("#moneyLeft"))
    ex = pg.evaluate("()=>exportChar()")
    ok("L5 the export carries the money and no loot", ex["camp"]["purse"] == 325 and ex["camp"]["loot"] == [])
    ok("L6 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
