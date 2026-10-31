"""Online table, step 2 (secret picks from phones). Tablet = colosseum.html, phones = phone.html, fake Firebase (?net=mem).
Run: python3 tests/online_picks_test.py  (needs Playwright). The real Firebase backend and rules are not covered."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

BEGIN = """(n)=>{ G=null; NP=n; MODE="ffa"; for(let i=0;i<4;i++) tmAB[i]=i%2; applyMode(); starts.fill(null);
  for(let i=0;i<4;i++) slot[i]=i<n?fromBuilder({name:"P"+(i+1),race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}):null; startFight(); }"""
TOPICK = """()=>{ let g=0; while(g++<60&&G.phase!=="over"&&!["cover","pick"].includes(G.phase)){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="rcover") G.phase="renew"; else if(G.phase==="renew") doRenew(); else break; } ui(); }"""

with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    code = host.inner_text("#onBody b")
    def phone(name):
        pg = mk("phone.html?net=mem&room=" + code); pg.fill("#nm", name); pg.click("#go")
        pg.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')"); return pg
    A = phone("Bo"); B = phone("Cy")

    host.evaluate(BEGIN, 2); host.evaluate(TOPICK)
    host.wait_for_function("G.phase==='pick'")
    labels = host.evaluate("()=>G.opts.map(o=>o.label)")
    A.wait_for_selector("#play .opt")
    a_labels = A.eval_on_selector_all("#play .opt", "e=>e.map(x=>x.textContent)")
    ok("P1 the first player's phone gets exactly the tablet's option labels", a_labels == labels and len(labels) > 1)
    ctl = host.inner_text("#ctl")
    ok("P2 the tablet shows no options while a phone player picks, only a waiting line", host.locator("#ctl [data-opt]").count() == 0 and "Waiting for" in ctl and not any(l in ctl for l in labels))
    B.wait_for_function("document.getElementById('play').textContent.includes('Waiting for P1')")
    ok("P3 the other phone is told who is picking and gets no options", B.locator("#play .opt").count() == 0)

    old_seq = host.evaluate("()=>__online.state().pending[Object.keys(__online.state().pending)[0]].seq")
    none_i = host.evaluate("()=>G.opts.findIndex(o=>o.t==='none')")
    A.click(f'#play .opt[data-b="{max(none_i,0)}"]')
    host.wait_for_function("G.phase==='pick'&&G.pi===1")
    ok("P4 tapping a button on the phone makes that pick, and the pick moves to the next player", host.evaluate("()=>!!(G.picks[0]&&G.picks[0].t)"))
    B.wait_for_selector("#play .opt")
    ok("P5 the second phone now gets its options", B.locator("#play .opt").count() > 1)
    # a late duplicate of the first command must do nothing
    A.evaluate("([c,s])=>Net.sendCmd(c,{seq:s,k:'b',i:0,t:Date.now()})", [code, old_seq]); A.wait_for_timeout(500)
    ok("P6 an old command (stale sequence number) is ignored", host.evaluate("()=>G.pi")==1)

    # ring again
    host.click("#bRing"); B.wait_for_selector("#play .ring")
    ok("P7 'Ring again' on the tablet makes the waiting phone show a reminder", B.locator("#play .ring").count()==1)
    # play it on the tablet instead
    host.click("#bTake")
    ok("P8 'Play on the tablet instead' brings the pick screen back to the tablet", host.locator("#ctl #bShow, #ctl [data-opt]").count()>0)
    B.wait_for_function("document.getElementById('play').textContent.includes('Waiting for')")
    host.evaluate("()=>{ if(G.phase==='cover') showPick(); }"); host.evaluate("()=>takePick({t:'none'})")
    host.wait_for_function("G.turn===2")
    ok("P9 after the tablet pick the turn resolves and turn 2 starts", host.evaluate("()=>G.turn")==2)

    # hex pick by direction (disengage) on the phone
    host.evaluate(TOPICK); host.wait_for_function("G.phase==='pick'")
    host.evaluate("()=>{ G.destT='disengage'; G.phase='dest'; G.dopts=new Map(freeNeighbors(G.cur).map(h=>[key(h.q,h.r),h])); ui(); }")
    A.wait_for_function("document.querySelectorAll('#play .opt').length>1")
    t = A.eval_on_selector_all("#play .opt", "e=>e.map(x=>x.textContent)")
    ok("P10 a disengage on the phone is offered as directions (ahead, behind, left, right), not map clicks", any(x.startswith("Move ") and ("ahead" in x or "behind" in x) for x in t))
    mv = [i for i, x in enumerate(t) if x.startswith("Move ")][0]
    A.click(f'#play .opt[data-b="{mv}"]')
    host.wait_for_function("G.picks&&G.picks[0]&&G.picks[0].t==='disengage'")
    ok("P11 tapping a direction records the disengage move to that hex", host.evaluate("()=>!!G.picks[0].dest&&G.picks[0].dest.q!==undefined"))
    host.evaluate("()=>{ takePick({t:'none'}); }"); host.wait_for_function("G.turn===3")

    # a player without a phone is still played on the tablet
    host.evaluate("()=>{ const s=__online.state(); const u=Object.keys(s.seat).find(k=>s.seat[k]===1); }")
    uidB = host.evaluate("()=>{ const s=__online.state(); return Object.keys(s.joins).find(u=>s.joins[u].name==='Cy'); }")
    host.select_option(f'[data-seat="{uidB}"]', "-1"); host.wait_for_timeout(300)
    host.evaluate(TOPICK); host.wait_for_function("G.phase==='pick'")
    A.wait_for_selector("#play .opt"); A.click('#play .opt[data-b="0"]')
    host.wait_for_function("G.pi===1")
    ok("P12 a player with no phone gets the normal 'pass the tablet' screen", host.locator("#ctl #bShow").count()==1 and "Pass the tablet" in host.inner_text("#ctl"))
    host.evaluate("()=>{ showPick(); takePick({t:'none'}); }"); host.wait_for_function("G.turn===4")

    # three players: target choice on the phone
    host.select_option(f'[data-seat="{uidB}"]', "1"); host.wait_for_timeout(300)
    phoneC = phone("Di")
    host.evaluate(BEGIN, 3); host.evaluate(TOPICK); host.wait_for_function("G.phase==='pick'")
    host.wait_for_timeout(600)
    cur_i = host.evaluate("()=>G.players.indexOf(G.cur)")
    who = [A, B, phoneC][cur_i]
    who.wait_for_selector("#play .tg")
    ok("P13 with three players the phone offers the two enemies as targets", who.locator("#play .tg").count()==2 and who.locator("#play .tg.on").count()==1)
    before = host.evaluate("()=>other(G.cur).p.name")
    who.click("#play .tg:not(.on)")
    host.wait_for_function("(b)=>other(G.cur).p.name!==b", arg=before)
    ok("P14 tapping the other target changes the target on the tablet", host.evaluate("()=>other(G.cur).p.name")!=before)
    ok("P15 no script errors on any page", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
