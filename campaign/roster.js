"use strict";
/* roster.js: shared by colosseum.html and phone.html. Spending an earned attribute point, and keeping the character open in the builder
   up to date (stats, total and EP) when the same character earns experience at the table. The arena has its own copy of the spend rules
   (wizard-arena.html spend()); keep them the same. A record r is the arena's roster record: {name,st,dx,iq,total0,pts,wins,ep,pend,must,banked,retired,src}. */
(function(){
const rk=n=>String(n||"").trim().toLowerCase();
const updated=r=>Object.assign({},r.src||{},{name:r.name,st:r.st,dx:r.dx,iq:r.iq!=null?r.iq:(r.src&&r.src.iq),total:r.total0+r.pts,ep:r.ep,arenaWins:r.wins||0,arenaRetired:!!r.retired});
/* which buttons a record may press right now: ["st","dx","iq"?,"bank"?] */
function options(r){ if(!r||!(r.pend>0)) return []; const cls=r.src&&r.src.cls, o=["st","dx"]; if(cls==="wizard") o.push("iq"); if(r.pend===1&&!r.must&&(r.wins||0)<16) o.push("bank"); return o; }
function spend(r,k){
  if(!options(r).includes(k)) return false;
  if(k==="bank"){ r.banked=true; r.pend=0; r.must=false; return true; }
  const base=r[k]!=null?r[k]:(k==="iq"?((r.src&&r.src.iq)||8):8);
  r[k]=base+1; r.pts=(r.pts||0)+1; r.pend--; if(r.pend===0) r.must=false;
  if(r.pend===0&&(r.wins||0)>=16) r.retired=true;
  return true;
}
/* if the builder (storage under key) holds this same character, bring its numbers up to date; its gear and spells are left alone */
function syncBuilder(storage,key,r){
  try{ const b=JSON.parse(storage.getItem(key)||"null"); if(!b||rk(b.name)!==rk(r.name)) return false;
    const u=updated(r); storage.setItem(key,JSON.stringify(Object.assign({},b,{st:u.st,dx:u.dx,iq:u.iq,total:u.total,ep:u.ep,arenaWins:u.arenaWins,arenaRetired:u.arenaRetired}))); return true; }catch(e){ return false; }
}
window.Roster={rk,updated,options,spend,syncBuilder};
})();
