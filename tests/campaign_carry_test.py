"""Campaign mode step 2 in colosseum.html: fighters keep their ST from one encounter fight to the next, and Rest heals them.
Run: python3 tests/campaign_carry_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

SETUP = r'''
()=>{ const mk=(n,st)=>fromBuilder({name:n,race:"human",cls:"fighter",st,dx:12,iq:8,armor:"leather",a:"broad",b:"small",total:st+12+8});
  CREK="enc"; CREN=ENC.foes.length; NP=2; MODE="ffa"; applyMode(); syncMap(); starts.fill(null); G=null; slot[0]=mk("Aria",12); slot[1]=mk("Bram",12); slot[2]=null; slot[3]=null; startFight(); return !!G; }'''
# a fight the players win: the monsters all fall; the players are hurt first
WIN = r'''
([a,b])=>{ G.players[0].hp=a; G.players[1].hp=b; G.mobs.forEach(m=>m.hp=0); endCheck(); return G.phase; }'''
LOSE = r'''
()=>{ G.players.forEach(u=>u.hp=0); endCheck(); return G.phase; }'''

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("K1 campaign is off at first, and the card says so", pg.evaluate("()=>!CAMP.on&&!$('campOn').checked&&/Off/.test($('campNote').textContent)"))
    pg.evaluate(SETUP)
    ok("K2 with it off, a won fight carries nothing", pg.evaluate(WIN, [5, 3]) == "over" and pg.evaluate("()=>Object.keys(CAMP.hp).length===0"))
    pg.evaluate("()=>{ $('campOn').checked=true; $('campOn').onchange(); }")
    ok("K3 switching it on is remembered in this browser", pg.evaluate("()=>JSON.parse(localStorage.getItem('colosseum-campaign')).on===true"))
    pg.evaluate(SETUP)
    ok("K4 the first fight starts everyone at full ST", pg.evaluate("()=>G.players.every(u=>u.hp===u.p.st)"))
    pg.evaluate(WIN, [5, 3])
    ok("K5 after a win each fighter's ST is carried (5 and 3)", pg.evaluate("()=>CAMP.hp.Aria===5&&CAMP.hp.Bram===3"))
    ok("K6 the card shows the carried ST", "Aria 5" in pg.text_content("#campNote") and "Bram 3" in pg.text_content("#campNote"))
    pg.evaluate(SETUP)
    ok("K7 the next fight starts them hurt, and says so in the log", pg.evaluate("()=>G.players[0].hp===5&&G.players[1].hp===3&&G.log.some(l=>/Aria starts hurt, at ST 5 of 12/.test(l))"))
    pg.evaluate(WIN, [0, 9])
    ok("K8 a fighter who went down comes back at 1 ST; the other keeps 9", pg.evaluate("()=>CAMP.hp.Aria===1&&CAMP.hp.Bram===9"))
    pg.reload()
    ok("K9 after a reload the carried ST and the switch are still there", pg.evaluate("()=>CAMP.on&&CAMP.hp.Aria===1&&CAMP.hp.Bram===9&&$('campOn').checked"))
    pg.evaluate(SETUP); pg.evaluate(LOSE)
    ok("K10 a lost fight does not change the carried ST", pg.evaluate("()=>CAMP.hp.Aria===1&&CAMP.hp.Bram===9"))
    pg.evaluate(SETUP)
    pg.evaluate("()=>{ G.mobs.forEach(m=>m.hp=0); G.players.forEach(u=>u.hp=u.p.st); endCheck(); ui(); drawMap(); }")
    ok("K11 an end-of-fight panel offers Rest while the campaign is on", pg.locator("#bRest").count() == 1)
    pg.click("#bRest")
    ok("K12 Rest clears the carried ST", pg.evaluate("()=>Object.keys(CAMP.hp).length===0") and pg.evaluate("()=>JSON.parse(localStorage.getItem('colosseum-campaign')).hp.Aria===undefined"))
    pg.evaluate(SETUP)
    ok("K13 after resting the next fight is at full ST", pg.evaluate("()=>G.players.every(u=>u.hp===u.p.st)"))
    # the Rest button in the setup card works too
    pg.evaluate(WIN, [4, 4]); pg.evaluate("()=>{ $('encCard').open=true; $('setup').open=true; }"); pg.click("#campRest")
    ok("K14 the Rest button in the encounter card also clears it", pg.evaluate("()=>Object.keys(CAMP.hp).length===0") and "full ST" in pg.text_content("#campNote"))
    # beasts and the Gladiator never use it
    pg.evaluate("()=>{ CAMP.hp={Aria:3}; campStore(); CREK='wolf'; CREN=1; NP=2; applyMode(); syncMap(); const mk=(n)=>fromBuilder({name:n,race:'human',cls:'fighter',st:12,dx:12,iq:8,armor:'leather',a:'broad',b:'small',total:32}); slot[0]=mk('Aria'); slot[1]=mk('Bram'); starts.fill(null); G=null; startFight(); }")
    ok("K15 a fight against beasts ignores the carried ST", pg.evaluate("()=>G.players.every(u=>u.hp===u.p.st)"))
    ok("K16 no script errors", not errs)
    print(errs[:3])
print(f"{sum(c for _, c in R)}/{len(R)} passed")
