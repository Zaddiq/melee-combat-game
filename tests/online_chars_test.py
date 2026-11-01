"""Online table, item 2: characters that come from the phones (their own roster and builder) and XP saved back to the phone.
Tablet = colosseum.html, phones = phone.html, fake Firebase (?net=mem; in that mode each phone tab keeps its roster in sessionStorage).
Run: python3 tests/online_chars_test.py  (needs Playwright). Real Firebase and rules are not covered."""
import http.server, socketserver, threading, os, functools, json
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
    EX = host.evaluate("()=>EXAMPLES")
    host.evaluate("()=>{ NP=2; slot[1]=fromBuilder(EXAMPLES[1]); }")
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")

    def rec(ex, **kw):
        r = dict(name=ex["name"], st=ex["st"], dx=ex["dx"], total0=ex["st"]+ex["dx"]+ex["iq"], pts=0, wins=0, losses=0, ep=0,
                 banked=False, pend=0, must=False, retired=False, dead=False, src=ex); r.update(kw); return r
    roster = {"flavius (example)": rec(EX[0], st=13, ep=90), "brynn (example)": rec(EX[2], ep=10)}
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.evaluate("([r,b])=>{ sessionStorage.setItem('melee-arena-v1',r); sessionStorage.setItem('wizard-builder-v1',b); fillChars(); }",
                [json.dumps(roster), json.dumps(EX[3])])
    opts = ph.eval_on_selector_all("#chr option", "e=>e.map(x=>x.textContent)")
    ok("C1 the phone offers its roster characters and the one open in the builder", len(opts) == 4 and any("Durgan" in o for o in opts) and any("Flavius" in o and "90/100" in o for o in opts))
    ok("C2 the character open in the builder is the default", "Durgan" in ph.eval_on_selector("#chr", "e=>e.options[e.selectedIndex].textContent"))
    ph.select_option("#chr", "r:flavius (example)")
    ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    host.wait_for_function("slot[0]&&slot[0].phone")
    ok("C3 a seated phone's character is loaded into its seat, with the phone's own stats (ST 13 from its roster)", host.evaluate("()=>slot[0].name==='Flavius (example)'&&slot[0].st===13&&slot[0].phone.rec.ep===90"))
    ok("C4 the tablet's own arena roster is not touched", host.evaluate("()=>!(JSON.parse(localStorage.getItem('melee-arena-v1')||'{}')['flavius (example)'])"))
    ok("C5 the phone's name defaults to the character's name when left empty", host.locator("#onList b", has_text="Flavius").count() == 1)

    ph.select_option("#chr", "r:brynn (example)")
    host.wait_for_function("slot[0]&&slot[0].name==='Brynn (example)'")
    ok("C6 choosing another character on the phone swaps it at the table (no duel running)", True)
    ph.select_option("#chr", "r:flavius (example)"); host.wait_for_function("slot[0]&&slot[0].name==='Flavius (example)'")

    host.evaluate("()=>{ G=null; starts.fill(null); startFight(); }")
    host.evaluate("()=>{ G.players[1].hp=-1; endCheck(); }")
    ok("C7 Flavius wins the duel: +30 XP", host.evaluate("()=>G.phase==='over'&&G.xp.some(x=>/Flavius.*\\+30 XP/.test(x))"))
    ph.wait_for_function("document.getElementById('xp').textContent.includes('Flavius')")
    saved = ph.evaluate("()=>JSON.parse(sessionStorage.getItem('melee-arena-v1'))['flavius (example)']")
    ok("C8 the experience is saved in the phone's own roster (90+30: a point earned, 20 EP left)", saved["ep"] == 20 and saved["pend"] == 1 and saved.get("src"))
    ok("C9 the arena message on the phone mentions the waiting attribute point", "attribute point" in ph.inner_text("#xp"))
    host.wait_for_timeout(1500)
    ok("C10 the finished duel screen on the tablet is not cleared by that update", host.evaluate("()=>G&&G.phase==='over'"))
    ok("C11 the tablet's own roster still has no entry for the phone's character", host.evaluate("()=>!(JSON.parse(localStorage.getItem('melee-arena-v1')||'{}')['flavius (example)'])"))

    host.evaluate("()=>{ G=null; ui(); drawMap(); }")
    host.wait_for_function("slot[0]&&slot[0].phone&&slot[0].phone.rec&&slot[0].phone.rec.ep===20")
    ok("C12 after Rematch the updated record comes back to the table for the next duel", True)

    ph.select_option("#chr", "none")
    host.wait_for_function("!slot[0]")
    ok("C13 a phone that brings no character leaves the seat empty for the host to fill", True)
    ok("C14 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
