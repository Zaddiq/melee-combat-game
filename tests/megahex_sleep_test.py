"""Megahex Sleep (Spell Reference Booklet: IQ 16, 8 ST, every figure under ST 20 except the wizard in one megahex, or one figure of ST 50 or less). Run: python3 tests/megahex_sleep_test.py  (needs Playwright). Numbers come from the Wizard 2018 rules and Spell Table."""
from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const R=[]; const ok=(n,c,extra)=>R.push([n,!!c,extra===undefined?"":String(extra)]);
 const A=P.find(h=>nbr(h,2)&&nbr(h,2).e===0&&nbr(nbr(h,2),2)); // a hex with open space around
 const mkF=o=>fromBuilder(Object.assign({name:"x",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"none",b:"none",s1:"none",d1:"dagger",armor:"none"},o));
 const unit=(p,h,f)=>{const u=mk(h,p);u.f=f;return u;};
 /* put two figures face to face: a at A, b one hex to its direction 2 */
 const B=nbr(A,2);
 const face=(a,b)=>{a.f=faceToward(a,b);b.f=faceToward(b,a);};
 let saved=rollN; const dice=(...q)=>{rollN=n=>{ if(!q.length) throw new Error("dice queue empty"); return q.shift(); };};
 const fresh=(a,b)=>{G={me:a,foe:b,log:[],floor:[],objs:[],phase:"x",turn:1,settled:true}; WALLS=new Set(); me={name:"Me",rec:null,st:a.p.st,dx:a.p.dx}; foe=b.p; };

 const ALL=["Staff","Magic Fist","Blur","Drop Weapon","Slow Movement","Clumsiness","Aid","Trip","Sleep","Fireball","Freeze","Stone Flesh","Stop","Lightning","Iron Flesh","Speed Movement","Dazzle","Blast","Break Weapon","Remove Thrown Spell","Spell Shield","Death Spell","Reverse Missiles","Flight","Teleport","Fire","Shadow","Create Wall","Rope","Destroy Creation","Summon Wolf","Summon Myrmidon","Summon Bear","Summon Gargoyle","Summon Giant","Image","Illusion","Dispel Illusions","Confusion","Shock Shield","Avert","Control Person","Control Animal","Invisibility","Mage Sight","Slippery Floor","Giant Rope","Reveal Magic","Megahex Sleep"];
 const wz=(o)=>mkF(Object.assign({name:"Wiz",cls:"wizard",st:14,dx:13,iq:14,spells:ALL.filter(x=>x!=="Staff"),silver:true},o));
 const pair=(wo,fo,rear)=>{ const w=unit(wz(wo||{}),A,0), f=unit(mkF(Object.assign({name:"Foe",st:12,dx:12,a:"shortsw"},fo||{})),B,0); fresh(w,f); face(w,f); return [w,f]; };
 const cast=(w,f,sp,n)=>{ w.act={t:"cast",sp,n}; doCast(w,f,w.act); };
 ok("H1 single target: offered at 8 ST for ST 30 and sleeps on a hit",(()=>{ const [w,f]=pair({},{st:30,dx:12,a:"twohsw"}); const c=castList(w,f).find(x=>x.sp==="Megahex Sleep"&&x.on==="one"); if(!c||c.cost!==8) return false; dice([3,3,2]); doCast(w,f,{t:"cast",sp:"Megahex Sleep",on:"one"}); return f.sleep&&f.down&&w.hp===14-8; })());
 ok("H2 single target is not offered above ST 50",(()=>{ const [w,f]=pair({},{st:51,dx:12,a:"twohsw"}); return !castList(w,f).some(x=>x.sp==="Megahex Sleep"&&x.on==="one"); })());
 ok("H3 not offered at all with less than 8 ST",(()=>{ const [w,f]=pair(); w.hp=7; return !castList(w,f).some(x=>x.sp==="Megahex Sleep"); })());
 const crowd=()=>{ const [w,f]=pair(); const ns=[0,1,2,3,4,5].map(d=>nbr(B,d)).filter(h=>h&&!same(h,A)); const x=unit(mkF({name:"Pal",st:12,dx:12,a:"shortsw"}),ns[0],0), y=unit(mkF({name:"Big",st:22,dx:12,a:"twohsw"}),ns[1],0), zh=P.find(h=>dist(h,B)===3&&dist(h,A)>=3&&!same(h,ns[0])&&!same(h,ns[1])), z=unit(mkF({name:"Far",st:12,dx:12,a:"shortsw"}),zh,0); G.units=[w,f,x,y,z]; return [w,f,x,y,z]; };
 ok("H4 megahex mode is offered with a centre to pick, DX minus the distance to it",(()=>{ const [w,f]=crowd(); const c=castList(w,f).find(x=>x.sp==="Megahex Sleep"&&x.on==="mh"); return c&&c.hexsel==="mslp"&&c.cost===8&&creaHexes(w,f,"mslp").some(h=>same(h,f)); })());
 ok("H5 every figure under ST 20 in the centre hex or next to it falls asleep, friends too; ST 22 and far figures do not; the wizard does not",(()=>{ const [w,f,x,y,z]=crowd(); w.hp=14; dice([3,3,2]); doCast(w,f,{t:"cast",sp:"Megahex Sleep",on:"mh",dest:{q:B.q,r:B.r}}); return f.sleep&&f.down&&x.sleep&&!y.sleep&&!z.sleep&&!w.sleep&&w.hp===6; })());
 ok("H6 the DX roll counts the hexes to the centre (a roll that fits ST-only fails when the centre is far)",(()=>{ const [w,f]=crowd(); const c=castList(w,f).find(q=>q.sp==="Megahex Sleep"&&q.on==="mh"); const need=c.dx-dist(w,f); dice([6,6,3]); doCast(w,f,{t:"cast",sp:"Megahex Sleep",on:"mh",dest:{q:B.q,r:B.r}}); return !f.sleep&&need<15&&w.hp===13; })());
 ok("H7 a Spell Shield keeps one figure out of it",(()=>{ const [w,f,x]=crowd(); x.shield=true; dice([3,3,2]); doCast(w,f,{t:"cast",sp:"Megahex Sleep",on:"mh",dest:{q:B.q,r:B.r}}); return f.sleep&&!x.sleep; })());
 ok("H8 a centre with nobody eligible is not offered",(()=>{ const [w,f]=pair({},{st:25,dx:12,a:"twohsw"}); return !castList(w,f).some(x=>x.sp==="Megahex Sleep"&&x.on==="mh"); })());
 ok("H9 a sleeper is hit awake and a second megahex cast skips those already asleep",(()=>{ const [w,f,x]=crowd(); dice([3,3,2]); doCast(w,f,{t:"cast",sp:"Megahex Sleep",on:"mh",dest:{q:B.q,r:B.r}}); return mslpHit(w,B).length===0; })());
 return R;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    import os; pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','wizard-arena.html')))
    try:
        R=pg.evaluate(JS)
        for n,ok,x in R: print(('PASS ' if ok else 'FAIL ')+n+(('  ['+x+']') if (x and not ok) else ''))
        print(sum(1 for r in R if r[1]),'/',len(R),'passed')
    except Exception as e: print('ERROR',str(e)[:600])
    print(errs[:3])
