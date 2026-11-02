"""Megahex Sleep in the two multi-figure pages (colosseum.html, duel.html). Run: python3 tests/megahex_sleep_multi_test.py (needs Playwright)."""
import os
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = []
def ok(n, c): R.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
JS = r'''(page)=>{
 const out=[]; const t=(n,c)=>out.push([n,!!c]);
 const W=n=>fromBuilder({name:n,race:"human",cls:"wizard",st:14,dx:13,iq:16,a:"none",b:"none",armor:"none",d1:"dagger",silver:true,spells:["Megahex Sleep","Sleep"]});
 const F=(n,st)=>fromBuilder({name:n,race:"human",cls:"fighter",st,dx:12,iq:8,a:"shortsw",b:"none",armor:"none",d1:"dagger"});
 if(page==="colosseum"){ G=null; NP=3; MODE="ffa"; applyMode(); starts.fill(null); slot[0]=W("Wiz"); slot[1]=F("Pal",12); slot[2]=F("Big",22); startFight(); }
 else { G=null; slot0=null; }
 return out;
}'''
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + ROOT + "/colosseum.html")
    pg.evaluate(JS, "colosseum")
    r = pg.evaluate(r'''()=>{
      const [w,a,b]=G.players, free=h=>!allU().some(x=>same(x,h));
      const c0=P.find(h=>free(h)&&nbr(h,0)&&free(nbr(h,0))&&nbr(h,1)&&free(nbr(h,1))&&dist(h,w)>=2&&dist(h,w)<=4);
      a.q=c0.q;a.r=c0.r; const n1=nbr(c0,0); b.q=n1.q;b.r=n1.r; w.hp=14; w.f=faceToward(w,a);
      const L=castList(w,a).filter(x=>x.sp==="Megahex Sleep");
      const mh=L.find(x=>x.on==="mh");
      const pick=()=>{ const rq=[[3,3,2]]; const o=rollN; rollN=n=>rq.shift()||o(n); };
      const was=rollN; pick(); doCast(w,a,{t:"cast",sp:"Megahex Sleep",on:"mh",dest:{q:c0.q,r:c0.r}}); rollN=was;
      return {n:L.length,mh:!!mh,hex:mh&&mh.hexsel,a:a.sleep,b:!!b.sleep,w:!!w.sleep,hp:w.hp,dest:G.destX===undefined};
    }''')
    ok("C1 colosseum offers single and megahex modes", r["n"] == 2 and r["mh"] and r["hex"] == "mslp")
    ok("C2 colosseum: the small one sleeps, the ST 22 one and the wizard do not, 8 ST paid", r["a"] and not r["b"] and not r["w"] and r["hp"] == 6)
    pg.goto("file://" + ROOT + "/duel.html")
    ok("C3 duel.html loads with the spell and no errors", pg.evaluate("()=>SP['Megahex Sleep']&&SP['Megahex Sleep'].cost()===8&&SPIQ['Megahex Sleep']===16") and not errs)
    if errs: print(errs)
    br.close()
bad = [n for n, c in R if not c]; print(f"{len(R)-len(bad)}/{len(R)} passed"); raise SystemExit(1 if bad else 0)
