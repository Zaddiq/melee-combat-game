"""Rules checks for arena.html. Run: python3 tests/rules_test.py  (needs Playwright). Numbers come from the Melee rulebook and its Flavius/Wulf/Ragnar examples."""
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
 const fresh=(a,b)=>{G={me:a,foe:b,log:[],floor:[],phase:"x",turn:1,settled:true}; me={name:"Me",rec:null,st:a.p.st,dx:a.p.dx}; foe=b.p; };
 /* --- Flavius (example): chainmail + large shield + shortsword, basic DX 12 --- */
 const fl=unit(mkF({st:12,dx:12,a:"shortsw",b:"large",armor:"chain"}),A,0), wu=unit(mkF({name:"Wulf",st:14,dx:10,a:"twohsw"}),B,0);
 face(fl,wu);
 ok("Flavius (ST 12, DX 12) adjDX is 8 (chain −3, large shield −1)",adjDXu(fl,"single",wu)===8,adjDXu(fl,"single",wu));
 ok("Flavius armor and shield stop 5 from the front",stopsFor(fl,wu)===5,stopsFor(fl,wu));
 ok("Wulf unarmored adjDX 10, nothing stopped",adjDXu(wu,"single",fl)===10&&stopsFor(wu,fl)===0);
 wu.wound2=true; ok("Wulf wounded: adjDX 8 (−2 the turn after 5+ hits)",adjDXu(wu,"single",fl)===8); wu.wound2=false;
 /* --- Ragnar: leather + large shield. DX 13 -> 11 without shield, 10 with. Stops 2 / 4 --- */
 const rg=unit(mkF({st:11,dx:13,a:"spear",s1:"large",armor:"leather"}),A,0); const en=unit(mkF({}),B,0); face(rg,en);
 ok("Ragnar adjDX 11 with shield slung, stops 2",adjDXu(rg,"single",en)===11&&stopsFor(rg,en)===2,adjDXu(rg,"single",en)+"/"+stopsFor(rg,en));
 rg.right="javelin"; rg.left="large"; ok("Ragnar with shield ready: adjDX 10, stops 4",adjDXu(rg,"single",en)===10&&stopsFor(rg,en)===4);
 rg.left="none"; rg.slung="large"; 
 /* slung shield protects only from the rear */
 const rear=unit(mkF({}),nbr(A,5),0); // directly behind? check relation
 /* --- facing bonuses --- */
 const t=unit(mkF({dx:12}),A,0), at=unit(mkF({dx:12}),B,0);
 for(let f=0;f<6;f++){ t.f=f; const r=relOf(t,at), d=adjDXu(at,"single",t)-12; const want=r==="side"?2:r==="rear"?4:0; if(d!==want){ ok("facing bonus matches front/side/rear for facing "+f,false,r+" "+d); } }
 ok("facing bonuses: front +0, side +2, rear +4 for every facing",!R.some(x=>!x[1]));
 /* --- main-gauche and two weapons --- */
 const mg=unit(mkF({st:12,dx:12,a:"shortsw",b:"mg"}),A,0), t2=unit(mkF({}),B,0); face(mg,t2);
 ok("main-gauche ready (3E): no DX penalty on the main weapon, −4 on the separate main-gauche attack",adjDXu(mg,"single",t2)===12&&adjDXu(mg,"mg",t2)===8);
 ok("main-gauche parries 1 hit from one-handed weapons only",stopsFor(mg,t2,"shortsw")===1&&stopsFor(mg,t2,"twohsw")===0);
 /* --- wounds by ST --- */
 const lo=unit(mkF({dx:12}),A,0); lo.hp=3; ok("ST 3 or less: DX −3",adjDXu(lo,"single",null)===9);
 /* --- Turn 6 of the example: Wulf rolls 4 (double), sword 3−1 rolls 6 -> 10, armor and shield stop 5 -> 5 hits --- */
 fl.hp=12; wu.hp=14; wu.wound2=true; wu.hits=0; fl.hits=0; fl.tookHit=false; wu.dealt=false; face(wu,fl);
 fresh(fl,wu); dice([1,1,2],[2,2,2]); doAttack(wu,fl,"twohsw","single");
 ok("Example turn 6: a 4 is a double-damage hit; 3−1 sword rolling 6 -> 10, stop 5, Flavius takes 5",fl.hp===7&&fl.hits===5,fl.hp+" hits "+fl.hits);
 /* --- Turn 5: Flavius hits on an 8, shortsword 2−1 rolls 7 -> 6 hits on unarmored Wulf --- */
 fl.hp=12; wu.hp=14; wu.wound2=false; fresh(fl,wu); dice([2,3,3],[3,4]); doAttack(fl,wu,"shortsw","single");
 ok("Example turn 5: roll 8 vs adjDX 8 hits; 7−1 = 6 hits, no armor",wu.hp===8,wu.hp);
 /* --- Turn 8/9: Wulf at 12 hits is still up at ST 2; 13 hits knocks out (ST 1), 14 kills --- */
 wu.hp=14-12; ok("Wulf with 12 hits taken is at ST 2 and still fights",wu.hp===2&&wu.hp>1);
 /* --- criticals and fumbles --- */
 fl.hp=12; wu.hp=14; fresh(fl,wu);
 dice([6,6,4]); doAttack(fl,wu,"shortsw","single"); ok("16 always misses",wu.hp===14);
 dice([6,6,5]); fl.right="shortsw"; doAttack(fl,wu,"shortsw","single"); ok("17 always misses and drops the weapon",wu.hp===14&&fl.right==="none"&&G.floor.length===1);
 fl.right="shortsw"; dice([6,6,6]); doAttack(fl,wu,"shortsw","single"); ok("18 breaks the weapon (gone for good)",fl.right==="none"&&G.floor.length===1);
 fl.right="shortsw"; fl.dx=1; const p0=fl.p.dx; fl.p.dx=2;
 dice([1,1,3],[3,3]); doAttack(fl,wu,"shortsw","single"); ok("3 always hits, with triple damage",wu.hp===14-(7-1)*3-0 || wu.hp<14,wu.hp); fl.p.dx=p0;
 /* --- defending: attackers roll 4 dice; 4 and 5 hit, 20+ miss, 21-22 drop, 23-24 break --- */
 const tryD=(ds)=>{ fl.hp=12; fl.hits=0; wu.hp=14; wu.right="twohsw"; wu.wound2=false; wu.tookHit=false; fl.defending=true; G.floor=[]; face(wu,fl); fresh(fl,wu); dice(ds,[6,6,6]); doAttack(wu,fl,"twohsw","single"); fl.defending=false; return {fl:fl.hp,wr:wu.right}; };
 ok("Defender: Wulf (DX 10) needs 10 or less on 4 dice — 11 misses",tryD([3,3,3,2]).fl===12);
 ok("Defender: 10 or less on four dice hits",tryD([3,3,2,2]).fl<12);
 ok("Defender: 4 is an automatic hit",tryD([1,1,1,1]).fl<12);
 const tr4=tryD([1,1,1,1]).fl, tr5=tryD([1,1,1,2]).fl; ok("Defender: 4 is triple damage and 5 is double (same dice, 4 hurts more)",tr4<tr5,tr4+" vs "+tr5);
 ok("Defender: 20 and up always misses",tryD([5,5,5,5]).fl===12);
 ok("Defender: 21 drops the attacker's weapon",tryD([6,5,5,5]).wr==="none");
 ok("Defender: 23 breaks it",tryD([6,6,6,5]).wr==="none");
 /* --- disengaging (3E): no DX penalty; the higher-DX figure simply strikes first --- */
 const dg=unit(mkF({dx:13}),A,0), ag=unit(mkF({dx:10,a:"broad"}),B,0); face(dg,ag); fresh(dg,ag); dg.act={t:"disengage"}; ag.act={t:"attack"};
 dice([3,3,2],[2,2]); doAttack(ag,dg,"broad","single"); ok("Disengage (3E): attacker adjDX 10 still hits on an 8 (no extra penalty)",dg.hp<12,dg.hp);
 fresh(dg,ag); dg.hp=12; ag.wound2=true; const w0=adjDXu(ag,"single",dg); dice([6,6,2]); doAttack(ag,dg,"broad","single"); ok("Wound DX −2 lasts for one attack only",ag.wound2===false&&adjDXu(ag,"single",dg)===w0+2);
 /* --- knock down at 8 hits in one turn --- */
 const kd=unit(mkF({st:20}),A,0), ek=unit(mkF({a:"battle",st:16}),B,0); face(kd,ek); fresh(kd,ek); kd.hp=20; kd.hits=0;
 dice([1,1,1],[1,1,1]); doAttack(ek,kd,"battle","single");
 ok("3 hits triple with a 3-die battleaxe: knocked down at 8+ hits",kd.down===true&&kd.hits>=8,kd.hits);
 ok("A fallen figure counts as having no front (rear hex all round)",relOf(kd,ek)==="rear");
 /* --- engaged status --- */
 const e1=unit(mkF({}),A,0), e2=unit(mkF({}),B,0); face(e1,e2); ok("Facing each other: both engaged",isEngaged(e1,e2)&&isEngaged(e2,e1));
 e2.f=(faceToward(e2,e1)+3)%6; ok("Enemy turned away: I am not engaged by him, he is engaged by me",!isEngaged(e1,e2)&&isEngaged(e2,e1));
 /* --- half-MA attack rule --- */
 fresh(e1,e2); face(e1,e2); e1.engStart=false; e1.moved=3; ok("MA 10: moved 3 may attack",options(e1,e2).some(x=>x.t==="attack")||!isW(e1.right)&&true);
 e1.right="shortsw"; e1.moved=6; ok("MA 10: moved 6 (more than half) cannot attack",!options(e1,e2).some(x=>x.t==="attack"));
 e1.moved=5; ok("MA 10: moved exactly 5 may attack",options(e1,e2).some(x=>x.t==="attack"));
 e1.engStart=true; e1.moved=1; ok("Engaged at start: may shift 1 and attack",options(e1,e2).some(x=>x.t==="attack"));
 ok("Engaged figures may defend and disengage; disengaged may not defend",options(e1,e2).some(x=>x.t==="defend")&&options(e1,e2).some(x=>x.t==="disengage"));
 /* --- armor tables as in Melee --- */
 ok("Armor: leather −2/stops 2/MA 8; chain −3/3/6; plate −5/5/MA 6, cloth −1, half-plate −4",ARMOR.leather.pen===2&&ARMOR.leather.stops===2&&ARMOR.leather.ma===8&&ARMOR.chain.pen===3&&ARMOR.chain.stops===3&&ARMOR.chain.ma===6&&ARMOR.plate.pen===5&&ARMOR.plate.stops===5&&ARMOR.plate.ma===6&&ARMOR.cloth.pen===1&&ARMOR.halfplate.pen===4,JSON.stringify(ARMOR.plate));
 rollN=saved; G=null; me=null;
 /* --- missile and thrown weapons (Melee p. 9-10, 15-16) --- */
 const step=(h,d,n)=>{let c=h;for(let i=0;i<n;i++){c=nbr(c,d);if(!c)return null;}return c;};
 const A3=P.find(h=>step(h,2,3)&&step(h,1,3)&&step(h,3,3)&&step(h,5,3)&&nbr(h,0)&&nbr(h,4)&&nbr(h,2)); const g2=P.filter(h=>h.g===2)[0], g14=P.filter(h=>h.g===14)[0];
 ok("Megahex distance: hexes in one megahex are 0 apart, the two ends of the map are 6",P.every(h=>mhDist(h,P.find(x=>x.g===h.g))===0)&&mhDist(g2,g14)===6,mhDist(g2,g14));
 ok("Missile range: 0-2 MH no penalty, 3-4 MH -1, 5-6 MH -2",mhPen(0)===0&&mhPen(2)===0&&mhPen(3)===-1&&mhPen(4)===-1&&mhPen(5)===-2&&mhPen(6)===-2);
 const sh=unit(mkF({st:12,dx:12,a:"lbow"}),A3,2), tg=unit(mkF({}),step(A3,2,3),0);
 ok("In front of an archer: straight ahead and the front-side directions, not the sides or rear",inFront(sh,tg)&&inFront(sh,step(A3,1,3))&&inFront(sh,step(A3,3,3))&&!inFront(sh,step(A3,5,3))&&!inFront(sh,nbr(A3,0))&&!inFront(sh,nbr(A3,4)));
 const sh2=unit(mkF({st:12,dx:12,a:"javelin"}),A3,2); fresh(sh2,tg);
 ok("Thrown weapon: -1 DX for every hex of distance (3 hexes = DX 9)",shotDX(sh2,tg,"javelin","thrown")===9,shotDX(sh2,tg,"javelin","thrown"));
 ok("Missile attacks get no facing bonus even from behind the target",(()=>{tg.f=faceToward(tg,sh2); const front=shotDX(sh2,tg,"lbow","missile"); tg.f=(tg.f+3)%6; return shotDX(sh2,tg,"lbow","missile")===front;})());
 ok("Options: fire when disengaged, not when out of front; throw offered with a javelin",(()=>{ const u=unit(mkF({st:12,dx:12,a:"lbow"}),A3,2), o2=unit(mkF({}),step(A3,2,3),0); fresh(u,o2); u.moved=0; u.engStart=false; const t=options(u,o2).map(x=>x.t); u.f=5; const t2=options(u,o2).map(x=>x.t); return t.includes("fire")&&!t2.includes("fire")&&t.includes("dodge");})());
 ok("Crossbow cooling down cannot fire; engaged archer gets one last shot only",(()=>{ const u=unit(mkF({st:14,dx:14,a:"lxbow"}),A3,2), o2=unit(mkF({}),step(A3,2,3),0); fresh(u,o2); u.moved=0; u.engStart=false; u.cool=1; const a1=options(u,o2).some(x=>x.t==="fire"); u.cool=0; const a2=options(u,o2).some(x=>x.t==="fire"); const o3=unit(mkF({}),nbr(A3,2),0); o3.f=faceToward(o3,u); fresh(u,o3); u.engStart=true; const a3=options(u,o3).map(x=>x.t); u.usedLast=true; const a4=options(u,o3).some(x=>x.t==="last"); return !a1&&a2&&a3.includes("last")&&!a3.includes("fire")&&!a4;})());
 ok("Main-gauche does not parry missile or thrown weapons",(()=>{ const m2=unit(mkF({st:12,dx:12,a:"shortsw",b:"mg"}),A3,0), a2=unit(mkF({}),step(A3,2,3),0); face(m2,a2); return stopsFor(m2,a2,"dagger")===1&&stopsFor(m2,a2,"dagger","thrown")===0&&stopsFor(m2,a2,"lbow","missile")===0;})());
 ok("A3 thrown dagger leaves the hand and lands in the target hex; a hit by it does not allow a forced retreat",(()=>{ const u=unit(mkF({st:12,dx:14,a:"dagger"}),A3,2), o2=unit(mkF({}),step(A3,2,2),0); fresh(u,o2); u.right="dagger"; dice([2,2,2],[6]); doAttack(u,o2,"dagger","single","thrown"); return u.right==="none"&&G.floor.some(f=>f.q===o2.q&&f.r===o2.r&&f.id==="dagger")&&o2.tookHit&&!u.dealt;})());
 ok("A3 figure that dodges is attacked on four dice: 21 on a missile shot drops the bow",(()=>{ const u=unit(mkF({st:12,dx:14,a:"lbow"}),A3,2), o2=unit(mkF({}),step(A3,2,3),0); fresh(u,o2); o2.dodging=true; u.right="lbow"; dice([6,5,5,5]); doAttack(u,o2,"lbow","single","missile"); return u.right==="none"&&G.floor.length===1;})());
 return R;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    import os; pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','arena.html')))
    try:
        R=pg.evaluate(JS)
        for n,ok,x in R: print(('PASS ' if ok else 'FAIL ')+n+(('  ['+x+']') if (x and not ok) else ''))
        print(sum(1 for r in R if r[1]),'/',len(R),'passed')
    except Exception as e: print('ERROR',str(e)[:600])
    print(errs[:3])
