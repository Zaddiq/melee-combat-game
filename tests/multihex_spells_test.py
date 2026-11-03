"""3-Hex and 7-Hex Fire, Shadow and Wall (Spell Reference Booklet): the chosen hex plus the dragon footprint. Colosseum page. Run: python3 tests/multihex_spells_test.py"""
from playwright.sync_api import sync_playwright
import os
JS=r'''
()=>{
 const R=[]; const ok=(n,c,x)=>R.push([n,!!c,x===undefined?"":String(x)]);
 const A=P.find(h=>nbr(h,2)&&nbr(h,2).e===0&&nbr(nbr(h,2),2)&&nbr(nbr(nbr(h,2),2),2)); const B=nbr(A,2);
 const mkF=o=>fromBuilder(Object.assign({name:"x",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"none",b:"none",s1:"none",d1:"dagger",armor:"none"},o));
 const unit=(p,h,f)=>{const u=mk(h,p);u.f=f;return u;};
 let dq=[]; rollN=n=>{ if(!dq.length) throw new Error("dice"); return dq.shift(); };
 const SPL=["3-Hex Fire","3-Hex Shadow","3-Hex Wall","7-Hex Shadow","7-Hex Fire","7-Hex Wall","Fire"];
 const pair=(iq)=>{ const w=unit(mkF({name:"Wiz",cls:"wizard",st:30,dx:14,iq:iq||17,spells:SPL,silver:true}),A,0), f=unit(mkF({name:"Foe",st:12,dx:12,a:"shortsw"}),B,0);
   G={me:w,foe:f,log:[],floor:[],objs:[],phase:"x",turn:1,settled:true,players:[w,f],units:[w,f],mobs:[]}; WALLS=new Set(); me={name:"Me",rec:null,st:30,dx:14}; foe=f.p; w.f=faceToward(w,f); f.f=faceToward(f,w); return [w,f]; };
 const cost={"3-Hex Fire":2,"3-Hex Shadow":2,"3-Hex Wall":4,"7-Hex Shadow":3,"7-Hex Fire":4,"7-Hex Wall":6};
 ok("X1 the six spells cost what the booklet says",(()=>{ const [w,f]=pair(); const L=castList(w,f); return Object.keys(cost).every(k=>{ const c=L.find(x=>x.sp===k); return c&&c.cost===cost[k]&&c.hexsel; }); })());
 ok("X2 IQ gates: 3-Hex Fire needs 12, 3-Hex Wall 13, 7-Hex Shadow 15, 7-Hex Fire and Wall 16",(()=>SPIQ["3-Hex Fire"]===12&&SPIQ["3-Hex Wall"]===13&&SPIQ["7-Hex Shadow"]===15&&SPIQ["7-Hex Fire"]===16&&SPIQ["7-Hex Wall"]===16)());
 const anchor=()=>P.find(h=>dist(h,A)===3&&[0,1,2,3,4,5].some(f=>fpAt(h.q,h.r,f,7).every(c=>M.get(key(c.q,c.r)))));
 const fire=(sp,h)=>{ const [w,f]=pair(); dq=[[3,3,2]]; doCast(w,f,{t:"cast",sp,dest:{q:h.q,r:h.r}}); return [w,f]; };
 for(const [sp,n] of [["3-Hex Fire",3],["3-Hex Shadow",3],["3-Hex Wall",3],["7-Hex Shadow",7],["7-Hex Fire",7],["7-Hex Wall",7]]){
   ok("X "+sp+" lays "+n+" connected hexes starting at the chosen hex",(()=>{ const h=anchor(); const [w,f]=fire(sp,h); const t=SP[sp].obj; const os=G.objs.filter(o=>o.t===t); if(os.length!==n||!os.some(o=>o.q===h.q&&o.r===h.r)) return false;
     const seen=new Set([key(os[0].q,os[0].r)]), q=[os[0]]; while(q.length){ const c=q.pop(); for(const o of os) if(!seen.has(key(o.q,o.r))&&dist(c,o)===1){ seen.add(key(o.q,o.r)); q.push(o); } } return seen.size===n; })());
 }
 ok("X7 fire in the hexes hurts a figure standing in one (2 hits less armor)",(()=>{ const [w,f]=pair(); const h=B; dq=[[3,3,2]]; const hp0=f.hp; doCast(w,f,{t:"cast",sp:"7-Hex Fire",dest:{q:h.q,r:h.r}}); return f.hp===hp0-2; })());
 ok("X8 a wall leaves out a hex that holds a figure but still goes up",(()=>{ const [w,f]=pair(); const h=nbr(B,2); dq=[[3,3,2]]; doCast(w,f,{t:"cast",sp:"7-Hex Wall",dest:{q:h.q,r:h.r}}); const ws=G.objs.filter(o=>o.t==="wall"); return ws.length>=1&&!ws.some(o=>same(o,B))&&!ws.some(o=>same(o,A)); })());
 ok("X9 walls block lines (WALLS updated)",(()=>{ const h=anchor(); fire("3-Hex Wall",h); return WALLS.has(key(h.q,h.r)); })());
 ok("X10 the cost is paid",(()=>{ const [w,f]=pair(); dq=[[3,3,2]]; doCast(w,f,{t:"cast",sp:"7-Hex Shadow",dest:{q:anchor().q,r:anchor().r}}); return w.hp===27; })());
 ok("X11 7-Hex Fire is never laid in the wizard's own hex",(()=>{ const [w,f]=pair(); const h=nbr(A,0)||nbr(A,1); dq=[[3,3,2]]; doCast(w,f,{t:"cast",sp:"7-Hex Fire",dest:{q:h.q,r:h.r}}); return !G.objs.some(o=>o.t==="fire"&&same(o,A)); })());
 return R;
}'''
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["colosseum.html","wizard-arena.html","duel.html"]:
        pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..',page)))
        print("==",page)
        try:
            R=pg.evaluate(JS)
            for n,ok,x in R: print(('PASS ' if ok else 'FAIL ')+n+(('  ['+x+']') if (x and not ok) else ''))
            print(sum(1 for r in R if r[1]),'/',len(R),'passed')
        except Exception as e: print('ERROR',str(e)[:600])
        print(errs[:3])
