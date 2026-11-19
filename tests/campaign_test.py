"""Campaign mode step 1 in colosseum.html: an encounter (mixed computer monsters in a rectangular room), its editor, and random play.
Run: python3 tests/campaign_test.py  (needs Playwright)."""
import http.server, socketserver, threading, os, functools, json
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT); H.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), H); BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
threading.Thread(target=srv.serve_forever, daemon=True).start()
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)

PLAY = r'''
()=>{
 const rnd=a=>a[Math.floor(Math.random()*a.length)];
 const out={games:0,over:0,errors:[],casts:0,shots:0,wins:0,losses:0,names:new Set()};
 const _dc=doCast; doCast=function(u,o,pa){ if(u.side==="mob") out.casts++; return _dc.apply(this,arguments); };
 const _da=doAttack; doAttack=function(a,d,w,m,kind){ if(a.side==="mob"&&kind==="missile") out.shots++; return _da.apply(this,arguments); };
 const mkp=g=>fromBuilder({name:"P"+g,race:"human",cls:g===2?"wizard":"fighter",st:g===2?9:12,dx:g===2?12:12,iq:g===2?13:8,armor:g===2?"none":"leather",a:g===2?"staff":"broad",b:g===2?"none":"small",spells:g===2?["Staff","Magic Fist","Blur"]:[],total:34});
 for(let g=0;g<24;g++){
  try{
   const n=2+(g%3); CREK="enc"; CREN=ENC.foes.length; G=null; NP=n; MODE="ffa"; applyMode(); syncMap(); starts.fill(null);
   for(let i=0;i<4;i++) slot[i]=i<n?mkp(i+1):null;
   startFight(); if(!G){ out.errors.push("no fight started"); continue; }
   G.mobs.forEach(m=>out.names.add(m.p.name));
   let guard=0;
   while(G.phase!=="over"&&guard++<900){
     const ph=G.phase;
     if(ph==="choose") choose(Math.random()<.5);
     else if(ph==="move"){ const R2=[...G.reach.values()]; const t=rnd(R2); G.cur.q=t.q;G.cur.r=t.r;G.moved=t.c; G.cur.f=faceToward(G.cur,G.oth); confirmMove(); }
     else if(ph==="cover") showPick();
     else if(ph==="rcover") G.phase="renew";
     else if(ph==="renew"){ for(const r of G.rlist) r.on=Math.random()<.6; doRenew(); }
     else if(ph==="pick"){ const L=G.opts; const att=L.filter(x=>["attack","dual","hattack","hth","fire"].includes(x.t)); const o2=att.length?rnd(att):(L.length?rnd(L):{t:"none"});
        if(o2.t==="cast"){ const sl=castList(G.cur,G.oth); if(sl.length){ const x=rnd(sl); takePick({t:"cast",sp:x.sp,n:x.n,on:x.on,objId:x.objId,form:x.form}); } else takePick({t:"none"}); }
        else if(o2.t==="disengage"||o2.t==="hesc"){ const fr=freeNeighbors(G.cur); takePick(fr.length?{t:o2.t,dest:rnd(fr)}:{t:"none"}); } else takePick(o2); }
     else if(ph==="retreat") doRetreat(rnd([...G.ropts.values()]));
     else if(ph==="advance") doAdvance(Math.random()<.5);
     else { out.errors.push("stuck "+ph); break; }
   }
   out.games++; if(G.phase==="over"){ out.over++; if(G.winners&&G.winners.length) out.wins++; else out.losses++; }
   if(G.log.some(l=>/undefined|NaN|\[object/.test(l))) out.errors.push("bad text: "+G.log.filter(l=>/undefined|NaN|\[object/.test(l))[0]);
  }catch(e){ out.errors.push(String(e.stack||e).slice(0,400)); }
 }
 out.names=[...out.names]; return out;
}'''

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(BASE + "colosseum.html"); pg.evaluate("localStorage.clear()"); pg.reload()
    ok("C1 the setup box offers the sample encounter", pg.locator("#creSel option[value=enc]").count() == 1 and "Sample room fight" in pg.locator("#creSel option[value=enc]").inner_text())
    pg.select_option("#npSel", "2"); pg.select_option("#creSel", "enc")
    ok("C2 choosing it switches to the room map (17 across, 23 deep = 391 hexes) and locks the map box", pg.evaluate("()=>P.length===391&&$('mapSel').disabled") )
    ok("C3 the room has four entrance hexes at each end, in the middle", pg.evaluate("()=>{ const e=P.filter(h=>h.e); const ys=e.map(h=>h.p[1]); const all=P.map(h=>h.p[1]), mid=(Math.min(...all)+Math.max(...all))/2; return e.length===8&&ys.filter(y=>y>mid).length===4; }"))
    ok("C4 the note names the room and the monsters", "50' × 60'" in pg.inner_text("#npNote") and "4 monsters" in pg.inner_text("#npNote"))
    pg.click("#ex0"); pg.click("#ex1")
    pg.click("#bNext")
    ok("C5 each player picks a start hex, then Start is offered", pg.locator("#bGo").count() == 1)
    pg.click("#bGo")
    ok("C6 the fight starts with 2 players and 4 monsters, all alive", pg.evaluate("()=>!!G&&G.players.length===2&&G.mobs.length===4&&G.mobs.every(m=>m.hp>0)"))
    ok("C7 the monsters are two Orcs (Orc, Orc 2), a Hobgoblin Shaman and a Kobold Archer", pg.evaluate("()=>G.mobs.map(m=>m.p.name).sort().join('|')==='Hobgoblin Shaman|Kobold Archer|Orc|Orc 2'"))
    ok("C8 the shaman is a wizard with a staff and spells; the archer carries a missile weapon; the orcs a broadsword and shield", pg.evaluate("()=>{ const s=G.mobs.find(m=>/Shaman/.test(m.p.name)), a=G.mobs.find(m=>/Archer/.test(m.p.name)), o=G.mobs.find(m=>m.p.name==='Orc'); return s.p.cls==='wizard'&&s.caster&&s.right==='staff'&&s.p.spells.includes('Magic Fist')&&W[a.right].miss&&o.right==='broad'&&o.left==='small'; }"))
    ok("C9 the monsters stand in the north half of the room, in different hexes, apart from the players", pg.evaluate("()=>{ const ys=P.map(h=>h.p[1]), mid=(Math.min(...ys)+Math.max(...ys))/2, ks=new Set(allU().map(u=>u.q+','+u.r)); return G.mobs.every(m=>pt(m.q,m.r)[1]<mid)&&ks.size===allU().length&&G.players.every(p=>pt(p.q,p.r)[1]>mid); }"))
    ok("C10 an encounter fight does not overwrite the saved choice of board", pg.evaluate("()=>(localStorage.getItem('melee-map')||'melee')!=='room'"))
    # the editor
    pg.evaluate("()=>{ $('encCard').open=true; $('setup').open=true; }")
    bad = json.loads(pg.input_value("#encJson")); bad["foes"][0]["c"] = "dragonlord"
    pg.fill("#encJson", json.dumps(bad)); pg.click("#encApply")
    ok("C11 an encounter that names an unknown creature is refused with a message", "creature id" in pg.inner_text("#encMsg") and pg.evaluate("()=>ENC.foes[0].c==='orc'"))
    good = pg.evaluate("()=>JSON.parse(JSON.stringify(ENC))"); good["name"] = "My cellar"; good["room"] = [30, 30]; good["foes"] = good["foes"][:2]
    pg.fill("#encJson", json.dumps(good)); pg.once("dialog", lambda d: d.accept()); pg.click("#encApply")
    ok("C12 a good one is saved and rebuilds the setup (smaller room, 2 monsters)", pg.evaluate("()=>ENC.name==='My cellar'&&CREK==='enc'&&CREN===2&&P.length===(Math.round(30/3)*Math.round(30/2.6))&&G===null"))
    pg.reload()
    ok("C13 after a reload the saved encounter and the choice come back", pg.evaluate("()=>ENC.name==='My cellar'&&CREK==='enc'&&P.length===120"))
    pg.evaluate("()=>{ $('encCard').open=true; $('setup').open=true; }")
    pg.once("dialog", lambda d: d.accept()); pg.click("#encReset")
    ok("C14 the sample comes back with one button", pg.evaluate("()=>ENC.name==='Sample room fight'&&P.length===391&&!localStorage.getItem('colosseum-encounter')"))
    # no encounter: the old boards are back and nothing else changed
    pg.select_option("#creSel", "wolf")
    ok("C15 choosing a beast again returns to the saved board (99 hexes) and unlocks the map box", pg.evaluate("()=>P.length===99&&!$('mapSel').disabled"))
    # random play
    pg.select_option("#creSel", "enc"); out = pg.evaluate(PLAY)
    print({k: v for k, v in out.items() if k != "errors"})
    ok("C16 24 random fights with 2 to 4 players all finish without errors", out["over"] == out["games"] == 24 and not out["errors"])
    ok("C17 the shaman really casts in those fights", out["casts"] > 0)
    ok("C18 the archer really shoots in those fights", out["shots"] > 0)
    ok("C19 no script errors", not errs)
    for e in out["errors"][:3]: print(e[:500])
    print(errs[:3])
print(f"{sum(c for _, c in R)}/{len(R)} passed")
