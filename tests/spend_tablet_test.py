"""Spending an earned point in the Colosseum on the tablet's own roster (non-phone fighters). Run: python3 tests/spend_tablet_test.py"""
import os, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + ROOT + "/colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ex = pg.evaluate("()=>EXAMPLES[1]")
    rec = dict(name=ex["name"], st=ex["st"], dx=ex["dx"], iq=ex["iq"], total0=ex["st"]+ex["dx"]+ex["iq"], pts=0, wins=0, losses=0, ep=10, banked=False, pend=1, must=False, retired=False, dead=False, src=ex)
    pg.evaluate("([r,b])=>{ localStorage.setItem('melee-arena-v1',JSON.stringify({'wulf (example)':r})); localStorage.setItem('wizard-builder-v1',JSON.stringify(b)); setP(0,fromBuilder(b),'x'); }", [rec, ex])
    btns = pg.eval_on_selector_all("#stats [data-spend]", "e=>e.map(x=>x.dataset.spend)")
    ok("T1 a loaded fighter with a waiting point shows +1 ST, +1 DX and Bank in the Fighters box", btns == ["0:st", "0:dx", "0:bank"])
    pg.click('#stats [data-spend="0:dx"]')
    r = pg.evaluate("()=>JSON.parse(localStorage.getItem('melee-arena-v1'))['wulf (example)']")
    b = pg.evaluate("()=>JSON.parse(localStorage.getItem('wizard-builder-v1'))")
    ok("T2 +1 DX is saved to the roster (DX +1, one point, none waiting)", r["dx"] == ex["dx"] + 1 and r["pts"] == 1 and r["pend"] == 0)
    ok("T3 the builder holding the same character shows the new DX, total and EP", b["dx"] == ex["dx"] + 1 and b["total"] == rec["total0"] + 1 and b["ep"] == 10)
    ok("T4 the loaded fighter has the new DX for the next fight and the buttons are gone", pg.evaluate("()=>slot[0].dx")==ex["dx"]+1 and pg.locator("#stats [data-spend]").count() == 0)
    # experience earned in a fight reaches the builder at once
    pg.evaluate("()=>{ awardXp(slot[0],20); }")
    ok("T5 experience earned at the table updates the builder's EP at once", pg.evaluate("()=>JSON.parse(localStorage.getItem('wizard-builder-v1')).ep") == 30)
    # after a fight the result panel offers Return to Colosseum (not the main menu), with the point waiting
    pg.evaluate("()=>{ const k='wulf (example)', R=JSON.parse(localStorage.getItem('melee-arena-v1')); R[k].pend=1; R[k].ep=0; localStorage.setItem('melee-arena-v1',JSON.stringify(R)); REC=R; }")
    pg.evaluate("()=>{ G={phase:'over',turn:3,log:[],xp:[],players:[],mobs:[],winners:[],qb:''}; ui(); }")
    ok("T6 the result panel has Rematch and Return to Colosseum, and no link to the main menu", pg.locator("#bHome").count() == 1 and pg.locator("#bNew").count() == 1 and pg.locator("a[href='index.html']:has(button)").count() == 0)
    pg.click("#bHome")
    ok("T7 Return to Colosseum leaves the fight, keeps the fighter loaded and shows the point to spend", pg.evaluate("()=>G===null && !!slot[0] && document.getElementById('setup').open") and pg.locator("#stats [data-spend]").count() >= 2)
    # the builder holds a different character: Send to builder offers to replace it
    pg.evaluate("()=>localStorage.setItem('wizard-builder-v1',JSON.stringify({name:'Someone Else',st:10,dx:10,iq:10,total:30}))"); pg.evaluate("()=>showStats()")
    ok("T8 with a different character in the builder, a Send to builder button shows", pg.locator("#stats [data-send]").count() == 1)
    pg.once("dialog", lambda d: d.dismiss()); pg.click("#stats [data-send]")
    ok("T9 declining the replace question leaves the builder alone", pg.evaluate("()=>JSON.parse(localStorage.getItem('wizard-builder-v1')).name") == "Someone Else")
    pg.once("dialog", lambda d: d.accept()); pg.click("#stats [data-send]")
    b2 = pg.evaluate("()=>JSON.parse(localStorage.getItem('wizard-builder-v1'))")
    ok("T10 accepting puts the fighter in the builder with its new DX and EP", b2["name"] == ex["name"] and b2["dx"] == ex["dx"] + 1 and b2["ep"] == 0 and b2["total"] == rec["total0"] + 1)
    ok("T11 afterwards the button gives way to the up-to-date note", pg.locator("#stats [data-send]").count() == 0)
    ok("T12 no script errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
