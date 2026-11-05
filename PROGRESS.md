# Colosseum: what is done (updated Nov 4, 2026)

Everything below is merged to `main` and live at https://zaddiq.github.io/melee-combat-game/ (hard-refresh; the footer should say "Table version 9").

## Built this session
- **Phone map**: phones show the board and move, turn, pick advance/retreat and far-hex spell targets themselves. Facing circles are bigger. Wording is now "1 to 4 players".
- **Megahex Sleep** (all three pages: Colosseum, Arena, Duel). Not done: Megahex Avert, 3-/4-/7-Hex Fire, Shadow, Wall (on hold).
- **XP and points**: spend an earned attribute point on the tablet and on the phone; XP and stats sync into the builder.
- **Shorter phone option names** with a "Show what each choice does" toggle; builder gear help is under a dropdown.
- **Licence**: LICENSE, README and a footer line (all rights reserved; Steve Jackson Games' material excluded). Please confirm the holder name and year.
- **Everyone picks at the same time**: phone players pick together, tablet players go first.
- **Phone layout v2**: map pinned at the top, choices under it, "What just happened" strip pinned at the bottom (to-hit number, roll, damage). Load/save box hidden during a fight. Megahex outlines by default, with a button to switch to range numbers. Phones choose their own starting hex.
- **Fight a friend online**: menu card, opens a table by itself, you are Player 1, friend joins by table name, no pass-the-tablet screens. If the host page closes, the fight ends.

## Not tested live
Real Firebase, real phone sound/vibration, wake lock. All tests use the fake backend (`?net=mem`). Test suites are in `tests/` (all pass).

## Backlog (see HANDOFF.md)
Multi-hex spells (your new idea first), compact phone setup, computer-run seats, lifting the two-weapon limit (ask: Colosseum-only house rule?), how-to-play page, feedback button, the stomp, encounter page. After friends have tried it: installable web app, private repo or obfuscated build, contacting Steve Jackson Games.

## To resume
Tell Claude to read HANDOFF.md and NOTES.md in the repo Zaddiq/melee-combat-game, then say what you want next.

## Added after the first version of this file
- Many-hex Fire, Shadow and Wall (3 and 7 hexes, dragon-shaped footprint).
- Voice chat (Join voice / Listen only / Mute; new Firebase rules were needed).
- Character pictures: builder upload, printed sheet, picture counters that turn with the facing.
- New black-and-white character sheets: blank (menu card) and the builder's filled-in printout.
- Phone fixes from the first solo playtest: choose start facing, End movement always on screen, connection info at the bottom.

## Waiting on you
- Easier start for new characters (first 4 points after 32) and a fairer rating for wizards: tell me which page you found too hard (Colosseum or Unlimited Arena) and say "build it".
- Your forgotten "new idea".
- Try voice chat and Fight a friend with a real friend.
