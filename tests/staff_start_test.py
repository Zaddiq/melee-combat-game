"""Campaign builder: a wizard who knows the Staff spell starts with the staff in his right hand; one who does not can pick a weapon.
Run: python3 tests/staff_start_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"dagger": 10, "broad": 80}, "talentFor": {"broad": "sword"}, "misc": []}
def wiz(spells): return {"name": "Wen", "cls": "wizard", "race": "human", "total": 32, "st": 9, "dx": 12, "iq": 11, "spells": spells, "a": "none", "b": "none", "s1": "none", "d1": "dagger", "d2": "none", "armor": "none"}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", wiz(["Staff", "Magic Fist"])); pg.reload()
    ok("S1 the right hand shows the Wizard's staff and cannot be changed", pg.input_value("#ld_a") == "staff" and pg.is_disabled("#ld_a") and "staff" in pg.inner_text("#ld_a").lower())
    ok("S2 adjusted DX has no iron penalty (the staff is not iron)", pg.evaluate("()=>adjDX()") == 12)
    ex = pg.evaluate("()=>exportChar()")
    ok("S3 the exported character still carries a:none (the staff is implied by the Staff spell)", ex["a"] == "none")
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", wiz(["Magic Fist", "Blur"])); pg.reload()
    ok("S4 a wizard without the Staff spell has a normal right hand", not pg.is_disabled("#ld_a") and pg.input_value("#ld_a") == "none")
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", wiz(["Staff"])); pg.reload()
    pg.goto(BASE + "colosseum.html")
    ok("S5 in the Colosseum the staff wizard fights with the staff", pg.evaluate("(o)=>fromBuilder(o).right", wiz(["Staff", "Blur"])) == "staff")
    ok("S6 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
