/* Shared rules data for the Melee game site. Edit numbers here only; builder.html, sim.html and arena.html all load this file.
   Source: The Fantasy Trip: Melee, Third Edition (SJG 2018): weapon table and armor p. 14, shields p. 15, races p. 22. See NOTES.md. */
const RULES=(function(){
/* Starting ST, DX are the Melee minimums; "extra" brings ST+DX to the Melee total (meleeTotal). iq is for Wizard. */
const RACES = {
  human:    {n:"Human",     st:8,  dx:8,  iq:8,  extra:8, meleeTotal:24, note:"Starts at ST 8, DX 8 with 8 extra points (24)."},
  orc:      {n:"Orc",       st:8,  dx:8,  iq:8,  extra:8, meleeTotal:24, note:"Just like a human figure."},
  elf:      {n:"Elf",       st:6,  dx:10, iq:8,  extra:8, meleeTotal:24, note:"Min ST 6, DX 10 (24). MA 12 with cloth armor or none, 10 in leather; other armor as a man."},
  dwarf:    {n:"Dwarf",     st:10, dx:6,  iq:8,  extra:8, meleeTotal:24, note:"Min ST 10, DX 6 (24)."},
  hobbit:   {n:"Halfling",  st:4,  dx:12, iq:8,  extra:6, meleeTotal:22, note:"Min ST 4, DX 12 (22). +2 DX when throwing; may throw any weapon the turn it is readied."},
  goblin:   {n:"Goblin",    st:6,  dx:8,  iq:10, extra:8, meleeTotal:22, note:"Min ST 6, DX 8 (22)."},
  hobgoblin:{n:"Hobgoblin", st:7,  dx:6,  iq:7,  extra:8, meleeTotal:20, note:"Min ST 7, DX 6, IQ 7; total 28 in Wizard, 20 in Melee."}
};
/* pen = DX penalty. pen.w and pen.m are the same now; the builder's old two-source switch is retired. */
const ARMOR = {
  none:     {n:"No armor",      stops:0, ma:10, pen:{w:0,m:0}},
  cloth:    {n:"Cloth armor",   stops:1, ma:10, pen:{w:1,m:1}},
  leather:  {n:"Leather armor", stops:2, ma:8,  pen:{w:2,m:2}},
  chain:    {n:"Chainmail",     stops:3, ma:6,  pen:{w:3,m:3}},
  halfplate:{n:"Half-plate",    stops:4, ma:6,  pen:{w:4,m:4}},
  plate:    {n:"Plate armor",   stops:5, ma:6,  pen:{w:5,m:5}}
};
/* d = dice, m = modifier. two = two-handed. th = may be thrown. */
const W = {
  staff:   {n:"Staff (magical)", d:1,m:0, st:0,  grp:"x"},
  dagger:  {n:"Dagger",        d:1,m:-1,st:0,  th:1, grp:"Melee weapons", note:"1+2 in hand-to-hand"},
  rapier:  {n:"Rapier",        d:1,m:0, st:9,  grp:"Melee weapons"},
  club:    {n:"Club",          d:1,m:0, st:9,  th:1, grp:"Melee weapons"},
  hammer:  {n:"Hammer",        d:1,m:1, st:10, th:1, grp:"Melee weapons"},
  cutlass: {n:"Saber",         d:2,m:-2,st:10, grp:"Melee weapons"},
  shortsw: {n:"Shortsword",    d:2,m:-1,st:11, grp:"Melee weapons"},
  mace:    {n:"Mace",          d:2,m:-1,st:11, th:1, grp:"Melee weapons"},
  smallax: {n:"Small ax",      d:1,m:2, st:11, th:1, grp:"Melee weapons"},
  broad:   {n:"Broadsword",    d:2,m:0, st:12, grp:"Melee weapons"},
  morning: {n:"Morningstar",   d:2,m:1, st:13, grp:"Melee weapons"},
  twohsw:  {n:"2-handed sword",d:3,m:-1,st:14, two:1, grp:"Melee weapons"},
  battle:  {n:"Battleaxe",     d:3,m:0, st:15, two:1, grp:"Melee weapons"},
  javelin: {n:"Javelin",       d:1,m:-1,st:9,  th:1, pole:1, grp:"Pole weapons"},
  spear:   {n:"Spear",         d:1,m:1, st:11, th:1, two:1, pole:1, grp:"Pole weapons"},
  halberd: {n:"Halberd",       d:2,m:0, st:13, two:1, pole:1, grp:"Pole weapons"},
  pikeaxe: {n:"Pike axe",      d:2,m:2, st:15, two:1, pole:1, grp:"Pole weapons"},
  sling:   {n:"Sling",         d:1,m:-2,st:0,  miss:1, grp:"Missile weapons"},
  sbow:    {n:"Small bow",     d:1,m:-1,st:9,  two:1, miss:1, rate:"2 shots/turn at adjDX 15+", grp:"Missile weapons"},
  hbow:    {n:"Horse bow",     d:1,m:0, st:10, two:1, miss:1, rate:"2 shots/turn at adjDX 16+", grp:"Missile weapons"},
  lbow:    {n:"Longbow",       d:1,m:2, st:11, two:1, miss:1, rate:"2 shots/turn at adjDX 18+", grp:"Missile weapons"},
  lxbow:   {n:"Light crossbow",d:2,m:0, st:12, two:1, miss:1, rate:"1 shot every other turn; every turn at adjDX 14+", grp:"Missile weapons"},
  hxbow:   {n:"Heavy crossbow",d:3,m:0, st:15, two:1, miss:1, rate:"1 shot every 3rd turn; every other turn at adjDX 14+", grp:"Missile weapons"},
  /* weapons the 2018 table (In the Labyrinth, Advanced Combat p. 109) has that this page lacked; adv marks them. Damage and ST were read from the owner's photo of that page. */
  bastard: {n:"Bastard sword (1 hand)", d:2,m:1, st:13, grp:"Melee weapons", adv:1},
  bastard2:{n:"Bastard sword (2 hands)",d:3,m:-2,st:13, two:1, grp:"Melee weapons", adv:1, note:"The same sword as the 1-hand one, held in both hands."},
  greatsw: {n:"Great sword",   d:3,m:1, st:16, two:1, grp:"Melee weapons", adv:1},
  hatchet: {n:"Hatchet",       d:1,m:0, st:9,  th:1, grp:"Melee weapons", adv:1},
  warax:   {n:"War ax",        d:2,m:0, st:12, grp:"Melee weapons", adv:1},
  greathm: {n:"Great hammer",  d:2,m:2, st:14, two:1, grp:"Melee weapons", adv:1},
  qstaff:  {n:"Quarterstaff",  d:1,m:2, st:11, two:1, grp:"Melee weapons", adv:1, note:"From the 1980 Advanced Melee table (not in the photographed 2018 page)."},
  trident: {n:"Trident",       d:1,m:0, st:10, th:1, grp:"Pole weapons", adv:1, note:"Too short for a 2-hex jab."},
  pike:    {n:"Pike",          d:2,m:1, st:12, two:1, pole:1, grp:"Pole weapons", adv:1},
  mg:      {n:"Main-gauche",   d:1,m:-1,st:0,  left:1, grp:"x", note:"Left hand. Parries 1 hit per attack from the front, from one-handed non-missile weapons only. No DX penalty for parrying. A separate dagger attack on an attack turn is at −4 DX. 1d−1 in hand-to-hand."},
};
const SHIELDS = {
  small:{n:"Small shield", stops:1, pen:0},
  large:{n:"Large shield", stops:2, pen:1}
};
/* Campaign-only items (from the 1980 In the Labyrinth). They are NOT in SHIELDS, so the builder, simulator and arenas never show them;
   the Colosseum and the campaign builder call RULES.addCampaign() to add them. */
const CAMP_SHIELDS = {
  tower:{n:"Tower shield", stops:3, pen:2},
  spike:{n:"Spike shield", stops:1, pen:0, note:"Used as a second weapon (shield rush) it does 1d-2; the game does not apply that."}   /* 2018 armor table: stops 1, DX 0, $40 */
};
const RATE = {sbow:15,hbow:16,lbow:18,lxbow:14,hxbow:14};

/* for the weapons marked adv: a price (from the 2018 table, read from the owner's photo; used when the rules data has none) and the weapon whose talent they use (when the rules data has no talent for them) */
const EXTRA={price:{bastard:100,bastard2:100,greatsw:150,hatchet:15,warax:60,greathm:110,qstaff:20,trident:30,pike:50,tower:70,spike:40},
  like:{bastard:"broad",bastard2:"broad",greatsw:"twohsw",hatchet:"smallax",warax:"smallax",greathm:"hammer",qstaff:"spear",trident:"spear",pike:"halberd"}};
function addCampaign(){ Object.assign(SHIELDS,CAMP_SHIELDS); return SHIELDS; }
/* natural weapons and hides for creatures (Wizard 2018 p. 15-16), kept out of the fighter menus with hid */
function addCreatureGear(){
  Object.assign(W,{bite:{n:"Bite",d:1,m:1,st:0,hid:1},bite2:{n:"Bite",d:2,m:2,st:0,hid:1},fist2:{n:"Fist",d:2,m:0,st:0,hid:1},club3:{n:"Club",d:3,m:3,st:0,hid:1},
    claw:{n:"Claw",d:2,m:-2,st:0,hid:1},claw3:{n:"Claw",d:3,m:-3,st:0,hid:1},claw2:{n:"Claw",d:2,m:0,st:0,hid:1}});
  for(const [k,v] of Object.entries({scales:["Scales",3,8],scales4:["Scales",4,8],scalesS:["Scales",3,6],scales5:["Scales",5,8],wolfhide:["Fur",1,12],bearhide:["Fur",2,8],stonehide:["Stone skin",3,8],bighide:["Hide",0,8]})) ARMOR[k]={n:v[0],stops:v[1],ma:v[2],pen:{w:0,m:0},hid:1};
}
/* A monster for the Bestiary: checks every field against the tables and returns a clean copy (or null when it has no name). Anything unknown falls back to a plain value. */
function cleanCreature(c){
  if(!c||typeof c!=="object") return null; const name=String(c.name||"").trim().slice(0,40); if(!name) return null;
  const n=(v,lo,hi,d)=>{ v=Math.round(+v); return v>=lo&&v<=hi?v:d; };
  return {name,st:n(c.st,1,80,10),dx:n(c.dx,1,40,10),iq:n(c.iq,1,40,8),
    w:W[c.w]&&!W[c.w].left&&c.w!=="staff"?c.w:"none",armor:ARMOR[c.armor]?c.armor:"none",sh:SHIELDS[c.sh]?c.sh:"none",
    d:c.d==="dagger"||c.d==="mg"?c.d:"none",race:RACES[c.race]?c.race:"human",cls:c.cls==="wizard"?"wizard":"fighter",
    spells:Array.isArray(c.spells)?c.spells.filter(x=>typeof x==="string").map(x=>x.slice(0,30)).slice(0,12):[],note:String(c.note||"").slice(0,300)}; }
/* Magic items a hero carries (Advanced Wizard 1980, Weapon/Armor Enchantment): {id:"mg_N",kind,n,base,dx,dm,stops,flame,lit,note}.
   kind "weapon": a copy of its base weapon with a DX bonus (dxb, counts whenever it is readied) and a damage bonus; DX + damage total at most 5.
   A weapon that can flame (flame:1) does extra damage when lit:1 (a missile weapon: +1 for a bow, +2 for a crossbow): +2 if it does 1 die or less, +3 if more than 1 up to 2 dice, one more die above 2 dice.
   kind "armor" or "shield": a copy of its base with 1 to 5 extra hits stopped. Anything unchecked is dropped; returns the list that was accepted. */
function flameOf(b,k){ if(b.miss) return {d:b.d,m:b.m+(/xbow$/.test(k)?2:1)};   /* a flaming missile weapon: +1 from a bow, +2 from a crossbow */
  return b.d<=1?{d:b.d,m:b.m+2}:b.d<=2?{d:b.d,m:b.m+3}:{d:b.d+1,m:b.m}; }
function addMagic(list){
  const out=[]; if(!Array.isArray(list)) return out;
  const num=(v,lo,hi)=>{ v=Math.round(+v); return v>=lo?Math.min(v,hi):0; };
  for(const m of list.slice(0,20)){
    if(!m||typeof m!=="object"||!/^mg_\d{1,2}$/.test(m.id)||out.some(x=>x.id===m.id)) continue;
    const kind=m.kind==="armor"||m.kind==="shield"?m.kind:"weapon", note=String(m.note||"").slice(0,300);
    if(kind==="weapon"){
      const b=W[m.base]; if(!b||b.hid||m.base==="staff"||m.base==="mg"||/^mg_/.test(m.base)) continue;
      let dx=num(m.dx,0,5), dm=num(m.dm,0,5); if(dx+dm>5){ dm=5-dx; }
      const flame=m.flame?1:0, lit=flame&&m.lit?1:0, nm=String(m.n||"Magic "+b.n).slice(0,40), fl=lit?flameOf(b,m.base):{d:b.d,m:b.m};
      W[m.id]=Object.assign({},b,{n:nm+(lit?" (flaming)":""),d:fl.d,m:fl.m+dm,dxb:dx,mag:1,base:m.base,note});
      out.push({id:m.id,kind,n:nm,base:m.base,dx,dm,flame,lit,note});
    } else {
      const T=kind==="armor"?ARMOR:SHIELDS, b=T[m.base]; if(!b||b.hid||m.base==="none"||/^mg_/.test(m.base)) continue;
      const stops=num(m.stops,1,5)||1, nm=String(m.n||"Magic "+b.n).slice(0,40);
      T[m.id]=Object.assign({},b,{n:nm,stops:b.stops+stops,mag:1,base:m.base,note});
      out.push({id:m.id,kind,n:nm,base:m.base,stops,note}); }
  }
  return out; }
return {EDITION:"Melee Third Edition (2018)",RACES,ARMOR,W,SHIELDS,RATE,CAMP_SHIELDS,EXTRA,addCampaign,addMagic,cleanCreature,addCreatureGear};
})();
