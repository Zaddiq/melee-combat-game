# Audit against Melee, Third Edition (SJG 2018)

Source: "The Fantasy Trip: Melee Rules, Third Edition", pages cited as (p. N). This replaces the 5th-edition booklet we worked from first.
Status key: **WRONG** = our number or rule differs from 3E. **MISSING** = 3E has it, we don't. **OK** = matches.

## rules.js (shared data) — DONE (armor, weapons, races updated to 3E on Oct 23)
Remaining follow-ups live in the pages: Elf MA 12 also with cloth armor; dwarf +1 damage and hobbit/halfling bonuses in builder/arena code must follow the new race notes; builder armor-source switch can go (pen.w = pen.m now).
| Item | Ours now | 3E | Status |
|---|---|---|---|
| Plate armor | stops 5, DX -6, MA 4 | stops 5, DX **-5**, MA **6** (p. 14) | WRONG |
| Chainmail | stops 3, DX -3, MA 6 | same | OK (after our earlier fix) |
| Leather | 2 / -2 / MA 8 | same | OK |
| Cloth armor | absent | stops 1, DX -1, MA 10 | MISSING |
| Half-plate | absent | stops 4, DX -4, MA 6 | MISSING |
| Large / small shield | 2, -1 / 1, 0 | same | OK |
| Cutlass | 2d-2, ST 10 | renamed **Saber**, same numbers | rename |
| Spear | 1d+2, two-handed | **1d+1**, two-handed | WRONG |
| Halberd | 2d-1 | **2d** | WRONG |
| Heavy crossbow | every other turn at adjDX 16+ | every other turn at adjDX **14+** | WRONG |
| Thrown rock | absent | 1d-4, always available | MISSING (missiles not in arena yet) |
| All other weapons | | match 3E table p. 14 | OK |
| Races, Melee-only | builder uses Wizard race table | Elf min ST 6 DX 10 total 24; Dwarf min ST 10 DX 6 total 24; **Halfling** min ST 4 DX 12 total **22**, +2 DX when throwing; **Goblin** min ST **6** DX **8** total 22; **Hobgoblin** min ST **7** DX 6 total 20; no dwarf damage bonus (p. 22) | DIFFERENT (see question 1) |

## arena.html — rules engine
| Rule | Ours now | 3E | Status |
|---|---|---|---|
| Collapse and death | out at ST 1, dead at ST 0 | **ST 0 = unconscious (out, survives); ST below 0 = dead** (p. 4, 20-21) | WRONG |
| Defending, 4-dice roll | 4 and 5 hit for normal damage | **4 = triple damage, 5 = double** (p. 20) | WRONG |
| Disengage | attacker slower than you loses the DX difference | no such penalty. Only order matters: a faster enemy strikes before you move, a slower one cannot (p. 19) | WRONG (remove penalty) |
| Forced retreat | any free adjacent hex; saving roll if none | enemy must move **one hex farther from the attacker** into a free or fallen-body hex; if none, **no retreat** (p. 20) | WRONG |
| Knocked down (8+ hits) | stands up in next turn's movement | next turn: option stand/crawl, **stands at end of that turn's combat phase**, so is still prone (+4 to hit) during it (p. 7, 20) | WRONG |
| Wound DX -2 (5+ hits) | applies for the whole next turn | applies to its **next attack only** (p. 20) | minor difference |
| Main-gauche parry | -2 DX whenever ready; stops 1 from any non-missile attack | **no DX penalty**; stops 1 hit only from **one-handed non-missile** weapons, front hexes only (p. 13-14) | WRONG |
| Two attacks with left dagger | both attacks at -4 | a separate dagger attack at **-4**; the main attack is not penalized (p. 13) | WRONG |
| Any weapon as second weapon | allowed in dual attack | 3E has only the left-hand dagger for a second attack | WRONG (remove) |
| Choosing the option | choose action after moving | choose the **option first**, then move as it allows; may change mind until the figure acts (p. 6) | equivalent in play, no change needed |
| Charge attack | move up to half MA then attack | same | OK |
| Engaged: shift 1 hex, attack/defend/change weapon/disengage | yes | same | OK |
| Ready weapon: pick up from own hex | yes | own hex **or an adjacent hex**; bending over to pick up leaves you with no front (p. 7, 9) | MISSING (adjacent hex) |
| Facing bonuses, 3d6 rolls, 3/4/5 hits, 16/17/18, damage, armor stops | yes | same | OK |
| Initiative | die, winner chooses order | same | OK |
| XP | 50 per win | to the death: **50, or 100 if the enemy is 4+ points higher** in ST+DX (p. 22) | WRONG (was 70) |
| 100 XP = 1 point, up to 8 points | yes | same; after 8 points see In the Labyrinth | OK |
| Pole weapons: jab at 2 hexes, charge rules, +2 vs charge, extra die | not implemented | pp. 12-13 | MISSING |
| Shield-rush attack | not implemented | p. 13 | MISSING |
| Hand-to-hand, missiles, thrown weapons, spells | not implemented | | MISSING (known) |
| Bodies as obstacles, leaping bodies, -2 standing on a body | not implemented | p. 8, 10 | MISSING |

