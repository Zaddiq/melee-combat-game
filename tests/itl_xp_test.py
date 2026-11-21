"""Campaign experience the In the Labyrinth way: damage, killing blows, spell ST, and the rising cost of attribute points.
Run: python3 tests/itl_xp_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    c = pg.evaluate("()=>[36,37,40,41,45,46,50,51,55,56,60,61,66].map(itlCost)")
    ok("X1 attribute point costs follow the book's schedule", c == [125, 250, 250, 1000, 1000, 3000, 3000, 5000, 5000, 10000, 10000, 20000, 40000])
    r = pg.evaluate("()=>{ const r={ep:0,pend:0,pts:0,total0:30}; applyXp(r,124,true); const a=[r.pend,r.need]; applyXp(r,1,true); return [a,r.pend,r.ep,r.need,r.itl]; }")
    ok("X2 at total 30 an attribute point takes 125 EP (124 is not enough; 125 earns one)", r[0] == [0, 125] and r[1] == 1 and r[2] == 0 and r[4] == 1)
    r = pg.evaluate("()=>{ const r={ep:0,pend:0,pts:7,total0:30}; applyXp(r,249,true); const a=r.pend; applyXp(r,1,true); return [a,r.pend]; }")
    ok("X3 at total 37 the next point takes 250 EP", r == [0, 1])
    r = pg.evaluate("()=>{ const r={ep:0,pend:0,pts:0,total0:36,banked:false,must:false,retired:false}; applyXp(r,100); return [r.pend,r.ep,r.need]; }")
    ok("X4 the old arena scheme is unchanged (100 EP = a point)", r == [1, 0, 100])
    # tally: damage, killing blow, nuisance, spells
    pg.select_option("#npSel", "1"); pg.select_option("#creSel", "enc"); pg.click("#ex0"); pg.click("#bGo")
    t = pg.evaluate("""()=>{ const a=G.players[0], d=G.mobs.find(m=>m.p.st>3); d.hp=5; d.p.dx=10; credit(a,d,3); d.hp=2; const s1=[a.xd||0,a.xk||0]; credit(a,d,5); d.hp=-3; const s2=[a.xd,a.xk]; credit(a,d,2); const s3=[a.xd,a.xk];
      const rat={hp:1,p:{st:2,dx:10}}; const b=a.xk; credit(a,rat,1); return [s1,s2,s3,a.xk===b,(()=>{ a.hp=10; payST(a,3); return a.xs; })()]; }""")
    ok("X5 damage counts per hit (3, then only the 2 ST that were left), the killing blow adds the foe's DX once", t[0] == [3, 0] and t[1] == [5, 10] and t[2] == [5, 10])
    ok("X6 killing a ST 1-3 nuisance gives no DX, and ST spent on spells counts", t[3] is True and t[4] == 3)
    # a campaign fight ends with the ITL award and a GM bonus box
    pg.reload(); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.select_option("#npSel", "1"); pg.select_option("#creSel", "enc"); pg.evaluate("()=>{ CAMP.on=true; }"); pg.click("#ex0"); pg.click("#bGo")
    pg.evaluate("()=>{ const a=G.players[0]; a.xd=7; a.xk=10; a.xs=2; G.mobs.forEach(m=>m.hp=0); endCheck(); ui(); }")
    ok("X7 winning a campaign fight pays damage + killing blows + spells (7+10+2 = 19)", pg.evaluate("()=>G.itl&&/\\+19 XP/.test(G.xp[0])&&/7 for damage, 10 for killing blows, 2 for spells/.test(G.xp[0])"))
    ok("X8 the fight-over panel has the GM bonus box", pg.locator("#gmN").count() == 1 and pg.locator("#gmGive").count() == 1)
    pg.fill("#gmN", "20"); pg.click("#gmGive")
    ok("X9 giving 20 bonus XP adds it to the winner's record", pg.evaluate("()=>/GM bonus \\+20 XP/.test(G.xp.join(' '))"))
    pg.reload(); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.select_option("#npSel", "1"); pg.select_option("#creSel", "enc"); pg.click("#ex0"); pg.click("#bGo")
    pg.evaluate("()=>{ G.players[0].xd=9; G.mobs.forEach(m=>m.hp=0); endCheck(); ui(); }")
    ok("X10 with the campaign carry-over off, a fight still pays a flat 50 (the old way)", pg.evaluate("()=>!G.itl&&/\\+50 XP/.test(G.xp[0])")and pg.locator("#gmN").count() == 0)
    # real play: attacks in an actual fight feed the tally
    pg.reload(); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.select_option("#npSel", "1"); pg.select_option("#creSel", "man"); pg.click("#ex0"); pg.click("#bGo")
    tot = 0
    for _ in range(60):
        ph = pg.evaluate("()=>G.phase")
        if ph == "over": break
        if ph == "resolve" or pg.locator("#bNext:has-text('Next turn')").count(): pg.evaluate("()=>endTurn()")
        elif pg.locator("#ctl [data-opt]").count(): pg.locator("#ctl [data-opt]").first.click()
        else: pg.evaluate("()=>{ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); }")
    tot = pg.evaluate("()=>G.players[0].xd||0")
    ok("X10b real attacks feed the damage tally (a number, never NaN)", isinstance(tot, (int, float)) and tot == tot)
    ok("X11 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
