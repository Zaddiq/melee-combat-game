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
