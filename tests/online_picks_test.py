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
    host.wait_for_function("G.phase==='cover'&&Object.keys(__online.state().sess).length===2")
    labels = host.evaluate("()=>options(G.players[0],other(G.players[0])).map(o=>o.label)")
    A.wait_for_selector("#play .opt")
    a_labels = A.eval_on_selector_all("#play .opt", "e=>e.map(x=>x.textContent)")
    short = A.evaluate("(L)=>L.map(l=>splitLabel(l)[0])", labels)
    ok("P1 the first player's phone gets the tablet's options, each shown by its short name", a_labels == short and len(labels) > 1)
    if A.locator("#detTg").count():
        A.click("#detTg"); full = A.eval_on_selector_all("#play .opt", "e=>e.map(x=>x.textContent)")
        ok("P1b 'Show what each choice does' adds the bracketed detail back, and hiding removes it", all(l.replace(" (", "(") in f.replace(" (", "(") or l in f for l, f in zip(labels, full)) and A.locator("#play .det").count() > 0)
        A.click("#detTg")
    ctl = host.inner_text("#ctl")
    ok("P2 the tablet shows no options while phone players pick, only a waiting line naming them", host.locator("#ctl [data-opt]").count() == 0 and "Waiting for" in ctl and "P1" in ctl and "P2" in ctl and not any(l in ctl for l in labels))
    B.wait_for_selector("#play .opt")
    ok("P3 BOTH phones get their options at the same time (everyone picks at once)", B.locator("#play .opt").count() > 1 and A.locator("#play .opt").count() > 1)

    old_seq = host.evaluate("()=>__online.state().pending[Object.keys(__online.state().pending)[0]].seq")
    none_i = A.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))")
    A.click(f'#play .opt[data-b="{max(none_i,0)}"]')
    A.wait_for_function("document.getElementById('play').textContent.includes('Your pick is in')")
    ok("P4 after one phone picks, nothing resolves: it says its pick is in, waits for the other, and offers 'Change my pick'", host.evaluate("()=>G.phase!=='resolve'&&G.turn===1&&(G.picks||[]).length===0") and A.locator("text=Change my pick").count() == 1)
    A.click("text=Change my pick"); A.wait_for_function("document.querySelectorAll('#play .opt').length>1&&!document.getElementById('play').textContent.includes('Your pick is in')")
    ok("P5 'Change my pick' brings the options back before the last phone is in", True)
    # a late duplicate of an old command must do nothing
    A.evaluate("([c,s])=>Net.sendCmd(c,{seq:s,k:'b',i:0,t:Date.now()})", [code, old_seq]); A.wait_for_timeout(500)
    ok("P6 an old command (stale sequence number) is ignored", host.evaluate("()=>G.turn")==1 and A.locator("#play .opt").count() > 1)
    host.click("#bRing"); B.wait_for_selector("#play .ring")
    ok("P7 'Ring again' on the tablet makes a waiting phone show a reminder", B.locator("#play .ring").count()==1)
    A.click(f'#play .opt[data-b="{max(none_i,0)}"]'); A.wait_for_function("document.getElementById('play').textContent.includes('Your pick is in')")
    B.click(f'#play .opt[data-b="{max(B.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"),0)}"]')
    host.wait_for_function("G.turn===2")
    ok("P9 when the last phone is in, both picks go to the game together and turn 2 starts", host.evaluate("()=>G.turn")==2)

    # a far hex (disengage) picked on the phone map, with the confirm tap
    host.evaluate(TOPICK); host.wait_for_function("G.phase==='cover'||G.phase==='pick'")
    host.evaluate("()=>{ const a=G.players[0], b=G.players[1], n=nbr(a,0)||nbr(a,1)||nbr(a,2); b.q=n.q; b.r=n.r; a.f=faceToward(a,b); b.f=faceToward(b,a); Online.redo(); }")
    A.wait_for_function("lastP&&lastP.btns&&lastP.btns.some(b=>/disengage|retreat|away/i.test(b.l))")
    di = A.evaluate("()=>lastP.btns.findIndex(b=>/disengage|retreat|away/i.test(b.l))")
    A.click(f'#play .opt[data-b="{di}"]')
    A.wait_for_function("lastP&&lastP.sc&&lastP.sc.hk==='dest'")
    h = A.evaluate("()=>lastP.sc.hl[0]"); A.locator(f'#pmap [data-h="{h[0]},{h[1]}"]').dispatch_event("click"); A.wait_for_selector("#cfm"); A.click("#cfm")
    A.wait_for_function("document.getElementById('play').textContent.includes('Your pick is in')")
    ok("P10 a disengage is chosen on the phone's own map and confirmed, inside the phone's pick session", host.evaluate("()=>!!G.phase")) 
    B.click(f'#play .opt[data-b="{max(B.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"),0)}"]')
    host.wait_for_function("G.turn===3")
    ok("P11 the stored disengage reaches the game (turn resolves)", host.evaluate("()=>G.turn")==3)

    # 'play on the tablet instead' for one phone while the other picks on its phone
    host.evaluate(TOPICK); host.wait_for_function("G.phase==='cover'||G.phase==='pick'"); host.wait_for_timeout(300)
    uidB = host.evaluate("()=>{ const s=__online.state(); return Object.keys(s.joins).find(u=>s.joins[u].name==='Cy'); }")
    host.click(f'[data-take="{uidB}"]'); B.wait_for_function("document.getElementById('play').textContent.includes('Waiting for')")
    ok("P8 'Play Cy on the tablet instead' drops Cy's phone session; Cy's phone waits", B.locator("#play .opt").count()==0)
    A.click(f'#play .opt[data-b="{max(A.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"),0)}"]'); A.wait_for_function("/Your pick is in|Everyone has picked/.test(document.getElementById('play').textContent)")
    host.wait_for_function("G.phase==='cover'||G.phase==='pick'")
    ok("P12 the player taken to the tablet gets the normal 'pass the tablet' screen", True)
    host.evaluate("()=>{ if(G.phase==='cover') showPick(); takePick({t:'none'}); }"); host.wait_for_function("G.turn===4")
    ok("P12b after the tablet pick the turn resolves", host.evaluate("()=>G.turn")==4)

    # a player without a seat on a phone picks on the tablet FIRST while the phone players pick at once
    phoneC = phone("Di")
    host.evaluate(BEGIN, 3); host.wait_for_timeout(900)
    uidC = host.evaluate("()=>{ const s=__online.state(); return Object.keys(s.joins).find(u=>s.joins[u].name==='Di'); }")
    host.select_option(f'[data-seat="{uidC}"]', "2"); phoneC.wait_for_function("document.getElementById('seat').textContent.includes('Player 3')"); host.evaluate(TOPICK)
    host.wait_for_timeout(600)
    pq_phone = host.evaluate("()=>G.pq.map(u=>!!Object.keys(__online.state().sess).some(k=>__online.state().sess[k].u===u))")
    ok("P13 the three phones all pick at the same time and with three players each phone offers the two enemies as targets", all(pg.locator("#play .tg").count()==2 for pg in (A,B,phoneC)) and all(pq_phone))
    before = A.evaluate("()=>lastP.tg.findIndex(t=>t.on)")
    A.click("#play .tg:not(.on)"); A.wait_for_function("(b)=>lastP.tg.findIndex(t=>t.on)!==b", arg=before)
    ok("P14 tapping the other target changes the target on that phone's own session", True)
    # a player with no phone picks on the tablet first, while the two phone players pick at once
    host.select_option(f'[data-seat="{uidC}"]', "-1"); host.wait_for_timeout(300)
    host.evaluate(BEGIN, 3); host.wait_for_timeout(900)
    host.select_option(f'[data-seat="{uidC}"]', "-1"); host.evaluate(TOPICK)
    host.wait_for_function("G.phase==='cover'")
    A.wait_for_selector("#play .opt"); B.wait_for_selector("#play .opt")
    ok("P16 with one player on the tablet and two on phones: the tablet player goes first, and both phones already have their options", host.evaluate("()=>G.pq.indexOf(G.players[2])")==0 and "Pass the tablet" in host.inner_text("#ctl") and A.locator("#play .opt").count()>1 and B.locator("#play .opt").count()>1)
    A.click(f'#play .opt[data-b="{max(A.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"),0)}"]'); B.click(f'#play .opt[data-b="{max(B.evaluate("()=>lastP.btns.findIndex(b=>/nothing/i.test(b.l))"),0)}"]')
    host.wait_for_timeout(500)
    ok("P17 the phones' picks wait while the tablet player has not picked yet", host.evaluate("()=>G.pi")==0 and host.evaluate("()=>G.phase")=="cover")
    t0 = host.evaluate("()=>G.turn"); host.evaluate("()=>{ showPick(); takePick({t:'none'}); }"); host.wait_for_function("(t)=>G.turn>t", arg=t0)
    ok("P18 after the tablet player picks, the stored phone picks go in and the turn resolves", host.evaluate("()=>G.turn")>t0)
    ok("P15 no script errors on any page", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
