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
- **Summons** (Wolf 2 ST IQ 9, Myrmidon 2 ST IQ 10, Bear 4 ST IQ 11, Gargoyle 4 ST IQ 13, Giant 4 ST IQ 14, each +1 ST a turn): a creation spell, so a to-hit roll with no range penalty and a free hex in your megahex or next to it. The creature cannot move or fight on the turn it appears. It is run by the computer on its owner's side. When you do not pay its 1 ST in the renew step it vanishes; at 0 ST it dies. The Gargoyle does not fly yet. Dragons are not in.
- **Targets:** with more than one enemy on the map, the nearest is your default target; click another enemy counter (dashed ring) to change it. Spells, missiles and attacks go at the chosen target.
- **Not in for minions:** hand-to-hand (they cannot grapple and cannot be grappled), forced-retreat choices for your own minions (done automatically), controlling a creature yourself (they attack the nearest enemy), and dragons.
- Tests S51 to S55.

## Random opponents, eased back
The "always the best weapon, always the most armor at adjDX 11" rule made the arena too hard. The arena and Wizard arena now use the original random generator again, but keep three acceptable fighters and take the best of them (more damage plus 0.7 per hit stopped). That is a little tougher than a pure random pick, not a maximised build. The "winnable for both sides" checks are unchanged.

### Summons and many figures in the duel
The duel now uses the same figure list as the Wizard arena. Summoned creatures are run by the computer on their owner's side, move after their owner moves, and pick their own actions. Each player has a default target (the nearest enemy) and can click another enemy counter, with the dashed rings, while moving or choosing an action. Creature upkeep (1 ST each, in the secret renew step), vanishing, and retreat rules are as in the Wizard arena. XP, escape and "quit" still only involve the two players' own figures. Tests: tests/duel_summon_test.py (D1 to D5).
Still not in: giving orders to a creature, creatures in hand-to-hand, dragons, flying gargoyles.

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
