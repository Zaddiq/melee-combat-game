"""Builder checks. Run: python3 tests/builder_test.py  (needs Playwright)."""
from playwright.sync_api import sync_playwright
import os
res=[]
def ok(n,c): res.append((n,bool(c))); print(('PASS ' if c else 'FAIL ')+n)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1100,"height":900}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','builder.html')))
    ok("B1 the page opens on the example wizard (named, with spells)", pg.evaluate("S.name.startsWith('Yzor')&&S.spells.length>0"))
    pg.once("dialog", lambda d: d.dismiss()); pg.click("#newChar")
    ok("B2 declining the warning keeps the character on screen", pg.evaluate("S.name.startsWith('Yzor')"))
    pg.once("dialog", lambda d: d.accept()); pg.click("#newChar")
    ok("B3 New character gives a Human fighter, 8/8/8, total 32, 8 points to spend", pg.evaluate("S.race==='human'&&S.cls==='fighter'&&S.st===8&&S.dx===8&&S.iq===8&&S.total===32&&S.total-(S.st+S.dx+S.iq)===8"))
    ok("B4 no name, no spells, no gear, no XP", pg.evaluate("S.name===''&&S.spells.length===0&&S.a==='none'&&S.b==='none'&&S.s1==='none'&&S.d1==='none'&&S.armor==='none'&&S.ep===0&&S.notes===''")
       and pg.input_value("#name")=="")
    ok("B5 the sheet shows 24 of 32 points used", "24 of 32" in pg.inner_text("#s-attr"))
    ok("B6 the new character is saved in the browser", pg.evaluate("JSON.parse(localStorage.getItem(KEY)).total===32&&JSON.parse(localStorage.getItem(KEY)).name===''"))
    dialogs=[]; pg.on("dialog", lambda d:(dialogs.append(d.message), d.accept())); pg.click("#newChar")
    ok("B7 starting over on an untouched blank character does not ask", not dialogs)
    pg.click("[data-inc='st']"); pg.click("#newChar")
    ok("B8 after spending a point it asks first, then resets to 8/8/8", len(dialogs)==1 and pg.evaluate("S.st===8"))
    pg.fill("#name","Zed"); pg.click("#newChar")
    ok("B9 a typed name also triggers the warning and is cleared by the reset", len(dialogs)==2 and pg.evaluate("S.name===''")  and pg.input_value("#name")=="")
    pg.screenshot(path=os.environ.get("SHOT","/tmp/builder_new.png"))
    print(sum(1 for r in res if r[1]),'/',len(res),'passed'); print(errs[:3])
