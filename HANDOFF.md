# Handoff notes (read this first in a new chat)

**What this is:** browser versions of The Fantasy Trip (Melee and Wizard) in single-file HTML/JS pages. Repo: https://github.com/Zaddiq/melee-combat-game · Site: https://zaddiq.github.io/melee-combat-game/

**Authoritative rules:** the owner's own Melee Third Edition 2018 and Wizard 2018 PDFs (not committed; ask the owner to attach them). Keep characters "Melee legal". Design decisions and guessed rules are in `NOTES.md`.

**Pages:** `builder.html` (characters, spell table), `arena.html` (Melee arena, FROZEN: do not change except what the owner asks), `wizard-arena.html` (Wizard arena, 1 human vs computer plus summons), `duel.html` (two humans on one device, secret orders). Shared: `rules.js`, `maps.js` (Wizard hex map).

**Owner preferences:** one feature at a time (save tokens); the owner tests it themselves; Claude makes branches, merges to main and pushes; no mid-fight saving; opponents "just a little harder than originally"; duel XP rules in NOTES.md.

**Tests** (Playwright headless, `pip install playwright`): `python3 tests/rules_test.py` (70, Melee arena), `python3 tests/spells_test.py` (101, Wizard arena), `python3 tests/duel_summon_test.py` (8). Random-play fuzzers are in `tests/fuzz/` (they were written in a scratch folder; fix the file paths at the top before running).

**Git quirks:** tags can't be pushed through the proxy; push branches one at a time if a combined push disconnects.

**Done:** Melee arena, builder, Wizard arena and duel with spells through Confusion and Shock Shield, Reverse Missiles, Flight, Teleport, creation spells, summons (Wolf, Myrmidon, Bear, Gargoyle, Giant), Image/Illusion/Dispel Illusions, Avert, Invisibility, Mage Sight, Control Person/Animal, Slippery Floor, Giant Rope, Reveal Magic (all one-hex spells are in), multi-figure engine, +1 IQ for wizards when spending earned points.

**Deferred ideas:** Human/Computer choice per duel side (and computer vs computer); two humans vs creatures (team play); doubles of real figures; multi-hex images/illusions/creations; dragons, flying Gargoyle; orders to creatures; hidden movement for Invisibility; a figure in an adjoining hex freeing someone else's Rope; spells still not in: the multi-hex versions (3-/4-/7-Hex Fire, Shadow, Image, Illusion, Wall), Megahex Avert and Megahex Sleep, Summon Small Dragon and Summon Dragon. The owner is holding the multi-hex work until flying over a figure is worked out.

**Known limits:** fliers can't pass over another figure; fire damage uses shortest path count; Lightning doesn't blast walls; minions can't grapple; some random duels stalemate legitimately. Live site and tablet play not verified by Claude.
