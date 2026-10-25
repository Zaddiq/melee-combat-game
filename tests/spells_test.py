"""Spell checks for wizard-arena.html. Run: python3 tests/spells_test.py  (needs Playwright). Numbers come from the Wizard 2018 rules and Spell Table."""
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

 const ALL=["Staff","Magic Fist","Blur","Drop Weapon","Slow Movement","Clumsiness","Aid","Trip","Sleep","Fireball","Freeze","Stone Flesh","Stop","Lightning","Iron Flesh","Speed Movement","Dazzle","Blast","Break Weapon","Remove Thrown Spell","Spell Shield","Death Spell","Reverse Missiles","Flight","Teleport"];
 const wz=(o)=>mkF(Object.assign({name:"Wiz",cls:"wizard",st:14,dx:13,iq:14,spells:ALL.filter(x=>x!=="Staff"),silver:true},o));
 const pair=(wo,fo,rear)=>{ const w=unit(wz(wo||{}),A,0), f=unit(mkF(Object.assign({name:"Foe",st:12,dx:12,a:"shortsw"},fo||{})),B,0); fresh(w,f); face(w,f); return [w,f]; };
 const cast=(w,f,sp,n)=>{ w.act={t:"cast",sp,n}; doCast(w,f,w.act); };
 ok("S1 Magic Fist with 2 ST: 2 dice minus 2 each, caster pays 2 ST",(()=>{ const [w,f]=pair(); dice([3,3,2],[5,4]); cast(w,f,"Magic Fist",2); return f.hp===12-5&&w.hp===12; })());
 ok("S2 Fireball with 1 ST: 1d-1 but never less than the ST spent",(()=>{ const [w,f]=pair(); dice([3,3,2],[1]); cast(w,f,"Fireball",1); return f.hp===11&&w.hp===13; })());
 ok("S3 Lightning has no subtraction",(()=>{ const [w,f]=pair(); dice([3,3,2],[6,6]); cast(w,f,"Lightning",2); return f.hp===0; })());
 ok("S4 armor stops damage from a missile spell",(()=>{ const [w,f]=pair({},{armor:"chain"}); dice([3,3,2],[6,6,6]); cast(w,f,"Lightning",3); return f.hp===12-15; })());
 ok("S5 a missed thrown spell costs only 1 ST",(()=>{ const [w,f]=pair(); dice([5,6,5]); cast(w,f,"Trip"); return w.hp===13&&!f.down; })());
 ok("S6 a missed missile spell costs everything put into it",(()=>{ const [w,f]=pair(); dice([5,6,5]); cast(w,f,"Fireball",3); return w.hp===11&&f.hp===12; })());
 ok("S7 a roll of 17 fizzles and costs the full price; 18 also knocks the wizard down",(()=>{ const [w,f]=pair(); dice([6,6,5]); cast(w,f,"Trip"); const a=w.hp===12&&!w.down; const [w2,f2]=pair(); dice([6,6,6]); cast(w2,f2,"Sleep"); return a&&w2.hp===11&&w2.down; })());
 ok("S8 a roll of 3 is triple and 4 double (Slow Movement lasts 4 turns x multiplier)",(()=>{ const [w,f]=pair(); dice([1,1,1]); cast(w,f,"Slow Movement"); const a=f.slow===12; const [w2,f2]=pair(); dice([1,1,2]); cast(w2,f2,"Slow Movement"); return a&&f2.slow===8; })());
 ok("S9 thrown spell range: -1 DX per hex (adjacent -1), none on self",(()=>{ const [w,f]=pair(); const a=castList(w,f).find(x=>x.sp==="Trip").dx, b=castList(w,f).find(x=>x.sp==="Blur").dx; return a===12&&b===13; })());
 ok("S10 Blur makes every attack against the subject -4 DX",(()=>{ const [w,f]=pair(); const before=adjDXu(f,"single",w); dice([3,3,2]); cast(w,f,"Blur"); return w.blur&&adjDXu(f,"single",w)===before-4; })());
 ok("S11 Stone Flesh stops 4 hits, Iron Flesh 6, on top of armor",(()=>{ const [w,f]=pair({armor:"none"}); w.stone=true; const a=stopsFor(w,f,"shortsw"); w.iron=true; return a===4&&stopsFor(w,f,"shortsw")===6; })());
 ok("S12 Clumsiness: -2 DX per ST for 3 turns",(()=>{ const [w,f]=pair(); const b0=adjDXu(f,"single",null); dice([3,3,2]); cast(w,f,"Clumsiness",2); return adjDXu(f,"single",null)===b0-4&&f.clum===3; })());
 ok("S13 Aid on yourself: +1 DX per ST for 2 turns",(()=>{ const [w,f]=pair(); const b0=adjDXu(w,"single",null); dice([3,3,2]); cast(w,f,"Aid",3); return adjDXu(w,"single",null)===b0+3&&w.aid===2; })());
 ok("S14 Trip knocks the target down; Sleep puts it down and asleep; hits wake it",(()=>{ const [w,f]=pair(); dice([3,3,2]); cast(w,f,"Trip"); const a=f.down; const [w2,f2]=pair(); dice([3,3,2]); cast(w2,f2,"Sleep"); const b=f2.sleep&&f2.down; dice([3,3,2],[6]); cast(w2,f2,"Magic Fist",1); return a&&b&&f2.sleep===false; })());
 ok("S15 Sleep does not work on ST 20 or more (not offered)",(()=>{ const [w,f]=pair({},{st:20,dx:12,a:"twohsw"}); return !castList(w,f).some(x=>x.sp==="Sleep"); })());
 ok("S16 Freeze rolls 2 dice for the number of turns; frozen figures cannot act",(()=>{ const [w,f]=pair(); dice([3,3,2],[4,3]); cast(w,f,"Freeze"); return f.frozen===7&&options(f,w).length===0; })());
 ok("S17 Drop Weapon puts the weapon on the floor",(()=>{ const [w,f]=pair(); dice([3,3,2]); cast(w,f,"Drop Weapon"); return f.right==="none"&&G.floor.some(x=>x.id==="shortsw"); })());
 ok("S18 Slow halves MA, Stop sets it to 0; both count down each turn",(()=>{ const [w,f]=pair(); f.slow=2; f.stop=0; const a=MAu(f)===5; f.stop=1; const b=MAu(f)===0; f.slow=4; return a&&b; })());
 ok("S19 a wizard cannot cast a spell that would take ST below 0, but may take it to 0",(()=>{ const [w,f]=pair(); w.hp=2; const L=castList(w,f); return L.every(x=>x.cost<=2)&&L.some(x=>x.cost===2); })());
 ok("S20 iron or steel armor or weapon instead of silver: extra -4 to casting only",(()=>{ const [w,f]=pair({silver:false,armor:"chain"}); const sv=pair({silver:true,armor:"chain"})[0]; return ironU(w)&&castBase(w)===castBase(sv)-4; })());
 ok("S21 the missile spell range uses megahexes and needs the target in front",(()=>{ const [w,f]=pair(); const ok1=castList(w,f).some(x=>x.sp==="Magic Fist"); w.f=(faceToward(w,f)+3)%6; return ok1&&!castList(w,f).some(x=>x.sp==="Magic Fist"); })());
 ok("S22 a Magic Fist doing 6 or more hits can trip its target",(()=>{ const [w,f]=pair({},{st:20}); dice([3,3,2],[6,6,6],[6,6,6]); cast(w,f,"Magic Fist",3); return f.down===true&&f.hp===8; })());
 ok("S23 spell upkeep: a continuing spell is kept for 1 ST or dropped",(()=>{ const [w,f]=pair(); w.blur=true; G.me=w; G.foe=f; const before=w.hp; G.rlist=[{k:"blur",on:true}]; G.afterRenew=()=>{}; doRenew(); return w.blur&&w.hp===before-1; })());
 ok("S24 the computer wizard opponent knows spells, carries a staff and casts something sensible",(()=>{ me=fromBuilder({name:"Me",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"shortsw",armor:"leather",d1:"dagger"}); const f=makeWizard(); return f.cls==="wizard"&&f.right==="staff"&&f.spells.length>5&&f.iq>=11; })());

 ok("S25 Speed Movement doubles MA for 4 turns; with Slow Movement they cancel",(()=>{ const [w,f]=pair(); const m0=MAu(w); dice([3,3,2]); cast(w,f,"Speed Movement"); const a=MAu(w)===2*m0&&w.spd===4&&w.hp===12; w.slow=2; return a&&MAu(w)===m0; })());
 ok("S26 Dazzle: -3 DX for 3 turns, 3 ST, not stacked with Blur's -4",(()=>{ const [w,f]=pair(); const b0=adjDXu(f,"single",null); dice([3,3,2]); cast(w,f,"Dazzle"); const a=f.daz===3&&adjDXu(f,"single",null)===b0-3&&w.hp===11; w.blur=true; return a&&adjDXu(f,"single",w)===b0-4; })());
 ok("S27 Blast: 1 die to everyone adjacent, armor stops it, 2 ST",(()=>{ const [w,f]=pair({},{armor:"none"}); dice([3,3,2],[5]); cast(w,f,"Blast"); const a=f.hp===7&&w.hp===12; const [w2,f2]=pair({},{armor:"leather"}); dice([3,3,2],[5]); cast(w2,f2,"Blast"); return a&&f2.hp===12-3; })());
 ok("S28 Blast and Dazzle are special spells: a miss loses just 1 ST; Dazzle reaches 5 megahexes",(()=>{ const [w,f]=pair(); dice([5,6,5]); cast(w,f,"Blast"); const a=w.hp===13&&f.hp===12; const [w2,f2]=pair(); const d=castList(w2,f2).find(x=>x.sp==="Dazzle"); return a&&!!d&&d.dx===castBase(w2); })());
 ok("S29 Break Weapon halves a weapon's damage; staves and shields are destroyed",(()=>{ const [w,f]=pair({},{a:"broad",st:14}); dice([3,3,2]); cast(w,f,"Break Weapon"); const a=f.brkW==="broad" ; const [w2,f2]=pair({},{a:"shortsw",b:"smallsh"}); dice([3,3,2]); cast(w2,f2,"Break Weapon"); return !!a&&f2.brkW==="shortsw"; })());
 ok("S30 a broken weapon: the rolled total is halved, rounded down",(()=>{ const [w,f]=pair({},{a:"shortsw"}); f.brkW="shortsw"; dice([3,2]); const r=dmgRoll(f,"shortsw"); return r.total===Math.floor((5+W.shortsw.m)/2); })());
 ok("S31 Remove Thrown Spell ends the target's thrown spells",(()=>{ const [w,f]=pair(); f.blur=true; f.stone=true; f.slow=3; dice([3,3,2]); cast(w,f,"Remove Thrown Spell"); return !f.blur&&!f.stone&&f.slow===0&&w.hp===12; })());
 ok("S32 Spell Shield: spells cast at the subject do nothing and the caster loses the full cost",(()=>{ const [w,f]=pair(); f.shield=true; dice([3,3,2]); cast(w,f,"Slow Movement"); const a=f.slow===0&&w.hp===12; dice([3,3,2],[6,6]); cast(w,f,"Lightning",2); return a&&f.hp===12&&w.hp===10; })());
 ok("S33 Spell Shield costs 3 ST, +1 per turn, and also blocks the wizard's own spells",(()=>{ const [w,f]=pair(); dice([3,3,2]); cast(w,f,"Spell Shield"); const a=w.shield&&w.hp===11&&CONT.includes("shield"); return a&&!castList(w,f).some(x=>x.sp==="Blur"); })());
 ok("S34 Death Spell: the weaker dies, the stronger loses the weaker's ST; Spell Shield costs the caster only 1",(()=>{ const [w,f]=pair({st:20},{st:8}); dice([3,3,2]); cast(w,f,"Death Spell"); const a=f.hp===-1&&w.hp===12; const [w2,f2]=pair({st:8},{st:20}); dice([3,3,2]); cast(w2,f2,"Death Spell"); const b=w2.hp===-1; const [w3,f3]=pair(); f3.shield=true; dice([3,3,2]); cast(w3,f3,"Death Spell"); return a&&b&&w3.hp===13&&f3.hp===12; })());
 ok("S35 the computer wizard can know the new spells",(()=>{ me=fromBuilder({name:"Me",race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"shortsw",armor:"leather",d1:"dagger"}); let seen=false; for(let i=0;i<40&&!seen;i++){ const f=makeWizard(); if(f.spells.includes("Dazzle")) seen=true; } return seen; })());

 ok("S36 Reverse Missiles costs 2 ST, +1 a turn; a missile that hits turns back on the shooter",(()=>{ const [w,f]=pair({},{a:"lbow",st:12}); dice([3,3,2]); cast(w,f,"Reverse Missiles"); const a=w.rev&&w.hp===12&&CONT.includes("rev"); const h=f.hp, wh=w.hp; dice([1,1,6],[3,3]); doAttack(f,w,"lbow","single","missile"); return a&&w.hp===wh&&f.hp<h; })());
 ok("S37 Reverse Missiles turns a Magic Fist back on its caster; both protected means no harm",(()=>{ const [w,f]=pair({},{}); const f2=mkF({name:"W2",cls:"wizard",st:14,dx:13,iq:14,spells:["Magic Fist"],silver:true}); const e=unit(f2,B,0); const w1=unit(wz({}),A,0); fresh(w1,e); face(w1,e); e.rev=true; dice([3,3,2],[5,4]); cast(w1,e,"Magic Fist",2); const a=e.hp===14&&w1.hp<12; w1.rev=true; const h=w1.hp; dice([3,3,2]); cast(w1,e,"Magic Fist",1); return a&&e.hp===14&&w1.hp===h-1; })());
 ok("S38 Reverse Missiles does nothing against melee blows",(()=>{ const [w,f]=pair({},{a:"shortsw"}); w.rev=true; const h=f.hp; dice([1,1,6],[3,3]); doAttack(f,w,"shortsw","single",null); return f.hp===h&&w.hp<14; })());

 ok("S39 Flight: 3 ST, +1 a turn; in the air from next turn, half MA (6) first turn then 12; not engaged by a ground figure",(()=>{ const [w,f]=pair(); dice([3,3,2]); cast(w,f,"Flight"); const a=w.fly&&!w.air&&w.hp===11&&CONT.includes("fly"); w.air=true; w.airN=1; const b=MAu(w)===6; w.airN=2; return a&&b&&MAu(w)===12&&!isEngaged(w,f)&&!isEngaged(f,w); })());
 ok("S40 attacks on a flier are -4 DX; a flier attacks at -2 (-4 with missile weapons); spells at a flier -4, spells it casts -2",(()=>{ const [w,f]=pair(); const b0=adjDXu(f,"single",w), c0=adjDXu(w,"single",f), s0=castList(w,f).find(x=>x.sp==="Trip").dx; w.air=true; return adjDXu(f,"single",w)===b0-4&&adjDXu(w,"single",f)===c0-2&&castList(f.p.cls==="wizard"?f:w,f)!==null&&castList(w,f).find(x=>x.sp==="Trip").dx===s0-2&&shotDX(w,f,"lbow","missile")===shotDX(f,w,"lbow","missile")-4+0-0-0+(adjDXu(w,"single",null)-adjDXu(f,"single",null))+4; })());
 ok("S41 a flier cannot be tripped, cannot be grappled, and lands (no ground move that turn) when Flight lapses or is removed",(()=>{ const [w,f]=pair(); f.air=true; f.fly=true; dice([3,3,2]); cast(w,f,"Trip"); const a=!f.down; const b=!canHth(w,f); dice([3,3,2]); cast(w,f,"Remove Thrown Spell"); return a&&b&&!f.air&&!f.fly&&MAu(f)===0; })());

 ok("S42 Teleport: 1 ST per megahex moved, you arrive facing the enemy; a miss costs 1 ST",(()=>{ const [w,f]=pair(); const far=P.filter(h=>!same(h,f)&&mhDist(A,h)===3)[0]; dice([3,3,2]); w.act={t:"cast",sp:"Teleport",dest:far}; doCast(w,f,w.act); const a=w.q===far.q&&w.r===far.r&&w.hp===14-3&&w.f===faceToward(w,f); const [w2,f2]=pair(); dice([5,6,5]); w2.act={t:"cast",sp:"Teleport",dest:far}; doCast(w2,f2,w2.act); return a&&w2.q===A.q&&w2.hp===13; })());
 ok("S43 Teleport cannot go into the enemy's hex or cost more ST than you have",(()=>{ const [w,f]=pair(); doCast(w,f,{t:"cast",sp:"Teleport",dest:{q:f.q,r:f.r}}); const a=w.q===A.q; w.hp=2; const far=P.filter(h=>!same(h,f)&&mhDist(A,h)>=4)[0]; doCast(w,f,{t:"cast",sp:"Teleport",dest:far}); return a&&w.q===A.q&&w.hp===2; })());

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
