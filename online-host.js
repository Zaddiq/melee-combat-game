"use strict";
/* online-host.js: the tablet's side of the online table (Colosseum). Step 1: open a room, see which phones joined,
   and say which phone runs which player. It reads the page's globals ($, esc, NP, slot, PCLS) and changes nothing in the game. */
(function(){
const body=$("onBody"); if(!body) return;
const KEYR="colosseum-host-room";
let code=null, offJoins=null, joins={}, seat={}, err="", sig="";   /* seat: phone uid -> player index, or -1 for "watching only" */
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
    body.innerHTML=`<div>Let players join from their own phones. Each phone gets a short code; the tablet keeps the board.</div>${e}<div class="row"><button class="pri" id="onOpen">Open a table</button>${old?`<button id="onRe">Reopen table ${esc(old)}</button>`:""}</div>`;
    $("onOpen").onclick=open; if(old) $("onRe").onclick=()=>reopen(old); return; }
  const ids=Object.keys(joins).sort((a,b)=>(joins[a].t||0)-(joins[b].t||0));
  body.innerHTML=`<div>Table code: <b style="font-size:28px;letter-spacing:3px">${esc(code)}</b></div>
   <div class="mut">On each phone open <b>${esc(url())}</b> and type the code${Net.kind==="mem"?" (test mode)":""}.</div>${e}
   <div id="onList" style="margin-top:8px">${ids.length?ids.map(u=>`<div class="row" data-u="${esc(u)}"><span title="${joins[u].on?"connected":"not connected"}" style="color:${joins[u].on?"var(--me)":"var(--mut)"}">●</span> <b>${esc(joins[u].name)}</b>
     <select data-seat="${esc(u)}"><option value="-1">watching only</option>${[...Array(NP)].map((_,i)=>`<option value="${i}"${seat[u]===i?" selected":""}>${esc(pname(i))}</option>`).join("")}</select>
     <button data-kick="${esc(u)}">Remove</button></div>`).join(""):`<div class="mut">Nobody has joined yet.</div>`}</div>
   <div class="row"><button id="onClose">Close the table</button></div>`;
  body.querySelectorAll("[data-seat]").forEach(s=>s.onchange=()=>{ const u=s.dataset.seat, p=+s.value; if(p>=0) for(const o of Object.keys(seat)) if(o!==u&&seat[o]===p) seat[o]=-1; seat[u]=p; render(); sync(); });
  body.querySelectorAll("[data-kick]").forEach(b=>b.onclick=()=>Net.kick(code,b.dataset.kick).catch(fail));
  $("onClose").onclick=close;
}
function watch(){ offJoins=Net.watchJoins(code,v=>{ joins=v||{}; autoSeat(); render(); sync(); }); }
async function open(){ err=""; try{ await Net.start(); code=await Net.openRoom(); try{ localStorage.setItem(KEYR,code); }catch(x){} seat={}; joins={}; watch(); render(); sync(); }catch(x){ code=null; fail(x); } }
async function reopen(c){ err=""; try{ await Net.start(); const h=await Net.b.get("rooms/"+c+"/host"); if(h!==Net.uid){ try{ localStorage.removeItem(KEYR); }catch(x){} throw new Error("That table is gone, or belongs to another tablet. Open a new one."); } code=c; seat={}; joins={}; watch(); render(); sync(); }catch(x){ code=null; fail(x); } }
async function close(){ const c=code; if(offJoins) offJoins(); offJoins=null; code=null; joins={}; seat={}; try{ localStorage.removeItem(KEYR); }catch(x){} try{ await Net.closeRoom(c); }catch(x){ err=x.message; } render(); }
/* the player count and the loaded fighters can change on the page, so keep the phones' view in step */
setInterval(()=>{ const s=code?NP+"|"+slot.slice(0,NP).map(f=>f?f.name:"").join(",")+"|"+JSON.stringify(seat):""; if(s!==sig){ sig=s; if(code){ autoSeat(); render(); sync(); } } },600);
render();
window.__online={state:()=>({code,joins,seat})};
})();
