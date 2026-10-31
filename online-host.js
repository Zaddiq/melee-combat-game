"use strict";
/* online-host.js: the tablet's side of the online table (Colosseum). Step 1: open a room, see which phones joined,
   and say which phone runs which player. It reads the page's globals ($, esc, NP, slot, PCLS) and changes nothing in the game. */
(function(){
const body=$("onBody"); if(!body) return;
const KEYR="colosseum-host-room";
let code=null, offJoins=null, offCmds=null, joins={}, seat={}, err="", sig="";   /* seat: phone uid -> player index, or -1 for "watching only" */
const saved=()=>{ try{ return localStorage.getItem(KEYR)||""; }catch(e){ return ""; } };
const url=()=>new URL("phone.html?room="+code+(Net.kind==="mem"?"&net=mem":""),location.href).href;
const pname=i=>"Player "+(i+1)+(slot[i]?" ("+slot[i].name+")":"");
function autoSeat(){
  for(const u of Object.keys(seat)) if(!joins[u]) delete seat[u];
  for(const u of Object.keys(seat)) if(seat[u]>=NP) seat[u]=-1;
  for(const u of Object.keys(joins)) if(seat[u]===undefined){ const used=new Set(Object.values(seat)); seat[u]=-1; for(let i=0;i<NP;i++) if(!used.has(i)){ seat[u]=i; break; } }
}
function pubObj(){ const seats={}; for(const u of Object.keys(seat)) if(joins[u]) seats[u]={p:seat[u],name:joins[u].name,fighter:seat[u]>=0&&slot[seat[u]]?slot[seat[u]].name:""}; return {open:true,np:NP,seats}; }
const fail=e=>{ err=(e&&e.message)||String(e); render(); };
function sync(){ if(code) Net.publish(code,pubObj()).catch(fail); }
function render(){
  const e=err?`<div style="color:var(--foe);margin:6px 0">${esc(err)}</div>`:"";
  if(!code){
    const old=saved();
    body.innerHTML=`<div class="mut">Table version 2 (secret picks)</div><div>Let players join from their own phones. Each phone gets a short code; the tablet keeps the board.</div>${e}<div class="row"><button class="pri" id="onOpen">Open a table</button>${old?`<button id="onRe">Reopen table ${esc(old)}</button>`:""}</div>`;
    $("onOpen").onclick=open; if(old) $("onRe").onclick=()=>reopen(old); return; }
  const ids=Object.keys(joins).sort((a,b)=>(joins[a].t||0)-(joins[b].t||0));
  body.innerHTML=`<div class="mut">Table version 2 (secret picks)</div><div>Table code: <b style="font-size:28px;letter-spacing:3px">${esc(code)}</b></div>
   <div class="mut">On each phone open <b>${esc(url())}</b> and type the code${Net.kind==="mem"?" (test mode)":""}.</div>${e}
   <div id="onList" style="margin-top:8px">${ids.length?ids.map(u=>`<div class="row" data-u="${esc(u)}"><span title="${joins[u].on?"connected":"not connected"}" style="color:${joins[u].on?"var(--me)":"var(--mut)"}">●</span> <b>${esc(joins[u].name)}</b>
     <select data-seat="${esc(u)}"><option value="-1">watching only</option>${[...Array(NP)].map((_,i)=>`<option value="${i}"${seat[u]===i?" selected":""}>${esc(pname(i))}</option>`).join("")}</select>
     <button data-kick="${esc(u)}">Remove</button></div>`).join(""):`<div class="mut">Nobody has joined yet.</div>`}</div>
   <div class="row"><button id="onClose">Close the table</button></div>`;
  body.querySelectorAll("[data-seat]").forEach(s=>s.onchange=()=>{ const u=s.dataset.seat, p=+s.value; if(p>=0) for(const o of Object.keys(seat)) if(o!==u&&seat[o]===p) seat[o]=-1; seat[u]=p; render(); sync(); });
  body.querySelectorAll("[data-kick]").forEach(b=>b.onclick=()=>Net.kick(code,b.dataset.kick).catch(fail));
  $("onClose").onclick=close;
}
function watch(){ offJoins=Net.watchJoins(code,v=>{ joins=v||{}; autoSeat(); render(); sync(); ui(); }); offCmds=Net.watchCmds(code,onCmds); }
async function open(){ err=""; try{ await Net.start(); code=await Net.openRoom(); try{ localStorage.setItem(KEYR,code); }catch(x){} seat={}; joins={}; watch(); render(); sync(); }catch(x){ code=null; fail(x); } }
async function reopen(c){ err=""; try{ await Net.start(); const h=await Net.b.get("rooms/"+c+"/host"); if(h!==Net.uid){ try{ localStorage.removeItem(KEYR); }catch(x){} throw new Error("That table is gone, or belongs to another tablet. Open a new one."); } code=c; seat={}; joins={}; watch(); render(); sync(); }catch(x){ code=null; fail(x); } }
async function close(){ const c=code; if(offJoins) offJoins(); offJoins=null; if(offCmds) offCmds(); offCmds=null; code=null; joins={}; seat={}; try{ localStorage.removeItem(KEYR); }catch(x){} try{ await Net.closeRoom(c); }catch(x){ err=x.message; } render(); }
/* the player count and the loaded fighters can change on the page, so keep the phones' view in step */
setInterval(()=>{ const s=code?NP+"|"+slot.slice(0,NP).map(f=>f?f.name:"").join(",")+"|"+JSON.stringify(seat):""; if(s!==sig){ sig=s; if(code){ autoSeat(); render(); sync(); } } },600);

/* ---- secret picks on the phones (step 2) ----
   While a player who has a phone is choosing, the tablet does not show their options. The panel's own buttons are collected,
   sent to that phone as plain labels (priv/UID) and, when the phone sends back "button i" (cmd/UID), the matching tablet button is clicked.
   So the rules and screens in colosseum.html are used unchanged. */
const SECRET=["cover","pick","spells","dest","rcover","renew"];
const plain=h=>{ const d=document.createElement("div"); d.innerHTML=h; return d.textContent.replace(/\s+/g," ").trim(); };
const REL=["straight ahead","ahead and left","behind and left","straight behind","behind and right","ahead and right"];
let seq={}, lastJ={}, done={}, pending={};
const uidOfPlayer=p=>Object.keys(seat).find(u=>seat[u]===p&&joins[u]);
function sendTo(u,payload){ const j=JSON.stringify(payload); if(lastJ[u]===j) return seq[u]; lastJ[u]=j; seq[u]=(seq[u]||Date.now())+1; Net.sendPriv(code,u,Object.assign({seq:seq[u]},payload)).catch(fail); return seq[u]; }
function waitText(){ if(!G) return "Waiting for the duel to start."; if(G.phase==="over") return (G.winner?(G.winners&&G.winners.length>1?G.winners:[G.winner]).map(u=>u.p.name).join(" and ")+" won the duel.":"The duel is over.")+" Watch the tablet."; if(SECRET.includes(G.phase)&&G.cur) return "Waiting for "+G.cur.p.name+" to pick."; if(G.phase==="move"&&G.cur) return G.cur.p.name+" is moving. Watch the tablet."; return "The table is playing. Watch the tablet."; }
function sendWaits(except){ for(const u of Object.keys(seat)) if(u!==except&&joins[u]){ delete pending[u]; sendTo(u,{mode:"wait",text:waitText(),turn:G?G.turn:0,ring:Online.ring}); } }
function onCmds(v){ v=v||{}; for(const u of Object.keys(v)){ const m=v[u], pd=pending[u]; if(!m||!pd||m.seq!==pd.seq||done[u]===m.seq) continue; done[u]=m.seq; const f=m.k==="t"?pd.tacts[m.i]:pd.acts[m.i]; if(typeof f==="function") f(); } }
const Online=window.Online={ override:null, ring:0,
  hook(c,t){
    if(!code) return;
    const cur=G&&G.cur;
    if(Online.override&&(!G||Online.override!==cur||!SECRET.includes(G.phase))) Online.override=null;
    const who=G&&SECRET.includes(G.phase)&&cur&&G.players.includes(cur)?uidOfPlayer(G.players.indexOf(cur)):null;
    if(!who||Online.override===cur){ sendWaits(null); return; }
    if(G.phase==="cover"||G.phase==="rcover"){ const b=c.querySelector("#bShow,#bRc"); if(b){ b.click(); return; } }   /* a phone needs no "pass the tablet" screen */
    const acts=[], btns=[], tacts=[], tg=[]; let mode="pick";
    const addEl=e=>{ acts.push(()=>e.click()); btns.push({l:e.textContent,p:e.classList.contains("pri")}); };
    if(G.phase==="pick") c.querySelectorAll("[data-opt]").forEach(addEl);
    else if(G.phase==="spells") { c.querySelectorAll("[data-sp]").forEach(addEl); const bb=c.querySelector("#bBack"); if(bb) addEl(bb); }
    else if(G.phase==="renew") { c.querySelectorAll("[data-rn]").forEach(addEl); const bn=c.querySelector("#bRn"); if(bn) addEl(bn); }
    else if(G.phase==="dest"){
      const hs=[...G.dopts.values()], near=!(cur.size>1)&&(G.destT==="disengage"||G.destT==="hesc")&&hs.every(h=>hdist(h,cur)===1);
      if(near){ mode="dest"; for(const h of hs){ const d=dirIdx(cur,h); acts.push(()=>{ takePick(Object.assign({t:G.destT||"disengage",dest:h},G.destX||{})); G.destX=null; }); btns.push({l:"Move "+REL[(d-cur.f+6)%6],p:false}); } }
      else mode="map";
      const bb=c.querySelector("#bBack"); if(bb) addEl(bb);
    }
    if(G.phase==="pick"){ const E=enemiesOf(cur); if(E.length>1){ const T=other(cur); for(const e of E){ tg.push({l:e.p.name,on:e===T}); tacts.push(()=>{ cur.tgtSel=e; G.oth=other(cur); G.opts=options(cur,G.oth); ui(); drawMap(); }); } } }
    let text=plain(t||"").replace(/\b(The others|[A-Z][^.]*?) must not look\. ?/,"");
    if(mode==="map") text=cur.p.name+": this choice needs the map. Ask the table to hand you the tablet, or tap Back.";
    const sq=sendTo(who,{mode,text,btns,tg,turn:G.turn,ph:G.phase,pi:G.pi||0,ring:Online.ring,who:cur.p.name});
    pending[who]={seq:sq,acts,tacts}; sendWaits(who);
    /* the tablet shows nothing secret: no options, no notes */
    const ch=c.children; if(ch[1]) ch[1].innerHTML=`Waiting for <b class="${pcCls(cur)}">${esc(cur.p.name)}</b>'s phone to pick.${joins[who]&&joins[who].on?"":" <span style=\"color:var(--foe)\">(That phone is not connected.)</span>"}`;
    if(ch[3]) ch[3].innerHTML=`<button id="bRing">Ring again</button> <button id="bTake">Play ${esc(cur.p.name)}'s pick on the tablet instead</button>`;
    const r=$("bRing"), k=$("bTake"); if(r) r.onclick=()=>{ Online.ring++; ui(); }; if(k) k.onclick=()=>{ Online.override=cur; ui(); drawMap(); };
  }
};
render();
window.__online={state:()=>({code,joins,seat,pending})};
})();
