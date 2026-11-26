import http.server,socketserver,threading,functools
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
    pg.goto(BASE+"colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    names=pg.eval_on_selector_all("#creSel option","e=>e.map(x=>x.textContent)")
    ok("L1 each opponent in the Colosseum list appears once (no doubled dragons)", len(names)==len(set(names)))
    ok("L2 the dragon and the small dragon are still offered (summon-spell stats)", any(x.startswith("Dragon") for x in names) and any(x.startswith("Small Dragon") for x in names))
    ok("L3 no script errors", not errs)
print(f"{n-bad}/{n} passed")
