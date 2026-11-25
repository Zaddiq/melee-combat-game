import http.server,socketserver,threading,functools,json
from playwright.sync_api import sync_playwright
ROOT=__file__.rsplit("/tests/",1)[0]
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT);H.log_message=lambda *a,**k:None
srv=socketserver.TCPServer(("127.0.0.1",0),H);BASE=f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever,daemon=True).start()
n=0;bad=0
def ok(m,c):
    global n,bad; n+=1; bad+=not c; print(("PASS " if c else "FAIL ")+m)
import os
_P="/tmp/claude-0/-home-claude/5985870c-959b-57f7-a411-8e71a192306f/scratchpad/out/campaign-data-updated.json"   # the owner's rules data is not in the repo
DATA=json.load(open(_P)) if os.path.exists(_P) else {"talents":[{"id":"knife","n":"Knife","iq":7,"c":1}],"prices":{"dagger":10},
  "spells":[{"n":n,"iq":q} for n,q in [("Staff",8),("Blur",8),("Light",8),("Image",8),("Trip",10),("Fireball",12),("Lightning",14)]]}
def hero(**k):
    c={"name":"H","race":"human","cls":"fighter","st":12,"dx":12,"iq":8,"total":32,"a":"none","b":"none","armor":"none","spells":[]}; c.update(k); return c
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(e)); pg.on("dialog",lambda d:d.accept())
    pg.goto(BASE+"campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox",json.dumps(DATA)); pg.click("#dataSave")
    def load(c):
        pg.evaluate("(c)=>{ C=normalize(c); render(); }",c) if pg.evaluate("typeof normalize")=="function" else None
    # use the paste box, the supported way in
    def paste(c):
        (pg.click("#pasteBtn") if not pg.is_visible("#pasteTxt") else None); pg.fill("#pasteTxt",json.dumps(c)); pg.click("#pasteGo")
    paste(hero())
    ok("S1 a hero with no spells gets a collapsed Spells heading that says none, 3 IQ each", "none; 3 IQ each" in pg.inner_text("#spellSum") and not pg.evaluate("()=>document.getElementById('spellSec').open"))
    ok("S2 a hero's talents are open and first", pg.evaluate("()=>document.getElementById('talSec').open")==True)
    paste(hero(name="H2",spells=["Fireball"]))
    t=pg.inner_text("#spellSum")
    ok("S3 a hero with one spell gets a collapsed Spells heading '3 of 8 IQ spent' after the talents", "Spells (3 of 8 IQ spent)" in t and pg.evaluate("()=>!document.getElementById('spellSec').open && +document.getElementById('spellSec').style.order > +document.getElementById('talSec').style.order"))
    paste(hero(name="W",cls="wizard",iq=12,spells=["Fireball","Blur"]))
    ok("S4 a wizard: Spells open and first, Talents a collapsed heading '0 of 12 IQ spent'", pg.evaluate("()=>{const a=document.getElementById('spellSec'),b=document.getElementById('talSec');return a.open&&!b.open&&+a.style.order<+b.style.order}") and "Talents (0 of 12 IQ spent)" in pg.inner_text("#talSum") and "Spells (2 of 12 IQ spent)" in pg.inner_text("#spellSum"))
    pg.click("#talSum")
    ok("S5 clicking Talents opens the full list", pg.is_visible("#talents .tal"))
    # the spell picker
    paste(hero(name="P",iq=10))
    pg.click("#spellSum")
    opts=pg.evaluate("()=>[...document.querySelectorAll('#spAdd option')].map(o=>o.value)")
    ok("P1 the picker offers spells of the hero's IQ or less and none above (Lightning is IQ 14)", "Fireball" not in opts and "Trip" in opts and "Lightning" not in opts and "Blur" in opts)
    pg.select_option("#spAdd","Trip"); pg.click("#spAddBtn")
    ok("P2 adding Trip to an IQ 10 hero costs 3 IQ (3 of 10) and lists it", "Spells (3 of 10 IQ spent)" in pg.inner_text("#spellSum") and "Trip" in pg.inner_text("#spellList"))
    ok("P3 a spell already known is no longer offered", "Trip" not in pg.evaluate("()=>[...document.querySelectorAll('#spAdd option')].map(o=>o.value)"))
    for nme in ["Blur","Light","Image"]: pg.select_option("#spAdd",nme); pg.click("#spAddBtn") if pg.is_enabled("#spAddBtn") else None
    ok("P4 at 3 IQ each, 10 IQ holds only three spells and the Add button then stops", "Spells (9 of 10 IQ spent)" in pg.inner_text("#spellSum") and pg.is_disabled("#spAddBtn"))
    pg.click("[data-spdel='Trip']")
    ok("P5 removing a spell gives the IQ back", "Spells (6 of 10 IQ spent)" in pg.inner_text("#spellSum") and not pg.is_disabled("#spAddBtn"))
    out=pg.evaluate("()=>exportChar()")
    ok("P6 the character carries its spells out to the game", sorted(out.get("spells",[]))==["Blur","Light"] if isinstance(out,dict) else False)
    paste(hero(name="Wz",cls="wizard",iq=9,spells=["Staff"]))
    ok("P7 a wizard pays 1 IQ per spell", pg.inner_text("#spellSum").startswith("Spells (1 of 9"))
    ok("S6 no script errors", not errs)
print(f"{n-bad}/{n} passed")
