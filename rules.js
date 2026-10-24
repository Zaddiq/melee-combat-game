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
const RATE = {sbow:15,hbow:16,lbow:18,lxbow:14,hxbow:14};

return {EDITION:"Melee Third Edition (2018)",RACES,ARMOR,W,SHIELDS,RATE};
})();