## builder.html
- Armor list needs cloth and half-plate; plate MA 6, DX -5 (comes from rules.js).
- Main-gauche gear math: remove the "-2 DX parry" and the "both attacks -4" rows. Replace with: parry costs no DX; the extra dagger attack is at adjDX -4 and the main attack is unchanged.
- "One dagger **or** main-gauche" carried free (p. 15). The builder currently allows both a free dagger and a free main-gauche.
- A second weapon in the left hand is only for parrying or swapping; there is no general two-weapon attack.
- Wizard-side numbers (spell table, Wizard armor penalties pen.w, race bonuses) come from the old Wizard scan and are not covered by this booklet.

## sim.html
- Out at **ST 0**, dead at **-1**; sheet notes and the explanatory text say 1 and 0.
- PDF sheet text cites "Fifth Edition (Metagaming, 1981)" and 5E page numbers. 3E: attributes p. 3-4, attacks p. 10-12, armor and weapons p. 14, injury p. 20-21.
- Sheet note "5 or more hits in one turn: DX -2 next turn" becomes "next attack only".
- Armor and weapon lists update automatically from rules.js (cloth, half-plate, plate MA 6, Saber, Spear, Halberd).
- The 17-roll rule in the sim (costs the next turn) is a simplification of "drops the weapon"; fine to keep.

## Suggested order
1. rules.js (small). 2. arena.html engine fixes (ST 0/-1, defend damage, retreat, disengage, knockdown timing, main-gauche, XP). 3. builder.html gear math and armor list. 4. sim.html text and thresholds. 5. Pole weapons and shield-rush in the arena.

## Wizard 2018 reference pages (photos received Oct 23) vs builder.html SPELLS
Checked: IQ 8 through IQ 15 up to 7-Hex Shadow, plus the Monster/Beast table and the range note.
Matches: IQ levels, ST costs and upkeep for nearly all spells seen; summoned creature stats for Wolf, Myrmidon, Bear, Gargoyle, Giant.
Differences / to fix:
1. Monster natural armor is missing from the builder: Wolf 1 hit, Bear 2 hits, Gargoyle 3 hits, Small dragon 3 hits, Dragon 5 hits (Myrmidon, Giant, Giant snake: none).
2. Magic Fist: damage never less than the ST spent, and 6+ hits before armor trips the target (3-die roll on ST or DX, whichever is higher).
3. Giant: spell text says MA 8, Monster table says MA 10 (the book disagrees with itself; pick one, note it).
4. Destroy Creation: RESOLVED, sharp photo says Costs 1 ST (builder correct).
5. Illusion cost: RESOLVED, 2 ST (builder correct).
Not yet seen: Fire cost (cut off), IQ 15-16 remainder (Iron Flesh, Teleport, Summon Small Dragon, Giant Rope, Megahex Avert, 7-Hex Illusion, Summon Dragon, Death Spell, 7-Hex Fire, 7-Hex Wall, Megahex Sleep), Creating a Figure, Fantasy Fighters, Combining Wizard with Melee.

## Wizard 2018 p.21 (Fantasy Fighters, Reactions to Injury) - photo received Oct 24
Races match rules.js (human/orc 32, elf 6/10/8 =32, dwarf 10/6/8 =32, halfling 4/12/8 =30, goblin 6/8/10 =32). Elf MA 12 with cloth or none, 10 in leather. Halfling +2 DX throwing, may throw any weapon the turn readied.
FIXED: hobgoblin was IQ 6 / 26 total; book says min IQ 7, total 28 (now iq 7, extra 8).
Reactions to Injury confirm: 5+ hits in a turn = DX -2 next action only; 8+ = fall down; ST 3 or less = extra -3 DX for the rest of the game; ST 0 unconscious; below 0 dead.

