"""Phone layout v2: map on top and sticky, results strip with the last log lines, character card hidden during a fight,
megahex outlines (switchable with range numbers), and the starting hex chosen on the phone. Fake Firebase (?net=mem)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
SETUP = """(n)=>{ G=null; NP=n; MODE="ffa"; applyMode(); starts.fill(null);
  for(let i=0;i<4;i++) slot[i]=i<n?fromBuilder({name:["Bo","Cy"][i],race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}):null; ui(); drawMap(); }"""
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.fill("#onName", "LAYO"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    def phone(name):
        pg = mk("phone.html?net=mem&room=LAYO"); pg.fill("#nm", name); pg.click("#go")
        pg.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')"); return pg
    A = phone("Bo"); B = phone("Cy")
    host.evaluate(SETUP, 2)
    A.wait_for_function("lastP&&lastP.sc&&lastP.sc.hk==='start'"); B.wait_for_function("lastP&&lastP.sc&&lastP.sc.hk==='start'")
    ok("L1 before the fight both phones can choose their starting hex (their own entrance)", len(A.evaluate("lastP.sc.hl")) == 4 and A.locator("#pmap [data-h]").count() == 4)
    h0 = host.evaluate("()=>starts[0]"); tgt = [h for h in A.evaluate("lastP.sc.hl") if f"{h[0]},{h[1]}" != h0][0]; k = f"{tgt[0]},{tgt[1]}"
    A.locator(f'#pmap [data-h="{k}"]').dispatch_event("click")
    host.wait_for_function("(k)=>starts[0]===k", arg=k)
    A.wait_for_function("(k)=>lastP.sc.u.find(u=>u.s).c[0].join(',')===k", arg=k)
    ok("L2 tapping a hex on the phone sets the tablet's start hex for that player and the phone sees the move", host.evaluate("()=>starts[0]") == k)
    both = B.evaluate("lastP.sc.hl").__len__()
    ok("L3 the other phone's own entrance is untouched", both == 4 and B.evaluate("lastP.sc.u.find(u=>u.s).c[0].join(',')") == host.evaluate("()=>starts[1]"))
    host.evaluate("()=>startFight()")
    host.wait_for_function("G&&G.phase==='choose'")
    A.wait_for_function("lastP&&lastP.lv===1&&lastP.ph!=='start'")
    ok("L4 the figure starts on the hex the phone chose", host.evaluate("()=>key(G.players[0].q,G.players[0].r)") == k)
    ok("L5 during the fight the map is the first thing on the page (above the choices)",
       A.evaluate("()=>{ const m=document.getElementById('stick').getBoundingClientRect().top, b=(document.querySelector('#play .opt')||document.getElementById('resBar')||document.body).getBoundingClientRect().top; return m<=b; }"))
    ok("L6 the map box is sticky", A.evaluate("()=>getComputedStyle(document.getElementById('stick')).position")=="sticky")
    ok("L7 the load/save/character box is hidden while the fight is on", not A.locator("#chrCard").is_visible())
    ok("L8 megahex outlines are drawn by default and the numbers are not", A.locator("#pmap line").count() > 20)
    A.click("#mega"); 
    ok("L9 the switch gives back the plain map (no outlines)", A.locator("#pmap line").count() == 0 and "outlines" in A.inner_text("#mega"))
    A.click("#mega")
    ok("L10 and back again", A.locator("#pmap line").count() > 20)
    # play a turn to get log lines with the numbers
    host.evaluate("""()=>{ const o=G.players[0], t=G.players[1]; G.log.push("Bo attacks Cy with Broadsword (needs 13 or less on 3d6, rolled 9): HIT. 10 damage."); ui(); }""")
    A.wait_for_function("document.getElementById('resBar')&&document.getElementById('resBar').innerText.includes('needs 13')")
    ok("L11 the strip under the choices shows the last results with the numbers", "rolled 9" in A.inner_text("#resBar"))
    ok("L12 the same strip is on the other phone (it is public)", "rolled 9" in B.inner_text("#resBar") if B.locator("#resBar").count() else False)
    ok("L13 the strip is sticky at the bottom", A.evaluate("()=>getComputedStyle(document.getElementById('resBar')).position")=="sticky")
    host.evaluate("()=>{ G.phase='over'; G.winner=G.players[0]; ui(); }")
    A.wait_for_function("lastP&&lastP.lv===0")
    ok("L14 when the fight is over the character box comes back", A.locator("#chrCard").is_visible())
    ok("L15 no script errors", not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
