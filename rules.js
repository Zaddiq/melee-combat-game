/* Shared rules data for the Melee game site. Edit numbers here only; builder.html, sim.html and arena.html all load this file.
   Sources: Melee weapon table and the Advanced Melee armor chart (leather -2, chainmail -3, plate -6). See NOTES.md. */
const RULES=(function(){
const RACES = {
  human:    {n:"Human",     st:8,  dx:8,  iq:8,  extra:8,  note:"8 / 8 / 8 plus 8 points."},
  orc:      {n:"Orc",       st:8,  dx:8,  iq:8,  extra:8,  note:"Orcs have attributes like men's."},
  elf:      {n:"Elf",       st:6,  dx:10, iq:8,  extra:8,  note:"MA 12 unarmored, 10 in leather; other armor as a man."},
  dwarf:    {n:"Dwarf",     st:10, dx:6,  iq:8,  extra:8,  note:"+1 damage with hammers and axes."},
  hobbit:   {n:"Hobbit",    st:4,  dx:12, iq:8,  extra:4,  note:"+3 DX with missile spells and thrown or missile weapons. +1 damage with thrown or missile weapons."},
  goblin:   {n:"Goblin",    st:4,  dx:4,  iq:10, extra:10, note:"Small, but starts at IQ 10."},
  hobgoblin:{n:"Hobgoblin", st:6,  dx:6,  iq:6,  extra:8,  note:"Fights like a man, but with lower starting attributes."}
};
const ARMOR = {
  none:   {n:"No armor",    stops:0, ma:10, pen:{w:0,m:0}},
  leather:{n:"Leather armor",stops:2, ma:8,  pen:{w:2,m:2}},
  chain:  {n:"Chainmail",   stops:3, ma:6,  pen:{w:3,m:3}},
  plate:  {n:"Plate armor", stops:5, ma:4,  pen:{w:6,m:6}}
};
/* d = dice, m = modifier. two = two-handed. th = may be thrown. */
const W = {
  staff:   {n:"Staff (magical)", d:1,m:0, st:0,  grp:"x"},
  dagger:  {n:"Dagger",        d:1,m:-1,st:0,  th:1, grp:"Melee weapons", note:"1+2 in hand-to-hand"},
  rapier:  {n:"Rapier",        d:1,m:0, st:9,  grp:"Melee weapons"},
  club:    {n:"Club",          d:1,m:0, st:9,  th:1, grp:"Melee weapons"},
  hammer:  {n:"Hammer",        d:1,m:1, st:10, th:1, grp:"Melee weapons"},
  cutlass: {n:"Cutlass",       d:2,m:-2,st:10, grp:"Melee weapons"},
  shortsw: {n:"Shortsword",    d:2,m:-1,st:11, grp:"Melee weapons"},
  mace:    {n:"Mace",          d:2,m:-1,st:11, th:1, grp:"Melee weapons"},
  smallax: {n:"Small ax",      d:1,m:2, st:11, th:1, grp:"Melee weapons"},
  broad:   {n:"Broadsword",    d:2,m:0, st:12, grp:"Melee weapons"},
  morning: {n:"Morningstar",   d:2,m:1, st:13, grp:"Melee weapons"},
  twohsw:  {n:"2-handed sword",d:3,m:-1,st:14, two:1, grp:"Melee weapons"},
  battle:  {n:"Battleaxe",     d:3,m:0, st:15, two:1, grp:"Melee weapons"},
  javelin: {n:"Javelin",       d:1,m:-1,st:9,  th:1, pole:1, grp:"Pole weapons"},
  spear:   {n:"Spear",         d:1,m:2, st:11, th:1, two:1, pole:1, grp:"Pole weapons"},
  halberd: {n:"Halberd",       d:2,m:-1,st:13, two:1, pole:1, grp:"Pole weapons"},
  pikeaxe: {n:"Pike axe",      d:2,m:2, st:15, two:1, pole:1, grp:"Pole weapons"},
  sling:   {n:"Sling",         d:1,m:-2,st:0,  miss:1, grp:"Missile weapons"},
  sbow:    {n:"Small bow",     d:1,m:-1,st:9,  two:1, miss:1, rate:"2 shots/turn at adjDX 15+", grp:"Missile weapons"},
  hbow:    {n:"Horse bow",     d:1,m:0, st:10, two:1, miss:1, rate:"2 shots/turn at adjDX 16+", grp:"Missile weapons"},
  lbow:    {n:"Longbow",       d:1,m:2, st:11, two:1, miss:1, rate:"2 shots/turn at adjDX 18+", grp:"Missile weapons"},
  lxbow:   {n:"Light crossbow",d:2,m:0, st:12, two:1, miss:1, rate:"1 shot every other turn; every turn at adjDX 14+", grp:"Missile weapons"},
  hxbow:   {n:"Heavy crossbow",d:3,m:0, st:15, two:1, miss:1, rate:"1 shot every 3rd turn; every other turn at adjDX 16+", grp:"Missile weapons"},
  mg:      {n:"Main-gauche",   d:1,m:-1,st:0,  left:1, grp:"x", note:"Left hand only. Parries 1 hit from non-missile attacks. DX −2 on defense-only turns; −4 on both attacks if it also attacks. 1−1 in hand-to-hand."}
};
const SHIELDS = {
  small:{n:"Small shield", stops:1, pen:0},
  large:{n:"Large shield", stops:2, pen:1}
};
const RATE = {sbow:15,hbow:16,lbow:18,lxbow:14,hxbow:16};

return {RACES,ARMOR,W,SHIELDS,RATE};
})();
