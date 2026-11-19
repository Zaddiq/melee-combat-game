"""campaign-builder.html: talents with an IQ budget, a purse and any amount of gear, and the character that comes out of it.
The page ships with no talent or price data; this test uses a small INVENTED data set (not any book's numbers).
Run: python3 tests/campaign_builder_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

DATA = {
  "talents": [
    {"id": "knife", "n": "Knife", "iq": 7, "c": 1},
    {"id": "sword", "n": "Sword", "iq": 7, "c": 2, "cIf": [["knife", 1]]},
    {"id": "shield", "n": "Shield", "iq": 7, "c": 1},
    {"id": "literacy", "n": "Literacy", "iq": 8, "c": 1, "wc": 1},
    {"id": "warrior", "n": "Warrior", "iq": 9, "c": 2, "st": 14},
    {"id": "fencing", "n": "Fencing", "iq": 10, "c": 3, "pre": ["sword"], "dx": 14},
    {"id": "twoweapons", "n": "Two Weapons", "iq": 11, "c": 3, "dx": 13},
  ],
  "prices": {"dagger": 10, "broad": 80, "small": 30, "leather": 100, "chain": 200, "twohsw": 120},
  "talentFor": {"dagger": "knife", "broad": "sword", "twohsw": "sword", "small": "shield"},
  "misc": [{"id": "rope", "n": "Rope", "p": 5}],
}
HERO = {"name": "Hera", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 14, "iq": 8, "spells": [], "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "armor": "none", "ep": 40, "notes": "x"}
WIZ = {"name": "Wen", "cls": "wizard", "race": "human", "total": 32, "st": 9, "dx": 12, "iq": 11, "spells": ["Staff", "Magic Fist", "Blur"], "a": "none", "b": "none", "s1": "none", "d1": "dagger", "d2": "none", "armor": "none"}

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("B1 with no data the page asks for it and shows nothing else", not pg.is_visible("#work") and pg.is_visible("#dataBox"))
    ok("B2 the page itself carries no talent or price list", "Fencing" not in pg.content().split("<script>")[0] and "broadsword" not in pg.content().lower().split("<script>")[0])
    bad = json.loads(json.dumps(DATA)); bad["prices"]["unicorn"] = 5
    pg.fill("#dataBox", json.dumps(bad)); pg.click("#dataSave")
    ok("B3 data naming an unknown item is refused with a message", "unicorn" in pg.inner_text("#dataMsg") and not pg.is_visible("#work"))
    bad = json.loads(json.dumps(DATA)); bad["talents"][5]["pre"] = ["nothing"]
    pg.fill("#dataBox", json.dumps(bad)); pg.click("#dataSave")
    ok("B4 data with a missing prerequisite is refused", "not in the list" in pg.inner_text("#dataMsg"))
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    ok("B5 good data is saved, the builder appears, and the box says what loaded", pg.is_visible("#work") and "7 talents" in pg.inner_text("#dataState"))
    # a hero from the regular builder
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", HERO); pg.once("dialog", lambda d: d.accept()); pg.click("#fromBuilder")
    ok("B6 the regular builder's open character comes in (name, ST/DX/IQ, points)", pg.input_value("#chName") == "Hera" and pg.input_value("#chSt") == "14" and pg.input_value("#chIq") == "8" and pg.input_value("#chTotal") == "36")
    ok("B7 IQ 8 offers Knife but locks Fencing (needs IQ 10) and Two Weapons (needs IQ 11)", pg.is_enabled("#tal_knife") and pg.is_disabled("#tal_fencing") and "needs IQ 10" in pg.inner_text("#talents") and pg.is_disabled("#tal_twoweapons"))
    pg.check("#tal_knife"); pg.check("#tal_sword")
    ok("B8 Sword costs 1 once Knife is known: IQ used 2 of 8", pg.inner_text("#iqUsed") == "IQ used 2 of 8")
    pg.check("#tal_shield"); pg.check("#tal_literacy")
    ok("B9 the IQ budget fills up (4 of 8) and a talent that no longer fits is locked", pg.inner_text("#iqUsed") == "IQ used 4 of 8" and pg.is_disabled("#tal_warrior") is True)
    pg.fill("#chIq", "11"); pg.dispatch_event("#chIq", "change"); pg.fill("#chDx", "14"); pg.dispatch_event("#chDx", "change"); pg.fill("#chTotal", "50"); pg.dispatch_event("#chTotal", "change")
    ok("B10 raising IQ and DX unlocks Fencing (needs Sword and DX 14) and Two Weapons", pg.is_enabled("#tal_fencing") and pg.is_enabled("#tal_twoweapons"))
    pg.check("#tal_fencing"); pg.uncheck("#tal_sword")
    ok("B11 dropping Sword also drops Fencing, and says so", not pg.is_checked("#tal_fencing") and "Fencing removed" in pg.inner_text("#iqNote"))
    pg.fill("#chIq", "8"); pg.dispatch_event("#chIq", "change")
    ok("B12 a talent above the character's IQ cannot stay when IQ goes down", not pg.is_checked("#tal_twoweapons") and pg.inner_text("#iqUsed").startswith("IQ used"))
    pg.fill("#chIq", "11"); pg.dispatch_event("#chIq", "change"); pg.fill("#chLangs", "2"); pg.dispatch_event("#chLangs", "change")
    ok("B13 languages cost 1 IQ each", pg.inner_text("#iqUsed") == "IQ used " + str(pg.evaluate("()=>2+C.tal.reduce((t,id)=>t+costOf(T(id)),0)")) + " of 11")
    # money and gear
    pg.fill("#purse", "250"); pg.dispatch_event("#purse", "change")
    pg.click("[data-buy=broad]"); pg.click("[data-buy=small]"); pg.click("[data-buy=dagger]")
    ok("B14 buying takes money: 250 − 80 − 30 − 10 = 130 left (the character's own gear counts as owned already)", pg.evaluate("()=>left()") == 250 - pg.evaluate("()=>spent()") and "Left: $" in pg.inner_text("#moneyLeft"))
    pg.click("[data-buy=dagger]"); pg.click("[data-buy=dagger]")
    ok("B15 there is no limit on how many of an item: three daggers owned", pg.evaluate("()=>own('dagger')") == 3)
    pg.fill("#purse", "10"); pg.dispatch_event("#purse", "change")
    ok("B16 with too little money the Buy buttons lock and the character cannot be used", pg.is_disabled("[data-buy=twohsw]") and pg.is_disabled("#copyBtn") and "costs more than the money" in pg.inner_text("#problems"))
    pg.fill("#purse", "1000"); pg.dispatch_event("#purse", "change")
    pg.check("#silver")
    ok("B17 silver costs ten times as much (a broadsword $800)", "$800" in pg.inner_text("#shop"))
    pg.uncheck("#silver")
    # loadout
    pg.select_option("#ld_a", "broad"); pg.select_option("#ld_b", "small"); pg.select_option("#ld_d1", "dagger"); pg.select_option("#ld_d2", "dagger")
    ok("B18 hands, a sheathed dagger and a second sheathed dagger can be set from what is owned", pg.input_value("#ld_a") == "broad" and pg.input_value("#ld_b") == "small" and pg.input_value("#ld_d2") == "dagger")
    ok("B19 the fight note shows adjusted DX and the missing talent", "Adjusted DX" in pg.inner_text("#fightNote"))
    pg.uncheck("#tal_shield")
    ok("B20 a shield without the Shield talent is flagged (DX −4)", "you lack Shield" in pg.inner_text("#fightNote"))
    pg.check("#tal_shield")
    pg.select_option("#ld_a", "twohsw") if pg.locator("#ld_a option[value=twohsw]").count() else None
    ok("B21 a weapon you do not own is not offered", pg.locator("#ld_a option[value=twohsw]").count() == 0)
    pg.click("[data-buy=twohsw]"); pg.fill("#chSt", "11"); pg.dispatch_event("#chSt", "change")
    ok("B22 a weapon that needs more ST than the character has is offered with a warning, and dropped if chosen", "needs ST 14" in pg.inner_text("#ld_a"))
    pg.fill("#chSt", "14"); pg.dispatch_event("#chSt", "change"); pg.select_option("#ld_a", "twohsw")
    ok("B23 a two-handed weapon with a shield: the shield may stay (it goes on the back)", pg.input_value("#ld_a") == "twohsw")
    pg.select_option("#ld_a", "broad")
    # output
    out = json.loads(pg.input_value("#outBox"))
    ok("B24 the output keeps what the regular builder knew (EP, notes) and adds a camp block with talents, purse and gear", out["ep"] == 40 and out["notes"] == "x" and out["camp"]["v"] == 1 and "knife" in out["camp"]["tal"] and out["camp"]["inv"]["dagger"] == 3 and out["camp"]["d2"] == "dagger")
    ok("B25 the regular fields carry the loadout (a, b, d1) and the attributes", out["a"] == "broad" and out["b"] == "small" and out["d1"] == "dagger" and out["st"] == 14 and out["iq"] == 11 and out["armor"] == "none")
    col = br.new_page(); col.goto(BASE + "colosseum.html")
    f = col.evaluate("(o)=>{ const f=fromBuilder(o); return {r:f.right,l:f.left,d:f.dag,name:f.name,st:f.st,tal:f.src.camp.tal.length}; }", out)
    ok("B26 the Colosseum reads that character: broadsword right, small shield left, one dagger, talents kept on the source", f["r"] == "broad" and f["l"] == "small" and f["d"] == ["dagger"] and f["name"] == "Hera" and f["tal"] >= 3)
    col.close()
    ok("B27 the output is small enough for a phone to send (under 6000 characters)", len(pg.input_value("#outBox")) < 6000)
    pg.click("[data-sell=dagger]")
    ok("B28 selling an item gives the money back and frees a slot (two daggers left, both sheathed)", pg.evaluate("()=>own('dagger')") == 2 and pg.input_value("#ld_d2") == "dagger")
    pg.click("[data-sell=dagger]")
    ok("B29 selling down to one dagger empties the second sheath", pg.input_value("#ld_d2") == "none" and pg.input_value("#ld_d1") == "dagger")
    # roster and reload
    pg.click("#rosterSave"); pg.reload()
    ok("B30 after a reload the working character is still there with its talents", pg.input_value("#chName") == "Hera" and pg.is_checked("#tal_knife"))
    pg.select_option("#rosterSel", "Hera"); pg.once("dialog", lambda d: d.accept()); pg.click("#rosterLoad")
    ok("B31 the saved list brings it back", pg.input_value("#chName") == "Hera")
    # a wizard
    pg.evaluate("(o)=>localStorage.setItem('wizard-builder-v1',JSON.stringify(o))", WIZ); pg.once("dialog", lambda d: d.accept()); pg.click("#fromBuilder")
    ok("B32 a wizard pays double for talents (Knife 2) except where the data says otherwise (Literacy 1)", "2 IQ" in pg.inner_text("label[for=tal_knife] + .c") and "1 IQ" in pg.inner_text("label[for=tal_literacy] + .c"))
    ok("B33 a wizard's spells use IQ too (3 spells = 3 of 11) and the Staff fills the right hand", pg.inner_text("#iqUsed") == "IQ used 3 of 11" and pg.is_disabled("#ld_a"))
    pg.once("dialog", lambda d: d.accept()); pg.click("#newChar")
    ok("B34 a new character starts as a human hero with 8 points to spend", pg.input_value("#chSt") == "8" and pg.input_value("#chTotal") == "32" and "8 points still to spend" in pg.inner_text("#ptsNote"))
    ok("B35 an unnamed character cannot be copied out", pg.is_disabled("#copyBtn") and "name" in pg.inner_text("#problems"))
    pg.evaluate("()=>{ $('dataCard').open=true; }"); pg.click("#dataClear")
    ok("B36 removing the data hides the builder again", not pg.is_visible("#work"))
    ok("B37 no script errors", not errs)
    print(errs[:3])
print(f"{sum(c for _, c in R)}/{len(R)} passed")