## Wizard 2018 DX Adjustment Table (photo received Oct 23, clear)
Armor and shield (Melee) rows MATCH rules.js: small shield 0, large shield -1, cloth -1, leather -2, chain -3, half plate -4, plate -5, main-gauche 0. Wizard 2018 does carry the armor table, on the DX table page.
Other rows: side +2, rear +4, crossbowman prone +1, pole weapon standing still vs mover/charger +2, standing in hex with a body -2, 5+ hits last turn -2 (not counting spell ST drain), knocked down last turn = DX 0 for most purposes (can only stand or crawl), ST 3 or less -3, Rope -2 and one more each turn, Clumsiness -2 per ST, Dazzle -3, standing in fire -2.
Target: invisible -6, Blurred -4, Shadow hex -4, one-hex flier -4, Giant Snake -3, multi-hex flier -1.
Own handicaps: total darkness or Shadow hex, or missile spell / missile or thrown weapon through Shadow -6. Using Flight: -4 with thrown or missile weapon, -2 with physical weapon or casting any spell.
BUILDER DIFFERENCES to fix:
 a) "Wizard using any weapon except his staff or a dagger: -4 DX" is its own rule. Builder applies -4 to any non-staff weapon (including a dagger) and ties it to the silver checkbox. Split these two rules.
 b) "Wizard whose weapon or armor is iron or steel instead of silver: an extra -4 to Spellcasting and ..." (line cut off at the bottom of the photo) - need the rest of that line.
 c) Shadow: builder text says -6 or -4 but the table says: -6 when YOU are in shadow (or shoot through it), -4 when the TARGET is in a shadow hex.
 d) Giant Snake -3 to hit and flying-figure rules (-4 one-hex flier, -1 multi-hex) are not modeled in the builder.

## Wizard 2018 p.6 (IQ 15 remainder, IQ 16) - photo received Oct 23
Costs and IQ levels MATCH builder: Giant Rope 5, Iron Flesh 3 +1, Megahex Avert 3 +1, Summon Small Dragon 5 +1, Teleport 1 per megahex, 7-Hex Fire 4, 7-Hex Illusion 5, 7-Hex Wall 6, Megahex Sleep 8, Summon Dragon 5 +2/turn.
Text to fix in builder SPELLS:
 - Death Spell: the WEAKER figure goes to ST -1 and dies; the STRONGER loses as much ST as the weaker one had. (Builder says both lose the lower ST: wrong.) Armor, Stone/Iron Flesh do not protect; Spell Shield does. Cost not visible on this page - confirm.
 - Teleport: wizard picks any facing; need not see the target hex; if he arrives in a hex with a solid object (illusions count, images do not) he dies, and so does the object if alive.
 - Summon Small Dragon: add MA 6 ground / 16 air. Summon Dragon: add MA 8 ground / 20 air.
 - 7-Hex Wall: add the note that it can wall in every hex around a figure to trap it (but not entomb in its own hex).
 - Giant Rope: on ST 20+ same as a Rope on a human; on weaker creatures it counts as two Ropes removed one at a time.
General: DX adjustments are cumulative, except an Invisible figure gains nothing extra from Shadow or Blur.
Spell list now fully checked except: Fire cost (cut off in the first photo) and the Death Spell cost.

## Silver rule resolved (Wizard 2018 p.7, photo Oct 23)
"Wizard whose weapon or armor is iron or steel, instead of silver: an extra -4 to Spellcasting ONLY."
Builder fix: the -4 applies to spellcasting DX only, not to physical attacks. Keep it separate from the other rule (wizard using any weapon except staff or dagger: -4 on physical attacks).
Armor/shield column re-confirmed: small shield 0, large -1, cloth -1, leather -2, chain -3, half plate -4, plate -5, main-gauche 0.

## IQ 10-12 block re-read (sharp photo Oct 23)
Create Wall 2, Destroy Creation 1, Illusion 2, Reverse Missiles 2 +1, Rope 2, Sleep 3, Summon Bear 4 +1, 3-Hex Fire 2, 3-Hex Shadow 2, Blast 2, Fire 1: all MATCH builder.
Small text to add: Rope - a figure whose DX is reduced to 2 or less by a rope falls helpless; another figure in an adjoining hex can remove the rope with an adjDX roll on 3 dice. Shadow wording: -6 attacking from/through a shadow hex, -4 attacking into one.
Remaining unverified: Death Spell cost (not shown on the page), Combining Wizard with Melee (p.23).
