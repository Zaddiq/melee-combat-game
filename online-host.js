"use strict";
/* online-host.js: the tablet's side of the online table (Colosseum). Step 1: open a room, see which phones joined,
   and say which phone runs which player. It reads the page's globals ($, esc, NP, slot, PCLS) and changes nothing in the game. */
(function(){
const body=$("onBody"); if(!body) return;
Bell.init(localStorage,"bell-on-host");
const KEYR="colosseum-host-room";
let awakeOk=null, code=null, offJoins=null, offCmds=null, joins={}, seat={}, err="", sig="", locked=false;   /* seat: phone uid -> player index, or -1 for "watching only" */
const saved=()=>{ try{ return localStorage.getItem(KEYR)||""; }catch(e){ return ""; } };
const url=()=>new URL("phone.html?room="+code+(Net.kind==="mem"?"&net=mem":""),location.href).href;
const pname=i=>"Player "+(i+1)+(slot[i]?" ("+slot[i].name+")":"");
function autoSeat(){
  for(const u of Object.keys(seat)) if(!joins[u]) delete seat[u];
  for(const u of Object.keys(seat)) if(seat[u]>=NP) seat[u]=-1;
  for(const u of Object.keys(joins)) if(seat[u]===undefined){ const used=new Set(Object.values(seat)); seat[u]=-1; for(let i=0;i<NP;i++) if(!used.has(i)){ seat[u]=i; break; } }
}
function pubObj(){ const seats={}; for(const u of Object.keys(seat)) if(joins[u]) seats[u]={p:seat[u],name:joins[u].name,fighter:seat[u]>=0&&slot[seat[u]]?slot[seat[u]].name:""}; return {open:true,locked,np:NP,seats,t:Date.now()}; }
const fail=e=>{ err=(e&&e.message)||String(e); render(); };
function sync(){ if(code) Net.publish(code,pubObj()).catch(fail); }
function render(){
  const e=err?`<div style="color:var(--foe);margin:6px 0">${esc(err)}</div>`:"";
  if(!code){
    const old=saved();
    body.innerHTML=`<div class="mut">Table version 7 (bell)</div><div>Let players join from their own phones. Choose a table name your group will remember (like STEVE) and use the same one every time, or leave it empty for a random code.</div>${e}<div class="row"><input id="onName" maxlength="12" placeholder="Table name, 3 to 12 letters or digits" value="${esc(old)}" style="font:inherit;padding:6px 8px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);text-transform:uppercase;min-width:230px"><button class="pri" id="onOpen">Open the table</button></div>`;
    $("onOpen").onclick=()=>open($("onName").value); $("onName").onkeydown=ev=>{ if(ev.key==="Enter") $("onOpen").click(); }; return; }
  const ids=Object.keys(joins).sort((a,b)=>(joins[a].t||0)-(joins[b].t||0));
  body.innerHTML=`<div class="mut">Table version 7 (bell)</div><div>Table name: <b style="font-size:28px;letter-spacing:3px">${esc(code)}</b></div>
   <div class="mut">On each phone open <b>${esc(url())}</b> and type the table name${Net.kind==="mem"?" (test mode)":""}.${locked?` <b style="color:var(--foe)">The table is locked: no new phones can join.</b>`:""}</div>${e}
   <div id="onList" style="margin-top:8px">${ids.length?ids.map(u=>`<div class="row" data-u="${esc(u)}"><span title="${joins[u].on?"connected":"not connected"}" style="color:${joins[u].on?"var(--me)":"var(--mut)"}">●</span> <b>${esc(joins[u].name)}</b>
     <select data-seat="${esc(u)}"><option value="-1">watching only</option>${[...Array(NP)].map((_,i)=>`<option value="${i}"${seat[u]===i?" selected":""}>${esc(pname(i))}</option>`).join("")}</select>
     <button data-test="${esc(u)}" title="play this player's bell">Test bell</button><button data-kick="${esc(u)}">Remove</button></div>`).join(""):`<div class="mut">Nobody has joined yet.</div>`}</div>
   <div class="row"><button id="onBell">Bell: ${Bell.on?"on":"off"}</button><span class="mut">${awakeOk===true?"The tablet screen is kept awake.":awakeOk===false?"This browser cannot keep the screen awake: turn off auto-lock.":""}</span></div>
   <div class="row"><button id="onLock">${locked?"Unlock the table":"Lock the table (no new phones)"}</button><button id="onClose">Close the table (and change the name)</button></div>`;
  body.querySelectorAll("[data-seat]").forEach(s=>s.onchange=()=>{ const u=s.dataset.seat, p=+s.value; if(p>=0) for(const o of Object.keys(seat)) if(o!==u&&seat[o]===p) seat[o]=-1; seat[u]=p; render(); sync(); });
  body.querySelectorAll("[data-kick]").forEach(b=>b.onclick=()=>Net.kick(code,b.dataset.kick).catch(fail));
  $("onBell").onclick=()=>{ Bell.setOn(!Bell.on); Bell.unlock(); if(Bell.on) Bell.ring(0); render(); };
  body.querySelectorAll("[data-test]").forEach(b=>b.onclick=()=>{ Bell.unlock(); Bell.ring(Math.max(0,seat[b.dataset.test])); });
  $("onLock").onclick=()=>{ locked=!locked; render(); sync(); };
  $("onClose").onclick=close;
}
function watch(){ offJoins=Net.watchJoins(code,v=>{ joins={}; for(const u of Object.keys(v||{})) if(v[u]&&typeof v[u].name==="string") joins[u]=v[u];   /* an entry without a name is a leftover, not a player */
     autoSeat(); render(); sync(); loadFromPhones(); ui(); }); offCmds=Net.watchCmds(code,onCmds); }
async function open(name){ err=""; Bell.unlock(); Bell.awake(true).then(v=>{ awakeOk=v; render(); }); try{ await Net.start(); const prev=saved(); code=await Net.openRoom(name); if(prev&&prev!==code) Net.closeRoom(prev).catch(()=>{});   /* the previous table of this tablet is closed (only its own host can: the rules refuse anyone else) */ try{ localStorage.setItem(KEYR,code); }catch(x){} seat={}; joins={}; applied={}; locked=false; try{ const pb=await Net.b.get("rooms/"+code+"/pub"); locked=!!(pb&&pb.locked); }catch(x){} watch(); render(); sync(); }catch(x){ code=null; fail(x); } }
async function close(){ const c=code; Bell.awake(false); awakeOk=null; if(offJoins) offJoins(); offJoins=null; if(offCmds) offCmds(); offCmds=null; code=null; joins={}; seat={}; locked=false; try{ await Net.closeRoom(c); }catch(x){ err=x.message; } render(); }
setInterval(()=>{ if(code) sync(); },5*60*1000);   /* keeps the table from looking abandoned */
/* the player count and the loaded fighters can change on the page, so keep the phones' view in step */
setInterval(()=>{ const s=code?NP+"|"+slot.slice(0,NP).map(f=>f?f.name:"").join(",")+"|"+JSON.stringify(seat):""; if(s!==sig){ sig=s; if(code){ autoSeat(); render(); sync(); } } if(code) loadFromPhones(); },600);


/* ---- characters from the phones (item 2) ----
   A phone may bring a character (join/UID/fj = JSON {name,st,dx,src,rec}: its builder data and its own roster record).
   When that phone is seated and no duel is on screen, the character is loaded into the seat. Experience for it is worked out here and
   sent back (res/UID) to be saved in the phone's own roster, so the character keeps growing in the arena between table sessions. */
let applied={};   /* phone uid -> "seat|fj" already loaded, so a hand-loaded fighter is not overwritten every tick */
function fromPhone(u,fj,i){
  try{ const o=JSON.parse(fj); if(!o||!o.src||typeof o.src!=="object") return null;
    const f=fromBuilder(Object.assign({},o.src,{st:o.st,dx:o.dx,name:String(o.name||o.src.name||"Unnamed").slice(0,40)}));
    const nm=String(o.name||o.src.name||"Unnamed").slice(0,40);
    f.phone={uid:u,fj,name:nm,key:nm.trim().toLowerCase(),src:o.src,rec:o.rec||null}; return f; }catch(e){ return null; }
}
function loadFromPhones(){
  if(G) return;   /* never while a duel (or its result screen) is showing; Rematch clears it and the next tick loads */
  let changed=false;
  for(const u of Object.keys(applied)) if(!(joins[u]&&seat[u]>=0)) delete applied[u];   /* a phone that left its seat will load again if it comes back */
  for(let i=0;i<NP;i++){ const u=uidOfPlayer(i), f0=slot[i];
    if(!u||!joins[u].fj){ if(f0&&f0.phone){ slot[i]=null; me=slot[0]; foe=slot[1]; $("msg"+i).textContent=""; showSlot(i); changed=true; } continue; }   /* no phone, or it brings nobody: drop what it had brought */
    const tag=i+"|"+joins[u].fj; if(applied[u]===tag) continue;   /* already loaded (or the host replaced it by hand: leave that) */
    applied[u]=tag; const f=fromPhone(u,joins[u].fj,i); if(!f) continue;
    setP(i,f,"Brought by "+(joins[u].name||"a phone")+"."); changed=true; }
  if(changed){ ui(); drawMap(); }
}

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
function waitText(){ if(!G) return "Waiting for the fight to start."; if(G.phase==="over") return (G.winner?(G.winners&&G.winners.length>1?G.winners:[G.winner]).map(u=>u.p.name).join(" and ")+" won the fight.":"The fight is over.")+" Watch the tablet."; if(SECRET.includes(G.phase)&&G.cur) return "Waiting for "+G.cur.p.name+" to pick."; if(G.phase==="move"&&G.cur) return G.cur.p.name+" is moving. Watch the tablet."; return "The table is playing. Watch the tablet."; }
function sendWaits(except){ for(const u of Object.keys(Online.lastKey)) if(u!==except&&!(G&&SECRET.includes(G.phase))) delete Online.lastKey[u]; for(const u of Object.keys(seat)) if(u!==except&&joins[u]){ delete pending[u]; sendTo(u,{mode:"wait",text:waitText(),turn:G?G.turn:0,ring:Online.ring}); } }
function onCmds(v){ v=v||{}; for(const u of Object.keys(v)){ const m=v[u], pd=pending[u]; if(!m||!pd||m.seq!==pd.seq||done[u]===m.seq) continue; done[u]=m.seq; const f=m.k==="t"?pd.tacts[m.i]:pd.acts[m.i]; if(typeof f==="function") f(); } }
const Online=window.Online={ override:null, ring:0, lastKey:{},
  result(f){ if(!code||!f.phone) return; Net.sendRes(code,f.phone.uid,{id:Date.now(),key:f.phone.key,rec:Object.assign({},f.phone.rec,{src:f.phone.src})}).catch(fail); },
  hook(c,t){
    if(!code) return;
    const cur=G&&G.cur;
    if(Online.override&&(!G||Online.override!==cur||!SECRET.includes(G.phase))) Online.override=null;
    const who=G&&SECRET.includes(G.phase)&&cur&&G.players.includes(cur)?uidOfPlayer(G.players.indexOf(cur)):null;
    if(!who||Online.override===cur){ sendWaits(null); return; }
    if(G.phase==="cover"||G.phase==="rcover"){ const b=c.querySelector("#bShow,#bRc"); if(b){ b.click(); return; } }   /* a phone needs no "pass the tablet" screen */
    const pidx=G.players.indexOf(cur), rkey=(G.phase==="renew"?"r":"p")+G.turn+"|"+(G.pi||0)+"|"+who;
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
    if(Online.lastKey[who]!==rkey){ Online.lastKey[who]=rkey; Bell.ring(pidx); }   /* the table hears whose turn it is, once per pick */
    const sq=sendTo(who,{mode,text,btns,tg,turn:G.turn,ph:G.phase,pi:G.pi||0,key:rkey,ring:Online.ring,who:cur.p.name});
    pending[who]={seq:sq,acts,tacts}; sendWaits(who);
    /* the tablet shows nothing secret: no options, no notes */
    const ch=c.children; if(ch[1]) ch[1].innerHTML=`Waiting for <b class="${pcCls(cur)}">${esc(cur.p.name)}</b>'s phone to pick.${joins[who]&&joins[who].on?"":" <span style=\"color:var(--foe)\">(That phone is not connected.)</span>"}`;
    if(ch[3]) ch[3].innerHTML=`<button id="bRing">Ring again</button> <button id="bTake">Play ${esc(cur.p.name)}'s pick on the tablet instead</button>`;
    const r=$("bRing"), k=$("bTake"); if(r) r.onclick=()=>{ Online.ring++; Bell.ring(pidx); ui(); }; if(k) k.onclick=()=>{ Online.override=cur; ui(); drawMap(); };
  }
};
render();
window.__online={state:()=>({code,joins,seat,pending,locked})};
})();
