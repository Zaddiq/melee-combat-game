"""A phone joins the table with a campaign hero (talents summary + extra carried gear); the tablet seats it and the fight uses it.
Tablet = colosseum.html, phone = phone.html, fake Firebase (?net=mem). Run: python3 tests/phone_campaign_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
HERO = {"name": "Hera", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 14, "iq": 9, "spells": [], "a": "broad", "b": "none", "s1": "none", "d1": "dagger", "d2": "none", "armor": "leather",
        "camp": {"v": 1, "langs": 0, "tal": ["sword"], "purse": 0, "inv": {}, "s2": "large", "d2": "mace", "fx": {"pen": ["dagger", "mace"], "ms": 1, "th": 0}}}
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.evaluate("()=>{ NP=1; CAMP.on=true; }")
    host.click("#online summary"); host.fill("#onName", "STEVE"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=STEVE")
    ph.evaluate("(b)=>{ sessionStorage.setItem('wizard-builder-v1',b); fillChars(); }", json.dumps(HERO))
    ph.click("#go")
    ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    host.wait_for_function("slot[0]&&slot[0].phone")
    ok("P1 the phone's campaign hero reaches the seat with its talent summary", host.evaluate("()=>slot[0].name==='Hera'&&!!slot[0].camp&&slot[0].camp.ms===1&&slot[0].camp.pen.includes('mace')"))
    ok("P2 and its extra carried gear: dagger and mace in the pack, the shield slung", host.evaluate("()=>{ const f=slot[0]; return f.dag.includes('dagger')&&f.dag.includes('mace')&&f.slung==='large'; }"))
    host.evaluate("()=>{ $('creSel').value='enc'; $('creSel').dispatchEvent(new Event('change')); }")
    host.click("#bGo")
    host.evaluate("()=>{ let g=0; while(g++<20&&G.phase!=='pick'&&G.phase!=='over'){ if(G.phase==='choose') choose(true); else if(G.phase==='move') confirmMove(); } }")
    ok("P3 in the fight the hero keeps its talent summary and gear", host.evaluate("()=>{ const u=G.players[0]; return !!u.p.camp&&u.p.camp.pen.length===2&&u.dag.length>=2; }"))
    ph.wait_for_function("document.querySelectorAll('#play button.opt').length>0||document.querySelectorAll('button.opt').length>0", timeout=15000)
    txt = ph.evaluate("()=>[...document.querySelectorAll('button.opt')].map(b=>b.textContent).join(' | ')")
    ok("P4 the phone's own buttons offer readying the carried mace and the shield", "Mace" in txt and "Large shield" in txt)
    ok("P5 the phone shows ordinary action buttons too (attack, fire or ready)", "Attack" in txt or "Fire" in txt or "Ready" in txt)
    bp = mk("builder.html"); bp.evaluate("(b)=>localStorage.setItem('wizard-builder-v1',b)", json.dumps(HERO)); bp.reload()
    bp.evaluate("()=>{ save(); }")
    kept = bp.evaluate("()=>{ const o=JSON.parse(localStorage.getItem('wizard-builder-v1')); return !!o.camp&&o.camp.fx.ms===1&&o.camp.s2==='large'; }")
    ok("P7 opening and saving a campaign hero in the regular builder keeps its campaign block", kept)
    ok("P6 no script errors", not errs)
    br.close()
print(sum(c for _, c in R), "/", len(R), "passed"); raise SystemExit(0 if all(c for _, c in R) else 1)
