"""Magic items list (campaign/magic.html): the Advanced Wizard enchantment rules, flaming weapons, magic armor in the fight.
Run: python3 tests/magic_page_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/campaign/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
DATA = {"talents": [{"id": "sword", "n": "Sword", "iq": 7, "c": 2}], "prices": {"broad": 80}, "talentFor": {"broad": "sword"}, "misc": []}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "magic.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("P1 starts empty", pg.is_visible("#empty"))
    pg.click("#add"); pg.fill("#f_n", "Dawnbringer"); pg.select_option("#f_base", "broad"); pg.fill("#f_dx", "2"); pg.fill("#f_dm", "4"); pg.click("#save")
    ok("P2 DX and damage over 5 together are refused", "at most 5" in pg.inner_text("#edMsg") and pg.evaluate("()=>localStorage.getItem('magic-items-v1')") is None)
    pg.fill("#f_dm", "3"); pg.check("#f_flame"); pg.fill("#f_note", "Say 'Dawn' to flame."); pg.click("#save")
    t = pg.inner_text("#list")
    ok("P3 saved: shows damage 2d+3, DX +2 and flaming 2d+6", all(x in t for x in ["Dawnbringer", "2d+3", "DX +2", "2d+6", "Say 'Dawn'"]))
    pg.click("#add"); pg.fill("#f_n", "Mithril"); pg.select_option("#f_kind", "armor"); pg.select_option("#f_base", "chain"); pg.fill("#f_stops", "2"); pg.click("#save")
    ok("P4 armor: shows 3 + 2 = 5 hits stopped", "3 +2 = 5" in pg.inner_text("#list"))
    pg.click("#add"); pg.fill("#f_n", "Bad"); pg.select_option("#f_kind", "armor"); pg.fill("#f_stops", "6"); pg.click("#save")
    ok("P5 armor stopping over 5 extra is refused", "1 to 5" in pg.inner_text("#edMsg")); pg.click("#cancel")
    ok("P6 flame rules by dice: 1 die +2, 2 dice +3, 3 dice one more die, bow +1, crossbow +2", pg.evaluate("""()=>{ const g=(b)=>{ RULES.addMagic([{id:'mg_1',base:b,flame:1,lit:1}]); const w=RULES.W.mg_1, o=RULES.W[b]; return [w.d-o.d,w.m-o.m]; };
        return JSON.stringify([g('dagger'),g('broad'),g('twohsw'),g('sbow'),g('lxbow')]); }""") == json.dumps([[0, 2], [0, 3], [1, 0], [0, 1], [0, 2]], separators=(",", ":")))
    pg.fill("#q", "mith"); ok("P7 search narrows", pg.locator("#list .it").count() == 1); pg.fill("#q", "")
    saved = pg.evaluate("()=>localStorage.getItem('magic-items-v1')")
    pg.goto(BASE + "campaign-builder.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.fill("#dataBox", json.dumps(DATA)); pg.click("#dataSave")
    HERO = {"name": "Sam", "cls": "fighter", "race": "human", "total": 36, "st": 14, "dx": 12, "iq": 10, "armor": "none", "a": "none", "b": "none", "s1": "none", "d1": "none", "d2": "none", "spells": [], "camp": {"v": 1, "langs": 0, "tal": [], "purse": 0, "inv": {}, "s2": "none", "d2": "none", "fx": {"pen": [], "ms": 0, "th": 0}, "magic": []}}
    pg.evaluate("([h,l])=>{ localStorage.setItem('campaign-char-v1',JSON.stringify(h)); localStorage.setItem('magic-items-v1',l); }", [HERO, saved]); pg.reload()
    opts = pg.evaluate("()=>[...document.querySelectorAll('#magicPick option')].map(o=>o.textContent)")
    ok("Q1 the builder lists the items from the magic list", sorted(opts) == ["Dawnbringer", "Mithril"])
    pg.select_option("#magicPick", label="Dawnbringer"); pg.click("#magicAdd"); pg.select_option("#magicPick", label="Mithril"); pg.click("#magicAdd")
    ok("Q2 both are on the hero and in the gear lists", pg.evaluate("()=>[C.magic.length,fightList('a').includes('mg_1'),Object.keys(C.inv).includes('mg_2')]") == [2, True, True])
    pg.select_option("#ld_a", "mg_1"); pg.select_option("#ldArmor", "mg_2")
    ok("Q3 readied: DX 12 +2 for the sword, chain -3 for the armor", pg.evaluate("()=>adjDX()") == 12 + 2 - 3)
    ok("Q4 Flame on appears for a flaming weapon and changes its damage", pg.evaluate("()=>[W.mg_1.m]")[0] == 3 and (pg.check("[data-lit]") or True) and pg.evaluate("()=>[W.mg_1.m,W.mg_1.n]") == [6, "Dawnbringer (flaming)"])
    ex = pg.evaluate("()=>exportChar()")
    pg.goto(BASE + "colosseum.html")
    st = pg.evaluate("""(h)=>{ const f=fromBuilder(h); return [f.right,f.armor,ARMOR[f.armor].stops,W[f.right].m,adjDX(f),stops(f)]; }""", ex)
    ok("Q5 the Colosseum gets the lit sword and the 5-stop armor", st == ["mg_1", "mg_2", 5, 6, 11, 5])
    ok("Q6 no page errors", not errs)
    br.close()
bad = [n for n, c in R if not c]; print("\n%d/%d passed" % (len(R) - len(bad), len(R))); raise SystemExit(1 if bad else 0)
