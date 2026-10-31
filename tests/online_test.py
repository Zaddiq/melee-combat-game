"""Online table, step 1 (rooms and lobby): colosseum.html as the tablet, phone.html as the phones, several tabs of one browser
talking through the in-browser fake of Firebase (?net=mem). Run: python3 tests/online_test.py  (needs Playwright).
The real Firebase backend and database.rules.json are NOT covered here (no internet in the test box)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H)
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/"

R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context()
    errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem")
    host.evaluate("localStorage.clear()")
    host.reload()
    host.evaluate("()=>{ NP=2; slot[0]=fromBuilder(EXAMPLES[0]); slot[1]=fromBuilder(EXAMPLES[1]); }")
    host.click("#online summary"); host.click("#onOpen")
    host.wait_for_selector("#onBody b")
    code = host.inner_text("#onBody b")
    ok("O1 the tablet opens a table with a 5-character code", len(code) == 5 and code.isalnum())

    a = mk("phone.html?net=mem&room=" + code)
    a.fill("#nm", "Bo"); a.click("#go")
    a.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("O2 the first phone joins and is seated at Player 1 with its fighter's name", "Player 1" in a.inner_text("#seat") and "Flavius" in a.inner_text("#seat"))
    ok("O3 the tablet lists the phone by name, connected", host.locator("#onList b", has_text="Bo").count() == 1)

    b = mk("phone.html?net=mem")
    b.fill("#code", code.lower()); b.fill("#nm", "Cy"); b.click("#go")
    b.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("O4 the second phone (code typed in lower case) is seated at Player 2", "Player 2" in b.inner_text("#seat"))

    c = mk("phone.html?net=mem")
    c.fill("#code", "ZZZZZ"); c.fill("#nm", "Di"); c.click("#go")
    c.wait_for_function("document.getElementById('err').textContent.length>0")
    ok("O5 a wrong code is refused with a clear message", "no table" in c.inner_text("#err").lower())
    c.fill("#code", code); c.fill("#nm", "Di"); c.click("#go")
    c.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("O6 a third phone with two players seated is put on watching only", c.inner_text("#seat").startswith("You are watching"))

    # the host moves seats: giving Player 1 to Cy swaps it away from Bo
    uid_c = host.evaluate("()=>{ const s=__online.state(); return Object.keys(s.joins).find(u=>s.joins[u].name==='Di'); }")
    host.select_option(f'[data-seat="{uid_c}"]', "0")
    c.wait_for_function("document.getElementById('seat').textContent.includes('Player 1')")
    a.wait_for_function("document.getElementById('seat').textContent.startsWith('You are watching')")
    ok("O7 giving a seat to another phone takes it from the first one (one phone per player)", "Player 1" in c.inner_text("#seat") and a.inner_text("#seat").startswith("You are watching"))

    # fewer players: seats beyond the count turn into watching
    host.select_option("#npSel", "2"); host.wait_for_timeout(900)
    host.evaluate("()=>{ NP=3; $('npSel').value='3'; $('npSel').onchange(); }")
    host.wait_for_timeout(900)
    host.evaluate("()=>{ NP=2; $('npSel').value='2'; $('npSel').onchange(); }")
    host.wait_for_timeout(900)
    ok("O8 the seat list follows the player count (no phone sits at a player who is not in the duel)", all(v < 2 for v in host.evaluate("()=>Object.values(__online.state().seat)")))

    # a phone that reloads comes back by itself
    b.reload()
    b.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    ok("O9 a phone that reloads rejoins on its own and keeps its seat", "Player 2" in b.inner_text("#seat") and host.locator("#onList b", has_text="Cy").count() == 1)

    # removing a phone
    uid_b = host.evaluate("()=>{ const s=__online.state(); return Object.keys(s.joins).find(u=>s.joins[u].name==='Cy'); }")
    host.click(f'[data-kick="{uid_b}"]')
    b.wait_for_function("document.getElementById('seat').textContent.includes('removed')")
    ok("O10 removing a phone tells that phone, and the tablet drops it from the list", host.locator("#onList b", has_text="Cy").count() == 0)

    # the tablet reloads and reopens the same table; phones stay joined
    host.reload()
    host.click("#online summary"); host.click("#onRe")
    host.wait_for_selector("#onBody b")
    ok("O11 after a tablet reload the same table can be reopened with the same code", host.inner_text("#onBody b") == code)
    host.wait_for_function("document.querySelectorAll('#onList b').length>=2")
    ok("O12 the phones that were joined are still listed after reopening", host.locator("#onList b", has_text="Bo").count() == 1)

    # closing the table
    host.click("#onClose")
    a.wait_for_function("document.getElementById('seat').textContent.includes('closed')||document.getElementById('conn').textContent.includes('not found')")
    ok("O13 closing the table tells the phones", True)
    ok("O14 no script errors on any page", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed")
srv.shutdown()
raise SystemExit(1 if bad else 0)
