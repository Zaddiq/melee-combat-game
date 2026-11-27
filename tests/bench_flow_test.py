"""Quick fighters: simulator -> bench A/B -> campaign builder (list) and the table's give card. Run: python3 tests/bench_flow_test.py"""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={"width":1200,"height":1000}); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    sim = mk("sim.html"); sim.evaluate("localStorage.clear()"); sim.reload()
    sim.fill("#a_name", "Kid One"); sim.fill("#a_st", "13"); sim.fill("#a_dx", "11"); sim.click("#a_bench")
    sim.fill("#b_name", "Kid Two"); sim.fill("#b_st", "12"); sim.fill("#b_dx", "12"); sim.select_option("#b_race", "1"); sim.click("#b_bench")
    B = sim.evaluate("()=>JSON.parse(localStorage.getItem('melee-bench-v1'))")
    ok("B1 simulator fighters land on bench A and B", B["a"]["name"] == "Kid One" and B["b"]["name"] == "Kid Two" and B["a"]["st"] == 13 and B["b"]["race"] == "elf")
    ok("B2 the message says where it went", "bench A" in sim.inner_text("#a_bmsg"))
    sim.fill("#a_st", "5"); sim.click("#a_bench")
    ok("B3 an invalid ST is refused", "ST and DX" in sim.inner_text("#a_bmsg") and sim.evaluate("()=>JSON.parse(localStorage.getItem('melee-bench-v1')).a.st")==13)
    cb = mk("campaign-builder.html")
    cb.wait_for_selector("#benchA")
    cb.click("#benchA")
    ok("B4 the campaign builder loads bench A", cb.input_value("#chName") == "Kid One" and "Loaded Kid One" in cb.inner_text("#benchMsg"))
    ok("B4b it bought its weapon and trained the matching talent", cb.evaluate("()=>{ const k=C.a; const tf=talentFor(k); return own(k)>0&&(C.b==='none'||own(C.b)>0)&&(!tf||has(tf.id))&&left()>=0&&iqUsed()<=C.iq; }") and "Trained:" in cb.inner_text("#benchMsg"))
    ok("B4c the shop shows no missing-talent warning for its weapon", "(you lack it)" not in cb.inner_text("#tf_"+cb.evaluate("()=>C.a")))
    cb.click("#rosterSave")
    ok("B5 and can save it in its list", "Kid One" in cb.eval_on_selector_all("#rosterSel option", "e=>e.map(x=>x.textContent)"))
    cb.click("#benchB")
    ok("B6 bench B loads too", cb.input_value("#chName") == "Kid Two")
    host = mk("colosseum.html?net=mem")
    host.evaluate("()=>{ $('setup').open=true; $('premCard').open=true; }")
    ok("B7 the table's give card lists the bench fighters", "From bench A: Kid One" in host.inner_text("#premSel") and "From bench B: Kid Two" in host.inner_text("#premSel"))
    host.select_option("#premSel", label="From bench B: Kid Two"); host.select_option("#premSeat", "1"); host.click("#premGo")
    ok("B8 giving a bench fighter to a seat works", host.evaluate("()=>slot[1]&&slot[1].name==='Kid Two'"))
    cb2 = mk("campaign-builder.html"); cb2.evaluate("localStorage.removeItem('melee-bench-v1')"); cb2.reload(); cb2.click("#benchA")
    ok("B9 an empty bench explains what to do", "Nothing on bench A" in cb2.inner_text("#benchMsg"))
    ok("B10 no page errors", not errs)
    if errs: print(errs)
print(f"{sum(1 for _,c in R if c)}/{len(R)} passed")
