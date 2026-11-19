"""Campaign talents and extra weapons in the fight engine. Uses an INVENTED mini data set (not book numbers).
Run: python3 tests/campaign_talents_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
DATA = {"talents": [{"id": "knife", "n": "Knife", "iq": 7, "c": 1}, {"id": "sword", "n": "Sword", "iq": 7, "c": 2},
  {"id": "bow", "n": "Bow", "iq": 7, "c": 1}, {"id": "missile", "n": "Missile Weapons", "iq": 9, "c": 2}, {"id": "thrown", "n": "Thrown Weapons", "iq": 8, "c": 1}],
  "prices": {"dagger": 10, "broad": 80, "lbow": 40, "javelin": 15}, "talentFor": {"dagger": "knife", "broad": "sword", "lbow": "bow"}, "misc": []}
HERO = {"name": "Hera", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "dagger", "d2": "none", "armor": "none"}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # --- the builder's export carries the summary the engine needs
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", HERO); pg.once("dialog", lambda d: d.accept()); pg.click("#fromBuilder")
    fx = pg.evaluate("()=>{ C.s2='lbow'; C.d2='javelin'; return exportChar().camp.fx; }")
    ok("T1 export lists carried items the hero lacks the talent for", sorted(fx["pen"]) == ["broad", "dagger", "lbow"] and fx["ms"] == 0 and fx["th"] == 0)
    fx = pg.evaluate("()=>{ C.tal=['sword','missile','thrown']; return exportChar().camp.fx; }")
    ok("T2 with Sword, Missile and Thrown the sword is clear and both bonuses are on", sorted(fx["pen"]) == ["dagger", "lbow"] and fx["ms"] == 1 and fx["th"] == 1)
    out = pg.evaluate("()=>{ C.tal=['sword','missile','thrown']; return exportChar(); }")
    # --- the engine
    pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    r = pg.evaluate("""(o)=>{ const f=fromBuilder(o); return {dag:f.dag, camp:f.camp, slung:f.slung}; }""", out)
    ok("T3 a campaign hero keeps every carried weapon: dagger, javelin and the bow all ready-able", sorted(r["dag"]) == ["dagger", "javelin", "lbow"])
    ok("T4 the talent summary reaches the fighter", r["camp"] == {"pen": ["dagger", "lbow"], "ms": 1, "th": 1})
    ok("T5 a regular builder fighter is untouched (one dagger, no talents)", pg.evaluate("(o)=>{ const x=Object.assign({},o); delete x.camp; const f=fromBuilder(x); return f.dag.length<=1&&!f.camp; }", out))
    w = pg.evaluate("""(o)=>{ const f=fromBuilder(o); const u={p:f}; return [wxu(u,'broad','melee'),wxu(u,'dagger','melee'),wxu(u,'lbow','missile'),wxu(u,'javelin','thrown'),wxu(u,'javelin','melee'),wxu({p:{}},'broad','melee')]; }""", out)
    ok("T6 modifiers: sword talent held 0; dagger −4; bow lacks talent but Missile +3 = −1; thrown +2; plain melee 0; ordinary fighters 0", w == [0, -4, -1, 2, 0, 0])
    # a live fight: the extra weapons show up as things to ready
    pg.select_option("#npSel", "1"); pg.evaluate("(o)=>{ setP(0,fromBuilder(o),'x'); }", out); pg.click("#bGo")
    pg.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); } }")
    txt = pg.evaluate("()=>options(G.players[0],G.mobs[0]).map(x=>x.label).join(' | ')")
    ok("T7 the pick screen offers readying the dagger, the bow and the javelin", all(k in txt for k in ["Ready Dagger", "Ready Longbow", "Ready Javelin"]))
    ts = pg.evaluate("()=>{ const f=fromBuilder({name:'T',race:'human',cls:'fighter',st:14,dx:14,iq:8,a:'broad',b:'tower',armor:'none'}); return [f.left, adjDX(f), stops(f)]; }")
    ok("T8 a tower shield stops 3 and costs 2 DX in the Colosseum (14 DX -> 12, stops 3)", ts == ["tower", 12, 3])
    pg.goto(BASE + "builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("T9 the regular builder does not know the tower shield", pg.evaluate("()=>!RULES.SHIELDS.tower&&Object.keys(RULES.SHIELDS).length===2"))
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    d = json.loads(json.dumps(DATA)); d["prices"]["tower"] = 60; d["talentFor"]["tower"] = "knife"
    pg.fill("#dataBox", json.dumps(d)); pg.click("#dataSave")
    ok("T10 campaign data may price the tower shield (it appears in the shop)", pg.is_visible("#work") and "Tower shield" in pg.inner_text("#work"))
    ok("T11 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
