"""The campaign game has one builder: the campaign builder's open character is the one the Colosseum and phones load; the old builder is not offered.
Run: python3 tests/one_builder_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"broad": 80}, "talentFor": {"broad": "sword"}, "misc": []}
OLD = {"name": "Kid", "cls": "fighter", "race": "human", "total": 34, "st": 14, "dx": 14, "iq": 8, "armor": "none", "a": "broad", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [], "ep": 40}
SENT = {"name": "Sam", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [], "ep": 70,
        "camp": {"v": 1, "langs": 0, "tal": [], "purse": 50, "inv": {"mg_1": 1}, "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0}, "magic": [{"id": "mg_1", "kind": "weapon", "n": "Dawnbringer", "base": "broad", "dx": 1, "dm": 1, "flame": 1, "lit": 0, "note": ""}], "loot": [{"n": "Ruby", "v": 250}]}}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "index.html")
    ok("O1 the campaign menu has the campaign builder and no old builder", pg.locator("a[href='campaign-builder.html']").count() == 1 and pg.locator("a[href='builder.html']").count() == 0)
    ok("O1b the menu links to the original game's builder (outside the campaign) for bringing characters over", pg.locator("a[href='../builder.html']").count() == 1)
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("O2 the builder offers no 'take the regular builder' buttons", pg.locator("#fromBuilder, #setBuilder").count() == 0 and pg.locator("a[href='builder.html']").count() == 0)
    pg.evaluate("document.getElementById('dataCard').open=true"); pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    ok("O3 an unnamed new hero is not written as the open character", pg.evaluate("()=>localStorage.getItem('wizard-builder-v1')") in (None, ""))
    pg.click("#pasteBtn"); pg.fill("#pasteTxt", json.dumps(OLD)); pg.click("#pasteGo")
    ok("O4 pasting a character from the old game brings it in, with its gear owned", pg.evaluate("()=>[C.name,C.a,own('broad')]") == ["Kid", "broad", 1])
    saved = pg.evaluate("()=>JSON.parse(localStorage.getItem('wizard-builder-v1'))")
    ok("O5 it is now the open character: saved where the Colosseum and phones read, with its campaign data", saved["name"] == "Kid" and "camp" in saved)
    pg.evaluate("(h)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(h))", SENT); pg.reload()
    ok("O6 a hero sent here from a phone (written to the open character) loads with its magic item and loot", pg.evaluate("()=>[C.name,C.magic.length,C.loot.length,C.purse]") == ["Sam", 1, 1, 50])
    pg.goto(BASE + "colosseum.html")
    ok("O7 the Colosseum's Load from builder gets the same hero", pg.evaluate("()=>{ const o=JSON.parse(localStorage.getItem('wizard-builder-v1')); return fromBuilder(o).name; }") == "Sam")
    pg.goto(BASE + "builder.html"); pg.wait_for_url("**/campaign-builder.html")
    ok("O8 the old builder address leads to the campaign builder", pg.url.endswith("campaign-builder.html"))
    ok("O9 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
