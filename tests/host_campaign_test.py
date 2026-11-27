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
    pg=p.chromium.launch().new_page(viewport={"width":1200,"height":900}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"colosseum.html?net=mem"); pg.evaluate("localStorage.clear()")
    pg.goto(BASE+"index.html")
    ok("H1 menu has the Host a campaign table button", "Host a campaign table" in pg.inner_text("#hostCamp"))
    ok("H2 with no module it says none is loaded", "No campaign is loaded" in pg.inner_text("#hostCampTxt"))
    pg.click("#hostCamp"); pg.wait_for_url("**/colosseum.html**"); pg.wait_for_selector("#campBanner")
    ok("H3 no module: Colosseum opens the Encounter box with a reminder", pg.evaluate("()=>$('encCard').open")  and "No campaign" in pg.inner_text("#campBanner"))
    base=pg.evaluate("()=>JSON.parse(JSON.stringify(SAMPLE_ENC))")
    def room(t): r=json.loads(json.dumps(base)); r["name"]=t; return r
    mod={"module":"Test cellars","encounters":[room("Room one"),room("Room two"),room("Room three")]}
    pg.fill("#encJson",json.dumps(mod)); pg.click("#encApply"); pg.click("#modNext")
    pg.evaluate("()=>localStorage.setItem('colosseum-host-room','STEVE')")
    pg.goto(BASE+"index.html")
    ok("H4 with a module the button says continue and names room 2 of 3", "room 2 of 3" in pg.inner_text("#hostCampTxt"))
    pg.click("#hostCamp"); pg.wait_for_selector("#campBanner"); pg.wait_for_timeout(1500)
    ok("H5 Encounter chosen, module room kept", pg.evaluate("()=>CREK==='enc'&&MOD.i===1&&ENC.name==='Room two'"))
    ok("H6 campaign ST is on", pg.evaluate("()=>CAMP.on&&$('campOn').checked"))
    ok("H7 phone table opened with the saved name", "STEVE" in pg.inner_text("#onBody"))
    ok("H8 no script errors", not errs)
    if errs: print(errs)
print(f"{n-bad}/{n} passed")
