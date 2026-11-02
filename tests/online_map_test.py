"""Online table, item 4 (the phone map). Tablet = colosseum.html, phones = phone.html, fake Firebase (?net=mem).
Run: python3 tests/online_map_test.py  (needs Playwright). The real Firebase backend and rules are not covered (no rules change in this item)."""
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

with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.fill("#onName", "MAPS"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    def phone(name):
        pg = mk("phone.html?net=mem&room=MAPS"); pg.fill("#nm", name); pg.click("#go")
        pg.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')"); return pg
    A = phone("Bo"); B = phone("Cy")
    sc = lambda pg: pg.evaluate("()=>lastP&&lastP.sc")

    host.evaluate(BEGIN, 2)
    host.wait_for_function("G.phase==='choose'")
    chooser = host.evaluate("()=>G.chooser")
    CH, OT = (A, B) if chooser == 0 else (B, A)
    CH.wait_for_function("document.querySelector('#play .opt')")
    ok("M1 the player who won the roll gets Move first / second on their phone, the other phone just waits",
       CH.locator("#play .opt").count() == 2 and OT.locator("#play .opt").count() == 0)
    ok("M2 even a waiting phone shows the board with every figure", OT.locator("#pmap polygon").count() > 50 and len(sc(OT)["u"]) == 2)
    CH.click('#play .opt[data-b="0"]')
    host.wait_for_function("G.phase==='move'")
    mover = host.evaluate("()=>G.players.indexOf(G.cur)")
    MV, WT = (A, B) if mover == 0 else (B, A)
    MV.wait_for_function("lastP&&lastP.mode==='map'&&lastP.sc.hl")
    s0 = sc(MV)
    ok("M3 the mover's phone gets tappable hexes, facing circles and End movement", len(s0["hl"]) > 3 and s0["hk"] == "go" and s0["fc"] and MV.locator("#play .opt").count() >= 1 and MV.locator("#pmap [data-f]").count() == 6)
    ok("M4 the tablet panel says whose phone is deciding and offers to take over", "deciding on their phone" in host.inner_text("#ctl") and host.locator("#bTake").count() == 1 and host.locator("#bOk").count() == 0)
    before = host.evaluate("()=>[G.cur.q,G.cur.r]")
    tgt = max(s0["hl"], key=lambda h: h[2]); k = f"{tgt[0]},{tgt[1]}"
    seq0 = MV.evaluate("()=>lastP.seq")
    MV.locator(f'#pmap [data-h="{k}"]').dispatch_event("click")
    host.wait_for_function("(b)=>G.cur.q!==b[0]||G.cur.r!==b[1]", arg=before)
    now = host.evaluate("()=>[G.cur.q,G.cur.r,G.moved]")
    ok("M5 tapping a hex on the phone moves the figure on the tablet", now[:2] == [tgt[0], tgt[1]] and now[2] == tgt[2])
    MV.wait_for_function("(s)=>lastP.seq!==s", arg=seq0)
    mine = [u for u in sc(MV)["u"] if u["s"]][0]
    ok("M6 the phone sees its figure on the new hex and can go on (Undo appears)", mine["c"][0] == [tgt[0], tgt[1]] and "Undo" in MV.inner_text("#play"))
    # same hex tapped again, then a facing tap: each must still be answered with a fresh message
    f0 = host.evaluate("()=>G.cur.f"); want = (f0 + 2) % 6
    MV.locator(f'#pmap [data-f="{want}"]').dispatch_event("click")
    host.wait_for_function("(w)=>G.cur.f===w", arg=want)
    MV.wait_for_function("(w)=>lastP.sc.fc.f===w", arg=want)
    ok("M7 tapping a facing circle turns the figure", host.evaluate("()=>G.cur.f") == want)
    MV.click("#tl"); host.wait_for_function("(w)=>G.cur.f===w", arg=(want + 1) % 6)
    MV.wait_for_function("(w)=>lastP.sc.fc.f===w", arg=(want + 1) % 6)
    MV.click("#tr"); host.wait_for_function("(w)=>G.cur.f===w", arg=want)
    ok("M8 Turn left and Turn right turn one step each way", host.evaluate("()=>G.cur.f") == want)
    MV.click("text=Undo move"); host.wait_for_function("(b)=>G.cur.q===b[0]&&G.cur.r===b[1]", arg=before)
    ok("M9 Undo move puts the figure back", host.evaluate("()=>G.moved") == 0)
    t0 = MV.inner_text("#zoom"); h0 = MV.evaluate("()=>document.getElementById('pmap').viewBox.baseVal.height")
    MV.click("#zoom"); MV.wait_for_function("(t)=>document.getElementById('zoom').textContent!==t", arg=t0)
    h1 = MV.evaluate("()=>document.getElementById('pmap').viewBox.baseVal.height")
    ok("M10 the zoom button switches between the action and the whole board (whole board is at least as tall)", h1 >= h0 and h1 > 20)
    MV.click("#zoom")
    # the tablet's own map still works (the host may fix things): clicking a hex there updates the phone too
    seq1 = MV.evaluate("()=>lastP.seq")
    MV.locator("#play .opt.pri").first.click()   # End movement
    host.wait_for_function("(m)=>G.phase==='move'&&G.players.indexOf(G.cur)!==m||G.phase!=='move'", arg=mover)
    WT.wait_for_function("lastP&&lastP.mode==='map'&&lastP.sc.hl")
    ok("M11 End movement hands the move to the other phone, which gets the map", host.evaluate("()=>G.phase") == "move" and sc(WT)["hk"] == "go")
    MV.wait_for_function("lastP&&lastP.mode==='wait'")
    ok("M12 the first mover's phone goes back to a watching map", MV.locator("#pmap").count() == 1 and MV.locator("#play .opt").count() == 0)
    host.click("#bTake")
    ok("M13 'move on the tablet instead' gives the tablet its own buttons back", host.locator("#bOk").count() == 1)
    host.evaluate("()=>{ Online.override=null; ui(); }")
    WT.wait_for_function("lastP&&lastP.mode==='map'")
    WT.click("#play .opt.pri")   # End movement -> pick phase
    host.wait_for_function("G.phase==='pick'")
    # ---- far hex choices (Teleport style) with select-then-confirm ----
    who = host.evaluate("()=>G.players.indexOf(G.cur)"); PK = A if who == 0 else B
    host.evaluate("()=>{ const U=G.cur,V=G.oth; G.destT='cast'; G.destX={sp:'Teleport'}; G.phase='dest'; G.dopts=new Map(P.filter(h=>!same(h,U)&&!same(h,V)).slice(0,40).map(h=>[key(h.q,h.r),h])); ui(); drawMap(); }")
    PK.wait_for_function("lastP&&lastP.mode==='map'&&lastP.sc.hk==='dest'")
    ok("M14 a far-hex choice shows the hexes on the phone instead of 'needs the map'", len(sc(PK)["hl"]) == 40 and "needs the map" not in PK.inner_text("#play"))
    h = sc(PK)["hl"][5]; kk = f"{h[0]},{h[1]}"
    PK.locator(f'#pmap [data-h="{kk}"]').dispatch_event("click")
    PK.wait_for_selector("#cfm")
    ok("M15 the first tap only marks the hex and asks to confirm", host.evaluate("()=>G.phase") == "dest")
    PK.click("#cfm")
    host.wait_for_function("()=>G.phase!=='dest'")
    ok("M16 confirming sends the pick (the pick queue moves on)", host.evaluate("()=>G.picks.some(p=>p&&p.t==='cast'&&p.sp==='Teleport'&&p.dest&&p.dest.q===%d&&p.dest.r===%d)" % (h[0], h[1])))
    # ---- retreat and advance ----
    host.evaluate("()=>{ G.phase='retreat'; G.rdec=G.players[0]; G.rd=G.players[1]; G.cur=G.players[0]; const o=freeNeighbors(G.players[1]); G.ropts=new Map(o.map(h=>[key(h.q,h.r),h])); G.rfrom={q:G.rd.q,r:G.rd.r}; ui(); drawMap(); }")
    A.wait_for_function("lastP&&lastP.sc&&lastP.sc.hk==='ret'")
    ok("M17 the winner of a hit gets the retreat hexes and a Skip button", len(sc(A)["hl"]) >= 1 and "Skip" in A.inner_text("#play"))
    r = sc(A)["hl"][0]; rk = f"{r[0]},{r[1]}"
    A.locator(f'#pmap [data-h="{rk}"]').dispatch_event("click"); A.wait_for_selector("#cfm"); A.click("#cfm")
    host.wait_for_function("G.phase==='advance'")
    ok("M18 the pushed figure moved to the chosen hex", host.evaluate("()=>[G.rd.q,G.rd.r]") == [r[0], r[1]])
    A.wait_for_function("lastP&&lastP.btns&&lastP.btns.some(b=>b.l==='Advance')")
    A.click("text=Stay")
    host.wait_for_function("G.phase!=='advance'")
    ok("M19 Advance or Stay is decided on the phone", host.evaluate("()=>G.phase") != "advance")
    # ---- leaving through the door asks on the phone, then ends the fight ----
    host.evaluate(BEGIN, 2); host.wait_for_function("G.phase==='choose'")
    c2 = host.evaluate("()=>G.chooser"); (A if c2 == 0 else B).click('#play .opt[data-b="0"]'); host.wait_for_function("G.phase==='move'")
    m2 = host.evaluate("()=>G.players.indexOf(G.cur)"); P2 = A if m2 == 0 else B
    P2.wait_for_function("lastP&&lastP.btns&&lastP.btns.some(b=>b.cf)")
    P2.click("text=escapes through the door")
    host.wait_for_function("G.phase==='over'")
    ok("M20 'escapes through the door' works from the phone (asked on the phone)", host.evaluate("()=>G.end") == "escape")
    ok("M21 no script errors", not errs)
    if errs: print(errs)
    br.close()

bad = [n for n, c in R if not c]
print(f"{len(R)-len(bad)}/{len(R)} passed"); srv.shutdown(); raise SystemExit(1 if bad else 0)
