"""Aid as the 1980 Advanced Wizard has it: +1 ST, DX or IQ of any figure per ST the caster spends, 2 turns; ST given must be used within 2 turns or it is lost.
Run: python3 tests/aid_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
ENC = {"name": "Aid test", "foe": "foes", "room": [50, 60], "creatures": {"orc": {"name": "Orc", "st": 12, "dx": 10, "iq": 8, "w": "broad"}}, "foes": [{"c": "orc", "at": [.5, .1]}]}
def W(name, iq, st, spells): return {"name": name, "cls": "wizard", "race": "human", "total": 36, "st": st, "dx": 12, "iq": iq, "spells": spells, "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none"}
SETUP = """([w1,w2])=>{ saveEnc(ENC_,true); ENC=ENC_; applyEnc(ENC_); CREK='enc'; CREN=1; NP=2; MODE='ffa'; applyMode(); syncMap(); starts.fill(null); G=null;
  slot[0]=fromBuilder(w1,0); slot[1]=fromBuilder(w2,1); slot[2]=null; slot[3]=null; startFight();
  const a=G.players[0], b=G.players[1], foe=G.mobs[0]; const h=P.find(x=>dist(x,a)===1&&!allU().some(y=>y.hp>0&&same(y,x))); b.q=h.q; b.r=h.r;
  window.__A=a; window.__B=b; window.__F=foe; window.__rn=rollN; return [a.hp,b.hp]; }"""
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.evaluate("(e)=>{ window.ENC_=e; }", ENC)
    st = pg.evaluate(SETUP, [W("Giver", 9, 12, ["Aid", "Magic Fist"]), W("Mage", 12, 10, ["Fireball", "Magic Fist"])])
    ok("A1 both wizards start at full ST", st == [12, 10])
    labels = pg.evaluate("()=>castList(__A,__F).map(x=>x.label)")
    ok("A2 the giver is offered Aid on himself and on the adjacent friend (ST, DX, IQ)", any("on yourself" in l for l in labels) and any("Aid on" in l and "+6 ST" in l for l in labels) and any("+2 IQ" in l and "Aid on" in l and "yourself" not in l for l in labels))
    ok("A3 nobody is offered Aid on the foe or on a friend who is not adjacent", pg.evaluate("()=>{ const b=__B; const q=b.q; b.q+=5; const n=castList(__A,__F).filter(x=>x.on==='ally').length; b.q=q; return n===0; }"))
    pg.evaluate("()=>{ rollN=n=>[3,3,2].slice(0,n); }")  # a 8: always succeeds against the need of 12
    pg.evaluate("()=>{ const i=allU().indexOf(__B); __A.act={t:'cast',sp:'Aid',att:'ST',n:6,al:i}; doCast(__A,__F,__A.act); }")
    s = pg.evaluate("()=>[__A.hp,__B.hp,__B.loan,__B.loanT]")
    ok("A4 giving 6 ST: the giver pays 6, the friend gains 6, the loan lasts 2 turns", s == [6, 16, 6, 2])
    pg.evaluate("()=>{ payST(__B,4); }")
    ok("A5 spending ST uses the lent ST first", pg.evaluate("()=>[__B.hp,__B.loan]") == [12, 2])
    pg.evaluate("()=>{ nextTurn(); }")
    ok("A6 after one turn the unspent loan is still there", pg.evaluate("()=>[__B.hp,__B.loan,__B.loanT]") == [12, 2, 1])
    pg.evaluate("()=>{ nextTurn(); }")
    ok("A7 after the 2nd turn the unspent 2 ST are lost (not paid back to the giver)", pg.evaluate("()=>[__B.hp,__B.loan,__A.hp]") == [10, 0, 6])
    pg.evaluate("()=>{ const i=allU().indexOf(__B); __A.hp=12; __A.act={t:'cast',sp:'Aid',att:'IQ',n:2,al:i}; doCast(__A,__F,__A.act); }")
    ok("A8 Aid IQ raises the friend's effective IQ by 2 and it wears off", pg.evaluate("()=>{ const a=effIQ(__B); nextTurn(); nextTurn(); return a===14&&effIQ(__B)===12; }"))
    pg.evaluate("()=>{ const i=allU().indexOf(__B); __A.hp=12; __A.act={t:'cast',sp:'Aid',att:'DX',n:3,al:i}; doCast(__A,__F,__A.act); }")
    ok("A9 Aid DX on a friend gives +3 DX for 2 turns", pg.evaluate("()=>__B.aid===2&&__B.aidN===3"))
    pg.evaluate("()=>{ __B.hp=3; __B.loan=0; __B.loanT=0; const i=allU().indexOf(__B); __A.hp=12; __B.hp=3; __A.act={t:'cast',sp:'Aid',att:'ST',n:4,al:i}; doCast(__A,__F,__A.act); payST(__B,0); __B.hp-=6; nextTurn(); nextTurn(); }")
    ok("A10 a friend wounded below the lent ST is never killed by the loan expiring (ST stays at least 1)", pg.evaluate("()=>__B.hp>=1&&__B.loan===0"))
    pg.evaluate("()=>{ rollN=__rn; }")
    ok("A11 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
