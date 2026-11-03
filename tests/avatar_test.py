"""Character pictures: builder upload (shrunk), print box, the counter on the Colosseum map and on a phone (turns with the facing). Fake Firebase (?net=mem)."""
import http.server, socketserver, threading, os, functools, base64, json, tempfile
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    b = mk("builder.html"); b.evaluate("localStorage.clear()"); b.reload()
    png = b.evaluate("""()=>{ const c=document.createElement('canvas'); c.width=600; c.height=400; const x=c.getContext('2d'); x.fillStyle='#c33'; x.fillRect(0,0,600,400); x.fillStyle='#fff'; x.fillRect(250,0,100,150); return c.toDataURL('image/png'); }""")
    path = os.path.join(tempfile.mkdtemp(), "art.png"); open(path, "wb").write(base64.b64decode(png.split(",")[1]))
    b.set_input_files("#picFile", path)
    b.wait_for_function("S.pic&&S.pt")
    ok("A1 a picture is shrunk to two small JPEGs (sheet size and table size)", b.evaluate("S.pic.startsWith('data:image/jpeg;base64,')&&S.pt.length<2700&&S.pic.length<30000"))
    ok("A2 the builder shows a thumbnail", b.locator("#picThumb").is_visible())
    ok("A3 the printed sheet puts the picture in both Figure boxes", b.locator(".figure img.figimg").count() == 1 and b.locator(".pfig img.figimg").count() == 1)
    ok("A4 the picture is saved with the character", "pic" in json.loads(b.evaluate("localStorage.getItem('wizard-builder-v1')")))
    b.set_input_files("#picFile", {"name": "a.svg", "mimeType": "image/svg+xml", "buffer": b"<svg xmlns='http://www.w3.org/2000/svg'><script>1</script></svg>"})
    b.wait_for_timeout(300)
    ok("A5 an SVG file is refused", b.evaluate("S.pic.startsWith('data:image/jpeg')") and "not SVG" in b.inner_text("#toast"))
    pic0 = b.evaluate("S.pic"); pt0 = b.evaluate("S.pt"); chosen = b.evaluate("localStorage.getItem('wizard-builder-v1')")
    # Colosseum: tablet counter
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.evaluate("(c)=>localStorage.setItem('wizard-builder-v1',c)", chosen); host.reload()
    host.evaluate("""()=>{ G=null; NP=2; MODE="ffa"; applyMode(); starts.fill(null); slot[0]=fromBuilder(JSON.parse(localStorage.getItem('wizard-builder-v1'))); slot[1]=fromBuilder({name:"Cy",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}); startFight(); }""")
    ok("A6 a fighter with a picture keeps a safe copy (only small JPEG data addresses accepted)", host.evaluate("G.players[0].p.pt.startsWith('data:image/jpeg')")  and host.evaluate("fromBuilder({name:'x',race:'human',cls:'fighter',st:12,dx:12,iq:8,pic:'javascript:alert(1)',pt:'data:image/svg+xml;base64,AAAA'}).pt")=="" )
    ok("A7 the tablet map draws the picture as the counter (rotated by the facing)", host.locator("#map image").count() >= 1 and "rotate(" in host.evaluate("document.querySelector('#map image').parentNode.getAttribute('transform')"))
    tr = lambda: host.evaluate("document.querySelector('#map image').parentNode.getAttribute('transform')")
    t0 = tr(); host.evaluate("()=>{ G.players[0].f=(G.players[0].f+2)%6; drawMap(); }")
    ok("A8 turning the figure turns the picture", tr() != t0)
    # a phone that brings this character: the small picture crosses the table, the big one stays
    host.evaluate("()=>{ G=null; ui(); drawMap(); }")
    host.click("#online summary"); host.fill("#onName", "AVAT"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    ph = mk("phone.html?net=mem&room=AVAT"); ph.evaluate("(c)=>sessionStorage.setItem('wizard-builder-v1',c)", chosen); ph.reload()
    ph.fill("#nm", "Bo"); ph.click("#go"); ph.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')")
    host.wait_for_function("slot[0]&&slot[0].phone")
    ok("A10 the small picture reaches the table with the character; the big one does not", host.evaluate("slot[0].pt.length>100") and "data:image/jpeg" not in (host.evaluate("slot[0].phone.fj").replace(pt0, "")))
    host.evaluate("""()=>{ slot[1]=fromBuilder({name:"Cy",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"}); NP=2; ui(); startFight(); }""")
    ph.wait_for_function("lastP&&lastP.sc&&lastP.sc.u.some(u=>u.im)")
    ok("A11 the phone map draws the picture as the counter, rotated", ph.locator("#pmap image").count() >= 1 and "rotate(" in ph.evaluate("document.querySelector('#pmap image').parentNode.getAttribute('transform')"))
    ok("A9 no script errors", not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
