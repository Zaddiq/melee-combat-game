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
    body.innerHTML=`<div class="mut">Table version 8 (phone map)</div><div>Let players join from their own phones. Choose a table name your group will remember (like STEVE) and use the same one every time, or leave it empty for a random code.</div>${e}<div class="row"><input id="onName" maxlength="12" placeholder="Table name, 3 to 12 letters or digits" value="${esc(old)}" style="font:inherit;padding:6px 8px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);text-transform:uppercase;min-width:230px"><button class="pri" id="onOpen">Open the table</button></div>`;
    $("onOpen").onclick=()=>open($("onName").value); $("onName").onkeydown=ev=>{ if(ev.key==="Enter") $("onOpen").click(); }; return; }
  const ids=Object.keys(joins).sort((a,b)=>(joins[a].t||0)-(joins[b].t||0));
  body.innerHTML=`<div class="mut">Table version 8 (phone map)</div><div>Table name: <b style="font-size:28px;letter-spacing:3px">${esc(code)}</b></div>
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
/* ---- the phone map (item 4) ----
   Every message to a seated phone carries a small picture of the board (sc): hexes, figures, created objects, plus, when this phone has a
   choice on the map, the hexes it may tap (hl, kind hk) and the six facing circles (fc). A tap comes back as cmd {k:"h",i:"q,r"} or {k:"f",i:d}.
   The host carries out the tap with the same few lines the tablet's own map uses (see drawMap in colosseum.html). */
const PUB=["choose","move","retreat","advance"], PHONE=SECRET.concat(PUB);   /* PUB: public steps that one player decides */
const actor=()=>!G?null:G.phase==="choose"?G.players[G.chooser]:(G.phase==="retreat"||G.phase==="advance")?G.rdec:G.cur;
function scene(who,hl,hk,fc){
  if(!G||!G.players) return null;
  const names=G.players.map(u=>u.p.name), cur=G.cur;
  const lab=u=>{ const n=(u.p.name||"?").trim(), a=n.charAt(0).toUpperCase(); const clash=names.includes(u.p.name)&&names.some(m=>m!==u.p.name&&m.trim().charAt(0).toUpperCase()===a); return clash&&n.length>1?a+n.charAt(1).toLowerCase():a; };
  const side=new Set(); try{ if(ffaOn()) zones().slice(2,NP).forEach(z=>z.hexes.forEach(h=>side.add(key(h.q,h.r)))); }catch(e){}
  const mine=who&&who.u;
  const objs=(G.objs||[]).filter(o=>o.t!=="slick"||o.g.shown||(mine&&mine===cur&&slickVis(o))).map(o=>[o.q,o.r,o.t==="fire"?"f":o.t==="wall"?"w":o.t==="shadow"?"s":o.t==="slick"?"l":"x"]);
  const us=allU().filter(u=>u.hp>0||!u.minion).map(u=>({c:cells(u).map(x=>[x.q,x.r]),f:u.f,k:pcI(u),L:lab(u),z:u.size>1?u.size:1,d:u.hp<=0?2:(u.down||u.low==="prone")?1:0,v:u.inv?1:0,s:mine&&u===mine?1:0}));
  const info=allU().filter(u=>u.hp>0||!u.minion).map(u=>u.p.name+" ST "+Math.max(u.hp,0)+"/"+u.p.st+(u.down?" down":"")+(u.sleep?" asleep":"")+(u.air?" flying":"")+(u.inv?" invisible":"")).join(" · ");
  const sc={bd:P.map(h=>(h.e||side.has(key(h.q,h.r)))?[h.q,h.r,1]:[h.q,h.r]),ob:objs,u:us,info};
  if(hl&&hl.length){ sc.hl=hl.map(h=>[h.q,h.r,h.c||0]); sc.hk=hk; }
  if(fc&&mine) sc.fc={q:mine.q,r:mine.r,f:mine.f};
  return sc;
}
let seq={}, lastJ={}, done={}, pending={};
/* ---- everyone picks at once (item 5) ----
   When the picks of a turn begin, every player who has a phone gets their own pick session (the same steps as the tablet panel:
   action, spell, far hex, with Back) and answers at the same time as the others. The tablet's own players (no phone) go first, one after
   another with the cover screen, as before. When every phone has answered, the stored picks are handed to the game one by one (Online.ready).
   A phone can change its pick until the last one is in. "Play X on the tablet instead" drops that phone's session. */
let sess={}, tabletTake=new Set();
const activeSess=u=>{ const x=sess[u]; return x&&!x.dead&&G&&x.turn===G.turn?x:null; };
const allIn=()=>Object.keys(sess).every(k=>{ const x=activeSess(k); return !x||x.step==="done"; });
const waitingNames=()=>Object.keys(sess).map(k=>activeSess(k)).filter(x=>x&&x.step!=="done").map(x=>x.u.p.name);
function sessOpts(S){ const o=other(S.u); S.oth=o; S.opts=options(S.u,o); S.note=pickNote(S.u,o,S.opts); }
function sessView(uid){
  const S=sess[uid], u=S.u, acts=[], btns=[], tacts=[], tg=[], hacts={}; let mode="pick", text="", hl=null, hk="";
  const add=(l,p,f)=>{ acts.push(f); btns.push({l,p}); };
  if(S.step==="pick"){
    text=`${u.p.name}: choose your action. ${S.note||""}`;
    S.opts.forEach((x,i)=>add(x.label,i===0&&x.t!=="none",()=>sessChoose(uid,i)));
    if(!S.opts.length) add("Continue",true,()=>sessFinish(uid,{t:"none"}));
    const E=enemiesOf(u); if(E.length>1) for(const e of E){ tg.push({l:e.p.name,on:e===S.oth}); tacts.push(()=>{ u.tgtSel=e; sessOpts(S); sessPush(uid); }); }
  } else if(S.step==="spells"){
    text=`${u.p.name}: choose a spell. A thrown spell that misses costs 1 ST, a missile spell costs everything you put into it, and a roll of 17 or 18 costs the full price.`;
    S.sopts.forEach((x,i)=>add(x.label,false,()=>sessSpell(uid,i)));
    add("Back",false,()=>{ S.step="pick"; sessPush(uid); });
  } else if(S.step==="dest"){
    mode="map"; text=`${u.p.name}: tap the highlighted hex you want to move or teleport into, then confirm.`; hl=[...S.dopts.values()]; hk="dest";
    for(const h of hl) hacts[key(h.q,h.r)]=()=>sessFinish(uid,Object.assign({t:S.destT||"disengage",dest:S.dopts.get(key(h.q,h.r))},S.destX||{}));
    add("Back",false,()=>{ S.step="pick"; S.destX=null; sessPush(uid); });
  } else {
    const w=waitingNames(); text=w.length?`Your pick is in. Waiting for ${w.join(", ")}. You can still change it.`:"Everyone has picked.";
    add("Change my pick",false,()=>{ S.step="pick"; S.act=null; sessOpts(S); sessPush(uid); });
  }
  return {mode,text,btns,tg,hl,hk,acts,tacts,hacts};
}
function sessPush(uid){
  const S=activeSess(uid); if(!S) return; const v=sessView(uid);
  const sq=sendTo(uid,{mode:v.mode,text:v.text,btns:v.btns,tg:v.tg,turn:G.turn,ph:"pick",pi:0,key:"s"+G.turn+"|"+uid,ring:Online.ring,who:S.u.p.name,sc:scene({u:S.u},v.hl,v.hk,false)});
  pending[uid]={seq:sq,acts:v.acts,tacts:v.tacts,hacts:v.hacts,facts:{}};
}
const sessPushAll=()=>Object.keys(sess).forEach(sessPush);
function sessChoose(uid,i){
  const S=sess[uid], u=S.u, x=S.opts[i]||{t:"none"};
  if(x.t==="cast"){ S.sopts=castList(u,S.oth); S.step="spells"; }
  else if(x.t==="disengage"||x.t==="hesc"){ const hs=freeNeighbors(u); if(!hs.length) S.note="There is no free hex to move into. "; else { S.destT=x.t; S.destX=null; S.dopts=new Map(hs.map(h=>[key(h.q,h.r),h])); S.step="dest"; } }
  else return sessFinish(uid,x);
  sessPush(uid);
}
function sessSpell(uid,i){
  const S=sess[uid], u=S.u, o=S.oth, x=S.sopts[i]; if(!x) return;
  if(x.hexsel){ S.destT="cast"; S.destX={sp:x.sp,form:x.form,on:x.on}; S.dopts=new Map(creaHexes(u,o,x.hexsel,x.sp,x.form).map(h=>[key(h.q,h.r),h])); S.step="dest"; sessPush(uid); return; }
  if(x.tele){ S.destT="cast"; S.destX={sp:"Teleport"}; S.dopts=new Map(P.filter(h=>!same(h,u)&&!same(h,o)&&Math.max(1,mhDist(u,h))<=u.hp).map(h=>[key(h.q,h.r),h])); S.step="dest"; sessPush(uid); return; }
  sessFinish(uid,{t:"cast",sp:x.sp,n:x.n,on:x.on,objId:x.objId,form:x.form});
}
function sessFinish(uid,act){ const S=sess[uid]; if(!S) return; S.act=act; S.step="done"; sessPushAll(); sessCheck(); if(G&&G.pq&&G.phase==="cover"&&activeSess(uid)) ui(); }   /* the tablet's waiting line names who is still to pick */
/* when the last phone is in and the game is waiting at one of them, let the game take the stored picks */
function sessCheck(){ if(!G||!G.pq||!["cover","pick"].includes(G.phase)) return; const cur=G.pq[G.pi]; if(cur&&Online.ready(cur)) startPick(); }
function sessKill(uid){ const x=sess[uid]; if(x){ x.dead=true; delete lastJ[uid]; delete pending[uid]; } }

const uidOfPlayer=p=>Object.keys(seat).find(u=>seat[u]===p&&joins[u]);
function sendTo(u,payload){ const j=JSON.stringify(payload); if(lastJ[u]===j) return seq[u]; lastJ[u]=j; seq[u]=(seq[u]||Date.now())+1; Net.sendPriv(code,u,Object.assign({seq:seq[u]},payload)).catch(fail); return seq[u]; }
function waitText(){ if(!G) return "Waiting for the fight to start."; if(G.phase==="over") return (G.winner?(G.winners&&G.winners.length>1?G.winners:[G.winner]).map(u=>u.p.name).join(" and ")+" won the fight.":"The fight is over.")+" Watch the tablet."; if(SECRET.includes(G.phase)&&G.cur) return "Waiting for "+G.cur.p.name+" to pick."; if(G.phase==="move"&&G.cur) return G.cur.p.name+" is moving. Watch the tablet."; return "The table is playing. Watch the tablet."; }
function sendWaits(except){ for(const u of Object.keys(Online.lastKey)) if(u!==except&&!(G&&PHONE.includes(G.phase))) delete Online.lastKey[u]; for(const u of Object.keys(seat)) if(u!==except&&joins[u]&&!activeSess(u)){ delete pending[u]; sendTo(u,{mode:"wait",text:waitText(),turn:G?G.turn:0,ring:Online.ring,sc:scene(null)}); } }
function onCmds(v){ v=v||{}; for(const u of Object.keys(v)){ const m=v[u], pd=pending[u]; if(!m||!pd||m.seq!==pd.seq||done[u]===m.seq) continue; done[u]=m.seq; const f=({b:pd.acts,t:pd.tacts,h:pd.hacts,f:pd.facts}[m.k]||{})[m.i]; lastJ[u]=null; if(typeof f==="function") f(); } }
const Online=window.Online={ override:null, ring:0, lastKey:{},
  begin(pq){ sess={}; tabletTake=new Set(); if(!code||!G||!G.players) return null;
    const ph=pq.filter(u=>u.hp>0&&uidOfPlayer(G.players.indexOf(u))); if(!ph.length) return null;
    for(const u of ph){ const uid=uidOfPlayer(G.players.indexOf(u)); u.tgtSel=u.tgtSel&&u.tgtSel.hp>0?u.tgtSel:null; sess[uid]={u,turn:G.turn,step:"pick",dead:false}; sessOpts(sess[uid]); }
    const t0=G.turn; setTimeout(()=>{ if(G&&G.turn===t0&&sess) sessPushAll(); },0);
    ph.forEach((u,k)=>setTimeout(()=>{ if(G&&G.turn===t0) Bell.ring(G.players.indexOf(u)); },k*700));   /* every phone's own pitch, one after the other so each can be heard */
    return pq.filter(u=>!ph.includes(u)).concat(ph); },
  redo(){ for(const k of Object.keys(sess)){ const x=activeSess(k); if(x&&x.step==='pick') sessOpts(x); } sessPushAll(); },   /* recompute every open pick session (used by tests after moving figures by hand) */
  ready(u){ if(!code||!G||!u) return null; const i=G.players.indexOf(u), uid=i>=0&&uidOfPlayer(i), S=uid&&activeSess(uid); if(!S||S.step!=="done"||!allIn()) return null; return S.act; },
  result(f){ if(!code||!f.phone) return; Net.sendRes(code,f.phone.uid,{id:Date.now(),key:f.phone.key,rec:Object.assign({},f.phone.rec,{src:f.phone.src})}).catch(fail); },
  hook(c,t){
    if(!code) return;
    if((!G||!G.pq||!G.players||!["cover","pick","spells","dest"].includes(G.phase))&&Object.keys(sess).length){ sess={}; tabletTake=new Set(); }   /* the turn's picks are over */
    const cur=actor();
    if(Online.override&&(!G||Online.override!==cur||!PHONE.includes(G.phase))) Online.override=null;
    const who=G&&PHONE.includes(G.phase)&&cur&&G.players.includes(cur)?uidOfPlayer(G.players.indexOf(cur)):null;
    if(!who||Online.override===cur||tabletTake.has(cur)){ sendWaits(null); return; }
    const secret=SECRET.includes(G.phase);
    if(secret&&activeSess(who)){   /* this phone is picking in its own session, at the same time as the others: the tablet only waits */
      const w=Object.keys(sess).map(k=>({k,s:activeSess(k)})).filter(x=>x.s&&x.s.step!=="done"), ch=c.children;
      if(ch[1]) ch[1].innerHTML=w.length?`Everyone with a phone is picking at the same time. Waiting for: ${w.map(x=>`<b class="${pcCls(x.s.u)}">${esc(x.s.u.p.name)}</b>${joins[x.k]&&joins[x.k].on?"":" (not connected)"}`).join(", ")}.`:"All the phones have picked.";
      if(ch[3]) ch[3].innerHTML=`<button id="bRing">Ring again</button> `+w.map(x=>`<button data-take="${esc(x.k)}">Play ${esc(x.s.u.p.name)} on the tablet instead</button>`).join(" ");
      const rg=$("bRing"); if(rg) rg.onclick=()=>{ Online.ring++; Object.keys(sess).map(activeSess).filter(x=>x&&x.step!=="done").forEach(x=>Bell.ring(G.players.indexOf(x.u))); sessPushAll(); };
      c.querySelectorAll("[data-take]").forEach(b=>b.onclick=()=>{ const k=b.dataset.take, x=sess[k]; if(!x) return; sessKill(k); tabletTake.add(x.u); sessCheck(); ui(); drawMap(); });
      sendWaits(null); return; }
    if(G.phase==="cover"||G.phase==="rcover"){ const b=c.querySelector("#bShow,#bRc"); if(b){ b.click(); return; } }   /* a phone needs no "pass the tablet" screen */
    const pidx=G.players.indexOf(cur), rkey=secret?(G.phase==="renew"?"r":"p")+G.turn+"|"+(G.pi||0)+"|"+who:G.phase+G.turn+"|"+(G.idx||0)+"|"+(G.pi||0)+"|"+who;
    const acts=[], btns=[], tacts=[], tg=[], hacts={}, facts={}; let mode="pick", hl=null, hk="", fc=false;
    const addEl=e=>{ acts.push(()=>e.click()); btns.push({l:e.textContent,p:e.classList.contains("pri")}); };
    if(G.phase==="pick") c.querySelectorAll("[data-opt]").forEach(addEl);
    else if(G.phase==="spells") { c.querySelectorAll("[data-sp]").forEach(addEl); const bb=c.querySelector("#bBack"); if(bb) addEl(bb); }
    else if(G.phase==="renew") { c.querySelectorAll("[data-rn]").forEach(addEl); const bn=c.querySelector("#bRn"); if(bn) addEl(bn); }
    else if(G.phase==="choose") c.querySelectorAll("#b1,#b2").forEach(addEl);
    else if(G.phase==="advance") c.querySelectorAll("#bAdv,#bStay").forEach(addEl);
    else if(G.phase==="retreat"){
      mode="map"; hk="ret"; hl=[...G.ropts.values()];
      for(const h of hl) hacts[key(h.q,h.r)]=()=>doRetreat(G.ropts.get(key(h.q,h.r)));
      const bs=c.querySelector("#bSkip"); if(bs) addEl(bs); }
    else if(G.phase==="move"){
      mode="map"; hk="go"; fc=true; hl=[...G.reach.values()].filter(r=>!same(r,cur));
      for(const r of hl) hacts[key(r.q,r.r)]=()=>{ const x=G.reach.get(key(r.q,r.r)); if(!x) return; G.cur.q=x.q; G.cur.r=x.r; G.moved=x.c; ui(); drawMap(); };
      for(let d=0;d<6;d++) facts[d]=()=>{ G.cur.f=d; ui(); drawMap(); };
      const ok=c.querySelector("#bOk"); if(ok) addEl(ok); const un=c.querySelector("#bUn"); if(un) addEl(un);
      if(c.querySelector("#bEsc")){ acts.push(()=>quitDuel(cur,"escape")); btns.push({l:cur.p.name+" escapes through the door",p:false,cf:cur.p.name+" leaves through the door? They are out of the fight."}); } }
    else if(G.phase==="dest"){
      const hs=[...G.dopts.values()], near=!(cur.size>1)&&(G.destT==="disengage"||G.destT==="hesc")&&hs.every(h=>hdist(h,cur)===1);
      hl=hs; hk="dest"; for(const h of hs) hacts[key(h.q,h.r)]=()=>{ const d=G.dopts.get(key(h.q,h.r)); if(!d) return; takePick(Object.assign({t:G.destT||"disengage",dest:d},G.destX||{})); G.destX=null; };
      if(near){ mode="dest"; for(const h of hs){ const d=dirIdx(cur,h); acts.push(()=>{ takePick(Object.assign({t:G.destT||"disengage",dest:h},G.destX||{})); G.destX=null; }); btns.push({l:"Move "+REL[(d-cur.f+6)%6],p:false}); } }
      else mode="map";
      const bb=c.querySelector("#bBack"); if(bb) addEl(bb);
    }
    if(G.phase==="pick"){ const E=enemiesOf(cur); if(E.length>1){ const T=other(cur); for(const e of E){ tg.push({l:e.p.name,on:e===T}); tacts.push(()=>{ cur.tgtSel=e; G.oth=other(cur); G.opts=options(cur,G.oth); ui(); drawMap(); }); } } }
    let text=plain(t||"").replace(/\b(The others|[A-Z][^.]*?) must not look\. ?/,"").replace(/ ?\(on a phone, scroll to the map\)/,"").replace(/\bClick\b/g,"Tap").replace(/\bclick\b/g,"tap");
    if(Online.lastKey[who]!==rkey){ Online.lastKey[who]=rkey; Bell.ring(pidx); }   /* the table hears whose turn it is, once per pick */
    const sq=sendTo(who,{mode,text,btns,tg,turn:G.turn,ph:G.phase,pi:G.pi||0,key:rkey,ring:Online.ring,who:cur.p.name,sc:scene({u:cur},hl,hk,fc)});
    pending[who]={seq:sq,acts,tacts,hacts,facts}; sendWaits(who);
    if(secret){
      /* the tablet shows nothing secret: no options, no notes */
      const ch=c.children; if(ch[1]) ch[1].innerHTML=`Waiting for <b class="${pcCls(cur)}">${esc(cur.p.name)}</b>'s phone to pick.${joins[who]&&joins[who].on?"":" <span style=\"color:var(--foe)\">(That phone is not connected.)</span>"}`;
      if(ch[3]) ch[3].innerHTML=`<button id="bRing">Ring again</button> <button id="bTake">Play ${esc(cur.p.name)}'s pick on the tablet instead</button>`; }
    else {
      /* public steps: the tablet map stays as it is, the panel says whose phone is deciding */
      const ch=c.children; if(ch[1]) ch[1].innerHTML=`<b class="${pcCls(cur)}">${esc(cur.p.name)}</b> is deciding on their phone.${joins[who]&&joins[who].on?"":" <span style=\"color:var(--foe)\">(That phone is not connected.)</span>"}`;
      if(ch[3]) ch[3].innerHTML=`<button id="bRing">Ring again</button> <button id="bTake">Play ${esc(cur.p.name)}'s move on the tablet instead</button>`; if(G.phase==="move"&&ch[4]&&ch[4].id!=="log") ch[4].innerHTML=""; }
    const r=$("bRing"), k=$("bTake"); if(r) r.onclick=()=>{ Online.ring++; Bell.ring(pidx); ui(); }; if(k) k.onclick=()=>{ Online.override=cur; ui(); drawMap(); };
  }
};
render();
window.__online={state:()=>({code,joins,seat,pending,locked,sess})};
})();
