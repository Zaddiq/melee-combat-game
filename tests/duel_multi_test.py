"""Three- and four-player checks for duel.html. Run: python3 tests/duel_multi_test.py  (needs Playwright)."""
from playwright.sync_api import sync_playwright
JS=r'''
()=>{
 const R=[]; const ok=(n,c)=>R.push([n,!!c]);
 const mkf=(n,o)=>fromBuilder(Object.assign({name:n,race:"human",cls:"fighter",st:12,dx:12,iq:8,a:"broad",b:"small",armor:"leather",d1:"dagger"},o||{}));
 const begin=(n,tm,o)=>{ G=null; NP=n; for(let i=0;i<4;i++) team[i]=tm?tm[i]:i; starts.fill(null); for(let i=0;i<4;i++) slot[i]=i<n?mkf("P"+(i+1),o&&o[i]):null; startFight(); };
 const lo=n=>Array.from({length:n},()=>1);
 const pass=()=>{ let g=0; while(G.phase!=="over"&&g++<50){ if(G.phase==="choose") choose(true); else if(G.phase==="rcover"){ G.phase="renew"; } else if(G.phase==="renew") doRenew(); else if(G.phase==="move") confirmMove(); else if(G.phase==="cover") showPick(); else break; } };
 begin(3);
 ok("M1 three players: three figures, each on its own side, all on the map",G.players.length===3&&new Set(G.players.map(sideOf)).size===3&&allU().length===3&&new Set(G.players.map(u=>u.q+","+u.r)).size===3);
 ok("M2 every player is an enemy of the other two",G.players.every(u=>enemiesOf(u).length===2));
 ok("M3 initiative rolls for all three with no ties and the winner chooses",G.rolls.length===3&&new Set(G.rolls.map(x=>x.r)).size===3&&G.players[G.chooser]===G.rolls[0].u);
 choose(true);
 ok("M4 moving first puts the roll winner first and everyone moves once",G.order.length===3&&G.order[0]===G.chooser&&new Set(G.order).size===3);
 pass();
 ok("M5 after the moves every player picks in secret, one after another, and the screen is passed three times",G.phase==="pick"&&G.pq.length===3&&G.pi===0);
 let seen=[]; { let g=0; while(G.phase==="pick"&&g++<6){ seen.push(G.cur.p.name); takePick({t:"none"}); if(G.phase==="cover") showPick(); } }
 ok("M6 each of the three picked once, then the turn resolved and a new turn began",seen.length===3&&new Set(seen).size===3&&G.turn===2);
 begin(4,[0,1,0,1]);
 ok("M7 four players in two teams: allies are not enemies and start at the same end",enemiesOf(G.players[0]).length===2&&!enemiesOf(G.players[0]).includes(G.players[2])&&sideOf(G.players[0])===sideOf(G.players[2])&&sideOf(G.players[1])===sideOf(G.players[3]));
 ok("M8 two teams start at opposite ends and teammates start on different hexes",G.players[0].r!==G.players[1].r&&(G.players[0].q!==G.players[2].q||G.players[0].r!==G.players[2].r));
 ok("M9 the fight goes on while one member of a team is still up",(()=>{ G.players[0].hp=0; G.players[1].hp=0; endCheck(); return G.phase!=="over"&&G.players[0].out&&G.players[1].out; })());
 ok("M10 it ends when the last member of a team goes down, and the survivors on the other team win together",(()=>{ G.players[3].hp=-1; endCheck(); return G.phase==="over"&&G.winners.length===1&&G.winners[0]===G.players[2]; })());
 ok("M11 XP is paid to all four: winner 30, everyone who went down 20",G.xp.length===4&&/\+30 XP/.test(G.xp[2])&&/\+20 XP/.test(G.xp[0])&&/\+20 XP/.test(G.xp[1])&&/\+20 XP/.test(G.xp[3]));
 begin(3);
 ok("M12 free for all: one player down does not end it, and the downed player is skipped in the move order",(()=>{ G.players[1].hp=0; endCheck(); const a=G.phase!=="over"; G.phase="choose"; nextTurn(); return a&&G.rolls.length===2; })());
 ok("M13 the last one standing wins",(()=>{ G.players[2].hp=-2; endCheck(); return G.phase==="over"&&G.winner===G.players[0]&&G.winners.length===1; })());
 begin(3);
 ok("M14 a player who escapes unhurt loses 10 XP; the others fight on and nobody else is cheated",(()=>{ const u=G.players[0]; G.phase="move"; G.cur=u; quitDuel(u,"escape"); const a=G.phase!=="over"&&u.esc&&!allU().includes(u); G.players[1].hp=0; endCheck(); return a&&G.phase==="over"&&G.winner===G.players[2]&&/-10 XP/.test(G.xp[0])&&/\+30 XP/.test(G.xp[2]); })());
 begin(3);
 ok("M15 when only two sides are left and one quits, the duel ends at once",(()=>{ G.players[1].hp=0; endCheck(); quitDuel(G.players[0],"escape"); return G.phase==="over"&&G.winner===G.players[2]; })());
 begin(3,null,[{a:"none",spells:["Staff","Summon Wolf"],cls:"wizard",iq:15,st:15},{},{}]);
 pass(); choose;
 const W0=G.players[0];
 ok("M16 a wolf belongs to its summoner: its owner is the player, and it is an enemy of both other players",(()=>{ const h=creaHexes(W0,other(W0),"summon")[0]; const sv=rollN; rollN=lo; W0.hp=15; doCast(W0,other(W0),{t:"cast",sp:"Summon Wolf",dest:h}); rollN=sv; const m=allU().find(x=>x.minion); return !!m&&ownerOf(m)===W0&&enemiesOf(G.players[1]).includes(m)&&enemiesOf(G.players[2]).includes(m)&&!enemiesOf(W0).includes(m); })());
 ok("M17 the wolf vanishes when its owner falls",(()=>{ const m=allU().find(x=>x.minion); W0.hp=0; endCheck(); return m.hp<=0&&m.gone; })());
 begin(4,[0,1,2,3]);
 drawMap(); ui();
 ok("M18 the map draws four colors for four players",["--me","--foe","--p3","--p4"].every(c=>$("map").innerHTML.includes("var("+c+")")));
 ok("M19 the pick screen only tells the others to look away",(()=>{ let g=0; while(G.phase!=="cover"&&g++<30){ if(G.phase==="choose") choose(true); else if(G.phase==="move") confirmMove(); else if(G.phase==="rcover"){G.phase="renew";} else if(G.phase==="renew") doRenew(); else break; } ui(); return G.phase==="cover"&&/Everyone else, look away/.test($("ctl").innerText); })());
 begin(2);
 ok("M20 two players still work as before (opp, winner, XP)",G.players.length===2&&opp(G.me)===G.foe&&(()=>{ G.foe.hp=-1; endCheck(); return G.phase==="over"&&G.winner===G.me&&G.xp.length===2&&/\+30 XP/.test(G.xp[0])&&/\+20 XP/.test(G.xp[1]); })());
 return R;
}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    import os; pg.goto('file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','duel.html')))
    try:
        R=pg.evaluate(JS)
        for n,ok in R: print(('PASS ' if ok else 'FAIL ')+n)
        print(sum(1 for r in R if r[1]),'/',len(R),'passed')
    except Exception as e: print('ERROR',str(e)[:900])
    print(errs[:3])
