/* The campaign game keeps its own saved things. It lives under /campaign/ on the same web address as the old Colosseum, and the browser would
   let the two share one storage box. This puts "campaign:" in front of every saved name, so neither can see or overwrite the other's characters,
   encounters, modules or settings. It must load before anything else on the page. */
(function(){ try{
  const S=Storage.prototype, g=S.getItem, s=S.setItem, r=S.removeItem, P="campaign:";
  const mine=o=>{ try{ return o===window.localStorage; }catch(e){ return false; } };
  S.getItem=function(k){ return mine(this)?g.call(this,P+k):g.call(this,k); };
  S.setItem=function(k,v){ return mine(this)?s.call(this,P+k,v):s.call(this,k,v); };
  S.removeItem=function(k){ return mine(this)?r.call(this,P+k):r.call(this,k); };
}catch(e){} })();
