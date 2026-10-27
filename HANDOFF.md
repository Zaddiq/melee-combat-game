# Handoff notes (read this first in a new chat)

**What this is:** browser versions of The Fantasy Trip (Melee and Wizard) in single-file HTML/JS pages. Repo: https://github.com/Zaddiq/melee-combat-game · Site: https://zaddiq.github.io/melee-combat-game/

**Authoritative rules:** the owner's own Melee Third Edition 2018 and Wizard 2018 PDFs (not committed; ask the owner to attach them). Keep characters "Melee legal". Design decisions and guessed rules are in `NOTES.md`.

**Pages:** `builder.html` (characters, spell table), `arena.html` (now called **Arena Classic**; Melee arena, FROZEN: do not change except what the owner asks), `wizard-arena.html` (now called **Unlimited Arena**, no longer beta; Wizard arena, 1 human vs computer plus summons). The owner decided to keep both pages, not merge them, `duel.html` (two humans on one device, secret orders). Shared: `rules.js`, `maps.js` (Wizard hex map).

**Owner preferences:** one feature at a time (save tokens); the owner tests it themselves; Claude makes branches, merges to main and pushes; no mid-fight saving; opponents "just a little harder than originally"; duel XP rules in NOTES.md.

**Tests** (Playwright headless, `pip install playwright`): `python3 tests/rules_test.py` (70, Melee arena), `python3 tests/spells_test.py` (116, Wizard arena), `python3 tests/duel_summon_test.py` (9). Random-play fuzzers are in `tests/fuzz/` (they were written in a scratch folder; fix the file paths at the top before running).

**Git quirks:** tags can't be pushed through the proxy; push branches one at a time if a combined push disconnects.

**Done:** Melee arena, builder, Wizard arena and duel with spells through Confusion and Shock Shield, Reverse Missiles, Flight, Teleport, creation spells, summons (Wolf, Myrmidon, Bear, Gargoyle, Giant), Image/Illusion/Dispel Illusions, Avert, Invisibility, Mage Sight, Control Person/Animal, Slippery Floor, Giant Rope, Reveal Magic (all one-hex spells are in), flying Gargoyle (natural flier, MA 16 in the air), multi-figure engine, +1 IQ for wizards when spending earned points. Creature opponents in the Unlimited Arena (Oct 27): single Wolf, Bear, Gargoyle or Giant from the opponent list at book stats, always an even match (50 EP, recorded); a random opponent is a creature (20%) when its book ST+DX is within 2 of the player's; in a champion's fights 14 to 16 a Gargoyle can be the random opponent at any ST+DX. Builder sheet scrolls on its own on wide screens (Oct 27).

**Deferred ideas:** more builder layout tweaks (done Oct 26: gear above spells, page links and save buttons above the sheet; still open: the ~3000 px spell list, the sheet column being taller than a short window, single-column stacking below 860 px; the owner had no preference on device or on how the spell list should change, so ask before redesigning the spell list); Human/Computer choice per duel side (and computer vs computer); two humans vs creatures (team play); doubles of real figures; multi-hex images/illusions/creations; dragons; orders to creatures; hidden movement for Invisibility; a figure in an adjoining hex freeing someone else's Rope; spells still not in: the multi-hex versions (3-/4-/7-Hex Fire, Shadow, Image, Illusion, Wall), Megahex Avert and Megahex Sleep, Summon Small Dragon and Summon Dragon. The owner is holding the multi-hex work until flying over a figure is worked out.

**Known limits:** fliers can't pass over another figure; fire damage uses shortest path count; Lightning doesn't blast walls; minions can't grapple; some random duels stalemate legitimately. Live site and tablet play not verified by Claude.
