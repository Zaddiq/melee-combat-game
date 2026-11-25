import http.server,socketserver,threading,functools
from playwright.sync_api import sync_playwright
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=__file__.rsplit("/tests/",1)[0]);H.log_message=lambda *a,**k:None
srv=socketserver.TCPServer(("127.0.0.1",0),H);B=f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever,daemon=True).start()
n=0;bad=0
def ok(m,c):
    global n,bad; n+=1; bad+=not c; print(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    br=p.chromium.launch()
    for page in ["colosseum","arena","duel","wizard-arena"]:
        pg=br.new_page(); pg.on("pageerror",lambda e:print("ERR",e)); pg.goto(B+page+".html")
        # dmgRoll is a top-level function: dice forced to 6s so the total shows the modifier
        r=pg.evaluate("""()=>{ rollN=n=>Array(n).fill(6); const a={right:'bastard',left:'none'}, b={right:'bastard',left:'small'}, c={right:'bastard2',left:'none'};
          return [dmgRoll(a,'bastard'),dmgRoll(b,'bastard'),dmgRoll(c,'bastard2')].map(x=>x.dice.length+':'+x.total+':'+!!x.two); }""")
        ok(f"G {page}: empty left hand 3d-2 (16), shield 2d+1 (13), explicit two-hand 3d-2", r==["3:16:true","2:13:false","3:16:false"])
        pg.close()
print(f"{n-bad}/{n} passed")
