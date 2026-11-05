"""The computer's fighter never wears the creatures' hidden armor (dragon scales stop 5 with no DX penalty; this made every Gladiator far too tough).
Run: python3 tests/opponent_gear_test.py"""
from playwright.sync_api import sync_playwright
import os
JS=r'''()=>{
 const R=[]; const ok=(n,c,x)=>R.push([n,!!c,x===undefined?"":String(x)]);
 const pl=fromBuilder({name:"U",race:"human",cls:"fighter",st:12,dx:13,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"});
 G=null; slot[0]=pl; window.me=pl; me=pl;
 const rows=[]; for(let i=0;i<300;i++) rows.push(makeOpponent(25));
 ok("G1 no opponent wears hidden (creature) armor",rows.every(f=>!ARMOR[f.armor].hid),[...new Set(rows.map(f=>f.armor))]);
 ok("G2 only the six book armors appear",rows.every(f=>["none","cloth","leather","chain","halfplate","plate"].includes(f.armor)));
 ok("G3 total protection never beats armor 5 + shield 2 = 7, and the average is modest",rows.every(f=>stops(f)<=7)&&rows.reduce((t,f)=>t+stops(f),0)/rows.length<4,rows.reduce((t,f)=>t+stops(f),0)/rows.length);
 ok("G4 the opponent's ST+DX equals the player's ST+DX",rows.every(f=>f.st+f.dx===25));
 return R; }'''
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["colosseum.html","duel.html"]:
        pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..',page))); print("==",page)
        try:
            R=pg.evaluate(JS)
            for n,ok,x in R: print(('PASS ' if ok else 'FAIL ')+n+(('  ['+x+']') if (x and not ok) else ''))
            print(sum(1 for r in R if r[1]),'/',len(R),'passed')
        except Exception as e: print('ERROR',str(e)[:400])
        print(errs[:2])
