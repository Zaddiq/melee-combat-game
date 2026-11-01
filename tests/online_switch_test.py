"""Online table: switching tables from a phone, and a tablet closing its previous table. Fake Firebase (?net=mem).
Run: python3 tests/online_switch_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.fill("#onName", "ALPHA"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem"); ph.fill("#code", "alpha"); ph.fill("#nm", "Bo"); ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("S1 inside a table the phone shows which table it is in and a Switch table button at the top", ph.inner_text("#tcode") == "ALPHA" and ph.locator("#leave").is_visible())

    # the tablet starts a different table without closing the first (page reload, then a new name)
    host.reload(); host.click("#online summary")
    ok("S2 the tablet offers the previous name again", host.input_value("#onName") == "ALPHA")
    host.fill("#onName", "BRAVO"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph.wait_for_function("document.getElementById('seat').textContent.includes('closed')")
    ok("S3 opening BRAVO closes the tablet's previous table ALPHA, and the phone is told", host.evaluate("()=>Net.b.get('rooms/ALPHA/host')") is None)

    # the phone reloads: the closed table is forgotten and the join screen is ready
    ph.reload()
    ok("S4 after the old table closed, the phone opens at the join screen with an empty table name", ph.locator("#joinCard").is_visible() and ph.input_value("#code") == "")
    ph.fill("#code", "BRAVO"); ph.fill("#nm", "Bo"); ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("S5 it joins the new table", ph.inner_text("#tcode") == "BRAVO")

    # switching by hand while the old table is still open
    ph.click("#leave")
    ok("S6 Switch table leaves the table and shows an empty join box", ph.locator("#joinCard").is_visible() and ph.input_value("#code") == "")
    ph.reload()
    ok("S7 a reload after switching does not jump back to the old table", ph.locator("#joinCard").is_visible())
    host.wait_for_function("document.querySelectorAll('#onList b').length===0")
    ok("S8 the tablet's list no longer shows the phone that switched away", True)
    ok("S9 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
