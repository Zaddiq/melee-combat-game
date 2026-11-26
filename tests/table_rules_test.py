"""The tablet shares its rules data with phones at the table; a phone saves it for its campaign builder.
Tablet = campaign/colosseum.html, phone = campaign/phone.html, fake Firebase (?net=mem). Run: python3 tests/table_rules_test.py"""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
RULES = json.dumps({"talents": [{"id": "knife", "n": "Knife", "iq": 7, "c": 1}], "prices": {"dagger": 10}, "spells": [{"n": "Blur", "iq": 8, "d": "Harder to hit."}]})
HERO = {"name": "Sam", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": []}
def rec(o): return dict(name=o["name"], st=o["st"], dx=o["dx"], total0=o["st"]+o["dx"]+o["iq"], pts=0, wins=0, losses=0, ep=0, banked=False, pend=0, must=False, retired=False, dead=False, src=o)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.evaluate("(r)=>localStorage.setItem('campaign-data-v1',r)", RULES)
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    host.wait_for_function("(()=>{ try{ const t=JSON.parse(localStorage.getItem('netmem-tree')||'{}'); return !!(t.rooms&&t.rooms.STEVE&&t.rooms.STEVE.rules); }catch(e){ return false; } })()", timeout=8000)
    ok("R1 opening a table publishes the tablet's saved rules data to the table", host.evaluate("()=>JSON.parse(localStorage.getItem('netmem-tree')).rooms.STEVE.rules") == RULES)
    host.evaluate("()=>localStorage.removeItem('campaign-data-v1')")   # so the phone has to get it from the table
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.evaluate("([r])=>{ sessionStorage.setItem('melee-arena-v1',r); fillChars(); }", [json.dumps({"sam": rec(HERO)})])
    ph.select_option("#chr", "r:sam"); ph.click("#go")
    ph.wait_for_function("localStorage.getItem('campaign-data-v1')!==null", timeout=8000)
    ok("R2 the phone saves the table's rules data for its builder", ph.evaluate("()=>localStorage.getItem('campaign-data-v1')") == RULES)
    ok("R3 the phone says so", "table's rules were saved" in ph.inner_text("#rulesNote") and "1 talents" in ph.inner_text("#rulesNote"))
    b = mk("campaign-builder.html"); 
    ok("R4 the phone's builder then runs on the table's data", "your data" in (b.text_content("#dataState") or "") and b.locator("#talents .tal").count() == 1)
    host.click("#onClose") if host.locator("#onClose").count() else None
    ok("R5 no page errors", not errs)
print(f"{sum(1 for _,c in R if c)}/{len(R)} passed")
