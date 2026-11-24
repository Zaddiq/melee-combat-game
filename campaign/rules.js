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
  mg:      {n:"Main-gauche",   d:1,m:-1,st:0,  left:1, grp:"x", note:"Left hand. Parries 1 hit per attack from the front, from one-handed non-missile weapons only. No DX penalty for parrying. A separate dagger attack on an attack turn is at −4 DX. 1d−1 in hand-to-hand."},
};
const SHIELDS = {
  small:{n:"Small shield", stops:1, pen:0},
  large:{n:"Large shield", stops:2, pen:1}
};
/* Campaign-only items (from the 1980 In the Labyrinth). They are NOT in SHIELDS, so the builder, simulator and arenas never show them;
   the Colosseum and the campaign builder call RULES.addCampaign() to add them. */
const CAMP_SHIELDS = {
  tower:{n:"Tower shield", stops:3, pen:2}
};
const RATE = {sbow:15,hbow:16,lbow:18,lxbow:14,hxbow:14};

function addCampaign(){ Object.assign(SHIELDS,CAMP_SHIELDS); return SHIELDS; }
/* Magic weapons a hero carries: {id:"mg_1",n,base,dx,dm,note}. Each becomes a copy of its base weapon with a new name, a damage bonus and a DX bonus (dxb) that
   counts whenever it is readied. Anything unchecked is dropped; returns the list that was accepted. */
function addMagic(list){
  const out=[]; if(!Array.isArray(list)) return out;
  for(const m of list.slice(0,10)){
    if(!m||typeof m!=="object"||!/^mg_\d{1,2}$/.test(m.id)||out.some(x=>x.id===m.id)) continue;
    const b=W[m.base]; if(!b||b.miss||b.hid||m.base==="staff"||m.base==="mg"||/^mg_/.test(m.base)) continue;
    const num=(v,lo,hi)=>{ v=Math.round(+v); return v>=lo&&v<=hi?v:0; };
    const it={id:m.id,n:String(m.n||"Magic "+b.n).slice(0,40),base:m.base,dx:num(m.dx,-3,6),dm:num(m.dm,-3,6),note:String(m.note||"").slice(0,300)};
    W[it.id]=Object.assign({},b,{n:it.n,m:b.m+it.dm,dxb:it.dx,mag:1,note:it.note}); out.push(it); }
  return out; }
return {EDITION:"Melee Third Edition (2018)",RACES,ARMOR,W,SHIELDS,RATE,CAMP_SHIELDS,addCampaign,addMagic};
})();
