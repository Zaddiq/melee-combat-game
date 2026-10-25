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
