"""Voice chat (voice.js): real WebRTC between browser tabs with Chromium's fake microphone; the setup messages go through the fake table (?net=mem).
Run: python3 tests/voice_test.py. Real networks (NAT, the public STUN servers) and real microphones are not covered."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream", "--autoplay-policy=no-user-gesture-required"])
    ctx = br.new_context(permissions=["microphone"]); errs = []
    def mk(url):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept()); pg.goto(BASE + url); return pg
    host = mk("colosseum.html?net=mem"); host.evaluate("localStorage.clear()"); host.reload()
    host.click("#online summary"); host.fill("#onName", "VOIC"); host.click("#onOpen"); host.wait_for_selector("#onBody b")
    def phone(name):
        pg = mk("phone.html?net=mem&room=VOIC"); pg.fill("#nm", name); pg.click("#go")
        pg.wait_for_function("document.getElementById('seat').textContent.startsWith('You are')"); return pg
    A = phone("Bo"); B = phone("Cy"); C = phone("Di")
    ok("V1 the host has a voice box once the table is open", host.locator("#vcHost").is_visible() and host.locator("#vcHost .vcJoin").count() == 1)
    ok("V2 every phone has a Join voice button and nothing starts by itself", A.locator("#vcPhone .vcJoin").count() == 1 and not A.evaluate("Voice.on") and not host.evaluate("Voice.on"))
    A.click("#vcPhone .vcJoin"); host.click("#vcHost .vcJoin")
    A.wait_for_function("Voice.on"); host.wait_for_function("Voice.on")
    def connected(pg, n): pg.wait_for_function("(n)=>Object.values(Voice.peers()).filter(s=>s==='connected').length>=n", arg=n, timeout=25000)
    try:
        connected(A, 1); connected(host, 1); good = True
    except Exception as e: good = False; print(str(e)[:200])
    ok("V3 a phone and the tablet connect to each other", good)
    import time
    for _ in range(40):
        if A.evaluate("Voice.rxBytes()") > 1000 and host.evaluate("Voice.rxBytes()") > 1000: break
        time.sleep(0.5)
    ok("V4 sound arrives (audio bytes received on both sides)", A.evaluate("Voice.rxBytes()") > 1000 and host.evaluate("Voice.rxBytes()") > 1000)
    B.click("#vcPhone .vcListen"); C.click("#vcPhone .vcJoin")
    for pg in (A, B, C, host): connected(pg, 3)
    ok("V5 four devices make a full mesh (each connected to the other three)", all(pg.evaluate("Object.keys(Voice.peers()).length")==3 for pg in (A, B, C, host)))
    ok("V6 the listen-only phone has no microphone, the others do", not B.evaluate("Voice.mic") and C.evaluate("Voice.mic"))
    A.click("#vcPhone .vcMute")
    ok("V7 Mute turns the microphone track off and the button says Unmute", A.evaluate("Voice.muted") and "Unmute" in A.inner_text("#vcPhone .vcMute"))
    aid = A.evaluate("Net.uid")
    A.click("#vcPhone .vcLeave")
    for pg in (B, C, host): pg.wait_for_function("Object.keys(Voice.peers()).length===2", timeout=15000)
    ok("V8 when one leaves the others drop that connection and keep the rest", all(pg.evaluate("Object.values(Voice.peers()).every(s=>s==='connected')") for pg in (B, C, host)))
    ok("V9 leaving removes the person from the voice list in the table", aid not in (host.evaluate("Net.b.get('rooms/VOIC/vc/peers')") or {}))
    A.click("#vcPhone .vcJoin"); A.wait_for_function("Voice.on")
    for pg in (A, B, C, host): connected(pg, 3)
    ok("V10 someone who left can come back and everyone reconnects", all(pg.evaluate("Object.values(Voice.peers()).filter(s=>s==='connected').length")==3 for pg in (A, B, C, host)))
    host.click("#vcHost .vcLeave"); 
    ok("V11 no script errors", not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
