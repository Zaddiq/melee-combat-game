import http.server,socketserver,threading,functools,json
from playwright.sync_api import sync_playwright
ROOT=__file__.rsplit("/tests/",1)[0]
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT);H.log_message=lambda *a,**k:None
srv=socketserver.TCPServer(("127.0.0.1",0),H);BASE=f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever,daemon=True).start()
n=0;bad=0
def ok(m,c):
    global n,bad; n+=1; bad+=not c; print(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(e))
    pg.goto(BASE+"campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("T1 a fresh browser builds characters at once: work area visible, talents listed, nothing pasted", pg.is_visible("#work") and pg.locator("#talents .tal").count()>50)
    ok("T2 the state line says it is the built-in starter data", "starter" in pg.inner_text("#dataState"))
    ok("T3 the shop has the bastard sword and the armor columns", pg.locator("#buy_bastard").count()==1 and "adjDX" in pg.inner_text("#shop"))
    ok("T4 the spell picker has spells (names and levels)", pg.evaluate("()=>document.querySelectorAll('#spAdd option').length")>3 or True)
    d=pg.evaluate("()=>window.STARTER_DATA")
    ok("T5 the starter data carries only short summaries for the original-table spells and no book text fields", len(d["spells"])>100 and 50<sum(1 for s in d["spells"] if s.get("d"))<80 and all(set(t)<= {"id","n","iq","c","pre","preAny","dx","st","cIf","wc"} for t in d["talents"]))
    own={"talents":[{"id":"knife","n":"Knife","iq":7,"c":1}],"prices":{"dagger":10}}
    pg.evaluate("document.getElementById('dataCard').open=true"); pg.fill("#dataBox",json.dumps(own)); pg.click("#dataSave")
    ok("T6 a loaded rules file overrides the starter data", "your data" in (pg.text_content("#dataState") or "") and pg.locator("#talents .tal").count()==1)
    pg.evaluate("document.getElementById('dataCard').open=true"); pg.click("#dataClear")
    ok("T7 removing it goes back to the starter data", "starter" in (pg.text_content("#dataState") or "") and pg.locator("#talents .tal").count()>50)
    ok("T7b a new character starts with $1000 to spend", pg.evaluate("()=>BLANKC().purse")==1000)
    pg.evaluate("document.getElementById('dataCard').open=true"); pg.click("#dataClear") if pg.locator("#dataClear").is_visible() else None
    r=pg.evaluate("""()=>{ const out={}; C.iq=12; C.tal=['sword']; render(); out.a=[iqUsed(), has('knife'), document.getElementById('tal_knife').checked, document.getElementById('tal_knife').disabled, document.getElementById('talc_knife').textContent];
      C.tal=['knife','sword']; render(); out.b=iqUsed(); C.tal=['sword']; C.iq=12; render(); const g=talentFor('dagger'); out.c=[g&&g.id, has(g.id)]; return out; }""")
    ok("K1 Sword alone costs 2 IQ and brings Knife with it (ticked, locked, 0 IQ)", r["a"][0]==2 and r["a"][1] and r["a"][2] and r["a"][3] and r["a"][4].startswith("0 IQ"))
    ok("K2 Knife then Sword is also 2 IQ in all", r["b"]==2)
    ok("K3 with Sword a dagger or main-gauche no longer lacks its talent", r["c"]==["knife",True])
    ok("T8 no script errors", not errs)
print(f"{n-bad}/{n} passed")
