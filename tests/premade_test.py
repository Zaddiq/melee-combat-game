"""Premade fighters: the host gives one to a tablet seat or to a phone seat. Run: python3 tests/premade_test.py"""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    n = host.evaluate("()=>PREMADE.length")
    ok("P1 a set of premade fighters is offered", n >= 8 and host.locator("#premSel option").count() == n)
    ok("P2 every premade is 32 points and fromBuilder accepts it", host.evaluate("()=>PREMADE.every(o=>o.st+o.dx+o.iq===32&&o.total===32&&!!fromBuilder(JSON.parse(JSON.stringify(o))))"))
    ok("P3 talent points never exceed IQ and weapons fit the ST", host.evaluate("""()=>{ const cost={knife:1,sword:2,axmace:2,pole:2,bow:2,crossbow:1,shield:1}; return PREMADE.every(o=>{ let t=o.camp.tal.reduce((a,k)=>a+cost[k],0); if(o.camp.tal.includes('knife')&&o.camp.tal.includes('sword')) t-=1; t+=(o.spells||[]).length; return t<=o.iq && [o.a,o.b].every(k=>!W[k]||W[k].st<=o.st); }); }""") )
    host.evaluate("()=>{ $('setup').open=true; }"); host.select_option("#npSel", "3"); host.evaluate("()=>{ $('premCard').open=true; }")
    host.select_option("#premSel", "0"); host.select_option("#premSeat", "0"); host.click("#premGo")
    ok("P4 a tablet seat gets the fighter", host.evaluate("()=>slot[0]&&slot[0].name===PREMADE[0].name&&!!slot[0].camp"))
    host.select_option("#premSel", "7"); host.select_option("#premSeat", "1"); host.click("#premGo")
    ok("P5 the wizard keeps its spells", host.evaluate("()=>slot[1].cls==='wizard'&&slot[1].spells.includes('Magic Fist')"))
    host.select_option("#premSel", "0"); host.select_option("#premSeat", "2"); host.click("#premGo")
    ok("P6 the same premade twice gets a different name", host.evaluate("()=>slot[2].name!==slot[0].name"))
    # a phone seat
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.fill("#nm", "Kid"); ph.click("#go")
    host.wait_for_function("()=>document.querySelectorAll('#onList [data-seat]').length>0", timeout=8000)
    host.select_option("#onList [data-seat]", "0")
    host.select_option("#premSel", "4"); host.select_option("#premSeat", "0"); host.click("#premGo")
    ok("P7 the phone seat gets it and says so", host.evaluate("()=>slot[0].name===PREMADE[4].name&&!!slot[0].phone&&slot[0].phone.given") and "on that phone" in host.inner_text("#premMsg"))
    host.wait_for_timeout(1500)
    ok("P8 it is still there after the table's next check (not dropped)", host.evaluate("()=>slot[0]&&slot[0].name===PREMADE[4].name"))
    ph.wait_for_timeout(1500)
    ok("P9 the phone saved it in its own list", ph.evaluate("()=>{ const r=JSON.parse(localStorage.getItem('melee-arena-v1')||sessionStorage.getItem('melee-arena-v1')||'{}'); return Object.values(r).some(x=>x.name===PREMADE_NAME); }".replace("PREMADE_NAME", json.dumps("Elara the Archer"))))
    ok("P10 no page errors", not errs)
    if errs: print(errs)
print(f"{sum(1 for _,c in R if c)}/{len(R)} passed")
