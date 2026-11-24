"""The tablet hands a magic item from its own list to a phone player's campaign hero (found or not); the phone saves it.
Tablet = campaign/colosseum.html, phone = campaign/phone.html, fake Firebase (?net=mem). Run: python3 tests/magic_give_test.py"""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
HERO = {"name": "Sam", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [],
        "camp": {"v": 1, "langs": 0, "tal": [], "purse": 0, "inv": {"broad": 1}, "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0}, "magic": []}}
PLAIN = {"name": "Pat", "cls": "fighter", "race": "human", "total": 32, "st": 12, "dx": 12, "iq": 8, "armor": "none", "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": []}
ITEMS = [{"id": "c1", "kind": "weapon", "n": "Dawnbringer", "base": "broad", "dx": 1, "dm": 1, "flame": 1, "note": "", "found": 0},
         {"id": "c2", "kind": "armor", "n": "Mithril", "base": "chain", "stops": 2, "note": "", "found": 1}]
def rec(o): return dict(name=o["name"], st=o["st"], dx=o["dx"], total0=o["st"]+o["dx"]+o["iq"], pts=0, wins=0, losses=0, ep=0, banked=False, pend=0, must=False, retired=False, dead=False, src=o)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.evaluate("(l)=>localStorage.setItem('magic-items-v1',JSON.stringify(l))", ITEMS)
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.evaluate("([r])=>{ sessionStorage.setItem('melee-arena-v1',r); fillChars(); }", [json.dumps({"sam": rec(HERO), "pat": rec(PLAIN)})])
    ph.select_option("#chr", "r:sam"); ph.click("#go")
    host.wait_for_function("slot[0]&&slot[0].phone")
    host.click("#giveCard summary"); host.wait_for_function("document.querySelectorAll('#gvItem option').length>1")
    opts = host.eval_on_selector_all("#gvItem option", "e=>e.map(x=>x.textContent)")
    ok("G1 the tablet's list offers every item, found or not", opts == ["Dawnbringer (not found yet)", "Mithril"])
    ok("G2 the player picker lists the phone player", host.eval_on_selector_all("#gvWho option", "e=>e.map(x=>x.textContent)") == ["Player 1: Sam"])
    host.select_option("#gvItem", "c1"); host.click("#gvGo")
    ok("G3 the tablet says it sent it", "Sent Dawnbringer" in host.inner_text("#gvMsg"))
    ph.wait_for_function("(()=>{ const r=JSON.parse(sessionStorage.getItem('melee-arena-v1')).sam; return r.src.camp.magic.length===1; })()")
    src = ph.evaluate("()=>JSON.parse(sessionStorage.getItem('melee-arena-v1')).sam.src")
    ok("G4 the phone's saved hero now has the sword, as an owned item", src["camp"]["magic"][0]["n"] == "Dawnbringer" and src["camp"]["inv"].get("mg_1") == 1)
    host.select_option("#gvItem", "c1"); host.click("#gvGo")
    ok("G5 giving the same item twice is refused", "already has" in host.inner_text("#gvMsg"))
    host.select_option("#gvItem", "c2"); host.click("#gvGo")
    ph.wait_for_function("JSON.parse(sessionStorage.getItem('melee-arena-v1')).sam.src.camp.magic.length===2")
    ok("G6 a second item gets the next id and both are kept", ph.evaluate("()=>JSON.parse(sessionStorage.getItem('melee-arena-v1')).sam.src.camp.magic.map(m=>m.id)") == ["mg_1", "mg_2"])
    ph.select_option("#chr", "r:pat"); host.wait_for_function("slot[0]&&slot[0].name==='Pat'")
    host.evaluate("()=>{ gvFill(); }"); host.select_option("#gvItem", "c2"); host.click("#gvGo")
    ok("G7 a character without campaign data is refused with a reason", "not a campaign hero" in host.inner_text("#gvMsg"))
    ok("G8 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
