# Melee Game: notes for working on one page at a time

**Rules edition: Melee Third Edition (SJG 2018).** See `AUDIT-3E.md` for what still differs from it.

Read this file first, then open only the page you are changing.

## Files
- `index.html`  Menu with three links.
- `rules.js`    Shared rules data (`RULES`: RACES, ARMOR, W weapons, SHIELDS, RATE). **Change a number here, nowhere else.**
- `builder.html` Character builder (Wizard + Melee). Autosaves one fighter. Has its own SPELLS table.
- `sim.html`    Fight simulator, two fighters, 10,000 duels. Straight combat at range 1 only.
- `arena.html`  Melee Arena: you vs a computer opponent on the two-board hex map, with XP.
- `tests/rules_test.py` Rules checks for the arena (needs Python + Playwright). Run after changing rules.js or the arena.

Every page loads `rules.js` with `<script src="rules.js">` before its own script. All pages keep working from files in one folder.

## rules.js
- `ARMOR[k] = {n, stops, ma, pen:{w, m}}`. `pen.m` is the Melee DX penalty (leather 2, chain 3, plate 6, per the Advanced Melee armor chart). Note: the Melee booklet scan's own table (p. 13) prints chainmail as -4; we follow the Advanced chart and other sources at -3. `pen.w` is the Wizard-rules value the builder can use.
- `W[id] = {n, d, m, st, two?, th?, pole?, miss?, left?, grp, note?}`: dice, modifier, ST needed, two-handed, throwable, pole, missile, left-hand only.
- `SHIELDS[k] = {n, stops, pen}`. `RACES[k] = {n, st, dx, iq, extra, note}`.

## Saved data (browser localStorage; all pages share one origin when hosted)
- `wizard-builder-v1`: the builder's current fighter, JSON: name, cls, race, total, st, dx, iq, spells[], a (right hand), b (left hand), s1 (slung), d1, d2 (sheathed daggers), armor, ep, notes, silver, armorSrc.
- `melee-arena-v1`: arena records by lowercase fighter name: st, dx, total0, pts, wins, losses, ep, banked, pend, must, retired, dead.

## Links between pages
Menu <-> every page. Builder links to Arena and Simulator. Arena links to Builder, Simulator and Menu (also "Back to menu" after each fight).

## Arena status
Done: map, counters with facing, turn engine, attacks and damage, wounds, defend, disengage, forced retreat, record/XP/banked point/retirement at 16 wins.
Not done: hand-to-hand, missiles and thrown weapons, spells, dodge, pole-weapon charge bonus, choosing the opponent, mid-fight save, roster of saved fighters.
Open decision: death rate is high (about 13-23% per fight for good builds), so 16 wins is rare.

## Planned: missiles in the arena (decided Oct 23)
- Both the player and the opponent can use missile and thrown weapons.
- Order: 1) convert basic fight to 2018 Melee, 2) thrown weapons (-1 DX per hex), 3) bows and crossbows (megahex range, reloads, one last shot when engaged).
- Needs: megahex distance, line-of-flight check, Fire action and target pick, reload tracking, AI for when to shoot or close in, new balance run.
- Source: Melee 2018, p.10 and p.15-16.

## Arena status (Oct 24)
Engine converted to Melee 2018: collapse at ST 0 (unconscious, you live), death below 0; defend rolls 4 dice (4 triple, 5 double, 20+ miss, 21-22 drop, 23-24 break); no disengage DX penalty; forced retreat goes one hex farther from the attacker and is skipped if no free hex; knocked down at 8+ hits and stands at the end of the next combat phase; 5+ hits = DX -2 for the next attack only; main-gauche parries one-handed non-missile weapons and gets a separate -4 attack; one dagger or main-gauche only; XP 50, or 100 if the enemy is more than 3 higher in ST+DX; elf MA 12 with cloth or none; no dwarf damage bonus; weapons can be picked up from adjacent hexes.
Tests: python3 tests/rules_test.py (36 checks). Balance run (40 fights each, simple bot): well-armored builds die about 10-22% of fights; unarmored builds die 45-60%.
Not done yet: pole-weapon jab/charge bonus, shield-rush, missiles and thrown weapons, save-with-XP/roster/opponent picker.

## Missiles and thrown weapons (Oct 24, arena)
Done: fire (disengaged, move at most 1 hex), one last shot when engaged, thrown weapons at -1 DX per hex, dodge, megahex range penalties (0-2 MH none, 3-4 -1, 5-6 -2), front-zone rule, no facing bonus for missiles, bows 2 shots at the DX in rules.js RATE, crossbows reload (light every other turn, heavy every 3rd, one turn faster at DX 14+), missile and thrown hits do not allow a forced retreat, main-gauche does not parry them, archer opponents (about 30%) with a slung melee weapon.
Simplifications: arrows are unlimited; a thrown weapon always lands in the target hex; the front zone is the half-plane ahead of the rear hex edges (approximation of the Melee p. 9 diagram); no kneeling or prone fire, no cover from fallen bodies, no hidden movement. Only one enemy on the map, so no line-of-flight rolls.
Not done: pole-weapon jab/charge bonus, shield-rush, spells.

## Saved fighters, roster, hall of fame, opponent picker (Oct 24, arena)
- Records (melee-arena-v1) now keep the builder JSON (src), so any fighter can be reloaded from the Roster card; the last fighter played is resumed on page load (melee-arena-last).
- Hall of fame (melee-hof-v1): written when a fighter wins 16 and spends the last point; kept even if the record is erased. Export/Import roster copies both as JSON.
- "Send to builder (with XP)" writes the updated fighter (stats, total, EP) to wizard-builder-v1 after a confirm. Works because the pages share one site.
- Opponent picker: random matched (default), four preset styles matched to your total, a custom figure, or a roster fighter. XP: 50, or 100 if the enemy is more than 3 higher in ST+DX. Chosen opponents more than 3 lower are exhibitions: nothing is recorded.
- Not done: saving in the middle of a fight; locking earned points when a fighter returns to the builder.

