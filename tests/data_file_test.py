import http.server,socketserver,threading,functools,json,os,tempfile
from playwright.sync_api import sync_playwright
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=__file__.rsplit("/tests/",1)[0]);H.log_message=lambda *a,**k:None
srv=socketserver.TCPServer(("127.0.0.1",0),H);BASE=f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever,daemon=True).start()
n=0;bad=0
def ok(m,c):
    global n,bad; n+=1; bad+=not c; print(("PASS " if c else "FAIL ")+m)
DATA={"talents":[{"id":"knife","n":"Knife","iq":7,"c":1}],"prices":{"dagger":10}}
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(e))
    pg.goto(BASE+"campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    f=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False); f.write(json.dumps(DATA)); f.close()
    ok("F1 before loading, the work area is hidden", not pg.is_visible("#work"))
    pg.set_input_files("#dataFile",f.name); pg.wait_for_selector("#work",state="visible",timeout=5000)
    ok("F2 choosing the file loads the rules data and opens the builder", pg.is_visible("#work") and "1 talents" in pg.inner_text("#dataState"))
    g=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False); g.write("not json"); g.close()
    pg.set_input_files("#dataFile",g.name); pg.wait_for_timeout(300)
    ok("F3 a bad file says so and keeps the saved data", "not valid" in (pg.text_content("#dataMsg") or "") and pg.is_visible("#work"))
    ok("F4 no script errors", not errs)
print(f"{n-bad}/{n} passed")