## Pole weapons and shield-rush (Oct 24, arena)
Done (Melee 2018 p. 12-13): jab (spear, halberd, pike axe, not javelin) at the hex two ahead and the two beside it, no DX penalty; charge = move from a non-adjacent hex to an adjacent one; pole charge of 3+ hexes in a straight line gets one extra die; a pole user who stands still (or only turns) against a charge gets +2 DX and the extra die, and pole results in a charge turn are rolled first in adjDX order; shield-rush as an attack (3 dice save if your original ST is at least the target's, 2 dice if weaker, 16-18 or a 12 on two dice always falls, no effect on a target with more than twice your ST, never puts hits on, hits do not allow a retreat). Computer pole users brace instead of walking in, and use jab and shield-rush.
Not done: jab blocked by a figure in the hex between (only one enemy on the map), kneeling and prone positions, hand-to-hand, spells.

## Hand-to-hand (Melee 2018 p. 17-20)
- Option "Move onto the target's hex": allowed if the target is down, has lower MA than you, or you are behind it. You drop weapon and shield (a ready dagger/main-gauche is kept). The defender rolls one die: 1-2 both fall in its hex and it drops its gear; 3-4 same, but it can ready a sheathed dagger; 5 it keeps its weapon and you back up; 6 it hits you automatically and you are driven back. Rear attacks reroll 6.
- Grappling figures share a hex, are down, get +4 DX, and may fight (bare hands 1d-4/-3/-2 by relative ST, dagger 1d+2, main-gauche 1d-1; armor still stops), try to draw a dagger (1-3), or break away (1 die: 1-3 if your DX is higher, else 1; then stand and step to an adjacent hex).
- Not done: back-to-the-wall and "enemy agrees" entry, multi-figure brawls.

## Kneeling and prone (Melee 2018 p. 6, 16)
- Options: drop to kneeling or lie prone (move up to half MA, no attack); or "Kneel and fire" / "Lie prone and fire" (crossbows only prone, +1 DX).
- A kneeling or prone figure does not move, cannot attack in melee, can fire (any bow kneeling, crossbows either) or stand up (on its feet at the end of the turn). Prone = rear hexes everywhere, so attackers get +4; kneeling keeps normal facing. Hand-to-hand may be started against either.
- Not done: crawling 2 hexes, sheltering behind fallen bodies (-4 to missiles).

## Random opponents
makeOpponent follows two rules: (1) the weapon that does the most damage for its ST (best average dice), (2) the most armor and shield it can wear while adjDX stays 11 or more. It tries every ST/DX split for each race and keeps the best by weapon damage, protection and ST, then picks among races, still avoiding matchups where neither side can get hits through. 15% are archers. Against a simple always-attack bot this is much deadlier (about 40-60% deaths, up from 10-20% for armored builds).

## Keeping the Melee arena safe
- `arena.html` is the finished Melee arena and is not touched by spell work. Branch `melee-stable` is a frozen copy of it (same as `main` when spells began).
- Spells are built in `wizard-arena.html` (a copy of the arena), on branch `spells`. It will be linked from the menu only when it works, and it shares the same saved fighters, roster and hall of fame keys unless noted.

## Spells (wizard-arena.html, first batch) - Wizard 2018 rules PDF read
- Casting: roll 3 dice vs adjDX (3-5 auto success, 16-18 miss; 3 triple effect, 4 double). A thrown spell that misses costs 1 ST; a missile spell costs everything put into it; 17 or 18 costs the full price (18 also knocks the wizard down). ST cost is drained like hits but is not counted as hits taken. A wizard may cast down to 0 ST (unconscious) but not below.
- Missile spells (target in front, megahex range penalties, ST 1-3): Magic Fist (1d-2 per ST, min = ST, 6+ hits before armor trips unless 3 dice vs the higher of ST/adjDX), Fireball (1d-1 per ST), Lightning (1d per ST). Armor and shield/flesh protection apply.
- Thrown spells: -1 DX per hex (none on self; target in your hex, adjacent or in front). Blur (-4 to all attacks and spells against it; continuing, 1 ST per turn), Stone Flesh (stops 4, cost 2 +1/turn), Iron Flesh (stops 6, 3 +1/turn), Drop Weapon, Trip, Slow Movement (halves MA, 4 turns), Stop (MA 0, 4 turns), Sleep (until hit; not ST 20+), Freeze (2d6 turns; not ST 30+), Clumsiness (-2 DX per ST, 3 turns), Aid (+1 DX per ST on yourself, 2 turns). Iron or steel armor/weapons instead of silver: extra -4 casting only.
- Continuing spells: a "Renew" step each turn asks which to keep (1 ST each).
- Wizard opponent: "Wizard (spells, matched to you)" in the opponent list; it casts with a simple scorer and keeps a 3 ST reserve.
- Not in yet: Aid on ST/IQ or on others, shaking a sleeper awake, Confusion, Avert, Speed, Shock Shield, Reverse Missiles, Spell Shield, Control, Flight, Dazzle, creation spells, summons, Death Spell, Teleport.
## Duel (two players, one screen) - duel.html
- A copy of the arena engine with both sides human. Player 1 is the engine's "me", Player 2 its "foe". Movement is public and in initiative order; each turn both pick actions in secret behind a "pass the tablet" cover screen, then results are revealed together. All the Melee rules in the solo arena apply (missiles, pole weapons, hand-to-hand, prone/kneeling).
- XP only (Melee 2018 p. 22, arena combat): winner 30, defeated 20, +10 for a side 3 or more points weaker in ST+DX. Escape through your own door (the surrender button was removed; quitDuel still handles both): if you have lost less than a third of your ST you lose 10 XP and the other gets 0 (house rule; the book only says a runaway who is unhurt loses 10), otherwise you get 20 and the other 30. XP goes into the same record as the solo arena (melee-arena-v1, field ep), turns into an attribute point at 100 as there; no deaths, wins or losses are recorded. Fighters come from the builder, a paste, an example, or (read only) the solo arena's roster. `arena.html` is untouched.
- Not done: spells, more than two fighters, hiding the log between picks (the log shows only public events anyway).

## The bench (builder -> sim -> duel)
- localStorage key `melee-bench-v1` holds `{a:<builder fighter>, b:<builder fighter>}`. The builder's Save and load box has "Send to bench as A / B".
- sim.html fills Fighter A and B from the bench on load (name, ST, DX, main weapon, shield, armor; two-handers drop the shield; bows and others it cannot model become a dagger) and says so. Empty bench means the Flavius and Wulf defaults.
- duel.html has "Load bench A / B" buttons that load the full builder fighter.

## Wizard map (maps.js)
- `maps.js` holds WIZARD_HEXES, traced from the Wizard 2018 map PDF (166 hexes: 21 full and 4 partial megahexes, 4 starred entrance hexes in each of two opposite corners, 6 shaded megahexes that are only walls in tunnel play; the shaded flag is stored but not used). Format `[q, r, megahex, entrance, shaded]` in the same axial system as the Melee map, shifted so the megahex lattice matches `mhCell`.
- duel.html and wizard-arena.html have a Map picker (remembered in localStorage `melee-map`); it can only be changed between fights. arena.html keeps the Melee map only.

## Wizards in the duel
- duel.html now has the same spell engine as wizard-arena.html (same first batch of spells). Differences: each player picks spells in secret behind the cover screen; Stone Flesh and Iron Flesh are "secret protection" (the log only says an attempt was made, the status line hides them, and the owner sees their own on their pick screen); continuing spells are renewed one wizard at a time behind a cover screen at the start of each turn.
- Wizards can duel on either map. XP rules are unchanged.

## Spells, second batch
Added to the Wizard arena and the duel: Speed Movement (self, 2 ST, doubles MA for 4 turns; cancels Slow Movement), Dazzle (special, 3 ST, −3 DX for 3 turns, within 5 megahexes; not added on top of Blur's −4), Blast (special, 2 ST, 1 die to the enemy next to you, armor and Stone/Iron Flesh stop it), Break Weapon (3 ST, weapon does half damage, shield or staff is destroyed), Remove Thrown Spell (2 ST, on the enemy or on yourself: ends Blur, Stone/Iron Flesh, Slow, Stop, Speed, Clumsiness, Aid, Sleep, Freeze), Spell Shield (3 ST +1 a turn, nothing can be cast on you, and you cannot cast on yourself; a spell that is stopped still costs the caster its full price) and Death Spell (the weaker of the two dies, the stronger loses the weaker's ST; equal ST kills both; a Spell Shield costs the caster just 1 ST).
- Special spells (Blast, Dazzle) are like thrown spells: a miss costs 1 ST.
- In the duel, Spell Shield is secret like Stone and Iron Flesh and is renewed in secret.
- Broken weapons are tracked by weapon id, so picking up another weapon of the same kind keeps the break. Shock Shield and Confusion are still to do, as are the summoning spells and images and illusions.
- Tests: S25 to S35 in tests/spells_test.py.

### Reverse Missiles
2 ST, +1 a turn, IQ 11. Missiles, thrown weapons and missile spells that hit the subject hit the sender instead (same damage, the sender's own armor). It does nothing against melee blows. If both are protected the missile harms no one. A fast archer's second arrow is not fired once the first has turned back. In the duel it is secret, like Stone Flesh. Tests S36 to S38.

### Flight
3 ST, +1 a turn, IQ 13, cast on yourself. The wizard takes off at the start of next turn: MA 6 on the first turn in the air, then 12. Fliers and ground figures do not engage each other (two fliers do), so a flier moves freely around a ground figure (it cannot yet fly over its hex). Attacks and spells aimed at a flier are −4 DX; a flier is −2 on melee attacks and on casting at others, −4 with missile or thrown weapons. A flier cannot be tripped or grappled. When the wizard stops renewing, or Remove Thrown Spell or Sleep hits, it lands and cannot move on the ground that turn. The computer wizard does not cast Flight. Tests S39 to S41.

### Teleport
Special spell, IQ 15. You pick the hex on the map after choosing the spell; it costs 1 ST per megahex moved (at least 1) and needs a to-hit roll on your adjDX with no range penalty (a miss costs 1 ST, a fizzle the full price). You arrive facing the enemy and leave any hand-to-hand. You cannot pick the enemy's hex (the rules would kill both of you), and nothing else on this map is solid. Spell Shield does not stop it, since it only moves you. The computer wizard does not cast it. Tests S42 and S43.

### Creation spells (first part: Fire, Shadow, Create Wall, Rope, Destroy Creation)
Creation spells need the to-hit roll on your adjDX with no range penalty; a miss costs 1 ST. A thing can appear in the caster's megahex or any megahex next to it, in a hex the caster can see into (a wall hex blocks the view). You choose the hex on the map. Created things last 12 turns (the optional time limit).
- **Fire** (1 ST, IQ 9): passing through a fire hex is 2 hits, stopping in one is 4 hits and −2 DX that turn; armor and Stone/Iron Flesh come off the total. A figure in the hex when it appears takes 2. The computer will not walk into fire. Fire is worked out for the end hex of a move by the shortest path found, so a route is not chosen to avoid it.
- **Shadow** (1 ST, IQ 10): attacks into it are −4 DX, attacks from it −6 (melee, missiles and spells).
- **Create Wall** (2 ST, IQ 11): a solid hex nobody can enter, and it blocks missiles, thrown weapons and spells aimed past it. It cannot be put on a figure. Lightning does not blast through it yet.
- **Rope** (2 ST, IQ 11): on an enemy in range, ST under 20. MA halved, DX −2, one worse each turn; a figure that stands still and does nothing else may roll its adjDX or less on 3 dice to break free; DX 2 or less leaves it helpless. The computer wizard uses Rope and struggles free. Another figure freeing a roped one is not in.
- **Destroy Creation** (1 ST, IQ 11, thrown): removes one fire, shadow or wall.
Not yet: summoning spells, images and illusions, the multi-hex versions. The picks for these spells use the same map-click step as Teleport. Tests S44 to S50.

## Many figures, and summoned creatures (Wizard arena only so far)
The Wizard arena now holds a list of figures (G.units) instead of just you and one enemy. Each has a side, finds its nearest living enemy as its target (other(u)), and the movement code treats every figure as an obstacle. The Melee arena and the duel are unchanged. This is the base for team play later (two players against three creatures): the creatures are computer-run figures just like the summons.
- **Summons** (Wolf 2 ST IQ 9, Myrmidon 2 ST IQ 10, Bear 4 ST IQ 11, Gargoyle 4 ST IQ 13, Giant 4 ST IQ 14, each +1 ST a turn): a creation spell, so a to-hit roll with no range penalty and a free hex in your megahex or next to it. The creature cannot move or fight on the turn it appears. It is run by the computer on its owner's side. When you do not pay its 1 ST in the renew step it vanishes; at 0 ST it dies. The Gargoyle flies (see Flying Gargoyle below). Dragons are not in.
- **Targets:** with more than one enemy on the map, the nearest is your default target; click another enemy counter (dashed ring) to change it. Spells, missiles and attacks go at the chosen target.
- **Not in for minions:** hand-to-hand (they cannot grapple and cannot be grappled), forced-retreat choices for your own minions (done automatically), controlling a creature yourself (they attack the nearest enemy), and dragons.
- Tests S51 to S55.

## Random opponents, eased back
The "always the best weapon, always the most armor at adjDX 11" rule made the arena too hard. The arena and Wizard arena now use the original random generator again, but keep three acceptable fighters and take the best of them (more damage plus 0.7 per hit stopped). That is a little tougher than a pure random pick, not a maximised build. The "winnable for both sides" checks are unchanged.

### Summons and many figures in the duel
The duel now uses the same figure list as the Wizard arena. Summoned creatures are run by the computer on their owner's side, move after their owner moves, and pick their own actions. Each player has a default target (the nearest enemy) and can click another enemy counter, with the dashed rings, while moving or choosing an action. Creature upkeep (1 ST each, in the secret renew step), vanishing, and retreat rules are as in the Wizard arena. XP, escape and "quit" still only involve the two players' own figures. Tests: tests/duel_summon_test.py (D1 to D5).
Still not in: giving orders to a creature, creatures in hand-to-hand, dragons.

### Images and illusions (one-hex versions)
- **Image** (1 ST, IQ 8) and **Illusion** (2 ST, IQ 11): a creation spell like the summons, so a to-hit roll, no range penalty, and a free hex in your megahex or next to it. You pick which creature it looks like (Wolf, Myrmidon, Bear, Gargoyle, Giant). The log says only "a creation spell", so the other side cannot tell a summon from an illusion or an image. Nothing here costs upkeep.
- An **image** does no damage. If it hits, or is hit by a weapon, a missile or a Magic Fist or Blast, it vanishes. A Death Spell destroys it for 1 ST.
- An **illusion** has the real creature's ST, DX and weapon and can hurt and be hurt like it. Damage it did stays real when it vanishes.
- **Disbelieve** is a new action for a human-type fighter (not creatures, images or illusions): move at most 1 hex, pick a creature, and its owner secretly rolls 3 dice against the disbeliever's IQ. At or under the IQ, an image or illusion vanishes; a real creature just stays. Nobody is told the result unless it vanishes. The computer disbelieves a creature about a third of the time it can.
- **Dispel Illusions** (5 ST, IQ 14): every image and illusion within 5 megahexes vanishes, yours too.
- Hidden information: the "keeps … going" log line is gone, only the owner's renew screen lists real creatures, and in the duel an owner only sees "(your illusion)" on their own pick screens. In the Wizard arena the stats line tells you which of your own creatures are fake.
- Not in: doubles of a real figure (yourself included), larger images and illusions, walls, fire or shadow made as illusions, moving through an image to destroy it (you just cannot enter its hex). Tests S56 to S62.

## Confusion and Shock Shield
- **Confusion** (IQ 9, thrown, n ST): the subject loses 2 IQ per ST for 3 turns (1 turn if ST 30+... same multiplier as other thrown spells). While confused he cannot cast any spell whose IQ is above his lowered IQ; running spells can still be renewed; Disbelieve rolls use the lowered IQ. The computer casts it only at wizards.
- **Shock Shield** (IQ 10, 2 ST, +1/turn): a running spell on the caster. At the end of each turn every other figure in the caster's hex takes 1 die, reduced by armor/protection. Secret in the duel.
- Tests S63–S66.

## Spending earned points on IQ
Wizards in the Wizard arena now get a +1 IQ button beside +1 ST / +1 DX when they earn an attribute point. The new IQ is stored in the record, used in later fights, and carried in Send to builder / Copy updated fighter / hall of fame.

## Avert
Thrown at a victim, 2 ST to cast and 1 ST a turn to keep (shown in the caster's renew step; ends if the caster dies or drops it). The victim's move is restricted to hexes at least 2 farther from the caster than where he started; if he cannot get 2 farther he goes as far as he can, and being engaged does not hold him (he disengages). If he cannot get any farther he rolls 3 dice against DX or falls down. The computer moves away automatically. Remove Thrown Spell clears it. Tests S67–S70.

## Fixes: creature weapons leaking, targeting, explanations
- Random opponents (arena and duel) could be handed the creature natural weapons (Bite, Club 3 dice, Fist 2 dice), so hobbits bit and some foes did almost nothing. The melee weapon list now skips creature weapons.
- Automatic targeting now prefers an enemy in the figure's front hex (an attack is impossible against one at the side or rear), so your minions and you less often "can't attack".
- When you cannot attack because the target is not in front, or cannot cast because you moved more than 1 hex, the log now says so.

## Control Person and Control Animal
- Thrown spells: Control Person IQ 13, 3 ST + 1/turn; Control Animal IQ 11, 2 ST + 1/turn. Person works on humanoids (men, Myrmidon, Gargoyle, Giant), Animal on Wolf and Bear. Neither on a dragon (none exist yet).
- To-hit as for other thrown spells; then the victim rolls 3 dice against IQ (lowered IQ if confused). Saves: the caster loses only 1 ST and nothing happens. Fails: the figure joins the caster's side while he pays 1 ST per turn (renew step). An image or illusion that is hit simply vanishes.
- The computer runs controlled figures (it picks their moves and attacks). A controlled figure ordered to attack a foe with more than twice its ST gets another IQ save each turn; passing breaks the spell.
- A controlled summoned creature vanishes when its new master stops paying (or dies, or it is killed); its original summoner stops paying. Control can be taken over by another wizard.
- Arena: Control Person may also be cast on the computer's main fighter. While controlled he has no friends to attack, so he simply holds still. Duel: only creatures can be controlled, not the other player's wizard. Computer wizards cast it only on creatures.
- Tests S71–S77.

## Invisibility (simple version)
- IQ 12, 3 ST + 1/turn, on yourself only (not on allies yet). Attacks and spells at the invisible figure are −6 DX; this does not add to Blur, Dazzle or Shadow (the worst applies). Remove Thrown Spell ends it. The figure's token stays on the map but is drawn faint.
- The book's hidden movement (counter removed from the map, revealed when adjacent, attacking, wounded or in fire) and Mage Sight are not in. Tests S78–S81.

## Mage Sight
IQ 12, 2 ST + 1/turn, on yourself only. While it runs, your melee, missile and spell attacks ignore the DX penalties for a target that is Blurred, Invisible or in Shadow. Remove Thrown Spell ends it. Secret in the duel. Tests S82–S84.

## Slippery Floor
- IQ 13, 3 ST, thrown at a megahex (a hex and its six neighbours). You pick the centre hex; the to-hit number is your DX minus the hexes from you to that centre. It lasts 12 turns like other created things. It is a secret protection: the other side cannot see it on the map (and the log says "a secret protection") until some figure rolls on it, then it is shown to everyone.
- Every figure standing in the area when it is cast, every figure that enters a slick hex (each hex on its path counts, as with fire), and every figure that stays still in one, rolls 3 dice against DX or falls. A fallen figure on the slick floor must roll DX each turn to start to stand up. Fliers are unaffected. The computer will not step on slick it can see or cast itself.
- Not in: crawling out of the slick without a roll (a fallen figure just keeps trying to stand); the exact hex of the fall along a path (a figure falls where it ends its move). Tests S85–S90.

## Giant Rope
- IQ 15, 5 ST, a creation spell cast like Rope (to-hit on your adjDX, no range penalty, target within your megahex or the next one, not through a wall). Wizard 2018 Spell Reference Booklet, p. 5.
- On a creature of ST 20 or more it is exactly one ordinary Rope (MA halved, DX -2, one worse each turn). On a weaker creature it is two Ropes at once: MA halved twice (a quarter), DX -4 at first and two worse each turn, and each rope is removed separately. Each successful "stand still and roll adjDX or less on 3 dice" takes off one rope; the second needs its own turn and roll. A figure whose DX falls to 2 or less falls helpless (two ropes make that easy).
- Plain Rope still does not work on ST 20 or more, and a Spell Shield does not stop either spell (the booklet says it does not protect against magic ropes). A figure that is already roped cannot be roped again. Both spells are in the Wizard arena and the duel.
- Implementation: `u.rope` is still the age counter, `u.ropeN` is how many ropes (1 or 2), `ropeNum(u)` reads it. The computer wizard's own IQ stops at 14, so it never casts Giant Rope; the scorer has a case for it anyway.
- Not in (also true of plain Rope): a figure in an adjoining hex standing still and rolling its own adjDX to free someone else's rope. Tests S91-S97 and D6.

## Reveal Magic
- IQ 9, 1 ST, a special spell (Wizard 2018 Spell Reference Booklet, p. 2): to-hit on your adjDX with no range penalty, a miss costs 1 ST. It is aimed at nobody, so a Spell Shield does not stop it.
- It shows the caster which enemy figures within 5 megahexes are protected by Reverse Missiles, a Spell Shield, Stone Flesh, Iron Flesh or a Shock Shield (who they are on, not who cast them), and marks every slippery floor within 5 megahexes. It says nothing about whether a figure is real, an image or an illusion.
- Arena: the result goes in the log. Protections are already shown in the arena's status lines, so in practice it is the slippery floors that it uncovers; the floor is drawn for you only and the computer does not learn of it.
- Duel: the log only says the spell worked. The caster alone is told what it found, in the note at the top of their pick screen on the next turn (it lasts that one turn), and any floors are drawn for that player only (`o.g.seen` lists the sides that were shown a floor). Not told: Mage Sight, Invisibility, Blur (not secret or not in the spell's list).
- The computer wizard never casts it (not in its spell list). Tests S98-S101, D7, D8.

## Flying Gargoyle
- Wizard 2018 monster table: Gargoyle MA 8 on the ground, 16 in the air. A Gargoyle (real, illusory, or the copy of one) is a natural flier: `m.natFly`.
- It uses the same "in the air" state as the Flight spell (attacks on it -4, no engagement between fliers and ground figures, cannot be tripped or grappled), but: MA is 16 from the first turn (the Flight spell's 6 then 12 is only for the spell), it takes off and lands at no cost and without losing its move, and it has no -2 handicap of its own (the booklet puts "not used to flight" on the Flight spell only; this is our reading).
- The computer decides at the start of its movement: foe 3 or more hexes away, it takes to the air; closer than that, it lands to fight. It attacks from the air on the turn it closes in, so its first blow lands with the -4 cover. The log says when it takes off or lands.
- It still cannot fly over another figure (known limit; it paths around). Natural fliers are not slowed by landing. Not in: orders to a Gargoyle (none for any creature yet), a human choosing when it flies. Tests S102-S105, D9.

## Fighter card: damage row and old warnings (Oct 26)
- The card (opponent and your own fighter) listed damage only for non-missile weapons, so an archer or a wizard with empty hands showed "Damage: none". It now lists every weapon in hand (and a slung one), marks missile weapons "(missile)", and says "none in hand (spells)" for a wizard with nothing in hand. Wizard arena and duel; `arena.html` is frozen and keeps its old card.
- The Wizard arena still warned that "missile weapons are not in the arena yet" and "hand-to-hand is not in the arena yet". Both are in; the warning now only says when a fighter carries no melee weapon and no bow. Tests S106, S107.
- Reminder when reading logs: "No damage gets through" is a real result, not a bug. A small bow does 1d-1 (it can roll 0, and any armor stops 1-3 hits), and a Gargoyle's hide stops 3.

## Builder layout (Oct 26)
- Step order is now 1 Race and class, 2 Attributes, 3 Armor and weapons, 4 Spells (spells last, so the long list is at the bottom).
- The top of the character sheet (right column) holds a toolbar: links to Menu, Melee Arena, Wizard Arena, Melee Duel and the Fight simulator; then Print or save as PDF, Copy data, Copy sheet as text, Send to bench as A / B; then a folded "Load a saved character" box with the data text and "Load from box". The status message ("Data copied.", "on the bench as A") shows right under the buttons. If copying to the clipboard fails, the box opens by itself with the text selected.
- The toolbar is hidden when printing; the printed sheet is unchanged. All buttons are found by id, so their code did not change.
- Still on the list (owner asked for more layout tweaks later): spell list length, the sheet column being taller than a short window, and the single-column stacking below 860 px (tablet portrait).

## Page names (Oct 26)
- The owner kept both arenas and renamed them: `arena.html` is **Arena Classic** (fighters, Melee rules only, still frozen) and `wizard-arena.html` is **Unlimited Arena** (everything in Classic plus spells, wizard opponents and summoned creatures; the "beta" label is gone). File names and links did not change. Older notes above still say "Melee arena" and "Wizard arena" for these two pages.
- Decision: do not merge the two pages. Considered and put aside: renaming `wizard-arena.html` to `arena.html` after a bot-vs-bot outcome comparison (the 70 Classic rules checks already pass 70/70 against the Unlimited Arena).

## Natural weapons cannot be dropped or broken (Oct 27)
- A summoned creature's bite, claw, fist or club (the weapons flagged `hid`) is part of the creature. Before this fix a Wolf or Bear that rolled 17 "dropped the bite" and one that rolled 18 "broke" it, then fought with nothing for the rest of the fight (about a 2% chance per attack). Now a 17 or 18 with a natural weapon is only a miss.
- Drop Weapon does nothing to a natural weapon (it can still drop a Myrmidon's sword), and Break Weapon finds "nothing to break" on a creature that has only a natural weapon. Fixed in both the Unlimited Arena and the duel. Tests S108, S109.

## Creature opponents in the Unlimited Arena (Oct 27)
- Single creature only (Wolf, Bear, Gargoyle, Giant), picked in the opponent list under "Creatures (always an even match)". Stats come from the `CRE` table; hides are armor, natural weapons are `hid`.
- Always counted as an even match: a win is 50 EP and is recorded, never an exhibition. Random opponent: a creature only when its book ST+DX is within 2 of the player's (Wolf 24, Gargoyle 31, Giant 39, Bear 41; stats are not scaled), and then a 20% chance; otherwise a normal random human.
- The gargoyle is a natural flier. Control Animal works on Wolf/Bear, Control Person on Giant/Gargoyle (`ctlOK`).
- Arena Classic and the duel are unchanged.
- Tests: spells_test S110-S115; fuzzer `tests/fuzz/creaturefz.py` (48 fights).
- Fights 14 to 16 of a champion's run (13 to 15 wins): a Gargoyle can be the random opponent at any ST+DX (same 20% chance, still an even match worth 50 EP).

- Random opponent is a wizard one time in four (after the creature check); before this a wizard came only from the opponent list. Test S117; wzfz2.py fuzzes wizard foes.

## Two Wolves test (Oct 27)
- Opponent list: "Two Wolves (test: a pack of 2)". The pack is a second full Wolf on the foe side (`m.pack`, not a summon: no upkeep), moved and played by the computer. The fight ends only when every foe figure is down; Control Animal can take a pack wolf (a controlled wolf stops counting against you). Always an even match, 50 EP. Only Wolf x2 is in the picker; the engine takes `foe.packN` for any creature.
- Tests S118-S119; creaturefz.py now mixes in packs. This is the first step toward the encounter module (several monsters on one side).

## Multi-hex figures, stage 1: the 4-hex dragon (Oct 27)
- Unlimited Arena only. Opponent list: "Small Dragon (test: 4 hexes)". Placeholder stats (ST 30, DX 12, IQ 12, claw 2d-2, scales stop 3, MA 8); the real scenario numbers will come from local data, not this repo.
- A big figure has `u.size` (4), `u.q,u.r` = its tail hex and `u.f` = which of six pointing directions it has (between two hex directions). `cells(u)` is its footprint (a diamond: tail, two flanks, head). `dist`, `same`, `relOf`, `relFar`, `faceToward`, `inFront` and `engagedAny` now work on whole footprints, so the old attack code works unchanged. One-hex figures behave exactly as before.
- Zones (matches the Wizard 2018 diagram counts): of the 10 hexes around the diamond, the 4 beyond the head are front, the 2 at its widest are side, the 4 behind are rear (`bigZone`).
- Engagement: a one-hex figure is engaged by a big one if it stands in one of its front hexes. A big figure is engaged only when 2 one-hex figures have it in their front hexes (or 1 big figure).
- Movement (`reachBig`): it moves as one rigid piece: slide one hex in any direction, or pivot a sixth of a turn about its tail or head. A step costs the farthest any part moves (straight = 1 per hex, a pivot about the tail = 2). It must stop as soon as it is engaged; engaged, it may only shift one hex. It cannot enter another figure's hex yet (pushing back small figures is stage 2). `placeBig` sets it up on the board.
- A big figure is never forced back and does not follow up; no hand-to-hand with it.
- Not done yet (next stages): second claw, fire breath, tail lash, stomp, push-back; flight (the rulebook lets a flier pass over figures, fires and walls; fixes the "fliers can't pass over a figure" limit); the 7-hex dragon. The Wizard counter sheet shows the 7-hex dragon counter is a long narrow strip, not a round 7-hex flower: model it from that counter. No Control spell works on a dragon.
- Tests S120-S124; `tests/fuzz/creaturefz.py` now mixes the dragon in and checks that a big figure stays whole, on the board and clear of other figures.

## Multi-hex figures, stage 2: the dragon's attacks (Oct 28)
- Claws: a dragon strikes twice a turn with its claw (2d-2 for the small dragon), at the same or another target in its front hexes (second strike in the second pass of `resolveTurn`).
- Fire breath (`doBreath`, option `breathe`): 2 dice for the small dragon (3 for a full dragon), costs 3 ST (5), needs the dragon's adjDX minus 1 per hex from its head to the target, works at any range and any direction, and armor stops hits as for fire. The computer breathes when no claw target is in front, or 30% of the time when it has more than 12 ST.
- Tail lash (`tailLash`): every turn while on the ground, whatever the dragon does, one roll at its adjDX against each one-hex enemy standing in a rear hex; a hit makes that figure roll 3 dice against its DX or fall. No damage.
- Push-back (`bigPush`, `doPush`): a dragon may end its move (or its shift) by moving one hex onto one-hex figures if their combined ST is below its ST and each has a free hex to step to. Each rolls 3 dice against DX: success steps aside and acts normally, failure falls and does nothing else that turn (a fallen figure skips its action; it stands up next turn). Tests: S125-S128. Pushed figures step to the free adjacent hex nearest the dragon.
- Not done: the stomp (it is a scenario-specific note in the Silver Dragon creature table, not in the Wizard rulebook), flight, the 7-hex dragon.

## Multi-hex figures, stage 3: flight and the fly-over rule (Oct 28)
- Wizard 2018 p. 8: "A flyer may freely go over another figure, a fire, a wall, etc." In the Unlimited Arena a flying figure (Flight spell, natural fliers, a flying dragon) now passes over other figures and created walls and takes no fire or slippery-floor effect on the way, but can only END its move on an empty, non-wall hex (`reach`, `reachBig`). The old limit "fliers can't pass over another figure" is gone here. The duel and Arena Classic still have it.
- Natural fliers: `u.natFly` is true (Gargoyle, air MA 16) or the air MA itself (the test Small Dragon, 20, set by `CRE.sdragon.fly`). The computer's flier takes to the air when the foe is 3 or more hexes off and lands to fight (`aiMoveBig` for the dragon, `aiMove` for the Gargoyle). A grounded figure is not engaged by a flier and vice versa.
- Tests S129-S132.
- Still not done: the 7-hex dragon, the stomp, orders and the encounter page itself.

## Multi-hex figures, stage 4: the 7-hex Dragon (Oct 28)
- Opponent list: "Dragon (test: 7 hexes)". Placeholder stats (ST 60, DX 12, IQ 14, claw 3d-3, scales stop 4, MA 8, air MA 20, breath 3 dice for 5 ST); the real scenario numbers stay in the owner's local data, not in this repo.
- Shape, read from the Wizard counter sheet 4 outline: two 4-hex diamonds chained end to end, sharing one hex. Columns of 1, 2, 1, 2 and 1 hexes (tail, wing pair, middle, wing pair, head), a long narrow strip pointing between two hex directions like the 4-hex diamond. `fpAt(q,r,f,size)` builds either shape; `headOf(u)` is its last cell. `u.size` is 4 or 7.
- Zones around the 14 hexes that touch it: the 4 beyond the head are front, the 4 beyond the tail rear, the 6 along its flanks side (`bigZone`, same rule as the 4-hex diamond but scaled by its length). This is my reading of the rule, not copied from a diagram: check it against the Wizard 2018 dragon diagram.
- Movement: slide one hex in any direction, or pivot a sixth of a turn about its tail, its head or (7-hex only) its middle hex. A step costs the farthest any part moves. Everything else (engagement, push-back, tail lash, fire breath from the head hex, flight and the fly-over rule) uses the stage 1 to 3 code unchanged.
- Tests S133-S138; `tests/fuzz/creaturefz.py` now mixes the 7-hex Dragon in (72 games) and checks every big figure stays whole.
- Still not done: the stomp, orders and the encounter page itself.


## 7-hex dragon art (Oct 28)
- The 7-hex Dragon token is drawn with original art (`dragonArt`, head toward +x on the flat-top strip); a dead Dragon shows an original skull-and-crossbones (`skullArt`), the counter's back-side idea. The owner's Wizard counter sheet is a reference for the footprint only; none of its artwork is copied or committed.

## Summon Small Dragon and Summon Dragon (Oct 28)
- Source: Spell Reference Booklet p. 5-6 (spells) and p. 8 (creature table), Wizard 2018 p. 21 (dragon attacks). Small Dragon: IQ 15 spell, 5 ST then 1 a turn; 4 hexes, ST 30, DX 13, IQ 16, MA 6 ground / 16 air, scales stop 3, claw 2d-2, breath 2 dice for 3 ST. Dragon: IQ 16 spell, 5 ST then 2 a turn; 7 hexes, ST 60, DX 14, IQ 20, MA 8 / 20, stops 5, claw 2 dice, breath 3 dice for 5 ST.
- Data: `CRE.bsdragon` and `CRE.bdragon` (book numbers, `up` = upkeep). The older `sdragon` and `dragon` stay as the placeholder test opponents.
- Placement (changed Oct 29, see the multi-hex section below): you pick the tail hex; only the tail has to be in your megahex or the ones next to it, the rest of the creature may stick out but must be on the board on free hexes. (Oct 28 version required every hex inside the area; the owner found it too crowded next to a big opponent.) It is turned to face the enemy as nearly as it fits. It cannot act on the turn it appears (`fresh`), like any summon.
- Upkeep is per creature (`upOf`): 1 ST, or 2 for the Dragon, at the renew step; the computer pays the same.
- Image and Illusion are only offered as one-hex creatures (before this they could make a one-hex "dragon"); multi-hex images and illusions are still to do.
- Computer wizards can cast them (only with ST for 5 plus about 10 or 14 spare). No Control spell works on a dragon (not in the Animal or Person lists).
- Tests S139-S145. The duel port and the 4-hex art are below.

## Small Dragon art and the dragons in the duel (Oct 28)
- Small Dragon: original 4-hex token art (`smallDragonArt`, unit coordinates, hex radius 1, head toward +x) in both pages; a dead 4-hex or 7-hex dragon shows the skull (`skullArt`). Dragon art is all original; the owner's Wizard counter sheet is only a reference for the footprint.
- `duel.html` now has the multi-hex engine (ported from the Unlimited Arena: footprints, rigid movement, flight, breath, claws, tail lash, push-back) plus Summon Small Dragon and Summon Dragon with the same rules, per-creature upkeep (renew list shows 2 ST for the Dragon) and the same map tokens. Players' own fighters are always one hex, so only computer-run summoned dragons are big and there is no player move UI for big figures. The duel's action names now include "breathe" (it logged "undefined" before).
- Tests: `tests/duel_summon_test.py` D10-D13. Fuzzer: `tests/fuzz/dsum.py` with the dragon spells added ran clean (no errors or bad log text, 3 runs of 30 duels).

## Multi-hex Image and Illusion; tail-only placement (Oct 29)
- New spells (Spell Reference Booklet): 4-Hex Image 2 ST (IQ 13), 4-Hex Illusion 3 ST (IQ 14), 7-Hex Image 4 ST (IQ 15), 7-Hex Illusion 5 ST (IQ 16). `SP[..].mh` = hexes covered; `formsFor(d)` lists what a spell can copy: the one-hex creatures, plus the book Small Dragon (4-hex spells and up) and book Dragon (7-hex spells). The placeholder test dragons are never offered. Plain Image and Illusion stay one-hex. Both pages.
- They reuse the dragon summon code: a fake big creature has the real stats (Small Dragon ST 30 etc.), is placed whole facing the enemy, cannot act the turn it appears, has no upkeep, and uses the existing image rules (an image vanishes when hit and does no harm; an illusion fights and takes damage until disbelieved or killed). Added: an image dragon that breathes vanishes without harm, breath that hits an image makes it vanish, an image's tail lash and push do nothing.
- Placement rule for every big summon, image and illusion: free hexes on the board for the whole creature, tail hex in your megahex or the ones next to it, the rest may stick out (the owner's request, Oct 29: it was crowded next to a big opponent).
- Menu: a known big summon/image/illusion with no legal place is named in a note ("No room right now for ...") in the pick and spell screens instead of silently missing.
- Computer wizards value illusions of dragons (AI values in castList: bsdragon 4.8, bdragon 6.0).
- Tests: S146-S151 (arena), D14 (duel). Fuzzer `tests/fuzz/creaturefz.py` with the new spells added ran clean (3 x 72 fights).
- Not done: 3-Hex Fire/Shadow/Wall, 7-Hex Fire/Shadow/Wall, Megahex Avert and Megahex Sleep.
- Owner question (Oct 29): a Gargoyle illusion beat a 7-hex Dragon opponent. In my simulation (elf wizard ST 12 DX 13 IQ 16, Illusion of a Gargoyle on turn 1, then standing still) the placeholder test Dragon (ST 60) wins 40 of 40 fights, usually in 2 to 5 turns, so a win needs something else (own dragon, other spells). Waiting for the owner's log.

## Colosseum: 2 to 4 players (Oct 30, branch colosseum)
- `colosseum.html` is a copy of the duel page taught to run 2 to 4 players. `duel.html` is unchanged and stays the two-player duel. It shares `rules.js`, `maps.js`, the builder, the bench and the XP records with the rest of the site.
- Players and modes: a Players box (2 to 4). With 3 or 4 players a mode box picks **Free for all** (everyone alone, each from their own entrance: south, north, west, east) or **Teams** (two sides, Team A at the south end, Team B at the north end; each player picks A or B, so 2v2, 2v1 or 3v1). No mixing the two (a team game with a lone third side was confusing). The west and east entrances are the four edge hexes nearest the middle of the west or east edge of the board (not the starred ends); they are shaded like the starred hexes while in use. Teammates start on different hexes of their end. Everyone starts facing their nearest enemy. Colors: green (lime in dark mode), blood red, deep blue, orange; each counter also carries a round badge with the first letter of the figure's name (two letters, like Bo and Be, when two players' names start alike).
- State: `G.players` (player figures in seat order), `team[]`, `starts[]`, `NP`; `G.me` / `G.foe` are players 1 and 2. `sideOf` is a team id; `ownerOf(u)` is the player who runs a figure (summoner or controller). Creatures vanish when their owner falls or leaves, and move right after their owner.
- Turn flow: every living player rolls initiative (no ties); the winner chooses first or last; moves follow that order; then each player picks in secret, one after another ("Everyone else, look away"); then all resolve together. Spell renewal is one player at a time.
- Ending: when only one side has anyone standing; that side wins together. XP: winner 30, anyone who went down 20, +10 if some opponent is 3 or more points stronger (ST+DX); an unhurt escaper -10 and anyone who beat only escapers gets 0. Escaping leaves the board and the rest fight on (the duel ends if one side is left). Control Person still cannot take over a player's own figure.
- Escape: a player may leave from any hex of their own entrance (the start hexes of their end or edge).
- Tests: `tests/colosseum_test.py` (M1 to M31), fuzzer `tests/fuzz/colosseumfz.py` (20 random 3 and 4 player games per run, free for all and teams, flags any attack on an ally; a few games stalemate). `tests/duel_summon_test.py` also passes against `colosseum.html` (run with the path changed).
- Not done: tablet host and phone controllers (room code, secret picks on each phone, bell on the tablet, phone map for hex picks, reconnects); there is no link to the Colosseum from the other pages except the menu.
## Builder: New character button (Oct 30, branch builder-new-char)
- A "New character" button at the top of builder.html starts a Human fighter at ST 8, DX 8, IQ 8 with 8 points left to spend (total 32), no name, no spells, no gear. It asks before replacing a character that has been changed or named. Tests: `tests/builder_test.py` (B1 to B9).


## Colosseum: computer creatures (Oct 31)
- Setup has a creature picker (None, Wolf, Myrmidon, Bear, Gargoyle, Giant, Small Dragon, Dragon) and a count: up to 3 of one kind, 2 Small Dragons, 1 Dragon. With a creature chosen, all the human players are one team (south end) against the creatures (north end, side "mob", charcoal color, no owner). The Free-for-all/Teams selector is hidden then.
- The creatures roll initiative as one more mover ("The Wolves 4"); if they win the roll they pick first/last at random. They move and act with the same computer rules as summons (aiMove/aiAct), no pick screen.
- XP (owner's choice): 50 to each human on the winning side (downed winners count, anyone who escaped does not); nothing if the creatures win.
- Control Person on a creature of the computer's side releases it (it does not vanish) when the spell ends.

## Colosseum online table, step 1: rooms (Oct 31, branch colosseum-online-rooms)
- Design (simpler than the handoff's "engine boundary"): the tablet stays the one real game (`colosseum.html`, rules untouched); phones are remote controls. Later steps send each player's option labels (from `options()`) to that player's phone and wait for the number tapped. Moves stay on the tablet map (they are public).
- Files: `net.js` (transport; Firebase Realtime Database with anonymous sign-in, or `?net=mem`, a localStorage fake so several tabs of one browser can test), `firebase-config.js` (public web-app settings of the owner's project colosseum-48705, Spark plan), `database.rules.json` (paste into the Firebase console, Realtime Database > Rules, Publish), `online-host.js` (the tablet's "Phones (online table)" card), `phone.html` (join page).
- Data: `rooms/CODE/host` (tablet uid), `pub` (open, np, seats {uid:{p,name,fighter}}; host writes, any signed-in user reads), `join/UID` (phone writes {name,on,t}; the host reads all), `priv/UID` (host to one phone), `cmd/UID` (one phone to host). Codes are 5 characters from A-Z/2-9 without I and O. The host path can only be created while empty, so nobody can take over a code.
- Lobby: phones are seated automatically at the first free player (up to the player count), the host can reassign (one phone per player), set "watching only", or remove a phone; a reloaded phone rejoins by itself (its anonymous identity and room are remembered); the tablet can reopen its table after a reload ("Reopen table CODE").
- Tests: `tests/online_test.py` (14, mem backend over a local http server). NOT tested by me: the real Firebase backend and the security rules (no internet in the test box; the emulator download is blocked). The owner must try it live.
- Not done yet: secret picks from phones (step 2), bell/wake lock/rejoin mid-fight (step 3), phone map for hex picks, phone-built characters, deleting stale rooms (rooms are removed when the tablet presses Close).

## Colosseum online table, step 2: secret picks from phones (Oct 31, branch colosseum-online-picks)
- How: `ui()` in colosseum.html ends with `Online.hook(c,t)` (online-host.js). While a player who has a seated phone is choosing (phases cover, pick, spells, dest, rcover, renew), the hook collects the tablet panel's own buttons, sends their labels to that phone (`priv/UID`: {seq,mode,text,btns,tg,ring,...}), blanks the options on the tablet ("Waiting for X's phone"), and clicks the matching tablet button when the phone writes `cmd/UID` {seq,k,i}. Commands with an old `seq` are ignored. The "pass the tablet" cover screens are skipped for phone players. Rules code is untouched.
- Phone shows: the question text, big option buttons, a Target row when there are 2+ enemies (same as clicking an enemy on the map), the spell list, renew toggles, and for disengage/retreat-type hex choices of a one-hex figure a list of directions (ahead and left, behind...). Choices that need far hexes (Teleport, creation spells with a hex) show "needs the map": the table can press "Play X's pick on the tablet instead" (also the fallback when a phone dies). "Ring again" re-sends with a counter; the phone shows a banner and buzzes if it can (real sound is step 3).
- Not done: moving, facing, advance/retreat choices from a phone (still on the tablet; the truly remote player needs the phone map), picking in parallel (picks are still one player at a time), bell sound, wake lock, phone-built characters.
- Tests: `tests/online_picks_test.py` (15, fake backend). Real Firebase path not tested by me except what the owner tries live.

## Colosseum online table, item 1: table names (Nov 1, branch online-table-name)
- The host types a table name (3 to 12 letters or digits, any case, e.g. STEVE) or leaves it empty for a random 5-character code. The tablet remembers the last name and offers it again; phones remember the table they joined. Closing the table (also how you "change the code") clears the phones and brings the name box back.
- Lock the table: `pub.locked`; phones already in can rejoin, new ones are refused (client message and the rules). Remove still works for one phone.
- A name held by another tablet is refused; a table whose `pub.t` is older than a day (the tablet republishes every 5 minutes while open) can be taken over, clearing its old phones. This is for a tablet whose browser data was cleared.
- Rules fixed: the host could not clear `join`, `priv` or `cmd` as a whole, so "Close the table" would have failed on real Firebase (the test fake does not enforce rules). `database.rules.json` must be pasted again in the console after this change.
- Links: "Join a table with your phone" card on index.html, "Join with a phone" link in colosseum.html's header line, "Menu" link on phone.html.
- Tests: `tests/online_test.py` now 24 (N1 to N10 cover names, in-use, lock, takeover). Real Firebase and rules still untested by me.

## Colosseum online table, item 2: characters from the phones (Nov 1, branch online-rosters)
- The phone page has a "Your character" box: the phone's own arena roster (`melee-arena-v1` in that phone's browser, so the same store the arena uses) plus whatever is open in the builder (`wizard-builder-v1`). Default: the builder's character, or the last one chosen. It can be changed before or after joining; "No character" leaves the seat to the host.
- The choice travels as `join/UID/fj` (JSON string, max 6000 characters: {name, st, dx, src, rec}; `src` is builder data, `rec` the phone's roster record without src). The tablet (online-host.js `loadFromPhones`) loads it into that phone's seat through `fromBuilder` + `setP` whenever no duel is on screen (G is null), once per change, so a fighter the host loads by hand is not overwritten until the phone changes its choice or seat. A phone that leaves its seat or brings nobody empties the seat it filled.
- XP: `awardXp` (colosseum.html) works on the record the phone sent (`f.phone.rec`), never on the tablet's own roster, then `Online.result` writes `res/UID` {id,key,rec+src}; the phone saves it into its own roster and tells the player (EP, attribute point waiting) and sends its updated character back, so the next duel at the table uses the new numbers. Spending the point and any further XP happen in the arena on the phone, until the next table session.
- Sanity: names are cut to 40 characters, `fromBuilder` clamps races/gear; stats and spells are otherwise trusted (friends' table; rules.js legality is not rechecked).
- Rules: join/$uid now allows only name, on, t, fj; new `res` node (host writes, the phone reads its own). `database.rules.json` must be pasted again in the console.
- Tests: `tests/online_chars_test.py` (14). Test mode keeps each phone tab's roster in sessionStorage.
- Not done: building a character on the phone from nothing without the builder page (the builder page is linked), computer-run seats.

## Colosseum online table: switching tables (Nov 1, branch online-switch-table)
- Phone: "Switch table" button at the top of the table card (with the table name); it leaves and clears the code box. A table that is closed or missing is forgotten (saved room cleared), so the next visit starts at the join screen. Selecting the code box selects its text.
- Tablet: opening a table closes this tablet's previous one (the name saved from last time), so old tables do not pile up; only its own host can (rules). 
- Bug fixed: a phone that left a table still had a registered "mark me offline on disconnect" write that recreated a nameless entry; `leaveRoom` now cancels it and the tablet ignores entries without a name.
- Version label now 5. Tests: `tests/online_switch_test.py` (9).

## Colosseum online table, item 3: bell, buzz, wake lock, rejoin (Nov 1, branch online-bell)
- `bell.js` (shared): `Bell.ring(i)` plays a two-strike bell (sine plus inharmonic overtones, Web Audio) at a pitch per player (C5, E5, G5, B5 for players 1 to 4); `Bell.buzz()` vibrates on Android (iPhones cannot vibrate from a web page); `Bell.awake(on)` holds the screen wake lock and takes it again when the page becomes visible. Browsers start sound only after a tap, so `Bell.unlock()` is called from Open the table, Join, Sound and Test buttons (and any pointerdown).
- Tablet (online-host.js): rings the player's pitch once when that player's pick (or spell renewal) starts on a phone (key = turn|pick index|phone), not on redraws; "Ring again" rings it again and makes the phone show a banner and ring/buzz; card has Bell on/off, a Test bell per phone, and keeps the tablet screen awake while a table is open.
- Phone: rings its own player's pitch and buzzes when a new pick arrives or Ring again is pressed; "Sound: on/off" button; keeps its screen awake after joining (a message says if the browser cannot). Rejoin: a phone that sleeps or reloads in the middle of its pick gets its choices back (the host's last message for it is still in the database); a reconnect rings again.
- Not testable here: the actual sound, vibration and screen lock. The tests (`tests/online_bell_test.py`, 13) check the calls, with the wake lock faked and a wrapper counting rings that really started.
- Version label 6. No rules change.

## Colosseum: Start button and starting facing with computer creatures (Nov 1, branch mob-start-fix)
- Bug: with a creature side chosen, all players are on one team, so the setup's "at least two teams" check hid the Start button (the tests started fights by code, so they missed it). Fixed: `tmOK=mobOn()||...`. The pre-fight preview also faced counters by team (default direction with a creature side); it now faces the creatures' end. The actual start already faced each figure at its nearest enemy. The setup text now says facing is changed during your own move (the small circles beside your counter).
- Test: `tests/colosseum_start_test.py` (9) clicks through the real buttons for 2 players against 3 wolves.

## Colosseum: "fight" instead of "duel", and Send to builder on the phone (Nov 1, branch fight-wording-send-builder)
- The Colosseum screens (colosseum.html, online-host.js) now say "fight" where they said "duel", since it is not only two people. duel.html and the "Melee Duel" link keep their name (it really is two players). Code names (quitDuel, duel2) are unchanged.
- Phone page: a "Send to builder (with XP)" button (same data as the arena's button: gear from the character's builder data plus name, ST, DX, IQ, total with earned points, EP, wins) writes the character into that phone's builder storage; the builder reads it when it opens. New XP records made by the Colosseum now keep the character's IQ. The XP result message says the point can be spent in the arena or the builder.
- Version label 7. Tests: online_chars_test now 16.

## Colosseum: one player against the computer (Nov 1, branch colosseum-solo)
- Players box now has "1 player (against the computer)". With one player a computer side is required (the picker has no "none"; choosing 1 player selects the Gladiator).
- New computer side "Gladiator" (CRE.man): a fighter made by the arena's `makeOpponent` (from the average ST+DX of the human players, so an even match; 1 to 3 of them; names like "Grak the Gladiator", II/III for more). It is a normal computer side ("mob", charcoal) run by the same `aiMove/aiAct` as the beasts, so it fights with a weapon and shield and does not cast spells (computer wizards are not in yet). XP to the human winners is the same 50 as for beasts (owner has not been asked about a different amount).
- A lone player has nobody to hide from: no "pass the tablet" cover screens, no "must not look" line (also for the spell-renew cover).
- `makeOpponent` no longer depends on the `me` global (uses the first player's fighter), so tests/fuzzers that fill slots directly work.
- Tests: `tests/colosseum_solo_test.py` (9) through the real buttons; `tests/fuzz/colosseumfz.py` now includes solo layouts (45 games per run; a couple of stalemates are normal).

## Colosseum: changing the setup in the middle of a fight (Nov 1, branch setup-change-midfight)
- The Players, computer-side, count, mode and team boxes used to snap back silently while a fight was running (only a grey note), so a player who switched to "1 player" mid-fight kept getting the old 2-player setup. They now ask "A fight is in progress. Leave it and change the setup?"; Yes starts the setup again with the new choice, No keeps the fight. Tests L10 to L13 in `tests/colosseum_solo_test.py` (13).

## Colosseum: setup boxes out of step with the game after a reload (Nov 1, branch setup-boxes-match-state)
- Bug (owner's phone): after a reload the browser restored the Players box to the last choice ("1 player") but the game restarted at NP=2, so the next click (e.g. a creature) ran a 2-player setup while the box said 1. Fixed two ways: `refreshPlayers()` sets the Players and team boxes from the game's own state, and the setup selects carry `autocomplete="off"` so the browser does not restore them. The last setup (players, mode, computer side, count) is now remembered on the device (`colosseum-setup` in localStorage) and comes back after a reload; one player with no computer side becomes the Gladiator.
- Tests L14, L15 in `tests/colosseum_solo_test.py` (15).

## Colosseum online table, item 4: the phone map (Nov 1, branch phone-map)
- Every message from the tablet to a seated phone now carries a small scene `sc` (board hexes, created objects, figures with facing/colour/letter/state, a one-line ST list). The phone draws it with `phone-map.js` (same hex geometry as colosseum.html, pointy-top, entrances shaded); a phone that is only waiting still shows the live board. "Show the whole board" / "Zoom to the action" button; the character box moves below the table card once joined.
- Steps a phone can now do itself (the hook in online-host.js, `PUB` phases): who moves first or second (`choose`), the move (tap a highlighted hex, six facing circles plus Turn left / Turn right buttons, End movement, Undo move, escape through the door asked on the phone), far-hex choices in `dest` (Teleport, creation spells; one-hex disengage keeps its direction buttons and also taps), the retreat hexes plus Skip, and Advance / Stay. Hex choices that cannot be undone (dest, retreat) need a second tap or a Confirm button; ordinary move taps go straight through (Undo exists).
- Commands from the phone: `{k:"h",i:"q,r"}` a hex, `{k:"f",i:d}` a facing 0 to 5 (besides `b` option and `t` target). The host does the same few lines the tablet's map click does (drawMap handlers); if those change, change `hook` too. After every command the host forgets its last message so a tap that changes nothing still gets a fresh answer.
- Tablet: during a phone's public step the panel says "X is deciding on their phone" with Ring again and "Play X's move on the tablet instead"; the tablet map stays clickable for the host. The bell now also rings for each phone-run step (who moves first, each move, retreat/advance), not only picks.
- No change to `database.rules.json` (priv and cmd take any data). Version label 8 (phone map).
- Not done: status effects in the phone's ST line (only down/asleep/flying/invisible), pinch zoom, the phone-side "Fight a friend online" start flow, several phones picking at once.
- Tests: `tests/online_map_test.py` (21); `online_bell_test` counts changed because moves ring too.

## Colosseum: wording for 1 to 4 players, bigger facing controls (Nov 1, branch colosseum-wording-facing)
- Intro, map caption and menu card now say one to four players (and mention phones). On the tablet's map the facing circles are larger (visible r .27, tap r .5), and the move panel has Turn left / Turn right buttons like the phone's.

## Megahex Sleep (Nov 2, branch megahex-sleep; Spell Reference Booklet)
- IQ 16, 8 ST, a thrown spell. Two ways to cast it, both listed in the spell menu: "on the enemy" (any one creature of basic ST 50 or less, in front or adjacent, DX −1 per hex like other thrown spells; it then works exactly like Sleep) and "on a megahex": you pick a centre hex on the map (like Slippery Floor; DX needed is your casting number minus the hexes to the centre); every real figure with basic ST under 20 in that hex or next to it falls asleep, friends and your own creatures included, never the wizard; images and illusions are skipped; a Spell Shield protects its figure; sleepers wake when hit, as before. The centre is offered only if someone would be affected. Cast-costs 8 ST and a miss costs 1 as usual.
- In wizard-arena.html (Unlimited Arena), duel.html and colosseum.html (same code in all three: `mslpHit`, `creaHexes(...,"mslp")`, `c.on==="mh"`). The pick of the centre travels with `G.destX.on`, so phones use the phone map for it.
- Computer wizards do not cast it (not in their spell lists). Not done: Megahex Avert (needs a shared upkeep: one ST a turn for the whole group, today's Avert upkeep is per victim), the 3-/4-/7-Hex Fire, Shadow and Wall.
- Tests: `tests/megahex_sleep_test.py` (9, arena), `tests/megahex_sleep_multi_test.py` (3, colosseum and duel).

## Spending earned points in the Colosseum, and the builder following along (Nov 2, branch spend-point-sync-builder)
- Owner's report (playing only on the phone): a point earned at the table had no place to be spent, and the builder did not show the EP earned. Before this, points could only be spent in the solo arena and the builder only changed through the manual "Send to builder (with XP)" button.
- New shared `roster.js` (`Roster.options/spend/syncBuilder`; the rules are the arena's `spend()`: +1 ST, +1 DX, +1 IQ for wizards, or Bank it when only one point is waiting and not a champion).
- Phone: a "has an attribute point to spend" box with those buttons under the character box; spending updates the phone's roster record, sends the new numbers to the table, and keeps the builder in step. When experience arrives from the table, the builder on that phone is updated at once if it holds the same character (matched by name; only ST, DX, IQ, total, EP and arena wins change, gear and spells stay). A builder holding a different character is never touched.
- Tablet (a fighter loaded from the tablet's own builder or roster): the Fighters box shows the same buttons; awarded XP also updates the tablet's builder if it holds that character. Fighters that came from a phone show "spend it on that phone".
- Not done: a 16-win champion retiring by spending (the arena's Hall of Fame entry is not made from the Colosseum).
- Tests: `tests/spend_tablet_test.py` (6), `online_chars_test` now 21.

## Phone: short option names (Nov 2, branch phone-short-options)
- Owner: too many words on the phone's pick screen. Options now show only the name before the first " (" (when the bracket is longer than 18 characters); a "Show what each choice does" button (remembered on that phone) adds the bracketed detail under each name. The seat note under "You are Player N" is hidden unless it says something unusual. `splitLabel` in phone.html; test P1/P1b in online_picks_test (16).


## Builder: gear help under a menu (Nov 2, branch builder-gear-help-menu)
- The two long paragraphs under the weapon boxes (hands, slings, sheaths) are now in a closed "How the hands, slings and sheaths work" menu, so the page is shorter on a phone. The gear section is redrawn when you change a choice, so an opened menu closes again.

## Licence (Nov 2, branch licence)
- Added LICENSE (all rights reserved, copyright holder "Zaddiq", Steve Jackson Games IP excluded), README.md, and a copyright line in the index footer. The repo is still public (owner chose to keep it public for now). If the owner goes private/other host later, see the options discussed Nov 2: private repo + Cloudflare Pages/Netlify, an obfuscated publish build, server-side rules only if it takes off. Owner should confirm the holder name and year in LICENSE.

## Colosseum online table: everyone picks at the same time (Nov 2, branch simultaneous-picks)
- At the start of a turn's secret picks (`beginActions`), every player with a seated phone gets their own pick session (online-host.js `sess`, `sessView`): action, spell, far-hex map step (tap, then confirm) with Back, the target buttons, and a "Your pick is in ... Change my pick" step. All phones answer at once. The tablet's own players (no phone) go first, one after another with the cover screen, as before (`Online.begin` reorders `G.pq`: tablet players first).
- Nothing is handed to the game until every phone session is done (so a phone can still change its pick): then `Online.ready(u)` (called at the top of `startPick`) returns each stored act and the game takes them in order and resolves the turn. The engine's own pick code is unchanged except `beginActions`, `startPick` and the new `pickNote(u,o,opts)` (the "why can't I attack" sentence, shared with the sessions).
- Tablet panel while phones are picking: "Everyone with a phone is picking at the same time. Waiting for: A, B" plus Ring again (only players still to pick) and a "Play X on the tablet instead" button per waiting phone (drops that phone's session; X then picks on the tablet when the game reaches them). Bell: every phone player's own pitch rings on the tablet at the start, 0.7 s apart; each phone rings its own.
- Not simultaneous: the move (still in initiative order, public) and the spell-renewal step. The old tablet-driven phone pick code in the hook (pick/spells/dest branches) still exists for the case where a session is not active.
- Tests: online_picks_test (20, rewritten), online_bell_test (13, rewritten), online_map_test (M14 to M16 now use a session). Real Firebase not tested by me.


## Colosseum online table: phone layout v2 (Nov 2, branch phone-layout-v2)
- Phone during a fight: map first and sticky at the top (max 40% of the screen), then the question and the choices, then a sticky "What just happened" strip at the bottom (last 3 log lines, "Show more" for 8). The character/load/save box is hidden while a fight is on (`lv` flag in every message) and comes back when it is over.
- Every message to a phone now carries `lg` (last 8 log lines, plain text, so the to-hit target and roll and the damage show) and `lv` (1 while a fight is on). Added in `sendTo`.
- Megahex outlines: board hexes are now `[q,r,end,megahex]`. phone-map.js draws a heavy line where the next hex is another megahex when `mega` is set; the move-cost numbers show only when it is off. A button under the map switches (default outlines, remembered in `colosseum-phone-mega`).
- Starting hex on the phone: before the fight, a seated phone gets the board with its own entrance's free hexes tappable (hk "start", taps answered at once). It sets `starts[p]`, the same as the tablet's tap. The tablet can still change it. Test: tests/online_layout_test.py (15). Version label: Table version 9 (map on top).

## Fight a friend online (Nov 2, branch fight-friend-online)
- Menu card "Fight a friend online" opens colosseum.html?friend=1: two players, free for all, the table opens by itself (random name), the host device is Player 1 (its seat is reserved, a joining phone gets Player 2), and `window.FRIEND` skips the pass-the-tablet cover screens (pick and renew) because the only other player is far away. A box at the top shows the table name, the link and whether the friend has joined. The "Phones" card is hidden in this mode. If the host page closes the fight ends for both.
- The friend uses phone.html as always (own character, secret pick, map). If they bring no character, the host loads Player 2's box. Test: tests/online_friend_test.py (6). No database rules change.

## Many-hex Fire, Shadow and Wall (Nov 2, branch multihex-spells)
- 3-Hex Fire/Shadow (IQ 12, 2 ST), 3-Hex Wall (IQ 13, 4), 7-Hex Shadow (IQ 15, 3), 7-Hex Fire (IQ 16, 4), 7-Hex Wall (IQ 16, 6): booklet numbers. There are no 4-hex versions of these in the booklet.
- Shape (the owner's idea, to avoid a connected-hex picker): you choose one hex (the usual creation pick, so the phones need nothing new); `multiCells` lays that hex plus the next hexes of the dragon footprint (`fpAt`: 3 = first three of the 4-hex shape, 7 = the 7-hex shape), turned to the facing that lays the most hexes, nearest the enemy on a tie. Hexes that cannot hold it are left out (off the board, a wall already there, a figure for a wall, the wizard's own hex for fire). Fire hurts each figure in the area 2 hits once. Same patch in colosseum.html, wizard-arena.html, duel.html. Test: tests/multihex_spells_test.py (13 per page). Not done: Megahex Avert.
- Possible later: let the player choose the facing of the shape (it is automatic now), and show the shape on the map before confirming.
